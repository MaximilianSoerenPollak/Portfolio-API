from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel


app = FastAPI()

class Stock(BaseModel):
    name: str
    ticker: str
    #for later these are all the fields.
    # yahoo_ticker:
    # exchange:
    # sector:
    # industry:
    # long_business_summary:
    # country:
    # website:
    # price:
    # marketcap:
    # dividends:
    # dividend_yield:
    # ex-dividend-date:
    # beta:
    # 52Week_high:
    # 52Week_low:
    # 50Day_avg:
    # recommendation:
    # total_cash_per_share:
    # profit_margins:
    # volume:

@app.get("/")
async def root():
    return {"message": "Welcome to my API!"}


@app.post("/createpost")
def create_post(new_stock: Stock):
    return {"new_stock": 
  
#title str, ticker str, exchange str.