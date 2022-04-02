#%%
import database
import pandas as pd
from sqlalchemy import create_engine
from pandas.io import sql

# #%%
# df = pd.read_csv("test.csv")
SQLALCHEMY_DATABASE_URL = "digital-ocean connection string."

engine = create_engine(SQLALCHEMY_DATABASE_URL)
# df.head()

if __name__ == '__main__':
    nyse_df = pd.read_csv("data/backup_csv/nyse2022-04-01.csv")
    nasdaq_df = pd.read_csv("data/backup_csv/nasdaq2022-04-01.csv")
    nyse_df.drop("Unnamed: 0", axis=1, inplace=True)
    nasdaq_df.drop("Unnamed: 0", axis=1, inplace=True)
    df_to_insert = pd.concat([nyse_df, nasdaq_df]).drop_duplicates().reset_index(drop=True)
    sql.execute("TRUNCATE stocks RESTART IDENTITY CASCADE;", engine)
    df_to_insert.to_sql("stocks", engine, if_exists="append", index=False)
# %%
# df["ex_dividend_date"].unique()
# # %%
# for index, value in enumerate(df["ex_dividend_date"]):
#     if type(value) is dict:
#         print(index, type(value))
# # %%
# df.loc[df["ex_dividend_date"] == "0", "ex_dividend_date"] = None
# df.loc[df["ex_dividend_date"] == "{}", "ex_dividend_date"] = None
# df["ex_dividend_date"] = pd.to_datetime(df["ex_dividend_date"], errors="ignore")
# # %%
# df.info()
# %%
