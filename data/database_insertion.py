import sys

sys.path.append("/home/maxi/dev")
import pandas as pd
from pandas.io import sql
from data.full_da import main

from api.database import engine

# nyse_df, nasdaq_df = main()
#!TODo make sure that there is a primary key that increments in the table.
nyse_df = pd.read_csv("/home/maxi/dev/datanyse.csv")
nyse_df = nyse_df.drop("Unnamed: 0", axis=1)
# nyse_df.rename({"index": "id"}, inplace=True)
# sql.execute("DROP TABLE IF EXISTS stocks CASCADE", engine)
# nyse_df.to_sql("stocks", engine)
sql.execute("ALTER TABLE stocks RENAME COLUMN index to id", engine)
