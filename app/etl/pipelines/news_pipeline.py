from __future__ import annotations

import logging
from typing import Iterable

from app.database import AsyncSessionLocal
from app.etl.config import get_retry_settings
from app.etl.extractors.news_extractor import NewsExtractor
from app.etl.loaders.db_loader import DBLoader
from app.etl.transformers.news_transformer import NewsTransformer
from app.etl.utils import run_with_retries, write_json_snapshot
from app.tools.sentiment_tool import enrich_article_with_sentiment

logger = logging.getLogger(__name__)


class NewsPipeline:
    """Pipeline to extract, clean, analyze sentiment, and load news articles."""

    def __init__(self, symbols: Iterable[str], dry_run: bool = False):
        self.symbols = list(symbols)
        self.dry_run = dry_run
        self.extractor = NewsExtractor()
        self.transformer = NewsTransformer()

    async def run(self) -> int:
        retries, delay = get_retry_settings()
        raw = await run_with_retries(self.extractor.fetch, self.symbols, retries=retries, delay=delay)
        cleaned = self.transformer.transform(list(raw))
        enriched = [enrich_article_with_sentiment(article) for article in cleaned]

        if self.dry_run:
            output_path = write_json_snapshot(enriched, "transformed_news")
            logger.info("News ETL dry-run snapshot written to %s", output_path)
            return len(enriched)

        try:
            async with AsyncSessionLocal() as session:
                count = await DBLoader.upsert_news_articles(session, enriched)
            return count
        except Exception:
            logger.exception("News ETL DB load failed; falling back to JSON snapshot")
            write_json_snapshot(enriched, "transformed_news")
            return len(enriched)
