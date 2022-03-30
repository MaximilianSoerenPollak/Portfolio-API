import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pandas.io import sql
from data.full_da import get_all_tickers, get_some_tickers
from datetime import datetime
from config import settings

# -------------- Establish Connection to DB --------------------------------

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password123@postgres:5432/fastapi"
print(SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------- Load Data into Database ----------------------


def load_all_data(save: bool = True):
    today = datetime.utcnow().date().strftime("%Y-%m-%d")
    nyse_df, nasdaq_df = get_all_tickers(save, today)
    df_to_insert = pd.concat([nyse_df, nasdaq_df]).drop_duplicates().reset_index(drop=True)
    sql.execute("TRUNCATE stocks RESTART IDENTITY CASCADE;", engine)
    df_to_insert.to_sql("stocks", engine, if_exists="append", index=False)


def load_some_data(tickerlist):
    updated_results = get_some_tickers(tickerlist)
    updated_results.to_sql("temp_stocks", engine, if_exists="replace")
    sql.execute(
        """UPDATE stocks
        SET
            price=temp_stocks.price,
            marketcap=temp_stocks.marketcap,
            dividends=temp_stocks.dividends,
            dividend_yield=temp_stocks.dividend_yield,
            ex_dividend_date=temp_stocks.ex_dividend_date,
            beta=temp_stocks.beta,
            fifty_two_week_high=temp_stocks.fifty_two_week_high,
            fifty_two_week_low=temp_stocks.fifty_two_week_low,
            fifty_day_avg=temp_stocks.fifty_day_avg,
            recommendation=temp_stocks.recommendation,
            total_cash_per_share=temp_stocks.total_cash_per_share,
            profit_margins=temp_stocks.profit_margins,
            volume=temp_stocks.volume,
            updated_at=current_timestamp
        FROM temp_stocks
        WHERE stocks.ticker = temp_stocks.ticker""",
        engine,
    )
