from __future__ import annotations

import os
from pathlib import Path
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOTENV_PATH = PROJECT_ROOT / ".env"

if DOTENV_PATH.exists():
    load_dotenv(DOTENV_PATH)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/ai_financial_research_platform",
)

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required to connect to PostgreSQL")

Base = declarative_base()

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    future=True,
    echo=False,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async SQLAlchemy session for PostgreSQL operations."""
    async with AsyncSessionLocal() as session:
        yield session
