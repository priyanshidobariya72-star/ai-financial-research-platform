from __future__ import annotations

from typing import Any

from app.etl.transformers.base import BaseTransformer


class CompanyTransformer(BaseTransformer):
    """Normalize yfinance company info to the Company model fields."""

    def transform(self, raw: dict[str, Any]) -> dict[str, Any]:
        return {
            "symbol": raw.get("symbol"),
            "short_name": raw.get("shortName"),
            "long_name": raw.get("longName"),
            "exchange": raw.get("exchange"),
            "exchange_timezone_name": raw.get("exchangeTimezoneName"),
            "exchange_timezone_short_name": raw.get("exchangeTimezoneShortName"),
            "market": raw.get("market"),
            "quote_type": raw.get("quoteType"),
            "currency": raw.get("currency"),
            "region": raw.get("region"),
            "sector": raw.get("sector"),
            "industry": raw.get("industry"),
            "sector_key": raw.get("sectorKey"),
            "address1": raw.get("address1"),
            "country": raw.get("country"),
            "website": raw.get("website"),
            "full_time_employees": raw.get("fullTimeEmployees"),
            "book_value": raw.get("bookValue"),
            "business_summary": raw.get("longBusinessSummary"),
            "financial_currency": raw.get("financialCurrency"),
            "market_state": raw.get("marketState"),
            "target_high_price": raw.get("targetHighPrice"),
            "target_low_price": raw.get("targetLowPrice"),
            "target_mean_price": raw.get("targetMeanPrice"),
            "target_median_price": raw.get("targetMedianPrice"),
            "recommendation_mean": raw.get("recommendationMean"),
            "recommendation_key": raw.get("recommendationKey"),
            "average_analyst_rating": raw.get("averageAnalystRating"),
        }
