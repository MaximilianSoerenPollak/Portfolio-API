import streamlit as st
import pandas as pd
import requests
import yahooquery as yq
import plotly.express as px
from decouple import config
from datetime import datetime
import numpy as np
from pypfopt import HRPOpt
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientCVaR

# ---- FUNCTIONS ----
# ---- LOGIN ----
@st.cache
def login(email, password):
    url = f"{config('API_URL')}/login"
    login_data = {"username": email, "password": password}
    request = requests.post(url, login_data)
    if request.status_code == 200:
        data = request.json()
        secret_token = data["access_token"]
        bearer_token = secret_token
        return bearer_token
    else:
        return False


def signup(email, password):
    url = f"{config('API_URL')}/users"
    headers = {"Content-Type": "application/json"}
    signup_data = {"email": email, "password": password}
    request = requests.post(url, json=signup_data, headers=headers)
    if request.status_code == 201:
        data = request.json()
        email = data["email"]
        return email
    else:
        return False


# ---- STOCK DATA COLLECTION ---


@st.cache
def get_all_stocks():
    token = st.session_state.jwt_token
    url = f"{config('API_URL')}/stocks?all_stocks=True"
    headers = {"Authorization": "Bearer " + token}
    request = requests.get(url, headers=headers)
    if request.status_code == 200:
        data = request.json()
        return pd.json_normalize(data)
    elif request.status_code == 401:
        return False


def get_historical_data(symbols, interval, period, adjusted):
    ticker = yq.Ticker(symbols)
    df = ticker.history(interval=interval, period=period, adj_ohlc=adjusted)
    df = df.reset_index()
    return df


# ---- DATAFRAME FUNCTIONS ----


@st.cache
def search_df(
    inc_df,
    div_check,
    exchanges,
    sectors,
    industries,
    countries,
    recommendation,
    max_price,
    marketcap,
    min_div,
    min_div_yield,
    fifty_day_avg,
    min_cps,
    min_profit,
    min_volume,
):
    df = inc_df.copy()
    if div_check:
        df = df[df["dividends"] > 0]
    if exchanges:
        df = df[df["exchange"].isin(exchanges)]
    if sectors:
        df = df[df["sector"].isin(sectors)]
    if industries:
        df = df[df["industry"].isin(industries)]
    if countries:
        df = df[df["country"].isin(countries)]
    if recommendation:
        df = df[df["recommendation"].isin(recommendation)]
    if max_price:
        df = df[df["price"] <= max_price]
    if min_div:
        df = df[df["dividends"] >= min_div]
    if min_div_yield:
        df = df[df["dividend_yield"] >= min_div_yield]
    if min_cps:
        df = df[df["total_cash_per_share"] >= min_cps]
    if min_profit:
        df = df[df["profit_margins"] >= min_profit]
    if min_volume:
        df = df[df["volume"] >= min_volume]
    return df


def save_df_as_cv(df):
    return df.to_csv().encode("utf-8")


def add_stock_to_db(
    name,
    ticker,
    yahoo_ticker,
    price,
    exchange=None,
    sector=None,
    industry=None,
    long_business_summary=None,
    country=None,
    website=None,
    recommendation=None,
    ex_dividend_date=None,
    marketcap=None,
    dividends=None,
    dividend_yield=None,
    beta=None,
    fifty_two_week_high=None,
    fifty_two_week_low=None,
    fifty_day_avg=None,
    total_cash_per_share=None,
    profit_margins=None,
    volume=None,
):
    token = st.session_state.jwt_token
    url = f"{config('API_URL')}/stocks"
    headers = {"Authorization": "Bearer " + token}
    if ex_dividend_date != "":
        ex_dividend_date = datetime.strptime(ex_dividend_date, "%Y-%m-%d")
    data = {
        "name": name,
        "ticker": ticker,
        "yahoo_ticker": yahoo_ticker,
        "price": price,
        "exchange": exchange,
        "sector": sector,
        "industry": industry,
        "long_business_summary": long_business_summary,
        "country": country,
        "website": website,
        "recommendation": recommendation,
        "ex_dividend_date": ex_dividend_date,
        "marketcap": marketcap,
        "dividends": dividends,
        "dividend_yield": dividend_yield,
        "beta": beta,
        "fifty_two_week_high": fifty_two_week_high,
        "fifty_two_week_low": fifty_two_week_low,
        "fifty_day_avg": fifty_day_avg,
        "total_cash_per_share": total_cash_per_share,
        "profit_margins": profit_margins,
        "volume": volume,
    }

    request = requests.post(url, json=data, headers=headers)
    if request.status_code == 201:
        data = request.json()
        return data
    else:
        return False


def get_portfolios(allow_output_mutation=True):
    token = st.session_state.jwt_token
    url = f"{config('API_URL')}/portfolios"
    headers = {"Authorization": "Bearer " + token}
    request = requests.get(url, headers=headers)
    if request.status_code == 200:
        data = request.json()
        portfolio_name_id = []
        for portfolio in data:
            portfolio_name_id.append((portfolio["name"], portfolio["id"]))
        return portfolio_name_id
    elif request.status_code == 401:
        st.session_state.logged_in = False
        return False
    else:
        return False


def get_one_portfolio(portfolio_id):
    token = st.session_state.jwt_token
    url = f"{config('API_URL')}/portfolios/{portfolio_id}"
    headers = {"Authorization": "Bearer " + token}
    request = requests.get(url, headers=headers)
    if request.status_code == 200:
        data = request.json()
        return data[0]
    elif request.status_code == 401:
        st.session_state.logged_in = False
        return False
    else:
        return False


