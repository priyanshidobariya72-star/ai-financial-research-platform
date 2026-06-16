from __future__ import annotations

from datetime import date
from unittest import TestCase
from unittest.mock import Mock, patch

import pandas as pd

from app.tools.yahoo_finance_tool import get_company_profile, get_stock_history


class YahooFinanceToolTests(TestCase):
    @patch("app.tools.yahoo_finance_tool.yf.Ticker")
    def test_get_company_profile_returns_info_with_symbol(self, ticker_cls: Mock) -> None:
        ticker_cls.return_value.info = {
            "shortName": "Apple Inc.",
            "sector": "Technology",
        }

        profile = get_company_profile("aapl")

        self.assertEqual(profile["symbol"], "AAPL")
        self.assertEqual(profile["shortName"], "Apple Inc.")
        self.assertEqual(profile["sector"], "Technology")
        ticker_cls.assert_called_once_with("AAPL")

    def test_get_company_profile_rejects_empty_symbol(self) -> None:
        with self.assertRaises(ValueError):
            get_company_profile("   ")

    @patch("app.tools.yahoo_finance_tool.yf.Ticker")
    def test_get_stock_history_returns_dataframe_with_symbol_column(self, ticker_cls: Mock) -> None:
        history = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [110.0],
                "Low": [95.0],
                "Close": [105.0],
                "Volume": [1000],
            },
            index=pd.to_datetime(["2026-06-01"]),
        )
        ticker_cls.return_value.history.return_value = history

        result = get_stock_history(
            "MSFT",
            start=date(2026, 6, 1),
            end=date(2026, 6, 2),
        )

        self.assertFalse(result.empty)
        self.assertEqual(result.iloc[0]["symbol"], "MSFT")
        self.assertEqual(result.iloc[0]["Close"], 105.0)
        ticker_cls.return_value.history.assert_called_once_with(
            start=date(2026, 6, 1),
            end=date(2026, 6, 2),
            interval="1d",
            actions=False,
            auto_adjust=False,
        )

    @patch("app.tools.yahoo_finance_tool.yf.Ticker")
    def test_get_stock_history_returns_empty_dataframe_when_no_data(self, ticker_cls: Mock) -> None:
        ticker_cls.return_value.history.return_value = pd.DataFrame()

        result = get_stock_history("INVALID")

        self.assertTrue(result.empty)

    def test_get_stock_history_rejects_empty_symbol(self) -> None:
        with self.assertRaises(ValueError):
            get_stock_history("")
