from __future__ import annotations

from typing import Iterable

from app.etl.config import get_symbols
from app.etl.pipelines.company_pipeline import CompanyPipeline
from app.etl.pipelines.stock_price_pipeline import StockPricePipeline
from app.etl.pipelines.financials_pipeline import FinancialsPipeline


class MarketDataPipeline:
    """Orchestrates market data ETL tasks."""

    def __init__(self, symbols: Iterable[str] | None = None, dry_run: bool = False):
        self.symbols = list(symbols) if symbols is not None else list(get_symbols())
        self.dry_run = dry_run

    async def run_companies(self) -> int:
        pipeline = CompanyPipeline(self.symbols, dry_run=self.dry_run)
        return await pipeline.run()

    async def run_prices(self) -> int:
        pipeline = StockPricePipeline(self.symbols, dry_run=self.dry_run)
        return await pipeline.run()

    async def run_financials(self) -> int:
        pipeline = FinancialsPipeline(self.symbols, dry_run=self.dry_run)
        return await pipeline.run()

    async def run_all(self) -> dict[str, int]:
        results = {
            "companies": await self.run_companies(),
            "prices": await self.run_prices(),
            "financials": await self.run_financials(),
        }
        return results
