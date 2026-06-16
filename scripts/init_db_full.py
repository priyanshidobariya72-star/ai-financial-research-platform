from __future__ import annotations

import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db() -> None:
    # First, connect to the default 'postgres' DB to create ai_research if needed
    admin_url = "postgresql+asyncpg://postgres:admin@localhost:5432/postgres"
    admin_engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    
    logger.info("Creating database 'ai_research' if it doesn't exist...")
    try:
        async with admin_engine.begin() as conn:
            await conn.execute(text("CREATE DATABASE ai_research;"))
        logger.info("Database 'ai_research' created")
    except Exception as e:
        if "already exists" in str(e):
            logger.info("Database 'ai_research' already exists")
        else:
            logger.warning("Error creating database: %s", e)
    finally:
        await admin_engine.dispose()
    
    # Now connect to ai_research and create tables
    from app.database.connection import engine, Base
    
    logger.info("Creating tables in 'ai_research'...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Tables created successfully")


if __name__ == "__main__":
    try:
        asyncio.run(init_db())
    except Exception as e:
        logger.exception("Failed to initialize database: %s", e)
        raise
