from __future__ import annotations

import asyncio
import logging

from app.etl.pipelines.stock_price_pipeline import StockPricePipeline
from app.etl.config import get_symbols, is_dry_run_enabled

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    symbols = get_symbols()
    pipeline = StockPricePipeline(symbols, dry_run=is_dry_run_enabled(default=False))
    count = await pipeline.run()
    logger.info("Stock price ETL finished; processed %s price rows", count)


if __name__ == "__main__":
    asyncio.run(main())
