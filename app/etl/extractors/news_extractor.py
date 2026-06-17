from __future__ import annotations

import asyncio
from typing import Iterable, Dict, Any

from app.etl.extractors.base import BaseExtractor
from app.etl.config import ETL_CONFIG
from app.tools.gnews_tool import fetch_news


class NewsExtractor(BaseExtractor):
    """Extract company news articles using the GNews API."""

    async def fetch(self, symbols: Iterable[str]) -> Iterable[Dict[str, Any]]:
        max_articles = ETL_CONFIG.get("news_max_articles", 10)

        async def fetch_symbol(symbol: str) -> list[Dict[str, Any]]:
            try:
                articles = await asyncio.to_thread(fetch_news, symbol, max_articles=max_articles)
                for article in articles:
                    article["symbol"] = symbol.strip().upper()
                return articles
            except Exception:
                return []

        batches = await asyncio.gather(*(fetch_symbol(symbol) for symbol in symbols))
        return [article for batch in batches for article in batch]
