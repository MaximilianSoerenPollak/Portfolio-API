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
    int_dict_filter = [
        "dividendRate",
        "currentPrice",
        "marketCap",
        "fiftyTwoWeekHigh",
        "fiftyTwoWeekLow",
        "fiftyDayAverage",
        "totalCashPerShare",
        "profitMargins",
        "volume",
    ]
    for ticker in ticker_list:
        try:
            wanted_info = dictionary[ticker][upperdict][lowerdict]
            if lowerdict in int_dict_filter:
                wanted_info = float(wanted_info)
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
        "marketcap": ["summaryDetail", "marketCap"],
        "dividends": ["summaryDetail", "dividendRate"],
        "ex_dividend_date": ["summaryDetail", "exDividendDate"],
        "fiftytwo_week_high": ["summaryDetail", "fiftyTwoWeekHigh"],
        "fiftytwo_week_low": ["summaryDetail", "fiftyTwoWeekLow"],
        "fifty_day_avgerage": ["summaryDetail", "fiftyDayAverage"],
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
def main():
    nyse_df = make_df_final(url_nyse)
    nasdaq_df = make_df_final(url_nasdaq)
    return nyse_df, nasdaq_df


# %%
# nyse_df, nasdaq_df = main()
# make_csv(nyse_df, "nyse.csv", "/home/maxi/dev/data")
# make_csv(nasdaq_df, "nasdaq.csv", "/home/maxi/dev/data")

# %%
