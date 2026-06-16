from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd
import yfinance as yf

from app.etl.config import ETL_CONFIG
from app.logger import get_logger

logger = get_logger(__name__)


def _normalize_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not normalized:
        raise ValueError("symbol is required")
    return normalized


def get_company_profile(symbol: str) -> dict[str, Any]:
    """Fetch company profile metadata from Yahoo Finance for a ticker symbol."""
    normalized = _normalize_symbol(symbol)
    logger.info("Fetching company profile for %s", normalized)

    ticker = yf.Ticker(normalized)
    info = dict(ticker.info or {})
    info["symbol"] = normalized
    return info


def get_stock_history(
    symbol: str,
    *,
    start: date | None = None,
    end: date | None = None,
    period: str | None = None,
    interval: str = "1d",
) -> pd.DataFrame:
    """Fetch historical OHLCV price data from Yahoo Finance for a ticker symbol."""
    normalized = _normalize_symbol(symbol)
    logger.info("Fetching stock history for %s", normalized)

    if start is None and end is None and period is None:
        lookback_days = ETL_CONFIG.get("stock_price_lookback_days", 365)
        end = datetime.utcnow().date()
        start = end - timedelta(days=lookback_days)

    ticker = yf.Ticker(normalized)
    if period is not None:
        history = ticker.history(period=period, interval=interval, actions=False, auto_adjust=False)
    else:
        history = ticker.history(
            start=start,
            end=end,
            interval=interval,
            actions=False,
            auto_adjust=False,
        )

    if history is None or history.empty:
        return pd.DataFrame()

    history = history.copy()
    history.index = pd.to_datetime(history.index)
    history["symbol"] = normalized
    return history
