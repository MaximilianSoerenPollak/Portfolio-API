import pandas as pd
from sqlalchemy import create_engine, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pandas.io import sql
from data.full_da import get_all_tickers, get_some_tickers
from datetime import datetime
from .config import settings

# -------------- Establish Connection to DB --------------------------------

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

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
    # nyse_df = pd.read_csv("/home/maxi/dev/data/backup_csv/nyse2022-03-17.csv")
    # nyse_df = nyse_df.drop("Unnamed: 0", axis=1)
    # nasdaq_df = pd.read_csv("/home/maxi/dev/data/backup_csv/nasdaq2022-03-17.csv")
    # nasdaq_df = nasdaq_df.drop("Unnamed: 0", axis=1)
    df_to_insert = pd.concat([nyse_df, nasdaq_df]).drop_duplicates().reset_index(drop=True)
    sql.execute("TRUNCATE stocks RESTART IDENTITY CASCADE;", engine)
    df_to_insert.to_sql("stocks", engine, if_exists="append", index=False)


# 10, 50, 20
def load_some_data(tickerlist):
    pass

    # sql.execute(
    #     """UPDATE stocks
    #     SET price={}, marketcap={}, dividends={}, dividend_yield={}, ex_dividend_date={},
    #             beta={}, fifty_two_week_high={}, fifty_two_week_low={}, fifty_day_avg={}, recommendation={},
    #             total_cash_per_share={}, profit_margins={}, volume={}
    #             WHERE ticker={};""".format(
    #         row["price"],
    #         row["marketcap"],
    #         row["dividends"],
    #         row["dividend_yield"],
    #         row["ex_dividend_date"],
    #         row["beta"],
    #         row["fifty_two_week_high"],
    #         row["fifty_two_week_low"],
    #         row["fifty_day_avg"],
    #         row["recommendation"],
    #         row["total_cash_per_share"],
    #         row["profit_margins"],
    #         row["volume"],
    #         row["ticker"],
    #     ),
    #     engine,
    # )
