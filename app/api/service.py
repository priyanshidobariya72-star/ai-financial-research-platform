from __future__ import annotations

from typing import Any

from app.api.schemas import (
    AnalyzeResponse,
    ChatResponse,
    CompareMetric,
    CompareResponse,
    NewsItem,
    PriceSummary,
    Recommendation,
    RecommendationSignals,
)
from app.logger import get_logger
from app.rag.service import DocumentRAGService
from app.tools.gnews_tool import fetch_news
from app.tools.yahoo_finance_tool import get_company_profile, get_stock_history

logger = get_logger(__name__)


class CompanyAnalysisService:
    def analyze_company(self, ticker: str) -> AnalyzeResponse:
        normalized = ticker.strip().upper()
        profile = get_company_profile(normalized)
        history = get_stock_history(normalized, period="1mo")
        recent_news = self._safe_fetch_news(profile.get("shortName") or normalized)

        return AnalyzeResponse(
            ticker=normalized,
            company_name=profile.get("longName") or profile.get("shortName"),
            sector=profile.get("sector"),
            industry=profile.get("industry"),
            website=profile.get("website"),
            business_summary=profile.get("longBusinessSummary"),
            market_cap=self._to_float(profile.get("marketCap")),
            trailing_pe=self._to_float(profile.get("trailingPE")),
            price_summary=self._build_price_summary(history),
            recent_news=[
                NewsItem(
                    title=article.get("title", "Untitled"),
                    url=article.get("url"),
                    published_at=article.get("publishedAt"),
                    source_name=(article.get("source") or {}).get("name"),
                )
                for article in recent_news[:5]
            ],
            recommendation=self._build_recommendation(
                ticker=normalized,
                trailing_pe=self._to_float(profile.get("trailingPE")),
                price_summary=self._build_price_summary(history),
                recent_news=recent_news[:5],
                business_summary=profile.get("longBusinessSummary"),
            ),
        )

    def compare_companies(self, ticker1: str, ticker2: str) -> CompareResponse:
        company1 = self.analyze_company(ticker1)
        company2 = self.analyze_company(ticker2)

        metrics = [
            CompareMetric(label="Company Name", ticker1_value=company1.company_name, ticker2_value=company2.company_name),
            CompareMetric(label="Sector", ticker1_value=company1.sector, ticker2_value=company2.sector),
            CompareMetric(label="Industry", ticker1_value=company1.industry, ticker2_value=company2.industry),
            CompareMetric(label="Market Cap", ticker1_value=company1.market_cap, ticker2_value=company2.market_cap),
            CompareMetric(label="Trailing P/E", ticker1_value=company1.trailing_pe, ticker2_value=company2.trailing_pe),
            CompareMetric(
                label="Current Price",
                ticker1_value=company1.price_summary.current_price,
                ticker2_value=company2.price_summary.current_price,
            ),
            CompareMetric(
                label="1M Change %",
                ticker1_value=company1.price_summary.change_percent,
                ticker2_value=company2.price_summary.change_percent,
            ),
        ]
        return CompareResponse(
            ticker1=company1.ticker,
            ticker2=company2.ticker,
            metrics=metrics,
        )

    @staticmethod
    def _build_price_summary(history: Any) -> PriceSummary:
        if history is None or getattr(history, "empty", True):
            return PriceSummary()

        closes = history["Close"].dropna()
        highs = history["High"].dropna()
        lows = history["Low"].dropna()
        if closes.empty:
            return PriceSummary()

        first_close = float(closes.iloc[0])
        last_close = float(closes.iloc[-1])
        change = last_close - first_close
        change_percent = (change / first_close * 100.0) if first_close else None

        return PriceSummary(
            current_price=round(last_close, 2),
            change=round(change, 2),
            change_percent=round(change_percent, 2) if change_percent is not None else None,
            period_high=round(float(highs.max()), 2) if not highs.empty else None,
            period_low=round(float(lows.min()), 2) if not lows.empty else None,
        )

    @classmethod
    def _build_recommendation(
        cls,
        *,
        ticker: str,
        trailing_pe: float | None,
        price_summary: PriceSummary,
        recent_news: list[dict[str, Any]],
        business_summary: str | None,
    ) -> Recommendation:
        fundamentals_signal, fundamentals_score = cls._score_fundamentals(trailing_pe)
        technicals_signal, technicals_score = cls._score_technicals(price_summary.change_percent)
        news_signal, news_score = cls._score_news_sentiment(recent_news)
        risk_signal, risk_score = cls._score_business_risk(business_summary)

        total_score = fundamentals_score + technicals_score + news_score + risk_score
        normalized_confidence = min(0.95, max(0.35, 0.5 + abs(total_score) / 10))

        if total_score >= 3:
            label = "Buy"
        elif total_score <= -2:
            label = "Avoid"
        else:
            label = "Hold"

        reasoning_summary = cls._build_reasoning_summary(
            ticker=ticker,
            label=label,
            fundamentals_signal=fundamentals_signal,
            technicals_signal=technicals_signal,
            news_signal=news_signal,
            risk_signal=risk_signal,
            trailing_pe=trailing_pe,
            change_percent=price_summary.change_percent,
        )

        return Recommendation(
            label=label,
            confidence=round(normalized_confidence, 2),
            reasoning_summary=reasoning_summary,
            what_would_change_view=(
                "A cheaper valuation, stronger price momentum, and fewer risk signals in company disclosures "
                "would improve this view. Weakening momentum or worsening news flow would reduce it."
            ),
            signals=RecommendationSignals(
                fundamentals=fundamentals_signal,
                technicals=technicals_signal,
                news_sentiment=news_signal,
                business_risk=risk_signal,
            ),
            disclaimer="This is an automated research summary for informational purposes, not financial advice.",
        )

    @staticmethod
    def _score_fundamentals(trailing_pe: float | None) -> tuple[str, int]:
        if trailing_pe is None:
            return "unknown", 0
        if trailing_pe <= 20:
            return "positive", 2
        if trailing_pe <= 35:
            return "neutral", 0
        return "negative", -2

    @staticmethod
    def _score_technicals(change_percent: float | None) -> tuple[str, int]:
        if change_percent is None:
            return "unknown", 0
        if change_percent >= 8:
            return "positive", 2
        if change_percent <= -8:
            return "negative", -2
        return "neutral", 0

    @classmethod
    def _score_news_sentiment(cls, recent_news: list[dict[str, Any]]) -> tuple[str, int]:
        if not recent_news:
            return "unknown", 0

        positive_keywords = {"beat", "growth", "surge", "record", "profit", "upgrade", "gain", "strong"}
        negative_keywords = {"miss", "drop", "lawsuit", "probe", "risk", "cut", "weak", "decline"}

        score = 0
        for article in recent_news:
            text = f"{article.get('title', '')} {article.get('description', '')}".lower()
            score += sum(1 for keyword in positive_keywords if keyword in text)
            score -= sum(1 for keyword in negative_keywords if keyword in text)

        if score > 0:
            return "positive", 1
        if score < 0:
            return "negative", -1
        return "neutral", 0

    @staticmethod
    def _score_business_risk(business_summary: str | None) -> tuple[str, int]:
        if not business_summary:
            return "unknown", 0

        risk_keywords = {
            "competition",
            "cyclical",
            "volatile",
            "regulation",
            "lawsuit",
            "litigation",
            "debt",
            "supply chain",
            "depend",
        }
        text = business_summary.lower()
        matches = sum(1 for keyword in risk_keywords if keyword in text)

        if matches >= 3:
            return "negative", -1
        if matches == 0:
            return "neutral", 0
        return "cautious", 0

    @staticmethod
    def _build_reasoning_summary(
        *,
        ticker: str,
        label: str,
        fundamentals_signal: str,
        technicals_signal: str,
        news_signal: str,
        risk_signal: str,
        trailing_pe: float | None,
        change_percent: float | None,
    ) -> str:
        pe_text = f"trailing P/E is {trailing_pe:.2f}" if trailing_pe is not None else "valuation data is limited"
        momentum_text = (
            f"1-month price change is {change_percent:.2f}%"
            if change_percent is not None
            else "recent momentum data is limited"
        )
        return (
            f"{label} view for {ticker}: fundamentals are {fundamentals_signal}, technicals are {technicals_signal}, "
            f"news flow is {news_signal}, and business risk reads as {risk_signal}. "
            f"Current context suggests {pe_text} and {momentum_text}."
        )

    @staticmethod
    def _safe_fetch_news(query: str) -> list[dict[str, Any]]:
        try:
            return fetch_news(query, max_articles=5)
        except Exception as exc:  # pragma: no cover - external API failure path
            logger.warning("News fetch failed for %s: %s", query, exc)
            return []

    @staticmethod
    def _to_float(value: Any) -> float | None:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None


class ChatService:
    def __init__(
        self,
        rag_service: DocumentRAGService | None = None,
        analysis_service: CompanyAnalysisService | None = None,
    ) -> None:
        self.rag_service = rag_service or DocumentRAGService()
        self.analysis_service = analysis_service or CompanyAnalysisService()

    def answer(self, query: str, k: int = 4) -> ChatResponse:
        from app.workflows import EquityResearchWorkflow

        workflow = EquityResearchWorkflow(
            analysis_service=self.analysis_service,
            rag_service=self.rag_service,
        )
        return workflow.run(query=query, k=k)