def calc_total_div(stocks):
    total_div = 0
    for stock in stocks:
        if stock["dividends"]:
            dividends = stock["dividends"]
            count = stock["count"]
            total_div += dividends * count
    return total_div


def calc_total_capital(stocks):
    capital = 0
    for stock in stocks:
        price = stock["price"]
        count = stock["count"]
        capital += price * count
    return capital


def calc_buyin_capital(stocks):
    buyin_capital = 0
    for stock in stocks:
        buyin = stock["buy_in"]
        count = stock["count"]
        buyin_capital += buyin * count
    return buyin_capital


def industry_distribution(stocks):
    fig = px.pie(
        stocks, values=stocks["industry"].value_counts(), names="industry", title="% of Stocks in each industry"
    )
    return fig


def sector_distribution(stocks):
    fig = px.pie(
        stocks,
        values=stocks["sector"].value_counts(),
        names=stocks["sector"].unique(),
        title="% of Stocks in each sector",
    )
    return fig


def div_vs_nondiv_distribution(stocks):
    zero_stocks = stocks["dividends"].isna().sum()
    div_stocks = len(stocks) - zero_stocks
    fig = px.pie(
        stocks,
        values=[div_stocks, zero_stocks],
        names=["Stocks with dividends", "Stock without dividend"],
        title="% of Stocks with and without dividends.",
    )
    return fig


def div_contrib_distribution(stocks, total_div):
    fig = px.pie(
        stocks,
        values=total_div / (stocks["count"] * stocks["dividends"]),
        names="name",
        title="% of contribution towards the total Dividends by stock.",
    )
    return fig


def stock_distribution_count(stocks):
    stock_nr = stocks["count"].sum()
    fig = px.pie(
        stocks,
        values=stocks["count"] / stock_nr,
        names="name",
        title="% of Stocks with and without dividends.",
    )
    return fig


def stock_distribution_percent_capital(list_of_stocks):
    capital = calc_total_capital(list_of_stocks)
    df = pd.DataFrame()
    stock_value_lst = []
    name_lst = []
    for stock in list_of_stocks:
        name_lst.append(stock["name"])
        value = stock["buy_in"] * stock["count"]
        stock_value_lst.append(value)
    df["name"] = name_lst
    df["value"] = stock_value_lst
    fig = px.pie(df, values=df["value"] / capital, names="name", title="% of capital per stock")
    return fig


def calc_cagr(stock):
    df = get_historical_data(stock, "1d", "1y", True)
    df["daily_returns"] = df["close"].pct_change()
    df["cumulative_returns"] = (1 + df["daily_returns"]).cumprod()
    trading_days = 252
    n = len(df) / trading_days
    cagr = (df.iloc[-1]["cumulative_returns"]) ** (1 / n) - 1
    return cagr


def calc_volatility(stock):
    df = get_historical_data(stock, "1d", "1y", True)
    df["daily_returns"] = df["close"].pct_change()
    trading_days = 252
    vol = df["daily_returns"].std() * np.sqrt(trading_days)
    return vol


def calc_sharpe_ratio(stock, rf):
    sharpe = (calc_cagr(stock) - rf) / calc_volatility(stock)
    return sharpe


def prep_historical_df(symbols, period):
    df = get_historical_data(symbols, "1d", period, True)
    df = df[["symbol", "date", "close"]]
    df = df.pivot_table(values="close", index="date", columns="symbol", aggfunc="first")
    return df


def calc_hrp(symbols, period):
    df = prep_historical_df(symbols, period)
    returns = df.pct_change().dropna()
    hrp = HRPOpt(returns)
    hrp_weights = hrp.optimize()
    return hrp.portfolio_performance(verbose=True), hrp_weights


def calc_mcvar(symbols, period):
    df = prep_historical_df(symbols, period)
    mu = mean_historical_return(df)
    S = df.cov()
    ef_cvar = EfficientCVaR(mu, S)
    cvar_weights = ef_cvar.min_cvar()
    cleaned_weights = ef_cvar.clean_weights()
    return ef_cvar, cvar_weights


def allocation_portfolio(tickers, period, weights, portfolio_value):
    df = prep_historical_df(tickers, period)
    latest_prices = get_latest_prices(df)
    da_hrp = DiscreteAllocation(weights, latest_prices, total_portfolio_value=portfolio_value)
    allocation, leftover = da_hrp.greedy_portfolio()
    return allocation, leftover


def combined_all_portfolios(portfolio_list):
    token = st.session_state.jwt_token
    url = f"{config('API_URL')}/portfolios"
    headers = {"Authorization": "Bearer " + token}
    request = requests.get(url, headers=headers)
    if request.status_code == 200:
        data = request.json()
        portfolio_combined = {}
        mon_goal = 0
        div_goal = 0
        stock_list = []
        for portfolio in data:
            div_goal += portfolio["dividends_goal"]
            mon_goal += portfolio["monetary_goal"]
            for stock in portfolio["stocks"]:
                stock_list.append(stock)
        portfolio_combined["monetary_goal"] = mon_goal
        portfolio_combined["dividends_goal"] = div_goal
        portfolio_combined["stocks"] = stock_list
        portfolio_combined["name"] = "Combined Portfolio"
        return portfolio_combined
    else:
        return False
