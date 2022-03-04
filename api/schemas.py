from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class StockBase(BaseModel):
    name: str
    ticker: str
    yahoo_ticker: str
    exchange: Optional[str]
    sector: Optional[str]
    industry: Optional[str]
    long_business_summary: Optional[str]
    country: Optional[str]
    website: Optional[str]
    price: float
    marketcap: Optional[int]
    dividends: Optional[float]
    dividend_yield: Optional[float]
    ex_dividend_date: Optional[str]
    beta: Optional[float]
    fifty_two_week_high: Optional[float]
    fifty_two_week_low: Optional[float]
    fifty_day_avg: Optional[float]
    total_cash_per_share: Optional[float]
    profit_margins: Optional[float]
    volume: Optional[int]
    status: Optional[int]


class StockCreate(StockBase):

    created_by = Optional[int]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class StockResponse(StockBase):
    id: int
    created_by: int
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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str]


class PortfolioCreate(BaseModel):
    name: str
    dividends_goal: Optional[float]
    monetary_goal: Optional[float]
