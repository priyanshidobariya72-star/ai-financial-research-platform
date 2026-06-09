from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Financials(Base):
    """Represents financial data for a company."""

    __tablename__ = "financials"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    fiscal_year = Column(Integer, nullable=False, index=True)
    fiscal_period = Column(String(10), nullable=False)  # Q1, Q2, Q3, Q4, FY
    report_date = Column(Date, nullable=False, index=True)

    # Income Statement
    revenue = Column(Float, nullable=True)
    cost_of_revenue = Column(Float, nullable=True)
    gross_profit = Column(Float, nullable=True)
    operating_expenses = Column(Float, nullable=True)
    operating_income = Column(Float, nullable=True)
    net_income = Column(Float, nullable=True)
    eps = Column(Float, nullable=True)  # Earnings Per Share

    # Balance Sheet
    total_assets = Column(Float, nullable=True)
    total_liabilities = Column(Float, nullable=True)
    total_equity = Column(Float, nullable=True)
    current_assets = Column(Float, nullable=True)
    current_liabilities = Column(Float, nullable=True)

    # Cash Flow
    operating_cash_flow = Column(Float, nullable=True)
    investing_cash_flow = Column(Float, nullable=True)
    financing_cash_flow = Column(Float, nullable=True)
    free_cash_flow = Column(Float, nullable=True)

    # Additional Metrics
    debt_to_equity = Column(Float, nullable=True)
    current_ratio = Column(Float, nullable=True)
    roa = Column(Float, nullable=True)  # Return on Assets
    roe = Column(Float, nullable=True)  # Return on Equity

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="financials")

    def __repr__(self) -> str:
        return f"<Financials(company_id={self.company_id}, fiscal_year={self.fiscal_year}, period={self.fiscal_period})>"
