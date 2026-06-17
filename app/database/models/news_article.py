from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.connection import Base


class NewsArticle(Base):
    """Represents a news article linked to a company with sentiment metadata."""

    __tablename__ = "news_articles"
    __table_args__ = (
        UniqueConstraint("company_id", "url", name="uq_news_article_company_url"),
    )

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String(1024), nullable=False)
    source_name = Column(String(255), nullable=True)
    published_at = Column(DateTime, nullable=True, index=True)
    sentiment = Column(String(16), nullable=True, index=True)
    sentiment_score = Column(Float, nullable=True)
    positive_score = Column(Float, nullable=True)
    negative_score = Column(Float, nullable=True)
    neutral_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="news_articles")

    def __repr__(self) -> str:
        return f"<NewsArticle(company_id={self.company_id}, title={self.title[:40]!r}, sentiment={self.sentiment})>"
