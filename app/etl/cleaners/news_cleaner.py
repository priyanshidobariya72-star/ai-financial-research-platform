from __future__ import annotations

import html
import re
from datetime import datetime
from typing import Any


def clean_html(text: str | None) -> str:
    """Remove HTML tags and normalize whitespace."""
    if not text:
        return ""
    unescaped = html.unescape(text)
    without_tags = re.sub(r"<[^>]+>", " ", unescaped)
    return re.sub(r"\s+", " ", without_tags).strip()


def parse_published_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def dedupe_articles(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove duplicate articles by URL while preserving order."""
    seen_urls: set[str] = set()
    unique_articles: list[dict[str, Any]] = []
    for article in articles:
        url = article.get("url")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        unique_articles.append(article)
    return unique_articles


def clean_article(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Normalize and validate a raw GNews article."""
    title = clean_html(raw.get("title"))
    description = clean_html(raw.get("description"))
    content = clean_html(raw.get("content"))
    url = (raw.get("url") or "").strip()

    if not title or not url:
        return None

    source = raw.get("source") or {}
    source_name = source.get("name") if isinstance(source, dict) else None

    return {
        "symbol": raw.get("symbol"),
        "title": title[:512],
        "description": description or None,
        "content": content or None,
        "url": url[:1024],
        "source_name": clean_html(source_name)[:255] if source_name else None,
        "published_at": parse_published_at(raw.get("publishedAt")),
    }


def clean_articles(raw_articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Clean and deduplicate a batch of raw articles."""
    cleaned = [article for article in (clean_article(raw) for raw in raw_articles) if article]
    return dedupe_articles(cleaned)
