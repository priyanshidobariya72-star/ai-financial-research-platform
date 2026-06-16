from __future__ import annotations

import logging
from typing import Iterable

from app.etl.extractors.ticker_extractor import TickerExtractor
from app.etl.config import get_retry_settings
from app.etl.transformers.company_transformer import CompanyTransformer
from app.etl.loaders.db_loader import DBLoader
from app.database import AsyncSessionLocal
from app.etl.utils import run_with_retries, write_json_snapshot

logger = logging.getLogger(__name__)


class CompanyPipeline:
    """Pipeline to extract, transform and load company profiles."""

    def __init__(self, symbols: Iterable[str], dry_run: bool = False):
        self.symbols = list(symbols)
        self.dry_run = dry_run
        self.extractor = TickerExtractor()
        self.transformer = CompanyTransformer()

    async def run(self) -> int:
        """Run the company ETL and optionally persist a dry-run snapshot."""
        retries, delay = get_retry_settings()
        raw = await run_with_retries(self.extractor.fetch, self.symbols, retries=retries, delay=delay)
        transformed = [self.transformer.transform(row) for row in raw if row]
        transformed = [row for row in transformed if row.get("symbol")]

        if self.dry_run:
            output_path = write_json_snapshot(transformed, "transformed_companies")
            logger.info("Company ETL dry-run snapshot written to %s", output_path)
            return len(transformed)

        try:
            async with AsyncSessionLocal() as session:
                count = await DBLoader.upsert_companies(session, transformed)
            return count
        except Exception:
            logger.exception("Company ETL DB load failed; falling back to JSON snapshot")
            write_json_snapshot(transformed, "transformed_companies")
            return len(transformed)
