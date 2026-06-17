from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Company(Base):
    """Represents a company in the financial research platform."""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(16), unique=True, nullable=False, index=True)
    short_name = Column(String(255), nullable=True, index=True)
    long_name = Column(String(255), nullable=True, index=True)
    exchange = Column(String(64), nullable=True)
    exchange_timezone_name = Column(String(64), nullable=True)
    exchange_timezone_short_name = Column(String(16), nullable=True)
    market = Column(String(32), nullable=True)
    quote_type = Column(String(64), nullable=True)
    currency = Column(String(16), nullable=True)
    region = Column(String(32), nullable=True)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    sector_key = Column(String(100), nullable=True)
    address1 = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    full_time_employees = Column(Integer, nullable=True)
    book_value = Column(Float, nullable=True)
    business_summary = Column(Text, nullable=True)
    financial_currency = Column(String(16), nullable=True)
    market_state = Column(String(32), nullable=True)
    target_high_price = Column(Float, nullable=True)
    target_low_price = Column(Float, nullable=True)
    target_mean_price = Column(Float, nullable=True)
    target_median_price = Column(Float, nullable=True)
    recommendation_mean = Column(Float, nullable=True)
    recommendation_key = Column(String(64), nullable=True)
    average_analyst_rating = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    stock_prices = relationship("StockPrice", back_populates="company", cascade="all, delete-orphan")
    financials = relationship("Financials", back_populates="company", cascade="all, delete-orphan")
    news_articles = relationship("NewsArticle", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, symbol={self.symbol}, short_name={self.short_name})>"
