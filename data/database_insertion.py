import sys

sys.path.append("/home/maxi/dev")
import pandas as pd
from pandas.io import sql
from data.full_da import main
from datetime import datetime
from api.database import engine


def load_all_data(save: bool = True):
    # today = datetime.utcnow().date().strftime("%Y-%m-%d")
    # nyse_df, nasdaq_df = main(save, today)
    nyse_df = pd.read_csv("/home/maxi/dev/data/backup_csv/nyse2022-03-16.csv")
    nyse_df = nyse_df.drop("Unnamed: 0", axis=1)
    nasdaq_df = pd.read_csv("/home/maxi/dev/data/backup_csv/nasdaq2022-03-16.csv")
    nasdaq_df = nasdaq_df.drop("Unnamed: 0", axis=1)
    df_to_insert = pd.concat([nyse_df, nasdaq_df], ignore_index=True)

    # sql.execute("ALTER TABLE stocks RENAME COLUMN index to id", engine)


#!TODo make sure that there is a primary key that increments in the table.

# nyse_df.rename({"index": "id"}, inplace=True)
# load_all_data()
# nyse_df = pd.read_csv("/home/maxi/dev/nyse2022-03-16.csv")
# nyse_df = nyse_df.drop("Unnamed: 0", axis=1)

# print(nyse_df.columns)
nyse_df = pd.read_csv("/home/maxi/dev/data/backup_csv/nyse2022-03-16.csv")
nyse_df = nyse_df.drop("Unnamed: 0", axis=1)
nasdaq_df = pd.read_csv("/home/maxi/dev/data/backup_csv/nasdaq2022-03-16.csv")
nasdaq_df = nasdaq_df.drop("Unnamed: 0", axis=1)
df_to_insert = pd.concat([nyse_df, nasdaq_df], ignore_index=True)
# print(df_to_insert[df_to_insert.eq("{}").any(1)])
df_to_insert = df_to_insert.applymap(lambda x: None if x == "{}" else x)
sql.execute("DELETE FROM stocks CASCADE;", engine)
df_to_insert.to_sql("stocks", engine, if_exists="append", index=False)
