from __future__ import annotations

import os
from typing import List

ETL_CONFIG = {
    "batch_size": 500,
    "max_retries": 3,
    "retry_delay": 5,  # seconds
    "symbols": ["AAPL", "META", "MSFT"],
    "stock_price_lookback_days": 365,
    "log_file": "logs/etl_pipeline.log",
}


def get_symbols() -> List[str]:
    raw_symbols = os.getenv("ETL_SYMBOLS")
    if raw_symbols:
        return [symbol.strip().upper() for symbol in raw_symbols.split(",") if symbol.strip()]
    return ETL_CONFIG["symbols"]


def get_retry_settings() -> tuple[int, int]:
    return ETL_CONFIG["max_retries"], ETL_CONFIG["retry_delay"]


def is_dry_run_enabled(default: bool = False) -> bool:
    raw_value = os.getenv("ETL_DRY_RUN")
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}
