from .database import Base
from sqlalchemy import Column, Integer, String, Float, Date, BigInteger, Text, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship


class PortfolioStocks(Base):
    __tablename__ = "portfolio_stocks"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id", ondelete="CASCADE"))
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"))


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    ticker = Column(String)
    yahoo_ticker = Column(String, nullable=False)
    exchange = Column(String(255), nullable=True)
    sector = Column(String(255), nullable=True)
    industry = Column(String(255), nullable=True)
    long_business_summary = Column(Text, nullable=True)
    country = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)
    marketcap = Column(Integer, nullable=True)
    dividends = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)
    ex_dividend_date = Column(Date, nullable=True)
    beta = Column(Float, nullable=True)
    fifty_two_week_high = Column(Float, nullable=True)
    fifty_two_week_low = Column(Float, nullable=True)
    fifty_day_avg = Column(Float, nullable=True)
    recommendation = Column(String(100), nullable=True)
    total_cash_per_share = Column(BigInteger, nullable=True)
    profit_margins = Column(Float, nullable=True)
    volume = Column(BigInteger, nullable=True)
    status = Column(Integer, nullable=False, server_default="0")
    created_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    # updated_at
    portfolios = relationship("Portfolio", secondary=PortfolioStocks.__table__, back_populates="stocks")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    monetary_goal = Column(Float, nullable=True)
    dividends_goal = Column(Float, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    # updated_at
    stocks = relationship("Stock", secondary=PortfolioStocks.__table__, back_populates="portfolios")
