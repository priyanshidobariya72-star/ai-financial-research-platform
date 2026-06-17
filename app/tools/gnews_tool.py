from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from typing import Any

import httpx

from app.etl.config import ETL_CONFIG, get_gnews_api_key
from app.logger import get_logger

logger = get_logger(__name__)

GNEWS_SEARCH_URL = "https://gnews.io/api/v4/search"


def fetch_news(
    query: str,
    *,
    lang: str | None = None,
    country: str | None = None,
    max_articles: int | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[dict[str, Any]]:
    """Fetch news articles from the GNews API for a search query."""
    normalized_query = query.strip()
    if not normalized_query:
        raise ValueError("query is required")

    api_key = get_gnews_api_key()
    lang = lang or ETL_CONFIG.get("news_lang", "en")
    country = country or ETL_CONFIG.get("news_country", "us")
    max_articles = max_articles or ETL_CONFIG.get("news_max_articles", 10)

    if from_date is None and to_date is None:
        lookback_days = ETL_CONFIG.get("news_lookback_days", 7)
        to_date = datetime.utcnow().date()
        from_date = to_date - timedelta(days=lookback_days)

    params: dict[str, Any] = {
        "q": normalized_query,
        "lang": lang,
        "country": country,
        "max": max(1, min(max_articles, 100)),
        "apikey": api_key,
        "sortby": "publishedAt",
    }
    if from_date is not None:
        params["from"] = from_date.isoformat()
    if to_date is not None:
        params["to"] = to_date.isoformat()

    logger.info("Fetching news for query=%r max=%s", normalized_query, max_articles)

    with httpx.Client(timeout=30.0) as client:
        response = client.get(GNEWS_SEARCH_URL, params=params)
        response.raise_for_status()
        payload = response.json()

    articles = payload.get("articles", [])
    logger.info("Fetched %s articles for query=%r", len(articles), normalized_query)
    return articles
