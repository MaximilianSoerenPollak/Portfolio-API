from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, List


# ---- USER ----
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


# --- TOKEN ---


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str]


# --- Stock ---


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
    ex_dividend_date: Optional[date]
    beta: Optional[float]
    recommendation: Optional[str]
    fifty_two_week_high: Optional[float]
    fifty_two_week_low: Optional[float]
    fifty_day_avg: Optional[float]
    total_cash_per_share: Optional[float]
    profit_margins: Optional[float]
    volume: Optional[int]
    status: Optional[int]


class StockResponseSolo(StockBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    # TODO add "updated at" field here once it's implemented in the model.

    class Config:
        orm_mode = True


class StockCreate(StockBase):
    pass

    class Config:
        orm_mode = True


# class StockResponsePortfolioInc(StockBase):
#     portfolios: Optional[List[PortfolioResponse]]

#     class Config:
#         orm_mode = True


class StockResponseInsidePortfolio(StockResponseSolo):
    buy_in: Optional[float]
    count: Optional[int]

    class Config:
        orm_mode = True
        validate_assignment = True


class PortfolioCreate(BaseModel):
    name: str
    dividends_goal: Optional[float]
    monetary_goal: Optional[float]

    class Config:
        orm_mode = True


class PortfolioResponse(PortfolioCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class StockSchema(StockResponseSolo):
    portfolios: List[PortfolioResponse]


class PortfolioSchema(PortfolioResponse):
    stocks: List[StockResponseInsidePortfolio]

    class Config:
        orm_mode = True


# -- Association ---
# class StockBaseAssociation(BaseModel):
#     name: str = Field(alias="stock_name")
#     ticker: str = Field(alias="stock_ticker")
#     yahoo_ticker: str = Field(alias="stock_yahoo_ticker")
#     exchange: Optional[str] = Field(alias="stock_exchange")
#     sector: Optional[str] = Field(alias="stock_sector")
#     industry: Optional[str] = Field(alias="stock_industry")
#     long_business_summary: Optional[str] = Field(alias="stock_long_business_summary")
#     country: Optional[str] = Field(alias="stock_country")
#     website: Optional[str] = Field(alias="stock_website")
#     price: float = Field(alias="stock_price")
#     marketcap: Optional[int] = Field(alias="stock_marketcap")
#     dividends: Optional[float] = Field(alias="stock_dividends")
#     dividend_yield: Optional[float] = Field(alias="stock_dividend_yield")
#     ex_dividend_date: Optional[str] = Field(alias="stock_ex_dividend_date")
#     beta: Optional[float] = Field(alias="stock_beta")
#     fifty_two_week_high: Optional[float] = Field(alias="stock_fifty_two_week_high")
#     fifty_two_week_low: Optional[float] = Field(alias="stock_fifty_two_week_low")
#     fifty_day_avg: Optional[float] = Field(alias="stock_fifty_day_avg")
#     total_cash_per_share: Optional[float] = Field(alias="stock_total_cash_per_share")
#     profit_margins: Optional[float] = Field(alias="stock_profit_margins")
#     volume: Optional[int] = Field(alias="stock_volume")
#     status: Optional[int] = Field(alias="stock_status")


# class StockResponseSoloAssociation(StockBaseAssociation):
#     id: int = Field(alias="stock_id")
#     created_by: int = Field(alias="stock_created_by")
#     created_at: datetime = Field(alias="stock_created_at")
#     # TODO add "updated at" field here once it's implemented in the model.

#     class Config:
#         orm_mode = True


# class StockCreateAssociation(StockBaseAssociation):
#     pass

#     class Config:
#         orm_mode = True


# class StockResponseAssociation(StockResponseSoloAssociation):
#     buy_in: Optional[float]
#     count: Optional[int]
#     # TODO add "updated at" field here once it's implemented in the model.

#     class Config:
#         orm_mode = True
#         validate_assignment = True


# class PortfolioCreateAssociation(BaseModel):
#     name: str = Field(alias="portfolio_name")
#     dividends_goal: Optional[float] = Field(alias="portfolio_dividends_goal")
#     monetary_goal: Optional[float] = Field(alias="portfolio_monetary_goal")

#     class Config:
#         orm_mode = True


# class PortfolioResponseAssociation(BaseModel):
#     id: int = Field(alias="portfolio_id")
#     name: str = Field(alias="portfolio_name")
#     dividends_goal: Optional[float] = Field(alias="portfolio_dividends_goal")
#     monetary_goal: Optional[float] = Field(alias="portfolio_monetary_goal")
#     created_at: datetime = Field(alias="portfolio_created_at")

#     class Config:
#         orm_mode = True


# class StockSchema(StockResponseSolo):
#     portfolios: List[PortfolioResponseAssociation]


# class PortfolioSchema(PortfolioResponse):
#     stocks: List[StockResponseAssociation]


# class StockResponsePortfolioInc(StockBaseAssociation):
#     id: int = Field(alias="stock_id")
#     created_by: int = Field(alias="stock_created_by")
#     created_at: datetime = Field(alias="stock_created_at")
#     portfolios: Optional[List[PortfolioResponse]]
#     # TODO add "updated at" field here once it's implemented in the model.

#     class Config:
#         orm_mode = True
