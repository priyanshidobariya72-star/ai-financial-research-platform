from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Iterable, Dict, Any

from app.etl.extractors.base import BaseExtractor
from app.etl.config import ETL_CONFIG
from app.tools.yahoo_finance_tool import get_company_profile, get_stock_history


class StockPriceExtractor(BaseExtractor):
    """Extract historical stock price data using yfinance."""

    async def fetch(self, symbols: Iterable[str]) -> Iterable[Dict[str, Any]]:
        results: list[Dict[str, Any]] = []
        lookback_days = ETL_CONFIG.get("stock_price_lookback_days", 365)
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=lookback_days)

        async def fetch_symbol(symbol: str) -> None:
            try:
                history = await asyncio.to_thread(
                    get_stock_history,
                    symbol,
                    start=start_date,
                    end=end_date,
                    interval="1d",
                )
                if history.empty:
                    return

                info = await asyncio.to_thread(get_company_profile, symbol)
                rows = []
                for dt, row in history.iterrows():
                    rows.append(
                        {
                            "symbol": symbol.strip().upper(),
                            "date": dt.date(),
                            "open": float(row.get("Open", 0)) if row.get("Open") is not None else None,
                            "high": float(row.get("High", 0)) if row.get("High") is not None else None,
                            "low": float(row.get("Low", 0)) if row.get("Low") is not None else None,
                            "close": float(row.get("Close", 0)) if row.get("Close") is not None else None,
                            "volume": int(row.get("Volume", 0)) if row.get("Volume") is not None else None,
                            "info": info,
                        }
                    )
                results.append({"symbol": symbol.strip().upper(), "price_rows": rows, "info": info})
            except Exception:
                return

        await asyncio.gather(*(fetch_symbol(symbol) for symbol in symbols))
        return results
