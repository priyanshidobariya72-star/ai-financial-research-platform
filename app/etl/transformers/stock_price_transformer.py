from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Iterable

from app.etl.transformers.base import BaseTransformer


class StockPriceTransformer(BaseTransformer):
    """Normalize yfinance historical price rows to the StockPrice model."""

    def transform(self, raw: dict[str, Any]) -> Iterable[dict[str, Any]]:
        symbol = raw.get("symbol")
        info = raw.get("info", {}) or {}
        rows = raw.get("price_rows", []) or []
        transformed = []

        for row in rows:
            price_row = {
                "symbol": symbol,
                "date": row["date"],
                "open_price": row.get("open"),
                "high_price": row.get("high"),
                "low_price": row.get("low"),
                "close_price": row.get("close"),
                "volume": row.get("volume"),
                "previous_close": info.get("previousClose"),
                "regular_market_open": info.get("regularMarketOpen"),
                "regular_market_previous_close": info.get("regularMarketPreviousClose"),
                "regular_market_day_low": info.get("regularMarketDayLow"),
                "regular_market_day_high": info.get("regularMarketDayHigh"),
                "current_price": info.get("currentPrice"),
                "regular_market_price": info.get("regularMarketPrice"),
                "regular_market_change": info.get("regularMarketChange"),
                "regular_market_change_percent": info.get("regularMarketChangePercent"),
                "regular_market_volume": info.get("regularMarketVolume"),
                "average_volume": info.get("averageVolume"),
                "average_daily_volume_10day": info.get("averageDailyVolume10Day"),
                "bid": info.get("bid"),
                "ask": info.get("ask"),
                "bid_size": info.get("bidSize"),
                "ask_size": info.get("askSize"),
                "market_cap": info.get("marketCap"),
                "enterprise_value": info.get("enterpriseValue"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low_change": info.get("fiftyTwoWeekLowChange"),
                "fifty_two_week_low_change_percent": info.get("fiftyTwoWeekLowChangePercent"),
                "fifty_two_week_high_change": info.get("fiftyTwoWeekHighChange"),
                "fifty_two_week_high_change_percent": info.get("fiftyTwoWeekHighChangePercent"),
                "fifty_two_week_change": info.get("fiftyTwoWeekChange"),
                "fifty_two_week_change_percent": info.get("fiftyTwoWeekChangePercent"),
                "fifty_two_week_range": info.get("fiftyTwoWeekRange"),
                "dividend_rate": info.get("dividendRate"),
                "dividend_yield": info.get("dividendYield"),
                "payout_ratio": info.get("payoutRatio"),
                "beta": info.get("beta"),
                "trailing_pe": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_book": info.get("priceToBook"),
                "price_to_sales_trailing_12_months": info.get("priceToSalesTrailing12Months"),
                "trailing_peg_ratio": info.get("trailingPegRatio"),
                "ex_dividend_date": self._normalize_date(info.get("exDividendDate")),
                "regular_market_time": self._normalize_datetime(info.get("regularMarketTime")),
                "market_state": info.get("marketState"),
            }
            transformed.append(price_row)

        return transformed

    @staticmethod
    def _normalize_date(value: Any) -> date | None:
        if value is None:
            return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=timezone.utc).date()
        return None

    @staticmethod
    def _normalize_datetime(value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=timezone.utc).replace(tzinfo=None)
        return None
