from __future__ import annotations

from typing import Dict, Any, Iterable

from app.etl.transformers.base import BaseTransformer


class FinancialsTransformer(BaseTransformer):
    """Normalize yfinance financial data to the Financials model."""

    def transform(self, raw: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
        symbol = raw.get("symbol")
        info = raw.get("info", {}) or {}
        financials_df = raw.get("financials")
        balance_sheet_df = raw.get("balance_sheet")
        cashflow_df = raw.get("cashflow")

        rows: list[Dict[str, Any]] = []

        def get_info_field(key: str) -> Any:
            return info.get(key)

        if financials_df is not None and not financials_df.empty:
            for period in financials_df.columns:
                row = {
                    "symbol": symbol,
                    "fiscal_year": int(period.year) if hasattr(period, "year") else None,
                    "fiscal_period": "FY",
                    "report_date": period.date() if hasattr(period, "date") else None,
                    "gross_profits": get_info_field("grossProfits"),
                    "ebitda": get_info_field("ebitda"),
                    "net_income_to_common": get_info_field("netIncomeToCommon"),
                    "operating_cashflow": get_info_field("operatingCashflow"),
                    "total_cash": get_info_field("totalCash"),
                    "total_cash_per_share": get_info_field("totalCashPerShare"),
                    "total_debt": self._safe_get(balance_sheet_df, "Total Debt", period) or get_info_field("totalDebt"),
                    "quick_ratio": get_info_field("quickRatio"),
                    "current_ratio": get_info_field("currentRatio"),
                    "debt_to_equity": get_info_field("debtToEquity"),
                    "revenue_per_share": get_info_field("revenuePerShare"),
                    "return_on_assets": get_info_field("returnOnAssets"),
                    "return_on_equity": get_info_field("returnOnEquity"),
                    "free_cashflow": get_info_field("freeCashflow"),
                    "total_revenue": get_info_field("totalRevenue") or self._safe_get(financials_df, "Total Revenue", period),
                    "earnings_growth": get_info_field("earningsGrowth"),
                    "revenue_growth": get_info_field("revenueGrowth"),
                    "gross_margins": get_info_field("grossMargins"),
                    "ebitda_margins": get_info_field("ebitdaMargins"),
                    "operating_margins": get_info_field("operatingMargins"),
                    "profit_margins": get_info_field("profitMargins"),
                    "trailing_eps": get_info_field("trailingEps"),
                    "forward_eps": get_info_field("forwardEps"),
                    "eps_current_year": get_info_field("epsCurrentYear"),
                    "eps_forward": get_info_field("epsForward"),
                    "eps_trailing_twelve_months": get_info_field("epsTrailingTwelveMonths"),
                    "price_eps_current_year": get_info_field("priceEpsCurrentYear"),
                    "peg_ratio": get_info_field("pegRatio"),
                    "enterprise_to_revenue": get_info_field("enterpriseToRevenue"),
                    "enterprise_to_ebitda": get_info_field("enterpriseToEbitda"),
                    "financial_currency": get_info_field("financialCurrency"),
                }
                rows.append(row)
        else:
            rows.append(
                {
                    "symbol": symbol,
                    "fiscal_year": None,
                    "fiscal_period": None,
                    "report_date": None,
                    "total_cash": get_info_field("totalCash"),
                    "total_cash_per_share": get_info_field("totalCashPerShare"),
                    "ebitda": get_info_field("ebitda"),
                    "total_debt": get_info_field("totalDebt"),
                    "quick_ratio": get_info_field("quickRatio"),
                    "current_ratio": get_info_field("currentRatio"),
                    "total_revenue": get_info_field("totalRevenue"),
                    "debt_to_equity": get_info_field("debtToEquity"),
                    "revenue_per_share": get_info_field("revenuePerShare"),
                    "return_on_assets": get_info_field("returnOnAssets"),
                    "return_on_equity": get_info_field("returnOnEquity"),
                    "gross_profits": get_info_field("grossProfits"),
                    "free_cashflow": get_info_field("freeCashflow"),
                    "operating_cashflow": get_info_field("operatingCashflow"),
                    "earnings_growth": get_info_field("earningsGrowth"),
                    "revenue_growth": get_info_field("revenueGrowth"),
                    "gross_margins": get_info_field("grossMargins"),
                    "ebitda_margins": get_info_field("ebitdaMargins"),
                    "operating_margins": get_info_field("operatingMargins"),
                    "profit_margins": get_info_field("profitMargins"),
                    "trailing_eps": get_info_field("trailingEps"),
                    "forward_eps": get_info_field("forwardEps"),
                    "eps_current_year": get_info_field("epsCurrentYear"),
                    "eps_forward": get_info_field("epsForward"),
                    "eps_trailing_twelve_months": get_info_field("epsTrailingTwelveMonths"),
                    "price_eps_current_year": get_info_field("priceEpsCurrentYear"),
                    "peg_ratio": get_info_field("pegRatio"),
                    "enterprise_to_revenue": get_info_field("enterpriseToRevenue"),
                    "enterprise_to_ebitda": get_info_field("enterpriseToEbitda"),
                    "financial_currency": get_info_field("financialCurrency"),
                }
            )

        return rows

    @staticmethod
    def _safe_get(df: Any, field: str, period: Any) -> Any:
        if df is None or df.empty:
            return None
        try:
            return df.at[field, period]
        except Exception:
            return None
