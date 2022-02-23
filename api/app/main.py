from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange


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

my_stocks = [{"name": "Apple INC.", "ticker": "AAPL", "id": 1}, {"name": "IBM", "ticker": "IBM", "id": 2}]

def find_stock(id):
    for s in my_stocks:
        if s["id"] == id:
            return s

def find_index_stock(id):
    for i, s in enumerate(my_stocks):
        if s["id"] == id:
            return i


@app.get("/")
async def root():
    return {"message": "Welcome to my API!"}

@app.get("/stocks")
def get_stocks():
    return {"data": my_stocks}
  


@app.post("/stocks", status_code=status.HTTP_201_CREATED)
def create_post(stock: Stock):
    stock_dict = stock.dict()
    stock_dict["id"] = randrange(0, 100000000)
    my_stocks.append(stock_dict)
    return {"data": stock_dict}
  

@app.get("/stocks/{id}")
def get_post(id: int, response: Response):
    stock = find_stock(id)
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"stock with id: {id} was not found.")
    return {"stock_detail": stock}

@app.delete("/stocks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stock(id: int):
    index = find_index_stock(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Stock with ID: {id} does not excist")
    my_stocks.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/stocks/{id}")
def update_stock(id: int, stock: Stock):
    index = find_index_stock(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Stock with ID: {id} does not excist")
    stock_dict = stock.dict()
    stock_dict["id"] = id
    my_stocks[index] = stock_dict
    return {"message": "updated post"}