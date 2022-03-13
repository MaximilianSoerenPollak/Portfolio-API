from .database import Base
from sqlalchemy import Column, Integer, String, Float, Date, BigInteger, Text, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

"""
You still have to figure out why there is a "key error" when you try to make a new row in the associaiton table.
YOu have tried almost everything. It seems that the function can not resolve the backref of Portfolio table so it seems 
to call the clolumn that is menitoned there instead.


    stocks_included = relationship("PortfolioStock", back_populates="portfolio")

instead of stocks_included it tries to search for portfolio. Which gives a keyerror.
"""


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
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
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=text("now()"))
    portfolios = relationship("PortfolioStock", back_populates="stock")

    # test


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
    stocks = relationship("PortfolioStock", back_populates="portfolio")
    # updated at.
    # proxy This is neccessary so that we can append stocks to the portfolio


class PortfolioStock(Base):
    __tablename__ = "portfolio_stocks"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id", ondelete="CASCADE"))
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"))
    count = Column(Integer, nullable=True)
    buy_in = Column(Float, nullable=True)
    stock = relationship(Stock, back_populates="portfolios")
    portfolio = relationship(Portfolio, back_populates="stocks")

    # proxies

    stock_name = association_proxy(target_collection="stock", attr="name")
    stock_ticker = association_proxy(target_collection="stock", attr="ticker")
    stock_yahoo_ticker = association_proxy(target_collection="stock", attr="yahoo_ticker")
    stock_exchange = association_proxy(target_collection="stock", attr="exchange")
    stock_sector = association_proxy(target_collection="stock", attr="sector")
    stock_industry = association_proxy(target_collection="stock", attr="industry")
    stock_long_business_summary = association_proxy(target_collection="stock", attr="long_business_summary")
    stock_country = association_proxy(target_collection="stock", attr="country")
    stock_website = association_proxy(target_collection="stock", attr="website")
    stock_price = association_proxy(target_collection="stock", attr="price")
    stock_marketcap = association_proxy(target_collection="stock", attr="marketcap")
    stock_dividends = association_proxy(target_collection="stock", attr="dividends")
    stock_dividend_yield = association_proxy(target_collection="stock", attr="dividend_yield")
    stock_ex_dividend_date = association_proxy(target_collection="stock", attr="ex_dividend_date")
    stock_beta = association_proxy(target_collection="stock", attr="beta")
    stock_fifty_two_week_high = association_proxy(target_collection="stock", attr="fifty_two_week_high")
    stock_fifty_two_week_low = association_proxy(target_collection="stock", attr="fifty_two_week_low")
    stock_fifty_day_avg = association_proxy(target_collection="stock", attr="fifty_day_avg")
    stock_recommendation = association_proxy(target_collection="stock", attr="recommendation")
    stock_total_cash_per_share = association_proxy(target_collection="stock", attr="total_cash_per_share")
    stock_profit_margins = association_proxy(target_collection="stock", attr="profit_margins")
    stock_volume = association_proxy(target_collection="stock", attr="volume")
    stock_status = association_proxy(target_collection="stock", attr="status")
    stock_created_by = association_proxy(target_collection="stock", attr="created_by")
    stock_created_at = association_proxy(target_collection="stock", attr="created_at")

    # proxy portfolio
    portfolio_name = association_proxy(target_collection="portfolio", attr="name")
    portfolio_monetary_goal = association_proxy(target_collection="portfolio", attr="monetary_goal")
    portfolio_dividends_goal = association_proxy(target_collection="portfolio", attr="dividends_goal")
    portfolio_created_at = association_proxy(target_collection="portfolio", attr="created_at")

    def __init__(self, portfolio=None, stock=None, buy_in=None, count=None):
        self.portfolio = portfolio
        self.stock = stock
        self.buy_in = buy_in
        self.count = count
