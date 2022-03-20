import streamlit as st
import pandas as pd
import requests
import yahooquery as yq
import plotly.express as px
from decouple import config

# ---- FUNCTIONS ----

st.set_page_config(layout="wide")

# ---- Inital Session state values ----

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


@st.cache
def login(email, password):
    url = f"{config('API_URL')}/login"
    login_data = {"username": email, "password": password}
    request = requests.post(url, login_data)
    if request.status_code == 200:
        data = request.json()
        bearer_token = data["access_token"]
        return bearer_token
    else:
        return False


def signup(email, password):
    url = f"{config('API_URL')}/users"
    headers = {"Content-Type": "application/json"}
    signup_data = {"email": email, "password": password}
    request = requests.post(url, signup_data, headers=headers)
    if request.status_code == 201:
        data = signup_data.json()
        email = data["email"]
        return email
    else:
        return False


@st.cache
def get_all_stocks(token):
    url = f"{config('API_URL')}/stocks?all_stocks=True"
    headers = {"Authorization": "Bearer " + token}
    request = requests.get(url, headers=headers)
    data = request.json()
    return pd.json_normalize(data)


def get_historical_data(symbol, interval, period, adjusted):
    ticker = yq.Ticker(symbol)
    df = ticker.history(interval=interval, period=period, adj_ohlc=adjusted)
    df = df.reset_index()
    return df


def save_df_as_cv(df):
    return df.to_csv().encode("utf-8")


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
    # & (inc_df["recommendation"] == eval(recommendation))
    #         (inc_df["exchange"] == eval(exchanges))
    # & (inc_df["sectors"] == eval(sectors))
    # & (inc_df["industry"] == eval(industries))
    # & (inc_df["country"] == eval(countries))


# ---- SIDEBAR ----
page_select = st.sidebar.selectbox(
    "Select Page", options=["Stocks", "Portfolio", "Stock-Detailed-View", "Login"], index=3
)

