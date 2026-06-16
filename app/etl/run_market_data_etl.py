from __future__ import annotations

import asyncio
import logging

from app.etl.pipelines.market_data_pipeline import MarketDataPipeline
from app.etl.config import get_symbols, is_dry_run_enabled

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    symbols = get_symbols()
    pipeline = MarketDataPipeline(symbols, dry_run=is_dry_run_enabled(default=False))
    results = await pipeline.run_all()
    logger.info("Market data ETL finished; results=%s", results)


if __name__ == "__main__":
    asyncio.run(main())
