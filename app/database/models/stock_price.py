from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Date, String
from sqlalchemy.orm import relationship

from app.database.connection import Base


class StockPrice(Base):
    """Represents historical or snapshot stock price data for a company."""

    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=True)
    previous_close = Column(Float, nullable=True)
    regular_market_open = Column(Float, nullable=True)
    regular_market_previous_close = Column(Float, nullable=True)
    regular_market_day_low = Column(Float, nullable=True)
    regular_market_day_high = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    regular_market_price = Column(Float, nullable=True)
    regular_market_change = Column(Float, nullable=True)
    regular_market_change_percent = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)
    regular_market_volume = Column(Integer, nullable=True)
    average_volume = Column(Integer, nullable=True)
    average_daily_volume_10day = Column(Integer, nullable=True)
    bid = Column(Float, nullable=True)
    ask = Column(Float, nullable=True)
    bid_size = Column(Integer, nullable=True)
    ask_size = Column(Integer, nullable=True)
    market_cap = Column(Float, nullable=True)
    enterprise_value = Column(Float, nullable=True)
    fifty_two_week_low = Column(Float, nullable=True)
    fifty_two_week_high = Column(Float, nullable=True)
    fifty_two_week_low_change = Column(Float, nullable=True)
    fifty_two_week_low_change_percent = Column(Float, nullable=True)
    fifty_two_week_high_change = Column(Float, nullable=True)
    fifty_two_week_high_change_percent = Column(Float, nullable=True)
    fifty_two_week_change = Column(Float, nullable=True)
    fifty_two_week_change_percent = Column(Float, nullable=True)
    fifty_two_week_range = Column(String(100), nullable=True)
    dividend_rate = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)
    ex_dividend_date = Column(Date, nullable=True)
    payout_ratio = Column(Float, nullable=True)
    beta = Column(Float, nullable=True)
    trailing_pe = Column(Float, nullable=True)
    forward_pe = Column(Float, nullable=True)
    peg_ratio = Column(Float, nullable=True)
    price_to_book = Column(Float, nullable=True)
    price_to_sales_trailing_12_months = Column(Float, nullable=True)
    trailing_peg_ratio = Column(Float, nullable=True)
    regular_market_time = Column(DateTime, nullable=True)
    market_state = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="stock_prices")

    def __repr__(self) -> str:
        return f"<StockPrice(company_id={self.company_id}, date={self.date}, current_price={self.current_price})>"
