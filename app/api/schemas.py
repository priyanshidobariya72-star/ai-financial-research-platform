from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.rag.schemas import Citation


class AnalyzeRequest(BaseModel):
    ticker: str = Field(min_length=1)


class PriceSummary(BaseModel):
    current_price: float | None = None
    change: float | None = None
    change_percent: float | None = None
    period_high: float | None = None
    period_low: float | None = None


class NewsItem(BaseModel):
    title: str
    url: str | None = None
    published_at: str | None = None
    source_name: str | None = None


class RecommendationSignals(BaseModel):
    fundamentals: str
    technicals: str
    news_sentiment: str
    business_risk: str


class Recommendation(BaseModel):
    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_summary: str
    what_would_change_view: str
    signals: RecommendationSignals
    disclaimer: str


class AnalyzeResponse(BaseModel):
    ticker: str
    company_name: str | None = None
    sector: str | None = None
    industry: str | None = None
    website: str | None = None
    business_summary: str | None = None
    market_cap: float | None = None
    trailing_pe: float | None = None
    price_summary: PriceSummary
    recent_news: list[NewsItem]
    recommendation: Recommendation


class CompareRequest(BaseModel):
    ticker1: str = Field(min_length=1)
    ticker2: str = Field(min_length=1)


class CompareMetric(BaseModel):
    label: str
    ticker1_value: Any
    ticker2_value: Any


class CompareResponse(BaseModel):
    ticker1: str
    ticker2: str
    metrics: list[CompareMetric]


class ChatRequest(BaseModel):
    query: str = Field(min_length=1)
    k: int = Field(default=4, ge=1, le=20)


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
