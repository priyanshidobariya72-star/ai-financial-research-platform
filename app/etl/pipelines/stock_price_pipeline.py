from __future__ import annotations

import logging
from typing import Iterable

from app.etl.config import get_retry_settings
from app.etl.extractors.stock_price_extractor import StockPriceExtractor
from app.etl.transformers.stock_price_transformer import StockPriceTransformer
from app.etl.loaders.db_loader import DBLoader
from app.database import AsyncSessionLocal
from app.etl.utils import run_with_retries, write_json_snapshot

logger = logging.getLogger(__name__)


class StockPricePipeline:
    """Pipeline to extract, transform, and load stock price data."""

    def __init__(self, symbols: Iterable[str], dry_run: bool = False):
        self.symbols = list(symbols)
        self.dry_run = dry_run
        self.extractor = StockPriceExtractor()
        self.transformer = StockPriceTransformer()

    async def run(self) -> int:
        retries, delay = get_retry_settings()
        raw = await run_with_retries(self.extractor.fetch, self.symbols, retries=retries, delay=delay)
        transformed: list[dict] = []
        for item in raw:
            transformed.extend(self.transformer.transform(item))

        if self.dry_run:
            output_path = write_json_snapshot(transformed, "transformed_stock_prices")
            logger.info("Stock price ETL dry-run snapshot written to %s", output_path)
            return len(transformed)

        try:
            async with AsyncSessionLocal() as session:
                count = await DBLoader.upsert_stock_prices(session, transformed)
            return count
        except Exception:
            logger.exception("Stock price ETL DB load failed; falling back to JSON snapshot")
            write_json_snapshot(transformed, "transformed_stock_prices")
            return len(transformed)
