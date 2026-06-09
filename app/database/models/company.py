from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Company(Base):
    """Represents a company in the financial research platform."""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    headquarters = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    stock_prices = relationship("StockPrice", back_populates="company", cascade="all, delete-orphan")
    financials = relationship("Financials", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, symbol={self.symbol}, name={self.name})>"
