from __future__ import annotations

import asyncio
import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)


async def run_with_retries(func: Callable[..., Any], *args, retries: int = 3, delay: int = 5, **kwargs):
    for attempt in range(1, retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as exc:
            logger.exception("Attempt %s failed: %s", attempt, exc)
            if attempt == retries:
                raise
            await asyncio.sleep(delay)


def write_json_snapshot(records: list[dict[str, Any]], prefix: str) -> str:
    output_dir = Path("data")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    output_path = output_dir / f"{prefix}_{timestamp}.json"
    with output_path.open("w", encoding="utf-8") as file_handle:
        json.dump(records, file_handle, default=_json_serializer, indent=2)
    return str(output_path)


def _json_serializer(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)
