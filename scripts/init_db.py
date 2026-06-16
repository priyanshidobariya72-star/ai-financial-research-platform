from __future__ import annotations

import asyncio
import logging

from app.database.connection import engine, Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db() -> None:
    logger.info("Creating database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema created")


if __name__ == "__main__":
    try:
        asyncio.run(init_db())
    except Exception as e:
        logger.exception("Failed to initialize database: %s", e)
        raise
