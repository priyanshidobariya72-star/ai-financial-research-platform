from __future__ import annotations

from datetime import date, datetime
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Mock, patch

import pandas as pd

from app.etl.pipelines.company_pipeline import CompanyPipeline
from app.etl.pipelines.financials_pipeline import FinancialsPipeline
from app.etl.pipelines.market_data_pipeline import MarketDataPipeline
from app.etl.pipelines.news_pipeline import NewsPipeline
from app.etl.pipelines.stock_price_pipeline import StockPricePipeline
from app.etl.transformers.company_transformer import CompanyTransformer
from app.etl.transformers.financials_transformer import FinancialsTransformer
from app.etl.transformers.news_transformer import NewsTransformer
from app.etl.transformers.stock_price_transformer import StockPriceTransformer
from app.etl.utils import run_with_retries


class _FailingSessionFactory:
    def __call__(self):
        return self

    async def __aenter__(self):
        raise RuntimeError("db unavailable")

    async def __aexit__(self, exc_type, exc, tb):
        return False


class RetryTests(IsolatedAsyncioTestCase):
    async def test_run_with_retries_retries_then_returns(self) -> None:
        mock = AsyncMock(side_effect=[RuntimeError("first"), RuntimeError("second"), "ok"])

        result = await run_with_retries(mock, retries=3, delay=0)

        self.assertEqual(result, "ok")
        self.assertEqual(mock.await_count, 3)


class TransformerTests(IsolatedAsyncioTestCase):
    async def test_company_transformer_maps_core_fields(self) -> None:
        transformed = CompanyTransformer().transform(
            {
                "symbol": "AAPL",
                "shortName": "Apple",
                "longName": "Apple Inc.",
                "exchange": "NMS",
                "sector": "Technology",
                "city": "Cupertino",
            }
        )

        self.assertEqual(transformed["symbol"], "AAPL")
        self.assertEqual(transformed["short_name"], "Apple")
        self.assertEqual(transformed["long_name"], "Apple Inc.")
        self.assertEqual(transformed["exchange"], "NMS")
        self.assertEqual(transformed["sector"], "Technology")
        self.assertNotIn("city", transformed)

    async def test_stock_price_transformer_expands_price_rows(self) -> None:
        transformed = StockPriceTransformer().transform(
            {
                "symbol": "MSFT",
                "info": {
                    "currentPrice": 420.0,
                    "marketCap": 1000.0,
                    "regularMarketTime": 1780315200,
                    "exDividendDate": 1780228800,
                    "enterpriseToRevenue": 8.5,
                },
                "price_rows": [
                    {
                        "date": date(2026, 6, 1),
                        "open": 410.0,
                        "high": 425.0,
                        "low": 405.0,
                        "close": 420.0,
                        "volume": 123,
                    }
                ],
            }
        )

        self.assertEqual(len(transformed), 1)
        self.assertEqual(transformed[0]["symbol"], "MSFT")
        self.assertEqual(transformed[0]["open_price"], 410.0)
        self.assertEqual(transformed[0]["current_price"], 420.0)
        self.assertEqual(transformed[0]["market_cap"], 1000.0)
        self.assertEqual(transformed[0]["ex_dividend_date"], date(2026, 5, 31))
        self.assertEqual(transformed[0]["regular_market_time"], datetime(2026, 6, 1, 12, 0, 0))
        self.assertNotIn("enterprise_to_revenue", transformed[0])

    async def test_financials_transformer_uses_dataframe_and_info_fallbacks(self) -> None:
        period = pd.Timestamp("2025-12-31")
        financials_df = pd.DataFrame({period: {"Total Revenue": 500.0}})
        balance_sheet_df = pd.DataFrame({period: {"Total Debt": 120.0}})

        transformed = FinancialsTransformer().transform(
            {
                "symbol": "META",
                "info": {
                    "financialCurrency": "USD",
                    "grossProfits": 300.0,
                },
                "financials": financials_df,
                "balance_sheet": balance_sheet_df,
                "cashflow": pd.DataFrame(),
            }
        )

        self.assertEqual(len(transformed), 1)
        self.assertEqual(transformed[0]["symbol"], "META")
        self.assertEqual(transformed[0]["report_date"], date(2025, 12, 31))
        self.assertEqual(transformed[0]["total_revenue"], 500.0)
        self.assertEqual(transformed[0]["total_debt"], 120.0)
        self.assertEqual(transformed[0]["financial_currency"], "USD")

    async def test_news_transformer_cleans_raw_batch(self) -> None:
        transformed = NewsTransformer().transform(
            [
                {
                    "symbol": "AAPL",
                    "title": "<b>Apple</b> update",
                    "description": "Strong quarter",
                    "url": "https://example.com/aapl",
                    "publishedAt": "2026-06-01T10:00:00Z",
                    "source": {"name": "Reuters"},
                }
            ]
        )

        self.assertEqual(len(transformed), 1)
        self.assertEqual(transformed[0]["title"], "Apple update")
        self.assertEqual(transformed[0]["source_name"], "Reuters")


