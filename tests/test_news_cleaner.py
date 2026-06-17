from __future__ import annotations

from datetime import datetime
from unittest import TestCase

from app.etl.cleaners.news_cleaner import clean_articles, dedupe_articles


class NewsCleanerTests(TestCase):
    def test_clean_articles_strips_html_and_deduplicates(self) -> None:
        raw_articles = [
            {
                "symbol": "AAPL",
                "title": "<b>Apple</b> rises",
                "description": "<p>Shares moved higher.</p>",
                "url": "https://example.com/aapl-1",
                "publishedAt": "2026-06-01T12:00:00Z",
                "source": {"name": "Market Watch"},
            },
            {
                "symbol": "AAPL",
                "title": "Duplicate article",
                "description": "Same URL",
                "url": "https://example.com/aapl-1",
                "publishedAt": "2026-06-01T13:00:00Z",
                "source": {"name": "Market Watch"},
            },
            {
                "symbol": "AAPL",
                "title": "",
                "description": "Missing title should be dropped",
                "url": "https://example.com/aapl-2",
                "publishedAt": "2026-06-01T14:00:00Z",
                "source": {"name": "Market Watch"},
            },
        ]

        cleaned = clean_articles(raw_articles)

        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0]["title"], "Apple rises")
        self.assertEqual(cleaned[0]["description"], "Shares moved higher.")
        self.assertEqual(cleaned[0]["source_name"], "Market Watch")
        self.assertEqual(cleaned[0]["published_at"], datetime(2026, 6, 1, 12, 0, 0))

    def test_dedupe_articles_preserves_first_occurrence(self) -> None:
        articles = dedupe_articles(
            [
                {"url": "https://example.com/1", "title": "First"},
                {"url": "https://example.com/1", "title": "Second"},
                {"url": "https://example.com/2", "title": "Third"},
            ]
        )

        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]["title"], "First")
