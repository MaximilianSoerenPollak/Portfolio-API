# %%
import pandas as pd
import requests
import yahooquery as yq

# %%
# TODO EUronext still does not work. For now I will download the csv manually but it should somehow be fixed in the future
# Link for HK https://www.hkex.com.hk/eng/services/trading/securities/securitieslists/ListOfSecurities.xlsx
url_nasdaq = "https://api.nasdaq.com/api/screener/stocks?exchange=NASDAQ&download=true&limit=10"
url_nyse = "https://api.nasdaq.com/api/screener/stocks?exchange=NYSE&download=true&limit=10"
# %%
# This function currently only works for NASDAQ and NYSE URLs. Has to be modified if others are introduced.


def get_tickers(url):
    headers = {
        """User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) 
        Chrome/81.0.4044.141 Safari/537.36"""
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
    ticker = yq.Ticker(
        ticker_list,
        asynchronous=True,
        progress=True,
        status_forcelist=[429, 500, 502, 503, 504, 404],
        validate=True,
    )
    modules = "financialData quoteType summaryProfile summaryDetail"
    results = ticker.get_modules(modules)
    return results, ticker.invalid_symbols


# %%
def make_data_list(dictionary, ticker_list, upperdict, lowerdict):
    result_list = []
    int_dict_filter = ["dividendRate", "currentPrice", "marketCap"]
    for ticker in ticker_list:
        try:
            wanted_info = dictionary[ticker][upperdict][lowerdict]
            result_list.append(wanted_info)
        except:
            if lowerdict in int_dict_filter:
                result_list.append(0)
            else:
                result_list.append("nan")
    return result_list


# %%
# %%
# ! Careful. yahooticker is integrated but not made working. It is for EU and Asian stocks once those are also in the DA pipeline
# ! Then there will be a need to rewrite yahoo_ticker BEFORE we gather the data via yahooquery (get_stock_data).


def make_df(dictionary, ticker_list):
    columns = [
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
        "fiftytwo_week_high",
        "fiftytwo_week_low",
        "fifty_day_average",
        "recommendation",
        "total_cash_per_share",
        "profit_margins",
        "volume",
    ]
    stock_df = pd.DataFrame(columns=columns)
    stock_df["name"] = make_data_list(dictionary, ticker_list, "quoteType", "shortName")
    stock_df["ticker"] = make_data_list(dictionary, ticker_list, "quoteType", "symbol")
    stock_df["yahoo_ticker"] = stock_df["ticker"]
    stock_df["exchange"] = make_data_list(dictionary, ticker_list, "quoteType", "exchange")
    stock_df["sector"] = make_data_list(dictionary, ticker_list, "summaryProfile", "sector")
    stock_df["industry"] = make_data_list(dictionary, ticker_list, "summaryProfile", "industry")
    stock_df["long_business_summary"] = make_data_list(dictionary, ticker_list, "summaryProfile", "longBusinessSummary")
    stock_df["country"] = make_data_list(dictionary, ticker_list, "summaryProfile", "country")
    stock_df["website"] = make_data_list(dictionary, ticker_list, "summaryProfile", "website")
    stock_df["price"] = make_data_list(dictionary, ticker_list, "financialData", "currentPrice")
    stock_df["marketcap"] = make_data_list(dictionary, ticker_list, "summaryDetail", "marketCap")
    stock_df["dividends"] = make_data_list(dictionary, ticker_list, "summaryDetail", "dividendRate")
    stock_df["dividend_yield"] = stock_df["dividends"].divide(stock_df["price"], fill_value=0)
    stock_df["ex_dividend_data"] = make_data_list(dictionary, ticker_list, "summaryDetail", "exDividendDate")
    stock_df["beta"] = make_data_list(dictionary, ticker_list, "summaryDetail", "beta")
    stock_df["fiftytwo_week_high"] = make_data_list(dictionary, ticker_list, "summaryDetail", "fiftyTwoWeekHigh")
    stock_df["fiftytwo_week_low"] = make_data_list(dictionary, ticker_list, "summaryDetail", "fiftyTwoWeekLow")
    stock_df["fifty_day_average"] = make_data_list(dictionary, ticker_list, "summaryDetail", "fiftyDayAverage")
    stock_df["recommendation"] = make_data_list(dictionary, ticker_list, "financialData", "recommendationKey")
    stock_df["total_cash_per_share"] = make_data_list(dictionary, ticker_list, "financialData", "totalCashPerShare")
    stock_df["profit_margins"] = make_data_list(dictionary, ticker_list, "financialData", "proiftMargins")
    stock_df["volume"] = make_data_list(dictionary, ticker_list, "summaryDetail", "volume")
    return stock_df


# %%
def make_csv(df, filename, path):
    df.to_csv(path + filename)
    print(f"CSV has been save under {filename} in {path}")


# %%
def make_nyse_df():
    nyse_tickers_df = get_tickers(url_nyse)
    # nasdaq_tickers_df = get_tickers(url_nasdaq)
    ticker_list_nyse = make_ticker_list(nyse_tickers_df)
    nyse_dict, invalid_tickers = get_stock_data(ticker_list_nyse)
    new_ticker_list_nyse = make_ticker_list(nyse_tickers_df, invalid_tickers)
    nyse_df = make_df(nyse_dict, new_ticker_list_nyse)
    return nyse_df


# %%
def make_nasdaq_df():
    nasdaq_tickers_df = get_tickers(url_nasdaq)
    ticker_list_nasdaq = make_ticker_list(nasdaq_tickers_df)
    nasdaq_dict, invalid_tickers = get_stock_data(ticker_list_nasdaq)
    new_ticker_list_nasdaq = make_ticker_list(nasdaq_tickers_df, invalid_tickers)
    nasdaq_df = make_df(nasdaq_dict, new_ticker_list_nasdaq)
    return nasdaq_df


# %%
# testing with just one atm. If this works then we are good
# TODO make
def main():
    nyse_df = make_nyse_df()
    nasdaq_df = make_nasdaq_df()
    return nyse_df, nasdaq_df


# # # %%
# %%

# %%
