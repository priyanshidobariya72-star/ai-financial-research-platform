from __future__ import annotations

import asyncio
import logging

from app.etl.config import get_symbols, is_dry_run_enabled
from app.etl.pipelines.news_pipeline import NewsPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    symbols = get_symbols()
    pipeline = NewsPipeline(symbols, dry_run=is_dry_run_enabled(default=False))
    count = await pipeline.run()
    logger.info("News ETL finished; articles_processed=%s", count)


if __name__ == "__main__":
    asyncio.run(main())
