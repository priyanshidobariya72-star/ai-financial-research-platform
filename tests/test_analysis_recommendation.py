from __future__ import annotations

from unittest import TestCase

from app.api.schemas import PriceSummary
from app.api.service import CompanyAnalysisService


class RecommendationTests(TestCase):
    def test_build_recommendation_returns_buy_for_positive_setup(self) -> None:
        recommendation = CompanyAnalysisService._build_recommendation(
            ticker="NVDA",
            trailing_pe=18.0,
            price_summary=PriceSummary(change_percent=12.0),
            recent_news=[
                {"title": "Revenue growth beats estimates", "description": "Strong profit and record demand."},
            ],
            business_summary="The company designs chips and software platforms.",
        )

        self.assertEqual(recommendation.label, "Buy")
        self.assertEqual(recommendation.signals.fundamentals, "positive")
        self.assertEqual(recommendation.signals.technicals, "positive")

    def test_build_recommendation_returns_avoid_for_negative_setup(self) -> None:
        recommendation = CompanyAnalysisService._build_recommendation(
            ticker="XYZ",
            trailing_pe=60.0,
            price_summary=PriceSummary(change_percent=-15.0),
            recent_news=[
                {"title": "Profit miss deepens decline", "description": "Company faces lawsuit and weak demand."},
            ],
            business_summary="The business faces competition, litigation, debt, and supply chain disruption.",
        )

        self.assertEqual(recommendation.label, "Avoid")
        self.assertEqual(recommendation.signals.news_sentiment, "negative")
        self.assertEqual(recommendation.signals.business_risk, "negative")
