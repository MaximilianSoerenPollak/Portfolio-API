# %%
import pandas as pd
import requests
import yahooquery as yq
import os
import numpy as np
import datetime as dt

basedir = os.path.dirname(os.path.abspath(__file__))

# %%
# TODO EUronext still does not work. For now I will download the csv manually but it should somehow be fixed in the future
# Link for HK https://www.hkex.com.hk/eng/services/trading/securities/securitieslists/ListOfSecurities.xlsx
url_nasdaq = "https://api.nasdaq.com/api/screener/stocks?exchange=NASDAQ&download=true&limit=10"
url_nyse = "https://api.nasdaq.com/api/screener/stocks?exchange=NYSE&download=true&limit=10"
# %%
# This function currently only works for NASDAQ and NYSE URLs. Has to be modified if others are introduced.


def get_tickers(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"
    }
    r = requests.get(url, headers=headers).json()
    df = pd.DataFrame(r["data"]["rows"])
    df = df[df["symbol"].str.len() < 5]
    index_to_delete = []
    for index, value in enumerate(df["symbol"]):
        if "^" in value:
            index_to_delete.append(index)
    df = df.drop(df.index[index_to_delete])
    df_result = pd.DataFrame(columns=["ticker"])
    df_result["ticker"] = df["symbol"]
    return df_result


# %%
def make_ticker_list(df, removed_tickers=None):
    ticker_list = list(df["ticker"])
    if removed_tickers:
        ticker_list = [x for x in ticker_list if x not in removed_tickers]
    return ticker_list


# %%
def get_stock_data(ticker_list):
    if ticker_list:
        ticker = yq.Ticker(
            ticker_list,
            asynchronous=True,
            status_forcelist=[429, 500, 502, 503, 504, 404],
            validate=True,
        )
        modules = "financialData quoteType summaryProfile summaryDetail"
        results = ticker.get_modules(modules)
        return results, ticker.invalid_symbols
    else:
        raise ValueError("Passed an empty list as Argument")


# %%
def make_data_list(dictionary, ticker_list, upperdict, lowerdict):
    result_list = []
    dict_filter_float = [
        "dividendRate",
        "currentPrice",
        "fiftyTwoWeekHigh",
        "fiftyTwoWeekLow",
        "fiftyDayAverage",
        "totalCashPerShare",
        "profitMargins",
        "beta",
    ]
    dict_filter_int = [
        "marketCap",
        "volume",
    ]
    for ticker in ticker_list:
        try:
            wanted_info = dictionary[ticker][upperdict][lowerdict]
            if lowerdict in dict_filter_float:
                wanted_info = float(wanted_info)
            if lowerdict in dict_filter_int:
                wanted_info = int(wanted_info)
            result_list.append(wanted_info)

        except:
            result_list.append(np.nan)
    return result_list


# %%
# ! Careful. yahooticker is integrated but not made working. It is for EU and Asian stocks once those are also in the DA pipeline
# ! Then there will be a need to rewrite yahoo_ticker BEFORE we gather the data via yahooquery (get_stock_data).


def make_df(dictionary, ticker_list):
    column_dict = {
        "name": ["quoteType", "shortName"],
        "ticker": ["quoteType", "symbol"],
        "exchange": ["quoteType", "exchange"],
        "sector": ["summaryProfile", "sector"],
        "industry": ["summaryProfile", "industry"],
        "long_business_summary": ["summaryProfile", "longBusinessSummary"],
        "country": ["summaryProfile", "country"],
        "website": ["summaryProfile", "website"],
        "price": ["financialData", "currentPrice"],
        "beta": ["summaryDetail", "beta"],
        "marketcap": ["summaryDetail", "marketCap"],
        "dividends": ["summaryDetail", "dividendRate"],
        "ex_dividend_date": ["summaryDetail", "exDividendDate"],
        "fifty_two_week_high": ["summaryDetail", "fiftyTwoWeekHigh"],
        "fifty_two_week_low": ["summaryDetail", "fiftyTwoWeekLow"],
        "fifty_day_avg": ["summaryDetail", "fiftyDayAverage"],
        "recommendation": ["financialData", "recommendationKey"],
        "total_cash_per_share": ["financialData", "totalCashPerShare"],
        "profit_margins": ["financialData", "profitMargins"],
        "volume": ["summaryDetail", "volume"],
    }
    stock_df = pd.DataFrame(columns=column_dict.keys())
    for k, v in column_dict.items():
        stock_df[k] = make_data_list(dictionary, ticker_list, v[0], v[1])
    stock_df["dividend_yield"] = stock_df["dividends"].divide(stock_df["price"], fill_value=0)
    stock_df["yahoo_ticker"] = stock_df["ticker"]
    stock_df[["dividend_yield", "profit_margins"]] = stock_df[["dividend_yield", "profit_margins"]].round(decimals=4)
    stock_df["fifty_day_avg"] = stock_df["fifty_day_avg"].round(decimals=2)
    new_column_order = [
        "name",
        "ticker",
        "yahoo_ticker",
        "exchange",
        "sector",
        "industry",
        "long_business_summary",
        "country",
        "website",
        "price",
        "marketcap",
        "dividends",
        "dividend_yield",
        "ex_dividend_date",
        "beta",
        "fifty_two_week_high",
        "fifty_two_week_low",
        "fifty_day_avg",
        "recommendation",
        "total_cash_per_share",
        "profit_margins",
        "volume",
    ]
    stock_df = stock_df[new_column_order]
    stock_df.loc[stock_df["ex_dividend_date"] == "0", "ex_dividend_date"] = None
    stock_df.loc[stock_df["ex_dividend_date"] == "{}", "ex_dividend_date"] = None
    stock_df["ex_dividend_date"] = pd.to_datetime(stock_df["ex_dividend_date"], errors="ignore")
    stock_df["ex_dividend_date"] = stock_df["ex_dividend_date"].dt.date
    stock_df = stock_df[stock_df["name"].notna()]
    stock_df = stock_df.replace(0, np.nan)
    stock_df = stock_df.replace("0", None)
    stock_df = stock_df[~stock_df["price"].isna()]
    cols = list(stock_df.columns)
    stock_df = stock_df.dropna(subset=cols, thresh=7)
    return stock_df


# %%
def make_csv(df, filename, path):
    df.to_csv(path + filename)
    print(f"CSV has been save under {filename} in {path}")


# %%
def make_df_final(exchange):
    tickers_df = get_tickers(exchange)
    ticker_list = make_ticker_list(tickers_df)
    temp_dict, invalid_tickers = get_stock_data(ticker_list)
    final_ticker_list = make_ticker_list(tickers_df, invalid_tickers)
    final_df = make_df(temp_dict, final_ticker_list)
    return final_df


# %%
def get_all_tickers(save: bool = False, date: str = None):
    nyse_df = make_df_final(url_nyse)
    nasdaq_df = make_df_final(url_nasdaq)
    if save:
        make_csv(df=nyse_df, filename=("nyse" + date + ".csv"), path=basedir + "/backup_csv/")
        make_csv(df=nasdaq_df, filename=("nasdaq" + date + ".csv"), path=basedir + "/backup_csv/")
    return nyse_df, nasdaq_df


# %%
def get_some_tickers(tickerlist):
    results, invalid_tickers = get_stock_data(tickerlist)
    results_df = make_df(results, tickerlist)
    return results_df
