from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session, joinedload
from .. import models, schemas, oauth2, utils
from ..database import get_db
from typing import List, Union

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.get("/", response_model=List[schemas.PortfolioSchema])
def get_all_portfolios(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    results = (
        db.query(models.Portfolio)
        .options(joinedload(models.Portfolio.stocks).options(joinedload(models.PortfolioStock.stock)))
        .all()
    )
    # breakpoint()
    return results


# Everything the validation model does not see seems to be in
# results[0]stocks[0].stock
# (so it somehow can't see that it has to validate the single instances of the list of stocks in the stock list)


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


@router.get("/{id}", response_model=List[Union[schemas.PortfolioSchema, schemas.PortfolioResponse]])
def get_portfolio(id: int, response: Response, db: Session = Depends(get_db)):
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.id == id).first()
    if not portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, details=f"No portfolio with id: {id} found.")
    return portfolio


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, details=f"No portfolio with id: {id} found.")
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized.")
    portfolio_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
