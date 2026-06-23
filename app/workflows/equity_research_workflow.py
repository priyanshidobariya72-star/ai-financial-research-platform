from __future__ import annotations

import re
from typing import Any, TypedDict

from app.api.schemas import ChatResponse
from app.logger import get_logger
from app.rag.schemas import Citation

logger = get_logger(__name__)


class WorkflowState(TypedDict, total=False):
    query: str
    k: int
    tickers: list[str]
    planner_notes: str
    market_summary: str
    news_summary: str
    rag_summary: str
    report_draft: str
    critique: str
    final_answer: str
    citations: list[Citation]


class EquityResearchWorkflow:
    """Coordinate planner, market, news, RAG, report, and critic agents."""

    def __init__(self, analysis_service: Any, rag_service: Any) -> None:
        self.analysis_service = analysis_service
        self.rag_service = rag_service

    def run(self, query: str, k: int = 4) -> ChatResponse:
        initial_state: WorkflowState = {
            "query": query,
            "k": k,
            "tickers": [],
            "citations": [],
        }
        state = self._run_graph(initial_state)
        return ChatResponse(
            answer=state.get("final_answer") or "No answer could be generated.",
            citations=state.get("citations", []),
        )

    def _run_graph(self, initial_state: WorkflowState) -> WorkflowState:
        try:
            from langgraph.graph import END, START, StateGraph
        except ImportError:
            logger.warning("langgraph is not installed; running workflow sequentially.")
            return self._run_sequential(initial_state)

        graph = StateGraph(WorkflowState)
        graph.add_node("planner", self._planner_agent)
        graph.add_node("market", self._market_agent)
        graph.add_node("news", self._news_agent)
        graph.add_node("rag", self._rag_agent)
        graph.add_node("report", self._report_agent)
        graph.add_node("critic", self._critic_agent)
        graph.add_edge(START, "planner")
        graph.add_edge("planner", "market")
        graph.add_edge("market", "news")
        graph.add_edge("news", "rag")
        graph.add_edge("rag", "report")
        graph.add_edge("report", "critic")
        graph.add_edge("critic", END)

        compiled = graph.compile()
        return compiled.invoke(initial_state)

    def _run_sequential(self, state: WorkflowState) -> WorkflowState:
        for node in (
            self._planner_agent,
            self._market_agent,
            self._news_agent,
            self._rag_agent,
            self._report_agent,
            self._critic_agent,
        ):
            state = node(state)
        return state

    def _planner_agent(self, state: WorkflowState) -> WorkflowState:
        query = state["query"]
        tickers = self._extract_tickers(query)
        planner_notes = (
            "Plan: collect market context, recent news, and document evidence before drafting an answer."
        )
        return {
            **state,
            "tickers": tickers,
            "planner_notes": planner_notes,
        }

    def _market_agent(self, state: WorkflowState) -> WorkflowState:
        tickers = state.get("tickers", [])
        if not tickers:
            return {**state, "market_summary": "Market agent: no ticker detected in the query."}

        insights: list[str] = []
        for ticker in tickers[:2]:
            try:
                analysis = self.analysis_service.analyze_company(ticker)
            except Exception as exc:
                logger.warning("Market agent failed for %s: %s", ticker, exc)
                insights.append(f"{ticker}: market data unavailable.")
                continue

            insights.append(
                (
                    f"{ticker}: recommendation {analysis.recommendation.label}, "
                    f"current price {analysis.price_summary.current_price}, "
                    f"1M change {analysis.price_summary.change_percent}%, "
                    f"trailing P/E {analysis.trailing_pe}."
                )
            )
        return {**state, "market_summary": " ".join(insights)}

    def _news_agent(self, state: WorkflowState) -> WorkflowState:
        tickers = state.get("tickers", [])
        if not tickers:
            return {**state, "news_summary": "News agent: no ticker detected in the query."}

        headlines: list[str] = []
        for ticker in tickers[:2]:
            try:
                analysis = self.analysis_service.analyze_company(ticker)
            except Exception as exc:
                logger.warning("News agent failed for %s: %s", ticker, exc)
                continue

            for article in analysis.recent_news[:3]:
                headlines.append(f"{ticker}: {article.title}")

        summary = " | ".join(headlines) if headlines else "News agent: no recent news was available."
        return {**state, "news_summary": summary}

    def _rag_agent(self, state: WorkflowState) -> WorkflowState:
        try:
            retrieval = self.rag_service.retrieve(query=state["query"], k=state.get("k", 4))
        except Exception as exc:
            logger.warning("RAG agent failed: %s", exc)
            return {**state, "rag_summary": "RAG agent: no document evidence available.", "citations": []}

        if not retrieval.chunks:
            return {**state, "rag_summary": "RAG agent: no document evidence available.", "citations": []}

        citations = [self._normalize_citation(chunk.citation) for chunk in retrieval.chunks[:3]]
        snippets = [chunk.content.strip().replace("\n", " ") for chunk in retrieval.chunks[:3]]
        return {
            **state,
            "rag_summary": " ".join(snippets),
            "citations": citations,
        }

    def _report_agent(self, state: WorkflowState) -> WorkflowState:
        sections = [
            state.get("planner_notes"),
            state.get("market_summary"),
            state.get("news_summary"),
            state.get("rag_summary"),
        ]
        report_draft = " ".join(section for section in sections if section)
        return {**state, "report_draft": report_draft}

    def _critic_agent(self, state: WorkflowState) -> WorkflowState:
        draft = state.get("report_draft", "").strip()
        if not draft:
            final_answer = "No answer could be produced from the available market, news, or document sources."
            critique = "Critic: insufficient evidence."
        else:
            critique = "Critic: answer grounded in tool outputs; treat any recommendation as informational only."
            final_answer = f"{draft} {critique}"

        return {
            **state,
            "critique": critique,
            "final_answer": final_answer,
        }

    @staticmethod
    def _extract_tickers(query: str) -> list[str]:
        stopwords = {
            "A",
            "AN",
            "AND",
            "ARE",
            "AT",
            "BUY",
            "FOR",
            "HOLD",
            "HOW",
            "I",
            "IF",
            "IN",
            "IS",
            "IT",
            "ME",
            "NOW",
            "OF",
            "ON",
            "OR",
            "RIGHT",
            "SELL",
            "SHOULD",
            "THE",
            "TO",
            "VS",
            "WHAT",
            "WITH",
        }
        tickers = [token for token in re.findall(r"\b[A-Z]{1,5}\b", query.upper()) if token not in stopwords]
        seen: list[str] = []
        for ticker in tickers:
            if ticker not in seen:
                seen.append(ticker)
        return seen[:2]

    @staticmethod
    def _normalize_citation(citation: Any) -> Citation:
        if isinstance(citation, Citation):
            return citation
        return Citation(
            source=getattr(citation, "source", "unknown"),
            page=getattr(citation, "page", None),
            chunk_id=getattr(citation, "chunk_id", None),
        )
