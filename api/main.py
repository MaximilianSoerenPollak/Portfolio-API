import psycopg2
import time
from sqlalchemy.orm import Session
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from typing import Optional, List
from random import randrange
from decouple import config
from psycopg2.extras import RealDictCursor
from .database import engine, get_db
from . import models, schemas



models.Base.metadata.create_all(bind=engine)




app = FastAPI()


while True:
    try:
        conn = psycopg2.connect(host=config("DATABASEIP"), database=config("DATABASENAME"), user=config("POSTGRESUSERNAME"), password=config("POSTGRESPASSWORD"),
        cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as e:
        print(f"Connecting to database failed")
        print("Error: ", e)
        time.sleep(2)


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


@app.get("/stocks", response_model=List[schemas.StockResponse])
def get_stocks(db: Session = Depends(get_db)):
    stocks = db.query(models.Stock).all()
    return stocks
  


@app.post("/stocks", status_code=status.HTTP_201_CREATED, response_model=schemas.StockResponse)
def create_stock(stock: schemas.StockCreate, db: Session = Depends(get_db)):
    new_stock = models.Stock(**stock.dict())
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    return new_stock
  

@app.get("/stocks/{id}", response_model=schemas.StockResponse)
def get_stock(id: int, response: Response, db: Session = Depends(get_db)):
    stock = db.query(models.Stock).filter(models.Stock.id == id).first()
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"stock with id: {id} was not found.")
    return stock


@app.delete("/stocks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stock(id: int, db: Session = Depends(get_db)):
    stock = db.query(models.Stock).filter(models.Stock.id == id)
    if stock.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Stock with ID: {id} does not exist")
    stock.delete(syncrhonize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/stocks/{id}", response_model=schemas.StockResponse)
def update_stock(id: int, update_stock: schemas.StockCreate, db: Session = Depends(get_db)):
    stock_query = db.query(models.Stock).filter(models.Stock.id == id)
    stock = stock_query.first()
    if stock == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Stock with ID: {id} does not excist")
    stock_query.update(updated_stock.dict(), syncrhonize_session=False)
    return updated_stock