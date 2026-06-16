from __future__ import annotations

import asyncio
import logging

from app.etl.pipelines.financials_pipeline import FinancialsPipeline
from app.etl.config import get_symbols, is_dry_run_enabled

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    symbols = get_symbols()
    pipeline = FinancialsPipeline(symbols, dry_run=is_dry_run_enabled(default=False))
    count = await pipeline.run()
    logger.info("Financials ETL finished; processed %s records", count)


if __name__ == "__main__":
    asyncio.run(main())
