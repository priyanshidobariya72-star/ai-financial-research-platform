from __future__ import annotations

from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class ApiEndpointTests(TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    @patch("app.api.router.analysis_service.analyze_company")
    def test_analyze_endpoint(self, analyze_company) -> None:
        analyze_company.return_value = {
            "ticker": "NVDA",
            "company_name": "NVIDIA Corporation",
            "sector": "Technology",
            "industry": "Semiconductors",
            "website": "https://www.nvidia.com",
            "business_summary": "Summary",
            "market_cap": 1.0,
            "trailing_pe": 2.0,
            "price_summary": {
                "current_price": 3.0,
                "change": 0.5,
                "change_percent": 10.0,
                "period_high": 3.5,
                "period_low": 2.5,
            },
            "recent_news": [],
            "recommendation": {
                "label": "Hold",
                "confidence": 0.68,
                "reasoning_summary": "Structured recommendation summary.",
                "what_would_change_view": "Cheaper valuation and stronger momentum.",
                "signals": {
                    "fundamentals": "neutral",
                    "technicals": "positive",
                    "news_sentiment": "unknown",
                    "business_risk": "cautious",
                },
                "disclaimer": "This is an automated research summary for informational purposes, not financial advice.",
            },
        }

        response = self.client.post("/analyze", json={"ticker": "NVDA"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ticker"], "NVDA")
        self.assertEqual(response.json()["recommendation"]["label"], "Hold")

    @patch("app.api.router.analysis_service.compare_companies")
    def test_compare_endpoint(self, compare_companies) -> None:
        compare_companies.return_value = {
            "ticker1": "NVDA",
            "ticker2": "AMD",
            "metrics": [
                {"label": "Market Cap", "ticker1_value": 1, "ticker2_value": 2},
            ],
        }

        response = self.client.post("/compare", json={"ticker1": "NVDA", "ticker2": "AMD"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["metrics"]), 1)

    @patch("app.api.router.chat_service.answer")
    def test_chat_endpoint(self, answer) -> None:
        answer.return_value = {
            "answer": "Planner and market agents found supportive evidence.",
            "citations": [{"source": "nvda.pdf", "page": 12, "chunk_id": "doc-1-chunk-1"}],
        }

        response = self.client.post("/chat", json={"query": "How did revenue grow?", "k": 3})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["citations"][0]["source"], "nvda.pdf")

    @patch("app.api.router.rag_service.ingest_upload")
    def test_upload_endpoint(self, ingest_upload) -> None:
        ingest_upload.return_value = {
            "document_id": "doc-123",
            "filename": "report.pdf",
            "chunks_indexed": 8,
            "collection_name": "financial_documents",
        }

        response = self.client.post(
            "/upload",
            files={"file": ("report.pdf", b"%PDF-1.4 sample", "application/pdf")},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["chunks_indexed"], 8)
