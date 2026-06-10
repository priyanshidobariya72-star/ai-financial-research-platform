from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Financials(Base):
    """Represents financial metrics and performance data for a company."""

    __tablename__ = "financials"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    fiscal_year = Column(Integer, nullable=True, index=True)
    fiscal_period = Column(String(10), nullable=True)
    report_date = Column(Date, nullable=True, index=True)
    total_cash = Column(Float, nullable=True)
    total_cash_per_share = Column(Float, nullable=True)
    ebitda = Column(Float, nullable=True)
    total_debt = Column(Float, nullable=True)
    quick_ratio = Column(Float, nullable=True)
    current_ratio = Column(Float, nullable=True)
    total_revenue = Column(Float, nullable=True)
    debt_to_equity = Column(Float, nullable=True)
    revenue_per_share = Column(Float, nullable=True)
    return_on_assets = Column(Float, nullable=True)
    return_on_equity = Column(Float, nullable=True)
    gross_profits = Column(Float, nullable=True)
    free_cashflow = Column(Float, nullable=True)
    operating_cashflow = Column(Float, nullable=True)
    earnings_growth = Column(Float, nullable=True)
    revenue_growth = Column(Float, nullable=True)
    gross_margins = Column(Float, nullable=True)
    ebitda_margins = Column(Float, nullable=True)
    operating_margins = Column(Float, nullable=True)
    profit_margins = Column(Float, nullable=True)
    trailing_eps = Column(Float, nullable=True)
    forward_eps = Column(Float, nullable=True)
    eps_current_year = Column(Float, nullable=True)
    eps_forward = Column(Float, nullable=True)
    eps_trailing_twelve_months = Column(Float, nullable=True)
    price_eps_current_year = Column(Float, nullable=True)
    peg_ratio = Column(Float, nullable=True)
    enterprise_to_revenue = Column(Float, nullable=True)
    enterprise_to_ebitda = Column(Float, nullable=True)
    financial_currency = Column(String(16), nullable=True)
    net_income_to_common = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="financials")

    def __repr__(self) -> str:
        return f"<Financials(company_id={self.company_id}, fiscal_year={self.fiscal_year}, period={self.fiscal_period})>"
