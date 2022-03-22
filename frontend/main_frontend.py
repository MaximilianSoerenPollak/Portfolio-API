import streamlit as st
import pandas as pd
import requests
import yahooquery as yq
import plotly.express as px
from decouple import config
from persist import persist, load_widget_state

# ---- FUNCTIONS ----

st.set_page_config(layout="wide")

# ---- Inital Session state values ----


@st.cache
def login(email, password):
    url = f"{config('API_URL')}/login"
    login_data = {"username": email, "password": password}
    request = requests.post(url, login_data)
    if request.status_code == 200:
        data = request.json()
        bearer_token = data["access_token"]
        st.session_state.jwt_token = bearer_token
        st.session_state.logged_in = True
        persist("logged_in")
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


@st.cache
def get_all_stocks():
    token = st.session_state.jwt_token
    url = f"{config('API_URL')}/stocks?all_stocks=True"
    headers = {"Authorization": "Bearer " + token}
    request = requests.get(url, headers=headers)
    if request.status_code == 200:
        data = request.json()
        return pd.json_normalize(data)
    if request.status_code == 401:
        st.session_state.logged_in = False
        return False


def get_historical_data(symbol, interval, period, adjusted):
    ticker = yq.Ticker(symbol)
    df = ticker.history(interval=interval, period=period, adj_ohlc=adjusted)
    df = df.reset_index()
    return df


def save_df_as_cv(df):
    return df.to_csv().encode("utf-8")


def change_session_state(key, value):
    st.session_state[key] = value


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


# --- Portfolio requests ----
def create_portfolio(name, div_goal, mon_goal):
    token = st.session_state.jwt_token
    if div_goal and mon_goal:
        portfolio_data = {"name": name, "dividends_goal": div_goal, "monetary_goal": mon_goal}
    elif div_goal and not mon_goal:
        portfolio_data = {"name": name, "dividends_goal": div_goal}
    elif mon_goal and not div_goal:
        portfolio_data = {"name": name, "monetary_goal": mon_goal}
    elif not mon_goal and not div_goal:
        portfolio_data = {"name": name}
    url = f"{config('API_URL')}/portfolios"
    headers = {"Authorization": "Bearer " + token}
    request = requests.post(url, json=portfolio_data, headers=headers)
    if request.status_code == 201:
        data = request.json()
        return data["name"], data["dividends_goal"], data["monetary_goal"]
    elif request.status_code == 401:
        st.session_state.logged_in = False
        return False, False, False
    else:
        return False, False, False


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


def add_stock_to_portfolio(ticker, portfolio_id, buy_in, count):
    token = st.session_state.jwt_token
    url = f"{config('API_URL')}/stocks/add/{portfolio_id}"
    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}
    data = {"stock_ticker": ticker, "buy_in": buy_in, "count": count}
    request = requests.post(url, json=data, headers=headers)
    if request.status_code == 200:
        return request.json()
    elif request.status_code == 401:
        st.session_state.logged_in = False
        return False
    else:
        return False


@st.cache
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


# --- MAIN ---


def main():
    if "page" not in st.session_state:
        st.session_state.update(
            {
                # Default page:
                "page": "login",
                # default values
                # loggin side
                "logged_in": False,
                # stocks side
                "saved_stocks": [],
            }
        )
    st.sidebar.subheader("Select your page")
    page = st.sidebar.radio("", options=tuple(PAGES.keys()), format_func=str.capitalize)
    st.sidebar.write("---")

    PAGES[page]()


def page_login():
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
def page_stock_detailed_view():
    if st.session_state.logged_in:
        main_df = get_all_stocks()
        r1_col1, r1_col2 = st.columns(2)
        with r1_col1:
            search_criteria = st.radio(
                "Search criteria", options=["Ticker", "Name"], key=(persist("search_criteria_svd"))
            )
            if search_criteria == "Ticker":
                select_option = main_df["ticker"][main_df["ticker"].notnull()].tolist()
            elif search_criteria == "Name":
                select_option = main_df["name"][main_df["name"].notnull()].tolist()
        with r1_col2:
            st.write("Stocks you wanted to look at.")
            st.text(st.session_state.saved_stocks)
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


