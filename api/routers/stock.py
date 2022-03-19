from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session, joinedload
from .. import models, schemas, oauth2
from ..database import get_db, engine
from typing import List, Optional, Union


router = APIRouter(prefix="/stocks", tags=["stocks"])

# ,
@router.get("/", response_model=List[schemas.StockResponseSolo])
def get_stocks(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 100,
    skip: int = 0,
    name_search: Optional[str] = None,
    ticker_search: Optional[str] = None,
    sector_search: Optional[str] = None,
    industry_search: Optional[str] = None,
    price: Optional[float] = None,
    dividends: Optional[float] = None,
    dividend_yield: Optional[float] = None,
    all_stocks: Optional[bool] = False,
):
    query = db.query(models.Stock)
    if name_search is not None:
        query = query.filter(models.Stock.name.contains(name_search))
    if ticker_search is not None:
        query = query.filter(models.Stock.ticker.contains(ticker_search))
    if sector_search is not None:
        query = query.filter(models.Stock.sector.contains(sector_search))
    if industry_search is not None:
        query = query.filter(models.Stock.industry.contains(industry_search))
    if price is not None:
        query = query.filter(models.Stock.price <= price)
    if dividends is not None:
        query = query.filter(models.Stock.dividends >= dividends)
    if dividend_yield is not None:
        query = query.filter(models.Stock.dividend_yield >= dividend_yield)
    if not all_stocks:
        return query.limit(limit).offset(skip).all()
    if all_stocks:
        return query.all()


@router.get("/user", response_model=List[schemas.StockResponseSolo])
def get_user_stocks(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    stocks = db.query(models.Stock).filter(models.Stock.created_by == current_user.id).all()
    return stocks


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.StockResponseSolo)
def create_stock(
    stock: schemas.StockCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    new_stock = models.Stock(created_by=current_user.id, **stock.dict())
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    return new_stock


@router.get("/{id}", response_model=schemas.StockResponseSolo)
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


@router.put("/{id}", response_model=schemas.StockResponseSolo)
def update_stock_manually(
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
    db.commit()
    return stock_query.first()


@router.post("/add/{portfolio_id}", response_model=List[Union[schemas.PortfolioSchema, schemas.PortfolioResponse]])
def add_stock_to_portfolio(portfolio_id: int, stock_ids: List[int], response: Response, db: Session = Depends(get_db)):
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.id == portfolio_id).first()
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No portfolio with id: {id} found.")
    for stock_id in stock_ids:
        stock = db.query(models.Stock).filter(models.Stock.id == stock_id).first()
        if stock is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No stock with id: {id} found.")
            continue
        for stock_model in portfolio.stocks:
            if stock_model.id in stock_ids:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Stock with id: {id} already in Portfolio."
                )
                continue
        for stock_id in stock_ids:
            query = """INSERT INTO portfolio_stocks (stock_id, portfolio_id) VALUES ({}, {})""".format(
                stock_id, portfolio_id
            )
            db.execute(query)
            db.commit()
        setattr(stock, "status", "1")
    db.refresh(portfolio)
    return portfolio
