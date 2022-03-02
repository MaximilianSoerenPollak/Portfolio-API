from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db
from typing import List


router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/", response_model=List[schemas.StockResponse])
def get_stocks(db: Session = Depends(get_db)):
    stocks = db.query(models.Stock).all()
    return stocks


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.StockResponse)
def create_stock(
    stock: schemas.StockCreate, db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)
):
    # !Todo: make a flag somehow in this stock so the stocks are marked as non searchable or "user_added" or something.
    new_stock = models.Stock(**stock.dict())
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    return new_stock


@router.get("/{id}", response_model=schemas.StockResponse)
def get_stock(id: int, response: Response, db: Session = Depends(get_db)):
    stock = db.query(models.Stock).filter(models.Stock.id == id).first()
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"stock with id: {id} was not found.")
    return stock


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stock(id: int, db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
    # !Todo only admin can delete.
    stock = db.query(models.Stock).filter(models.Stock.id == id)
    if stock.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Stock with ID: {id} does not exist")
    stock.delete(syncrhonize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.StockResponse)
def update_stock(id: int, updated_stock: schemas.StockCreate, db: Session = Depends(get_db)):
    stock_query = db.query(models.Stock).filter(models.Stock.id == id)
    stock = stock_query.first()
    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Stock with ID: {id} does not excist")
    stock_query.update(updated_stock.dict(), syncrhonize_session=False)
    return updated_stock