def page_stocks():
    if st.session_state.logged_in:
        main_df = get_all_stocks()
        with st.sidebar.form("StockSearch"):
            st.sidebar.subheader("Use the filters below to search the DB.")
            st.sidebar.write("Only enter the things you want to be filtered, there is no need to fill out all fields.")
            st.sidebar.write("---")
            exchange_cotainer = st.sidebar.container()
            all_exhanges = st.sidebar.checkbox("Select all exchanges", key=persist("all_exhanges"))
            if all_exhanges:
                searched_exchange = exchange_cotainer.multiselect(
                    "Exchange",
                    main_df["exchange"][main_df["exchange"].notnull()].unique().tolist(),
                    main_df["exchange"][main_df["exchange"].notnull()].unique().tolist(),
                )
            else:
                searched_exchange = exchange_cotainer.multiselect(
                    "Exchange",
                    main_df["exchange"][main_df["exchange"].notnull()].unique().tolist(),
                    key=persist("exchanges"),
                )
            sector_container = st.sidebar.container()
            all_sectors = st.sidebar.checkbox("Select all Sectors", key=persist("all_sectors"))
            if all_sectors:
                searched_sector = sector_container.multiselect(
                    "Sectors",
                    main_df["sector"][main_df["sector"].notnull()].unique().tolist(),
                    main_df["sector"][main_df["sector"].notnull()].unique().tolist(),
                )
            else:
                searched_sector = sector_container.multiselect(
                    "Sectors",
                    main_df["sector"][main_df["sector"].notnull()].unique().tolist(),
                    key=persist("sectors"),
                )
            industry_container = st.sidebar.container()
            all_industries = st.sidebar.checkbox("Select all industries", key=persist("all_industries"))
            if all_industries:
                searched_industry = industry_container.multiselect(
                    "Industries",
                    main_df["industry"][main_df["industry"].notnull()].unique().tolist(),
                    main_df["industry"][main_df["industry"].notnull()].unique().tolist(),
                )
            else:
                searched_industry = industry_container.multiselect(
                    "Industries",
                    main_df["industry"][main_df["industry"].notnull()].unique().tolist(),
                    key=persist("indsutries"),
                )
            country_container = st.sidebar.container()
            all_countries = st.sidebar.checkbox("Select all countries", key=persist("all_countries"))
            if all_countries:
                searched_country = country_container.multiselect(
                    "Countries",
                    main_df["country"][main_df["country"].notnull()].unique().tolist(),
                    main_df["country"][main_df["country"].notnull()].unique().tolist(),
                )
            else:
                searched_country = country_container.multiselect(
                    "Countries",
                    main_df["country"][main_df["country"].notnull()].unique().tolist(),
                    key=persist("countries"),
                )
            searched_max_price = st.sidebar.number_input(
                "Max. Price", max_value=main_df["price"].max(), key=persist("max_price")
            )
            searched_market_cap = st.sidebar.number_input(
                "Min. Marketcap", max_value=main_df["marketcap"].max(), key=persist("min_marketcap")
            )
            dividends_check = st.sidebar.checkbox("Only show Stocks with Dividends", key=persist("div_only"))
            searched_min_div = st.sidebar.number_input(
                "Min. Dividends", max_value=main_df["dividends"].max(), key=persist("min_div")
            )
            searched_min_div_yield = st.sidebar.number_input(
                "Min. Dividend yield", max_value=main_df["dividend_yield"].max(), key=persist("min_div_yield")
            )
            searched_recommendation = st.sidebar.multiselect(
                "Recommendation", options=main_df["recommendation"].unique(), key=persist("recommendation")
            )
            searched_50day_avg = st.sidebar.number_input(
                "Max 50day Average", max_value=main_df["fifty_day_avg"].max(), key=persist("max_50_day_avg")
            )
            searched_min_cps = st.sidebar.number_input(
                "Min. Cash per share", max_value=main_df["total_cash_per_share"].max(), key=persist("min_cps")
            )
            searched_min_profit = st.sidebar.number_input(
                "Min profit margin",
                max_value=main_df["profit_margins"].max(),
                help="1 is 100% here",
                key=persist("min_profit"),
            )
            searched_min_volume = st.sidebar.number_input(
                "Min. Volume", max_value=main_df["volume"].max(), key=persist("min_volume")
            )
            with st.sidebar:
                submitted = st.form_submit_button("Search")
        filtered_df = main_df
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
        st.write(filtered_df)
        st.write("---")
        r3_col1, r2_col2 = st.columns(2)
        with r2_col2:
            download_csv = st.expander("Download your filtered DataFrame as CSV")
            with download_csv:
                filename = st.text_input("Name your file")
                st.download_button(
                    "Download the Filtered Stocks as CSV",
                    data=save_df_as_cv(filtered_df),
                    file_name=(filename + ".csv"),
                    mime="text/csv",
                )
        with r3_col1:
            save_stocks = st.expander("Save stocks to remember them in the Detailed Stock View")
            with save_stocks:
                search_criteria = st.radio(
                    "Search criteria", options=["Ticker", "Name"], key="stocks_save_search_criteria"
                )
                if search_criteria == "Ticker":
                    select_option = filtered_df["ticker"].unique().tolist()
                elif search_criteria == "Name":
                    select_option = filtered_df["name"].unique().tolist()
                st.multiselect(
                    label="Select the Stocks you want to save.", options=select_option, key=persist("saved_stocks")
                )
        portfolio_expander = st.expander("Add stocks to your Portfolio")
        with portfolio_expander:
            r4_col1, r4_col2 = st.columns(2)
            with r4_col1:
                stock_to_add = st.selectbox(
                    label="Select the Stocks you want to save.", options=filtered_df["ticker"].unique().tolist()
                )
                buy_in = st.number_input("What is your average buy in for this stock?")
                count = st.number_input("How many of this stock do you own?")
                portfolios = get_portfolios()
            with r4_col2:
                if portfolios:
                    selected_portfolio = st.selectbox(
                        label="Portfolio to add Stocks to | Portfolio Name, Portfolio_ID",
                        options=[(x[0], x[1]) for x in portfolios],
                        help="If this selection is empty, please create a portfolio from the portfolios tab.",
                    )
                else:
                    st.write("Something went wrong. We could not grab your portfolios.")
                add_stock_button = st.button("Add stocks in the list to portfolio.")
                if add_stock_button:
                    add_stock_to_portfolio_response = add_stock_to_portfolio(
                        stock_to_add, selected_portfolio[1], buy_in, count
                    )
                    st.write(add_stock_to_portfolio_response["detail"])
    else:
        st.error("Please log in.")


