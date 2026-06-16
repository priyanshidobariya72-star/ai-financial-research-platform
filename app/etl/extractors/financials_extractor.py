from __future__ import annotations

import asyncio
from typing import Iterable, Dict, Any

import yfinance as yf

from app.etl.extractors.base import BaseExtractor


class FinancialsExtractor(BaseExtractor):
    """Extract financial data using yfinance."""

    async def fetch(self, symbols: Iterable[str]) -> Iterable[Dict[str, Any]]:
        results: list[Dict[str, Any]] = []

        async def fetch_symbol(symbol: str) -> None:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info or {}
                financials = await asyncio.to_thread(lambda: ticker.financials)
                balance_sheet = await asyncio.to_thread(lambda: ticker.balance_sheet)
                cashflow = await asyncio.to_thread(lambda: ticker.cashflow)

                results.append(
                    {
                        "symbol": symbol,
                        "info": info,
                        "financials": financials,
                        "balance_sheet": balance_sheet,
                        "cashflow": cashflow,
                    }
                )
            except Exception:
                return

        await asyncio.gather(*(fetch_symbol(symbol) for symbol in symbols))
        return results
