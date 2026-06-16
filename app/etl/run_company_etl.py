from __future__ import annotations

import asyncio
import logging

from app.etl.pipelines.company_pipeline import CompanyPipeline
from app.etl.config import get_symbols, is_dry_run_enabled

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main(dry_run: bool = True) -> None:
    symbols = get_symbols()
    pipeline = CompanyPipeline(symbols, dry_run=dry_run)
    count = await pipeline.run()
    logger.info("Company ETL finished; processed %s records", count)


if __name__ == "__main__":
    asyncio.run(main(dry_run=is_dry_run_enabled(default=False)))
