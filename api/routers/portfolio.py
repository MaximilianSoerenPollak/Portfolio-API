from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db
from typing import List

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.get("/", response_model=List[schemas.PortfolioResponse])
def get_all_portfolios(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    portfolios = db.query(models.Portfolio).filter(models.Portfolio.user_id == current_user.id).all()
    return portfolios


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


@router.get("/{id}", response_model=schemas.PortfolioResponse)
def get_portfolio(id: int, response: Response, db: Session = Depends(get_db)):
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.id == id).first()
    if not portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, details=f"No portfolio with id: {id} found.")
    return portfolio


# TODO figure out how to add stocks (as lists) to portfolios.
