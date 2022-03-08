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


@router.get("/user", response_model=List[schemas.StockResponse])
def get_user_stocks(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    stocks = db.query(models.Stock).filter(models.Stock.created_by == current_user.id).all()
    return stocks


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.StockResponse)
def create_stock(
    stock: List[schemas.StockCreate],
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    new_stock = models.Stock(created_by=current_user.id, **stock.dict())
    db.add(new_stock)
    db.commit()
    db.refresh(stock)
    return stock


@router.get("/{id}", response_model=schemas.StockResponse)
def get_stock(id: int, response: Response, db: Session = Depends(get_db)):
    stock = db.query(models.Stock).filter(models.Stock.id == id).first()
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"stock with id: {id} was not found.")
    return stock


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stock(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # !Todo only admin can delete.
    stock_query = db.query(models.Stock).filter(models.Stock.id == id)
    stock = stock_query.first()
    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Stock with ID: {id} does not exist")
    if stock.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized.")
    stock_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.StockResponse)
def update_stock(
    id: int,
    updated_stock: schemas.StockCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    stock_query = db.query(models.Stock).filter(models.Stock.id == id)
    stock = stock_query.first()
    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Stock with ID: {id} does not excist")
    if stock.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized.")
    stock_query.update(updated_stock.dict(), synchronize_session=False)
    return stock_query.first()
