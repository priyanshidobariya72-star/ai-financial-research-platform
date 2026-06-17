from app.tools.yahoo_finance_tool import get_company_profile, get_stock_history

__all__ = [
    "fetch_news",
    "analyze_sentiment",
    "enrich_article_with_sentiment",
    "get_news_sentiment",
    "get_company_profile",
    "get_stock_history",
]


def __getattr__(name: str):
    if name == "fetch_news":
        from app.tools.gnews_tool import fetch_news

        return fetch_news
    if name in {"analyze_sentiment", "enrich_article_with_sentiment", "get_news_sentiment"}:
        from app.tools import sentiment_tool

        return getattr(sentiment_tool, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
