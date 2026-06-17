from __future__ import annotations

from typing import Any

from app.etl.cleaners.news_cleaner import clean_articles
from app.etl.transformers.base import BaseTransformer


class NewsTransformer(BaseTransformer):
    """Clean and normalize raw GNews articles for database loading."""

    def transform(self, raw: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
        articles = raw if isinstance(raw, list) else raw.get("articles", [])
        if not isinstance(articles, list):
            return []
        return clean_articles(articles)
