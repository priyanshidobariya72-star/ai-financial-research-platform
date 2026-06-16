from __future__ import annotations

from typing import Dict, Iterable

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Company, Financials, StockPrice


class DBLoader:
    """Database loader utilities for ETL.

    Methods accept an `AsyncSession` (SQLAlchemy) and perform upserts.
    """

    @staticmethod
    async def upsert_companies(session: AsyncSession, companies: Iterable[Dict]) -> int:
        """Upsert company records by `symbol`. Returns number of upserts performed."""
        count = 0
        for data in companies:
            symbol = data.get("symbol")
            if not symbol:
                continue
            stmt = select(Company).where(Company.symbol == symbol)
            res = await session.execute(stmt)
            existing = res.scalars().first()
            if existing:
                for key, val in data.items():
                    if hasattr(existing, key) and val is not None:
                        setattr(existing, key, val)
                count += 1
            else:
                company = Company(**data)
                session.add(company)
                count += 1
        await session.commit()
        return count

    @staticmethod
    async def upsert_stock_prices(session: AsyncSession, rows: Iterable[Dict]) -> int:
        """Bulk upsert stock price rows by (company_id, date)."""
        symbols = {row["symbol"] for row in rows if row.get("symbol")}
        if not symbols:
            return 0

        stmt = select(Company).where(Company.symbol.in_(symbols))
        res = await session.execute(stmt)
        companies = {company.symbol: company.id for company in res.scalars().all()}

        value_rows = []
        for row in rows:
            symbol = row.get("symbol")
            company_id = companies.get(symbol)
            if not company_id:
                continue
            row_data = {key: val for key, val in row.items() if key != "symbol"}
            row_data["company_id"] = company_id
            value_rows.append(row_data)

        if not value_rows:
            return 0

        insert_stmt = pg_insert(StockPrice).values(value_rows)
        excluded = insert_stmt.excluded
        update_cols = {
            column.name: getattr(excluded, column.name)
            for column in StockPrice.__table__.columns
            if column.name not in {"company_id", "date", "id"}
        }
        stmt = insert_stmt.on_conflict_do_update(
            index_elements=[StockPrice.company_id, StockPrice.date],
            set_=update_cols,
        )
        await session.execute(stmt)
        await session.commit()
        return len(value_rows)

    @staticmethod
    async def upsert_financials(session: AsyncSession, rows: Iterable[Dict]) -> int:
        """Upsert financial records by company_id and report_date."""
        symbols = {row["symbol"] for row in rows if row.get("symbol")}
        if not symbols:
            return 0

        stmt = select(Company).where(Company.symbol.in_(symbols))
        res = await session.execute(stmt)
        companies = {company.symbol: company.id for company in res.scalars().all()}

        count = 0
        for row in rows:
            symbol = row.get("symbol")
            company_id = companies.get(symbol)
            if not company_id:
                continue

            row_data = {key: val for key, val in row.items() if key != "symbol"}
            row_data["company_id"] = company_id

            stmt = select(Financials).where(
                Financials.company_id == company_id,
                Financials.report_date == row_data.get("report_date"),
            )
            res = await session.execute(stmt)
            existing = res.scalars().first()
            if existing:
                for key, val in row_data.items():
                    if hasattr(existing, key) and val is not None:
                        setattr(existing, key, val)
            else:
                session.add(Financials(**row_data))
            count += 1

        await session.commit()
        return count
