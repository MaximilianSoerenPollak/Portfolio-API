from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session, joinedload
from .. import models, schemas, oauth2
from ..database import get_db, engine, load_some_data
from typing import List, Optional, Union
from datetime import timedelta, datetime
from sqlalchemy import update
from pandas.io import sql
from data.full_da import get_some_tickers

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
    return query.limit(limit).offset(skip).all()


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


#! TODO need to update route route for new FK (stock.ticker)
@router.get("/{id}", response_model=schemas.StockResponseSolo)
def get_stock(id: int, response: Response, db: Session = Depends(get_db)):
    stock = db.query(models.Stock).filter(models.Stock.id == id).first()
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"stock with id: {id} was not found.")
    return stock


#! TODO need to update route route for new FK (stock.ticker)
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


#! TODO need to update route route for new FK (stock.ticker)
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


#! TODO need to update route route for new FK (stock.ticker)
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


@router.post("/update")
def update_stocks(tickerlist_inc: List[str], db: Session = Depends(get_db)):
    print(tickerlist_inc)
    refused_tickers = []
    tickerlist = tickerlist_inc
    for ticker in tickerlist_inc:
        try:
            updated_at = db.query(models.Stock.updated_at).filter(models.Stock.ticker == ticker).first()
            if datetime.now() - timedelta(hours=5) <= updated_at or updated_at is None:
                refused_tickers.append(ticker)
                tickerlist.remove(ticker)
        except:
            pass
    updated_results = get_some_tickers(tickerlist)
    print(updated_results["ex_dividend_date"])
    for index, row in updated_results.iterrows():
        query = (
            update(models.Stock)
            .where(models.Stock.ticker == row["ticker"])
            .values(
                price=row["price"],
                marketcap=row["marketcap"],
                dividends=row["dividends"],
                dividend_yield=row["dividend_yield"],
                ex_dividend_date=row["ex_dividend_date"],
                beta=row["beta"],
                fifty_two_week_high=row["fifty_two_week_high"],
                fifty_two_week_low=row["fifty_two_week_low"],
                fifty_day_avg=row["fifty_day_avg"],
                recommendation=row["recommendation"],
                total_cash_per_share=row["total_cash_per_share"],
                profit_margins=row["profit_margins"],
                volume=row["volume"],
            )
        )
        sql.execute(query, engine)
    updated_tickers = []
    for ticker in tickerlist:
        ticker_queried = db.query(models.Stock).filter(models.Stock.ticker == ticker).first()
        updated_tickers.append(ticker_queried)
    result = {}
    result["refused_tickers"] = {
        "tickers": refused_tickers,
        "reason": "These tickers have already been updated recently",
    }
    result["updated_tickers"] = {"tickers": updated_tickers}
    print(result)
    return result