def page_portfolios():
    if st.session_state.logged_in:
        portfolios = get_portfolios()
        if not portfolios:
            st.session_state.logged_in = False
        portfolios.append("All")
        selected_portfolio = st.sidebar.selectbox("Select which Portfolio to look at", options=portfolios)
        search_button = st.sidebar.button("Confirm selected Portfolio.")
        st.sidebar.write("---")
        if selected_portfolio != "All":
            portfolio_response = get_one_portfolio(selected_portfolio[1])
        else:
            st.write("I have not implemented the combine function yet.")
        try:
            capital = calc_total_capital(portfolio_response["stocks"])
            dividends = calc_total_div(portfolio_response["stocks"])
            r1_col1, r1_col2, r1_col3 = st.columns(3)
            with r1_col1:
                st.metric(
                    "Monetary Goal",
                    value=f"${portfolio_response['monetary_goal']}",
                    delta=f"{round(capital - portfolio_response['monetary_goal'],2)}",
                )
                st.subheader(f"Nr. of Stocks: {len(portfolio_response['stocks'])}")
            with r1_col2:
                st.metric(
                    "Dividends Goal",
                    value=f"${portfolio_response['dividends_goal']}",
                    delta=f"{round(dividends- portfolio_response['dividends_goal'],2)}",
                )
                st.subheader(f"Dividends p.a: ${dividends:.2f}")
            with r1_col3:
                st.metric(
                    "Capital: ",
                    value=f"${round(capital,2)}",
                    delta=round(calc_buyin_capital(portfolio_response["stocks"]), 2),
                )
                st.subheader(f"Dividend yield: {(dividends/capital)*100:.2f}%")
            st.write("---")
            portfolio_expander = st.expander("Stocks in portfolio")
            stocks_in_portfolio_df = pd.DataFrame(portfolio_response["stocks"])
            with portfolio_expander:
                st.write(stocks_in_portfolio_df)
            r3_col1, r3_col2 = st.columns(2)
            with r3_col1:
                add_stocks_pf = st.expander("Add stocks to your portfolio")
                with add_stocks_pf:
                    stock_to_add = st.selectbox(
                        label="Select the Stocks you want to save.",
                        options=stocks_in_portfolio_df["ticker"].unique().tolist(),
                    )
                    buy_in = st.number_input("What is your average buy in for this stock?")
                    count = st.number_input("How many of this stock do you own?")
                    if portfolios:
                        selected_portfolio = st.selectbox(
                            label="Portfolio to add Stocks to | Portfolio Name, Portfolio_ID",
                            options=[(x[0], x[1]) for x in portfolios],
                            help="If this selection is empty, please create a portfolio from the portfolios tab.",
                        )
                    else:
                        st.write("Something went wrong. We could not grab your portfolios.")
                    add_stock_button = st.button("Add stocks in the list to portfolio.")
                    if add_stock_button:
                        add_stock_to_portfolio_response = add_stock_to_portfolio(
                            stock_to_add, selected_portfolio[1], buy_in, count
                        )
                        st.write(add_stock_to_portfolio_response["detail"])
            with r3_col2:
                download_csv = st.expander("Download the stocks in your Portfolio as CSV")
                with download_csv:
                    filename2 = st.text_input("Name your file")
                    st.download_button(
                        "Download your portfolio stocks as CSV",
                        data=save_df_as_cv(stocks_in_portfolio_df),
                        file_name=f"{filename2}.csv",
                        mime="text/csv",
                        key="portfolio_download",
                    )

        except UnboundLocalError:
            st.info("Please select a Portfolio and press the search button")

        with st.sidebar.form("Add stock to selected portfolio"):
            portfolio_name = st.sidebar.text_input("Portfolio Name")
            dividends_goal = st.sidebar.number_input(
                "Dividends Goal [OPTIONAL]", help="This is a goal on how much dividends you want to get in a year."
            )
            monetary_goal = st.sidebar.number_input(
                "Monetary Goal [OPTIONAL]", help="This is a goal on what the value of the portfolio"
            )
            with st.sidebar:
                submitted = st.form_submit_button("Create Portfolio")
            if submitted:
                name, dividends_goal, monetary_goal = create_portfolio(portfolio_name, dividends_goal, monetary_goal)
                if name:
                    st.success("Created portfolio successfully")
                    st.write(f"Portfolio name: {name}")
                    st.write(f"Dividends Goal: {dividends_goal}")
                    st.write(f"Monetary Goal: {monetary_goal}")
                else:
                    st.error("Something went wrong, please try again.")
    else:
        st.error("Please log in.")


def page_add_stock_to_db():
    pass


PAGES = {
    "login": page_login,
    "stocks": page_stocks,
    "stock_detailed_view": page_stock_detailed_view,
    "portfolios": page_portfolios,
    "add stock to database": page_add_stock_to_db,
}

if __name__ == "__main__":
    load_widget_state()
    main()
