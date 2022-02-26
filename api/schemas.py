from pydantic import BaseModel
from datetime import datetime


class Stock(BaseModel):
    name: str
    ticker: str
    yahoo_ticker: str
    exchange: str
    sector: str
    industry: str
    long_business_summary: str
    country: str
    website: str
    price: float
    marketcap: int
    dividends: float
    dividend_yield: float
    ex_dividend_date: str
    beta: float
    fifty_two_week_high: float
    fifty_two_week_low: float
    fifty_day_avg: float
    total_cash_per_share: float
    profit_margins: float
    volume: int
    status: int
