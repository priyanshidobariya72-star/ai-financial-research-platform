from __future__ import annotations

from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock, patch

from app.tools.sentiment_tool import analyze_sentiment, enrich_article_with_sentiment, get_news_sentiment


class SentimentToolTests(IsolatedAsyncioTestCase):
    @patch("app.tools.sentiment_tool._get_finbert")
    def test_analyze_sentiment_returns_positive(self, get_finbert: Mock) -> None:
        torch = __import__("torch")
        tokenizer = Mock()
        tokenizer.return_value = {
            "input_ids": torch.tensor([[1]]),
            "attention_mask": torch.tensor([[1]]),
        }

        model = Mock()
        model.config.id2label = {0: "positive", 1: "negative", 2: "neutral"}
        output = Mock()
        output.logits = torch.tensor([[3.0, 1.0, 0.0]])
        model.return_value = output
        get_finbert.return_value = (tokenizer, model)

        result = analyze_sentiment("Apple beats earnings expectations")

        self.assertEqual(result["sentiment"], "positive")
        self.assertGreater(result["positive_score"], result["negative_score"])

    def test_analyze_sentiment_defaults_to_neutral_for_empty_text(self) -> None:
        result = analyze_sentiment("   ")
        self.assertEqual(result["sentiment"], "neutral")
        self.assertEqual(result["neutral_score"], 1.0)

    @patch("app.tools.sentiment_tool.analyze_sentiment")
    def test_enrich_article_with_sentiment_adds_fields(self, analyze_sentiment_mock: Mock) -> None:
        analyze_sentiment_mock.return_value = {
            "sentiment": "negative",
            "sentiment_score": 0.91,
            "positive_score": 0.02,
            "negative_score": 0.91,
            "neutral_score": 0.07,
        }

        enriched = enrich_article_with_sentiment(
            {
                "title": "Stock falls after guidance cut",
                "description": "Shares dropped in after-hours trading.",
                "url": "https://example.com/news",
            }
        )

        self.assertEqual(enriched["sentiment"], "negative")
        self.assertEqual(enriched["negative_score"], 0.91)

    async def test_get_news_sentiment_returns_empty_summary_when_no_rows(self) -> None:
        class _SessionFactory:
            def __call__(self):
                return self

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

            async def execute(self, _stmt):
                result = Mock()
                result.scalars.return_value.all.return_value = []
                return result

        with patch("app.tools.sentiment_tool.AsyncSessionLocal", _SessionFactory()):
            summary = await get_news_sentiment("AAPL")

        self.assertEqual(summary["symbol"], "AAPL")
        self.assertEqual(summary["article_count"], 0)
        self.assertEqual(summary["overall_sentiment"], "neutral")
