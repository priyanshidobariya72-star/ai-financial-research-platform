from __future__ import annotations

from datetime import date
from unittest import TestCase
from unittest.mock import Mock, patch

from app.tools.gnews_tool import fetch_news


class GNewsToolTests(TestCase):
    @patch("app.tools.gnews_tool.httpx.Client")
    @patch("app.tools.gnews_tool.get_gnews_api_key", return_value="test-key")
    def test_fetch_news_returns_articles(self, _api_key: Mock, client_cls: Mock) -> None:
        response = Mock()
        response.json.return_value = {
            "articles": [
                {
                    "title": "Apple launches new product",
                    "description": "Apple announced a new device today.",
                    "url": "https://example.com/apple",
                    "publishedAt": "2026-06-01T10:00:00Z",
                    "source": {"name": "Example News"},
                }
            ]
        }
        response.raise_for_status = Mock()
        client_cls.return_value.__enter__.return_value.get.return_value = response

        articles = fetch_news(
            "AAPL",
            max_articles=5,
            from_date=date(2026, 6, 1),
            to_date=date(2026, 6, 2),
        )

        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["title"], "Apple launches new product")
        client_cls.return_value.__enter__.return_value.get.assert_called_once()

    def test_fetch_news_rejects_empty_query(self) -> None:
        with self.assertRaises(ValueError):
            fetch_news("  ")
