from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Iterable, Dict, Any

from app.etl.extractors.base import BaseExtractor
from app.etl.config import ETL_CONFIG
from app.tools.yahoo_finance_tool import get_company_profile, get_stock_history


class TickerExtractor(BaseExtractor):
    """Extract company profile data using yfinance."""

    async def fetch(self, symbols: Iterable[str]) -> Iterable[Dict[str, Any]]:
        results = []
        for symbol in symbols:
            try:
                info = await asyncio.to_thread(get_company_profile, symbol)
                if info:
                    results.append(info)
            except Exception:
                continue
        return results
