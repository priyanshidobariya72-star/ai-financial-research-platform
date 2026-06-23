from __future__ import annotations

from types import SimpleNamespace
from unittest import TestCase

from app.api.schemas import NewsItem, PriceSummary, Recommendation, RecommendationSignals
from app.workflows import EquityResearchWorkflow


class _AnalysisServiceStub:
    def analyze_company(self, ticker: str):
        return SimpleNamespace(
            ticker=ticker,
            trailing_pe=24.0,
            price_summary=PriceSummary(current_price=150.0, change_percent=9.5),
            recent_news=[
                NewsItem(title=f"{ticker} reports strong demand", source_name="Reuters"),
                NewsItem(title=f"{ticker} expands product line", source_name="Bloomberg"),
            ],
            recommendation=Recommendation(
                label="Buy",
                confidence=0.8,
                reasoning_summary="Positive setup.",
                what_would_change_view="Weaker earnings.",
                signals=RecommendationSignals(
                    fundamentals="neutral",
                    technicals="positive",
                    news_sentiment="positive",
                    business_risk="neutral",
                ),
                disclaimer="Informational only.",
            ),
        )


class _RagServiceStub:
    def retrieve(self, query: str, k: int = 4):
        chunk = SimpleNamespace(
            content="Annual report highlights margin expansion and AI demand.",
            citation=SimpleNamespace(source="nvda_10k.pdf", page=12, chunk_id="doc-1-chunk-1"),
        )
        return SimpleNamespace(chunks=[chunk])


class WorkflowTests(TestCase):
    def test_workflow_runs_end_to_end_without_langgraph(self) -> None:
        workflow = EquityResearchWorkflow(
            analysis_service=_AnalysisServiceStub(),
            rag_service=_RagServiceStub(),
        )

        result = workflow.run("Should I buy NVDA right now?", k=3)

        self.assertIn("NVDA", result.answer)
        self.assertIn("Annual report highlights margin expansion", result.answer)
        self.assertEqual(len(result.citations), 1)
        self.assertEqual(result.citations[0].source, "nvda_10k.pdf")
