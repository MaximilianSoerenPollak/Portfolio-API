import streamlit as st
import pandas as pd
import requests
import yahooquery as yq
import plotly.express as px
from decouple import config
from datetime import datetime

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


def get_historical_data(symbol, interval, period, adjusted):
    ticker = yq.Ticker(symbol)
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
    print(ex_dividend_date)
    if ex_dividend_date is not "":
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