from __future__ import annotations

import os
import unittest
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.connection import Base
from app.database.models import Company, Financials, NewsArticle, StockPrice
from app.etl.loaders.db_loader import DBLoader

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


@unittest.skipUnless(TEST_DATABASE_URL, "TEST_DATABASE_URL is not configured")
class DBLoaderIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=False)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)

    async def asyncTearDown(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await self.engine.dispose()

    async def test_upsert_companies_inserts_and_updates(self) -> None:
        async with self.session_factory() as session:
            inserted = await DBLoader.upsert_companies(
                session,
                [
                    {
                        "symbol": "AAPL",
                        "short_name": "Apple",
                        "long_name": "Apple Inc.",
                        "sector": "Technology",
                    }
                ],
            )

        self.assertEqual(inserted, 1)

        async with self.session_factory() as session:
            updated = await DBLoader.upsert_companies(
                session,
                [
                    {
                        "symbol": "AAPL",
                        "short_name": "Apple Updated",
                        "long_name": "Apple Incorporated",
                        "sector": "Consumer Electronics",
                    }
                ],
            )

            company = await session.scalar(select(Company).where(Company.symbol == "AAPL"))

        self.assertEqual(updated, 1)
        self.assertIsNotNone(company)
        self.assertEqual(company.short_name, "Apple Updated")
        self.assertEqual(company.sector, "Consumer Electronics")

    async def test_upsert_stock_prices_upserts_by_company_and_date(self) -> None:
        async with self.session_factory() as session:
            company = Company(symbol="MSFT", short_name="Microsoft")
            session.add(company)
            await session.commit()

            inserted = await DBLoader.upsert_stock_prices(
                session,
                [
                    {
                        "symbol": "MSFT",
                        "date": date(2026, 6, 1),
                        "close_price": 100.0,
                        "volume": 10,
                    }
                ],
            )

            updated = await DBLoader.upsert_stock_prices(
                session,
                [
                    {
                        "symbol": "MSFT",
                        "date": date(2026, 6, 1),
                        "close_price": 110.0,
                        "volume": 12,
                    }
                ],
            )

            price_rows = (
                await session.execute(select(StockPrice).where(StockPrice.company_id == company.id))
            ).scalars().all()

        self.assertEqual(inserted, 1)
        self.assertEqual(updated, 1)
        self.assertEqual(len(price_rows), 1)
        self.assertEqual(price_rows[0].close_price, 110.0)
        self.assertEqual(price_rows[0].volume, 12)

    async def test_upsert_financials_upserts_by_company_and_report_date(self) -> None:
        async with self.session_factory() as session:
            company = Company(symbol="NVDA", short_name="NVIDIA")
            session.add(company)
            await session.commit()

            inserted = await DBLoader.upsert_financials(
                session,
                [
                    {
                        "symbol": "NVDA",
                        "report_date": date(2025, 12, 31),
                        "fiscal_year": 2025,
                        "total_revenue": 500.0,
                        "net_income_to_common": 120.0,
                    }
                ],
            )

            updated = await DBLoader.upsert_financials(
                session,
                [
                    {
                        "symbol": "NVDA",
                        "report_date": date(2025, 12, 31),
                        "fiscal_year": 2025,
                        "total_revenue": 550.0,
                        "net_income_to_common": 150.0,
                    }
                ],
            )

            financial_rows = (
                await session.execute(select(Financials).where(Financials.company_id == company.id))
            ).scalars().all()

        self.assertEqual(inserted, 1)
        self.assertEqual(updated, 1)
        self.assertEqual(len(financial_rows), 1)
        self.assertEqual(financial_rows[0].total_revenue, 550.0)
        self.assertEqual(financial_rows[0].net_income_to_common, 150.0)

    async def test_upsert_news_articles_upserts_by_company_and_url(self) -> None:
        async with self.session_factory() as session:
            company = Company(symbol="AAPL", short_name="Apple")
            session.add(company)
            await session.commit()

            inserted = await DBLoader.upsert_news_articles(
                session,
                [
                    {
                        "symbol": "AAPL",
                        "title": "Apple launches product",
                        "description": "New device announced",
                        "url": "https://example.com/apple-1",
                        "source_name": "Reuters",
                        "published_at": date(2026, 6, 1),
                        "sentiment": "positive",
                        "sentiment_score": 0.92,
                        "positive_score": 0.92,
                        "negative_score": 0.03,
                        "neutral_score": 0.05,
                    }
                ],
            )

            updated = await DBLoader.upsert_news_articles(
                session,
                [
                    {
                        "symbol": "AAPL",
                        "title": "Apple launches product (updated)",
                        "description": "Updated headline",
                        "url": "https://example.com/apple-1",
                        "source_name": "Reuters",
                        "published_at": date(2026, 6, 1),
                        "sentiment": "neutral",
                        "sentiment_score": 0.55,
                        "positive_score": 0.20,
                        "negative_score": 0.25,
                        "neutral_score": 0.55,
                    }
                ],
            )

            news_rows = (
                await session.execute(select(NewsArticle).where(NewsArticle.company_id == company.id))
            ).scalars().all()

        self.assertEqual(inserted, 1)
        self.assertEqual(updated, 1)
        self.assertEqual(len(news_rows), 1)
        self.assertEqual(news_rows[0].title, "Apple launches product (updated)")
        self.assertEqual(news_rows[0].sentiment, "neutral")
