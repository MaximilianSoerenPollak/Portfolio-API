from pydantic import BaseModel, EmailStr
from datetime import datetime


class StockBase(BaseModel):
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


class StockCreate(StockBase):
    pass


class StockResponse(StockBase):
    id: int
    created_at: datetime
    # TODO add "updated at" field here once it's implemented in the model.

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str