# ---- LOGIN -----
st.header("Welcome to Finance Capital.")
if page_select == "Login":
    login_expander = st.expander("Login")
    signup_expander = st.expander("Signup")
    with login_expander:
        with st.form("Login"):
            email = st.text_input("Email", placeholder="user@user.com")
            password = st.text_input("Password", placeholder="*******", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                token = login(email, password)
                if token:
                    if "jwt_token" not in st.session_state:
                        st.session_state.jwt_token = token
                    st.session_state.logged_in = True
                    st.success("You have successfully loged in")
                    st.balloons()

                else:
                    st.error("Could not authenticate you, please try again or if you have no account sign up.")
    with signup_expander:
        with st.form("Sign Up"):
            email = st.text_input("Email", placeholder="user@user.com")
            password = st.text_input("Password", placeholder="*******", type="password")
            password2 = st.text_input("Repeat Password", placeholder="*******", type="password")
            submitted = st.form_submit_button("Sign Up")
            if submitted:
                if password == password2:
                    answer = signup(email, password)
                    if answer:
                        st.info("You have successfully signed up!")
                        st.info("Please now Login.")
                    else:
                        st.error(
                            "Something went wrong, please check that you have entered a correct e-mail and try again. Or maybe you already have an account?"
                        )


# ---- STOCK DETAIL VIEW ----
if page_select == "Stock-Detailed-View":
    if st.session_state.logged_in:
        main_df = get_all_stocks(st.session_state.jwt_token)
        st.write(main_df[main_df["exchange"].isin([])])
        r1_col1, r1_col2 = st.columns(2)
        with r1_col1:
            search_criteria = st.radio("Search criteria", options=["Ticker", "Name"])
            if search_criteria == "Ticker":
                select_option = main_df["ticker"].tolist()
            elif search_criteria == "Name":
                select_option = main_df["name"].tolist()
        with r1_col2:
            searched_stock = st.selectbox(label="Stock to search for detailed view", options=select_option)
        st.write("---")
        if search_criteria == "Ticker":
            wanted_stock = main_df[main_df["ticker"] == searched_stock]
        elif search_criteria == "Name":
            wanted_stock = main_df[main_df["name"] == searched_stock]
        r2_col1, r2_col2, r2_col3, r2_col4 = st.columns((1.5, 2, 1.5, 2))
        with r2_col1:
            st.subheader(f"Name: {wanted_stock.iloc[0]['name']}")
            st.subheader(f"Ticker: {wanted_stock.iloc[0]['ticker']}")
            st.subheader(f"Exchange: {wanted_stock.iloc[0]['exchange']}")
            st.subheader(f"Recommendation: {wanted_stock.iloc[0]['recommendation']}")
        with r2_col2:
            st.subheader(f"Sector: {wanted_stock.iloc[0]['sector']}")
            st.subheader(f"Industry: {wanted_stock.iloc[0]['industry']}")
            st.subheader(f"Website: {wanted_stock.iloc[0]['website']}")
            st.subheader(f"Country: {wanted_stock.iloc[0]['country']}")
        with r2_col3:
            st.subheader(f"Price: ${wanted_stock.iloc[0]['price']} ")
            st.subheader(f"52 Week high: ${wanted_stock.iloc[0]['fifty_two_week_high']}")
            st.subheader(f"52 Week low: ${wanted_stock.iloc[0]['fifty_two_week_low']}")
            st.subheader(f"50 Day avg.: ${wanted_stock.iloc[0]['fifty_day_avg']}")
        with r2_col4:
            st.subheader(f"Dividends: ${wanted_stock.iloc[0]['dividends']}")
            st.subheader(f"Dividend yield: {(wanted_stock.iloc[0]['dividend_yield'])*100:.3f}%")
            st.subheader(f"Ex dividend date: {wanted_stock.iloc[0]['ex_dividend_date']}")
            st.subheader(f"Marketcap: ${int(wanted_stock.iloc[0]['marketcap']):,}")
        st.write("---")
        r3_col1, r3_col2 = st.columns(2)
        with r3_col1:
            adjusted_check = st.checkbox("Adjusted")
            period_selected = st.selectbox(
                "Period", options=["1d", "5d", "7d", "60d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
            )
            interval_selected = st.selectbox(
                "Interval",
                options=["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"],
            )
            history_df = get_historical_data(
                symbol=wanted_stock["ticker"],
                interval=interval_selected,
                period=period_selected,
                adjusted=adjusted_check,
            )
            fig = px.line(history_df, x="date", y="close")
            fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig)
        with r3_col2:
            st.subheader(f"Profit margin: {(wanted_stock.iloc[0]['profit_margins'])*100}%")
            st.subheader(f"Volume: {int((wanted_stock.iloc[0]['volume'])):,}")
            st.subheader(f"Cash per share: ${wanted_stock.iloc[0]['total_cash_per_share']}")
            with st.expander("Long business summary"):
                st.subheader(wanted_stock.iloc[0]["long_business_summary"])
        with st.expander(label="Raw data"):
            st.dataframe(wanted_stock)
    else:
        st.error("You need to be logged in to view this page.")
        st.info(
            "Please Login by selecting 'Login' on the drop down on the sidebar and logging in with your credentials."
        )
if page_select == "Stocks":
    main_df = get_all_stocks(st.session_state.jwt_token)
    with st.sidebar.form("StockSearch"):
        st.sidebar.subheader("Use the filters below to search the DB.")
        st.sidebar.write("Only enter the things you want to be filtered, there is no need to fill out all fields.")
        st.sidebar.write("---")
        exchange_cotainer = st.sidebar.container()
        all_exhanges = st.sidebar.checkbox("Select all exchanges")
        if all_exhanges:
            searched_exchange = exchange_cotainer.multiselect(
                "Exchange", main_df["exchange"].unique().tolist(), main_df["exchange"].unique().tolist()
            )
        else:
            searched_exchange = exchange_cotainer.multiselect("Exchange", main_df["exchange"].unique().tolist())
        sector_container = st.sidebar.container()
        all_sectors = st.sidebar.checkbox("Select all Sectors")
        if all_sectors:
            searched_sector = sector_container.multiselect(
                "Sectors", main_df["sector"].unique().tolist(), main_df["sector"].unique().tolist()
            )
        else:
            searched_sector = sector_container.multiselect("Sectors", main_df["sector"].unique().tolist())
        industry_container = st.sidebar.container()
        all_industries = st.sidebar.checkbox("Select all industries")
        if all_industries:
            searched_industry = industry_container.multiselect(
                "Industries", main_df["industry"].unique().tolist(), main_df["industry"].unique().tolist()
            )
        else:
            searched_industry = industry_container.multiselect("Industries", main_df["industry"].unique().tolist())
        country_container = st.sidebar.container()
        all_countries = st.sidebar.checkbox("Select all countries")
        if all_countries:
            searched_country = country_container.multiselect(
                "Countries", main_df["country"].unique().tolist(), main_df["country"].unique().tolist()
            )
        else:
            searched_country = country_container.multiselect("Countries", main_df["country"].unique().tolist())
        searched_max_price = st.sidebar.number_input("Max. Price", max_value=main_df["price"].max())
        searched_market_cap = st.sidebar.number_input("Min. Marketcap", max_value=main_df["marketcap"].max())
        dividends_check = st.sidebar.checkbox("Only show Stocks with Dividends")
        searched_min_div = st.sidebar.number_input("Min. Dividends", max_value=main_df["dividends"].max())
        searched_min_div_yield = st.sidebar.number_input(
            "Min. Dividend yield", max_value=main_df["dividend_yield"].max()
        )
        searched_recommendation = st.sidebar.multiselect("Recommendation", options=main_df["recommendation"].unique())
        searched_50day_avg = st.sidebar.number_input("Max 50day Average", max_value=main_df["fifty_day_avg"].max())
        searched_min_cps = st.sidebar.number_input(
            "Min. Cash per share", max_value=main_df["total_cash_per_share"].max()
        )
        searched_min_profit = st.sidebar.number_input(
            "Min profit margin", max_value=main_df["profit_margins"].max(), help="1 is 100% here"
        )
        searched_min_volume = st.sidebar.number_input("Min. Volume", max_value=main_df["volume"].max())
        submitted = st.form_submit_button("Search")
    if submitted:
        filtered_df = search_df(
            main_df,
            dividends_check,
            searched_exchange,
            searched_sector,
            searched_industry,
            searched_country,
            searched_recommendation,
            searched_max_price,
            searched_market_cap,
            searched_min_div,
            searched_min_div_yield,
            searched_50day_avg,
            searched_min_cps,
            searched_min_profit,
            searched_min_volume,
        )
        try:
            st.write(filtered_df)
        except NameError:
            st.error(
                "Please press the search button after you have set your filters to filter the stocks. Or press it without to get all."
            )
    st.write("---")
    r3_col1, r2_col2 = st.columns(2)
    with r2_col2:
        filename = st.text_input("Name your file")
        try:
            st.download_button(
                "Download the Filtered Stocks as CSV",
                data=save_df_as_cv(filtered_df),
                file_name=(filename + ".csv"),
                mime="text/csv",
            )
        except NameError:
            st.error(
                "Please press the search button after you have set your filters to filter the stocks. Or press it without to get all."
            )
# st.dataframe(main_df)
# numer = st.number_input("test")
# if not numer:
#     st.write("Numer is mepty")
# st.write(numer)
# # print(numer)
