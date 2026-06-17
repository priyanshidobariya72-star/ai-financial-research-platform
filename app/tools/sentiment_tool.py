from __future__ import annotations

from typing import Any

from sqlalchemy import select

from app.database import AsyncSessionLocal, Company, NewsArticle
from app.logger import get_logger

logger = get_logger(__name__)

FINBERT_MODEL_NAME = "ProsusAI/finbert"
SENTIMENT_LABELS = ("positive", "negative", "neutral")

_tokenizer = None
_model = None


def _get_finbert():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        _tokenizer = AutoTokenizer.from_pretrained(FINBERT_MODEL_NAME)
        _model = AutoModelForSequenceClassification.from_pretrained(FINBERT_MODEL_NAME)
        _model.eval()
    return _tokenizer, _model


def _empty_sentiment() -> dict[str, Any]:
    return {
        "sentiment": "neutral",
        "sentiment_score": 0.0,
        "positive_score": 0.0,
        "negative_score": 0.0,
        "neutral_score": 1.0,
    }


def analyze_sentiment(text: str) -> dict[str, Any]:
    """Classify financial text sentiment as positive, negative, or neutral using FinBERT."""
    cleaned = (text or "").strip()
    if not cleaned:
        return _empty_sentiment()

    import torch
    import torch.nn.functional as F

    tokenizer, model = _get_finbert()
    inputs = tokenizer(
        cleaned,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True,
    )

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = F.softmax(outputs.logits, dim=-1).squeeze().tolist()
    label_map = {value.lower(): index for index, value in model.config.id2label.items()}
    scores = {
        label: float(probabilities[label_map[label]])
        for label in SENTIMENT_LABELS
        if label in label_map
    }
    sentiment = max(scores, key=scores.get)

    return {
        "sentiment": sentiment,
        "sentiment_score": scores[sentiment],
        "positive_score": scores.get("positive", 0.0),
        "negative_score": scores.get("negative", 0.0),
        "neutral_score": scores.get("neutral", 0.0),
    }


def enrich_article_with_sentiment(article: dict[str, Any]) -> dict[str, Any]:
    """Add FinBERT sentiment fields to a cleaned article dict."""
    text = " ".join(
        part for part in [article.get("title"), article.get("description"), article.get("content")] if part
    )
    sentiment = analyze_sentiment(text)
    return {**article, **sentiment}


async def get_news_sentiment(symbol: str, *, limit: int = 50) -> dict[str, Any]:
    """Return aggregated sentiment for stored news articles of a company symbol."""
    normalized_symbol = symbol.strip().upper()
    if not normalized_symbol:
        raise ValueError("symbol is required")

    async with AsyncSessionLocal() as session:
        articles = (
            await session.execute(
                select(NewsArticle)
                .join(Company, Company.id == NewsArticle.company_id)
                .where(Company.symbol == normalized_symbol)
                .order_by(NewsArticle.published_at.desc().nullslast(), NewsArticle.id.desc())
                .limit(limit)
            )
        ).scalars().all()

        if not articles:
            return {
                "symbol": normalized_symbol,
                "article_count": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "overall_sentiment": "neutral",
                "average_sentiment_score": 0.0,
                "articles": [],
            }

        counts = {"positive": 0, "negative": 0, "neutral": 0}
        score_total = 0.0
        article_rows: list[dict[str, Any]] = []

        for article in articles:
            sentiment = (article.sentiment or "neutral").lower()
            if sentiment not in counts:
                sentiment = "neutral"
            counts[sentiment] += 1
            score_total += article.sentiment_score or 0.0
            article_rows.append(
                {
                    "title": article.title,
                    "url": article.url,
                    "published_at": article.published_at.isoformat() if article.published_at else None,
                    "sentiment": sentiment,
                    "sentiment_score": article.sentiment_score,
                    "source_name": article.source_name,
                }
            )

        overall_sentiment = max(counts, key=counts.get)

        return {
            "symbol": normalized_symbol,
            "article_count": len(articles),
            "positive_count": counts["positive"],
            "negative_count": counts["negative"],
            "neutral_count": counts["neutral"],
            "overall_sentiment": overall_sentiment,
            "average_sentiment_score": round(score_total / len(articles), 4),
            "articles": article_rows,
        }
