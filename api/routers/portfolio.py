from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session, joinedload
import models
import schemas
import oauth2
from database import get_db
from typing import List, Union

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.get("/")
def get_all_portfolios(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    results = (
        db.query(models.Portfolio)
        .options(joinedload(models.Portfolio.stocks).joinedload(models.PortfolioStock.stock))
        .all()
    )
    result_list = []
    for portfolio in results:
        result_dict = portfolio.__dict__
        stock_list = []
        for sto in result_dict["stocks"]:
            sto_dict = sto.__dict__
            temp_sto = {}
            temp_sto = sto_dict["stock"]
            setattr(temp_sto, "buy_in", sto_dict["buy_in"])
            setattr(temp_sto, "count", sto_dict["count"])
            stock_list.append(temp_sto)
        result_dict["stocks"] = stock_list
        result_list.append(result_dict)
    return result_list


@router.post("/", response_model=schemas.PortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    portfolio: schemas.PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    new_portfolio = models.Portfolio(user_id=current_user.id, **portfolio.dict())
    db.add(new_portfolio)
    db.commit()
    db.refresh(new_portfolio)
    return new_portfolio


@router.get("/{portfolio_id}", response_model=List[Union[schemas.PortfolioSchema, schemas.PortfolioResponse]])
def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(models.Portfolio)
        .filter(models.Portfolio.id == portfolio_id)
        .options(joinedload(models.Portfolio.stocks).joinedload(models.PortfolioStock.stock))
        .all()
    )
    result_list = []
    for portfolio in results:
        result_dict = portfolio.__dict__
        stock_list = []
        for sto in result_dict["stocks"]:
            sto_dict = sto.__dict__
            temp_sto = {}
            temp_sto = sto_dict["stock"]
            setattr(temp_sto, "buy_in", sto_dict["buy_in"])
            setattr(temp_sto, "count", sto_dict["count"])
            stock_list.append(temp_sto)
        result_dict["stocks"] = stock_list
        result_list.append(result_dict)
    return result_list


@router.put("/update/{portfolio_id}")
def update_stock_in_portfolio(
    updated_row: schemas.StockInPortfolioUpdate,
    portfolio_id=int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    association_row_query = (
        db.query(models.PortfolioStock)
        .filter(models.PortfolioStock.stock_ticker == updated_row.stock_ticker)
        .filter(models.PortfolioStock.portfolio_id == updated_row.portfolio_id)
    )
    association_row = association_row_query.first()
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.id == updated_row.portfolio_id).first()
    if not association_row:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Found no portfolio {updated_row.portfolio_id} with stock {updated_row.stock_ticker} in it.",
        )
    if portfolio.user_id != current_user.id:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized.")
    association_row_query.update(updated_row.dict(), synchronize_session=False)
    db.commit()
    return association_row_query.first()


@router.delete("/{portfolio_id}/{stock_ticker}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticker_from_portfolio(
    portfolio_id: int,
    stock_ticker: str,
    response: Response,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    association_row_query = (
        db.query(models.PortfolioStock)
        .filter(models.PortfolioStock.stock_ticker == stock_ticker)
        .filter(models.PortfolioStock.portfolio_id == portfolio_id)
    )
    association_row = association_row_query.first()
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.id == portfolio_id).first()
    if not association_row:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Found no portfolio {portfolio_id} with stock {stock_ticker} in it.",
        )
    if portfolio.user_id != current_user.id:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized.")
    association_row_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(
    portfolio_id: int,
    response: Response,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    portfolio_query = db.query(models.Portfolio).filter(models.Portfolio.id == portfolio_id)
    portfolio = portfolio_query.first()
    if not portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No portfolio with id: {id} found.")
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized.")
    portfolio_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