class PipelineTests(IsolatedAsyncioTestCase):
    async def test_market_data_pipeline_runs_all_children(self) -> None:
        pipeline = MarketDataPipeline(["AAPL"])

        with (
            patch.object(pipeline, "run_companies", AsyncMock(return_value=2)),
            patch.object(pipeline, "run_prices", AsyncMock(return_value=5)),
            patch.object(pipeline, "run_financials", AsyncMock(return_value=3)),
        ):
            result = await pipeline.run_all()

        self.assertEqual(result, {"companies": 2, "prices": 5, "financials": 3})

    async def test_company_pipeline_returns_transformed_count_when_db_unavailable(self) -> None:
        pipeline = CompanyPipeline(["AAPL"])
        raw_rows = [{"symbol": "AAPL", "shortName": "Apple"}]
        transformed_row = {"symbol": "AAPL", "short_name": "Apple"}

        with (
            patch("app.etl.pipelines.company_pipeline.run_with_retries", AsyncMock(return_value=raw_rows)),
            patch.object(pipeline.transformer, "transform", Mock(return_value=transformed_row)),
            patch("app.etl.pipelines.company_pipeline.AsyncSessionLocal", _FailingSessionFactory()),
            patch("app.etl.pipelines.company_pipeline.write_json_snapshot", Mock(return_value="data/out.json")),
        ):
            result = await pipeline.run()

        self.assertEqual(result, 1)

    async def test_financials_pipeline_dry_run_writes_snapshot(self) -> None:
        pipeline = FinancialsPipeline(["NVDA"], dry_run=True)
        raw_rows = [{"symbol": "NVDA"}]
        transformed_rows = [{"symbol": "NVDA", "report_date": date(2025, 12, 31)}]

        with (
            patch("app.etl.pipelines.financials_pipeline.run_with_retries", AsyncMock(return_value=raw_rows)),
            patch.object(pipeline.transformer, "transform", Mock(return_value=transformed_rows)),
            patch("app.etl.pipelines.financials_pipeline.write_json_snapshot", Mock(return_value="data/out.json")) as snapshot_mock,
        ):
            result = await pipeline.run()

        self.assertEqual(result, 1)
        snapshot_mock.assert_called_once_with(transformed_rows, "transformed_financials")

    async def test_stock_price_pipeline_flattens_rows_before_loading(self) -> None:
        pipeline = StockPricePipeline(["MSFT"])
        raw_rows = [{"symbol": "MSFT", "price_rows": []}]
        transformed_rows = [
            {"symbol": "MSFT", "date": date(2026, 6, 1), "close_price": 10.0},
            {"symbol": "MSFT", "date": date(2026, 6, 2), "close_price": 11.0},
        ]

        class _SessionFactory:
            def __call__(self):
                return self

            async def __aenter__(self):
                return object()

            async def __aexit__(self, exc_type, exc, tb):
                return False

        loader = AsyncMock(return_value=2)

        with (
            patch("app.etl.pipelines.stock_price_pipeline.run_with_retries", AsyncMock(return_value=raw_rows)),
            patch.object(pipeline.transformer, "transform", Mock(return_value=transformed_rows)),
            patch("app.etl.pipelines.stock_price_pipeline.AsyncSessionLocal", _SessionFactory()),
            patch("app.etl.pipelines.stock_price_pipeline.DBLoader.upsert_stock_prices", loader),
        ):
            result = await pipeline.run()

        self.assertEqual(result, 2)
        loader.assert_awaited_once()
        self.assertEqual(loader.await_args.args[1], transformed_rows)

    async def test_financials_pipeline_flattens_transformer_output(self) -> None:
        pipeline = FinancialsPipeline(["NVDA"])
        raw_rows = [{"symbol": "NVDA"}]
        transformed_rows = [
            {"symbol": "NVDA", "report_date": date(2025, 12, 31)},
            {"symbol": "NVDA", "report_date": date(2024, 12, 31)},
        ]

        class _SessionFactory:
            def __call__(self):
                return self

            async def __aenter__(self):
                return object()

            async def __aexit__(self, exc_type, exc, tb):
                return False

        loader = AsyncMock(return_value=2)

        with (
            patch("app.etl.pipelines.financials_pipeline.run_with_retries", AsyncMock(return_value=raw_rows)),
            patch.object(pipeline.transformer, "transform", Mock(return_value=transformed_rows)),
            patch("app.etl.pipelines.financials_pipeline.AsyncSessionLocal", _SessionFactory()),
            patch("app.etl.pipelines.financials_pipeline.DBLoader.upsert_financials", loader),
        ):
            result = await pipeline.run()

        self.assertEqual(result, 2)
        loader.assert_awaited_once()
        self.assertEqual(loader.await_args.args[1], transformed_rows)

    async def test_news_pipeline_runs_cleaning_sentiment_and_load(self) -> None:
        pipeline = NewsPipeline(["AAPL"])
        raw_rows = [
            {
                "symbol": "AAPL",
                "title": "Apple news",
                "description": "Market update",
                "url": "https://example.com/aapl",
                "publishedAt": "2026-06-01T10:00:00Z",
                "source": {"name": "Reuters"},
            }
        ]
        cleaned_rows = [
            {
                "symbol": "AAPL",
                "title": "Apple news",
                "description": "Market update",
                "url": "https://example.com/aapl",
                "published_at": date(2026, 6, 1),
                "source_name": "Reuters",
            }
        ]
        enriched_rows = [{**cleaned_rows[0], "sentiment": "positive", "sentiment_score": 0.9}]

        class _SessionFactory:
            def __call__(self):
                return self

            async def __aenter__(self):
                return object()

            async def __aexit__(self, exc_type, exc, tb):
                return False

        loader = AsyncMock(return_value=1)

        with (
            patch("app.etl.pipelines.news_pipeline.run_with_retries", AsyncMock(return_value=raw_rows)),
            patch.object(pipeline.transformer, "transform", Mock(return_value=cleaned_rows)),
            patch("app.etl.pipelines.news_pipeline.enrich_article_with_sentiment", Mock(side_effect=enriched_rows)),
            patch("app.etl.pipelines.news_pipeline.AsyncSessionLocal", _SessionFactory()),
            patch("app.etl.pipelines.news_pipeline.DBLoader.upsert_news_articles", loader),
        ):
            result = await pipeline.run()

        self.assertEqual(result, 1)
        loader.assert_awaited_once()
