from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db, load_some_data
from typing import List, Optional
from datetime import timedelta, datetime, timezone
from sqlalchemy import insert

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/", response_model=List[schemas.StockResponseSolo])
def get_stocks(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
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
    if all_stocks:
        return query.order_by(models.Stock.ticker).all()
    else:
        return query.order_by(models.Stock.ticker).limit(limit).offset(skip).all()


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


@router.get("/{ticker}", response_model=schemas.StockResponseSolo)
def get_stock(ticker: str, response: Response, db: Session = Depends(get_db)):
    stock = db.query(models.Stock).filter(models.Stock.ticker == ticker).first()
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"stock with ticker: {ticker} was not found.")
    return stock


@router.delete("/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stock(ticker: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # !Todo only admin can delete.
    stock_query = db.query(models.Stock).filter(models.Stock.ticker == ticker)
    stock = stock_query.first()
    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Stock with ticker: {ticker} does not exist")
    if stock.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized.")
    stock_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{ticker}", response_model=schemas.StockResponseSolo)
def update_stock_manually(
    ticker: str,
    updated_stock: schemas.StockCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    stock_query = db.query(models.Stock).filter(models.Stock.ticker == ticker)
    stock = stock_query.first()
    if stock is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Stock with ticker: {ticker} does not excist"
        )
    if stock.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized.")
    stock_query.update(updated_stock.dict(), synchronize_session=False)
    db.commit()
    return stock_query.first()


@router.post("/add/{portfolio_id}")
def add_stock_to_portfolio(
    portfolio_id: int, stock_tickers: List[str], response: Response, db: Session = Depends(get_db)
):
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.id == portfolio_id).first()
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No portfolio with id: {id} found.")
    not_found_stocks = []
    stocks_already_in_portfolio = []
    results = {}
    for ticker in set(stock_tickers):
        stock = db.query(models.Stock).filter(models.Stock.ticker == ticker).first()
        if stock is None:
            not_found_stocks.append(ticker)
    for ticker in stock_tickers:
        try:
            db.execute(insert(models.PortfolioStock).values(stock_ticker=ticker, portfolio_id=portfolio_id))
            setattr(stock, "status", "1")
            db.commit()
        except Exception:
            # Todo: Figure out what the correct exception is. Does not seem to be "Unique Violation" from psygop2.
            stocks_already_in_portfolio.append(ticker)
            db.rollback()
    if not_found_stocks:
        results["tickers_not_found"] = set(not_found_stocks)
    if stocks_already_in_portfolio:
        results["tickers_not_added"] = {
            "tickers": set(stocks_already_in_portfolio),
            "reason": "These stocks are already in this portfolio",
        }
    results["tickers_inserted"] = [
        x for x in stock_tickers if x not in not_found_stocks and x not in stocks_already_in_portfolio
    ]
    return results


# TODO Test Route
@router.post("/update")
def update_stocks(tickerlist_inc: List[str], response: Response, db: Session = Depends(get_db)):
    refused_tickers = []
    updated_tickers = []
    result = {}
    tickerlist = tickerlist_inc.copy()
    for ticker in set(tickerlist_inc):
        updated_at = db.query(models.Stock.updated_at).filter(models.Stock.ticker == ticker).first()
        time_threshold = datetime.now(timezone.utc) - timedelta(hours=5)
        if updated_at.updated_at is None:
            continue
        if time_threshold < updated_at.updated_at:
            refused_tickers.append(ticker)
            tickerlist.remove(ticker)
    try:
        load_some_data(tickerlist)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail=f"Stocks with the tickers {tickerlist_inc} were already updated recently.",
        )
    for ticker in tickerlist:
        ticker_queried = db.query(models.Stock).filter(models.Stock.ticker == ticker).first()
        updated_tickers.append(ticker_queried)
    if refused_tickers and updated_tickers:
        result["refused_tickers"] = {
            "tickers": refused_tickers,
            "reason": "These tickers have already been updated recently",
        }
        result["updated_tickers"] = {"tickers": updated_tickers}
    elif not refused_tickers and updated_tickers:
        result["updated_tickers"] = {"tickers": updated_tickers}
    return result
