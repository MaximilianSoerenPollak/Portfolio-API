import streamlit as st
import pandas as pd
import requests
import yahooquery as yq
import plotly.express as px
from decouple import config
from utils import *

st.set_page_config(layout="wide")

# --- Initialize session_states ----
# if "jwt_token" not in st.session_state:
#     st.session_state.jwt_token = ""
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
# ---- STREAMLIT PAGE -----
# ---- LOGIN ----
login_signup_expander = st.expander("Login/Sign Up")
with login_signup_expander:
    r1_col1, r1_col2 = st.columns(2)
    with r1_col1:
        with st.form("Login"):
            st.subheader("Login")
            email = st.text_input("Email", placeholder="user@user.com")
            password = st.text_input("Password", placeholder="*******", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                token = login(email, password)
                if token:
                    st.session_state.jwt_token = token
                    st.session_state.logged_in = True
                    st.success("You have successfully loged in")
                    st.balloons()
                else:
                    st.error("Could not authenticate you, please try again or if you have no account sign up.")
    with r1_col2:
        with st.form("Sign Up"):
            st.subheader("Sign-Up")
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
                            """Something went wrong, please check that you have entered a correct e-mail and try again.
                            Or maybe you already have an account?"""
                        )
st.write("---")
# ---- STOCKS ----
st.subheader("Stocks")
stocks_container = st.container()
with stocks_container:
    if st.session_state.logged_in:
        main_df = get_all_stocks()
        if main_df is bool:
            st.session_state.logged_in = False
        else:
            stock_filter_expander = st.sidebar.expander("Stock Filters")
            with stock_filter_expander:
                with st.form("StockSearch"):
                    st.subheader("Stock Search")
                    st.write("Only enter the things you want to be filtered, there is no need to fill out all fields.")
                    st.write("---")
                    exchange_cotainer = st.container()
                    all_exhanges = st.checkbox("Select all exchanges")
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
                        )
                    sector_container = st.container()
                    all_sectors = st.checkbox("Select all Sectors")
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
                        )
                    industry_container = st.container()
                    all_industries = st.checkbox("Select all industries")
                    if all_industries:
                        searched_industry = industry_container.multiselect(
                            "Industries",
                            main_df["industry"][main_df["industry"].notnull()].unique().tolist(),
                            main_df["industry"][main_df["industry"].notnull()].unique().tolist(),
                        )
                    else:
                        searched_industry = industry_container.multiselect(
                            "Industries", main_df["industry"][main_df["industry"].notnull()].unique().tolist()
                        )
                    country_container = st.container()
                    all_countries = st.checkbox("Select all countries")
                    if all_countries:
                        searched_country = country_container.multiselect(
                            "Countries",
                            main_df["country"][main_df["country"].notnull()].unique().tolist(),
                            main_df["country"][main_df["country"].notnull()].unique().tolist(),
                        )
                    else:
                        searched_country = country_container.multiselect(
                            "Countries", main_df["country"][main_df["country"].notnull()].unique().tolist()
                        )
                    searched_max_price = st.number_input("Max. Price", max_value=main_df["price"].max())
                    searched_market_cap = st.number_input("Min. Marketcap", max_value=main_df["marketcap"].max())
                    dividends_check = st.checkbox("Only show Stocks with Dividends")
                    searched_min_div = st.number_input("Min. Dividends", max_value=main_df["dividends"].max())
                    searched_min_div_yield = st.number_input(
                        "Min. Dividend yield", max_value=main_df["dividend_yield"].max()
                    )
                    searched_recommendation = st.multiselect(
                        "Recommendation", options=main_df["recommendation"].unique()
                    )
                    searched_50day_avg = st.number_input("Max 50day Average", max_value=main_df["fifty_day_avg"].max())
                    searched_min_cps = st.number_input(
                        "Min. Cash per share", max_value=main_df["total_cash_per_share"].max()
                    )
                    searched_min_profit = st.number_input(
                        "Min profit margin",
                        max_value=main_df["profit_margins"].max(),
                        help="1 is 100% here",
                    )
                    searched_min_volume = st.number_input("Min. Volume", max_value=main_df["volume"].max())
                    submitted = st.form_submit_button("Search")
                    st.write("---")
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
            filtered_stocks_expander = st.expander("Filtered Stocks DataFrame")
            with filtered_stocks_expander:
                st.write("You can filter these with the filters on the Sidebar.")
                st.dataframe(filtered_df)
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
                save_stocks_expander = st.expander("Save stocks to update or remember for detailed viewing.")
                with save_stocks_expander:
                    search_criteria = st.radio(
                        "Search criteria", options=["Ticker", "Name"], key="stocks_save_search_criteria"
                    )
                    if search_criteria == "Ticker":
                        select_option = filtered_df["ticker"].unique().tolist()
                    elif search_criteria == "Name":
                        select_option = filtered_df["name"].unique().tolist()
                    stocks_to_remember = st.multiselect(
                        label="Select the stocks you want to save or update.", options=select_option
                    )
                    update_stocks = st.button(label="Update selected stocks")
                    save_stocks_to_remember = st.button(label="Save stocks")
                    clear_saves = st.button(label="Clear saved stocks")
                    if save_stocks_to_remember:
                        if "stocks_to_remember" not in st.session_state:
                            st.session_state.stocks_to_remember = stocks_to_remember
                        else:
                            st.session_state.stocks_to_remember = stocks_to_remember
                    if clear_saves:
                        del st.session_state.stocks_to_remember
            # --- STOCKS DETAILED VIEW ----
            stock_detail_expander = st.expander(label="Detailed stock view")
            with stock_detail_expander:
                r4_col1, r4_col2 = st.columns(2)
                with r4_col1:
                    search_criteria = st.radio("Search criteria", options=["Ticker", "Name"])
                    if search_criteria == "Ticker":
                        select_option = main_df["ticker"][main_df["ticker"].notnull()].tolist()
                    elif search_criteria == "Name":
                        select_option = main_df["name"][main_df["name"].notnull()].tolist()
                with r4_col2:
                    st.write("Stocks you wanted to look at.")
                    if "stocks_to_remember" in st.session_state:
                        st.text(st.session_state.stocks_to_remember)
                    searched_stock = st.selectbox(label="Stock to search for detailed view", options=select_option)
                st.write("---")
                if search_criteria == "Ticker":
                    wanted_stock = main_df[main_df["ticker"] == searched_stock]
                elif search_criteria == "Name":
                    wanted_stock = main_df[main_df["name"] == searched_stock]
                r5_col1, r5_col2, r5_col3, r5_col4 = st.columns((1.5, 2, 1.5, 2))
                with r5_col1:
                    st.subheader(f"Name: {wanted_stock.iloc[0]['name']}")
                    st.subheader(f"Ticker: {wanted_stock.iloc[0]['ticker']}")
                    st.subheader(f"Exchange: {wanted_stock.iloc[0]['exchange']}")
                    st.subheader(f"Recommendation: {wanted_stock.iloc[0]['recommendation']}")
                with r5_col2:
                    st.subheader(f"Sector: {wanted_stock.iloc[0]['sector']}")
                    st.subheader(f"Industry: {wanted_stock.iloc[0]['industry']}")
                    st.subheader(f"Website: {wanted_stock.iloc[0]['website']}")
                    st.subheader(f"Country: {wanted_stock.iloc[0]['country']}")
                with r5_col3:
                    st.subheader(f"Price: ${wanted_stock.iloc[0]['price']} ")
                    st.subheader(f"52 Week high: ${wanted_stock.iloc[0]['fifty_two_week_high']}")
                    st.subheader(f"52 Week low: ${wanted_stock.iloc[0]['fifty_two_week_low']}")
                    st.subheader(f"50 Day avg.: ${wanted_stock.iloc[0]['fifty_day_avg']}")
                with r5_col4:
                    st.subheader(f"Dividends: ${wanted_stock.iloc[0]['dividends']}")
                    st.subheader(f"Dividend yield: {(wanted_stock.iloc[0]['dividend_yield'])*100:.3f}%")
                    st.subheader(f"Ex dividend date: {wanted_stock.iloc[0]['ex_dividend_date']}")
                    st.subheader(f"Marketcap: ${int(wanted_stock.iloc[0]['marketcap']):,}")
                st.write("---")
                r6_col1, r6_col2 = st.columns(2)
                with r6_col1:
                    adjusted_check = st.checkbox("Adjusted")
                    period_selected = st.selectbox(
                        "Period",
                        options=["1d", "5d", "7d", "60d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
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
                with r6_col2:
                    st.subheader(f"Profit margin: {(wanted_stock.iloc[0]['profit_margins'])*100}%")
                    st.subheader(f"Volume: {int((wanted_stock.iloc[0]['volume'])):,}")
                    st.subheader(f"Cash per share: ${wanted_stock.iloc[0]['total_cash_per_share']}")
                    st.subheader("Long Business Summary:")
                    st.write(wanted_stock.iloc[0]["long_business_summary"])
                st.write("Raw Data")
                st.dataframe(wanted_stock)
            # ---- ADD STOCK TO DATABASE ----
            add_stock_to_db_expander = st.expander("Add stock to database")
            with add_stock_to_db_expander:
                stock_add_to_db_form = st.form("Stock to db form.")
                r7_col1, r7_col2 = st.columns(2)
                with r7_col1:
                    name = st.text_input("Name [REQUIRED]")
                    ticker = st.text_input("Ticker [REQUIRED]")
                    yahoo_ticker = ticker
                    exchange = st.text_input("Exchange [OPTIONAL]")
                    sector = st.text_input("Sector [OPTIONAL]")
                    industry = st.text_input("Industry [OPTIONAL]")
                    long_business_summary = st.text_area("Long Business Summary [OPTIONAL]")
                    country = st.text_input("Country [OPTIONAL]")
                    website = st.text_input("Website [OPTIONAL]")
                    recommendation = st.text_input("Recommendation [OPTIONAL]")
                    ex_dividend_date = st.text_input("Ex-dividend-date [YYYY-MM-DD] [OPTIONAL]")
                with r7_col2:
                    price = st.number_input("Price [REQUIRED]")
                    marketcap = st.number_input("Marketcap [OPTIONAL]")
                    dividends = st.number_input("Dividends (yearly) [OPTIONAL]")
                    if dividends:
                        dividend_yield = round(dividends / price, 2)
                    else:
                        dividend_yield = None
                    beta = st.number_input("Beta [OPTIONAL]")
                    fifty_two_week_high = st.number_input("52 Week high [OPTIONAL]")
                    fifty_two_week_low = st.number_input("52 Week low [OPTIONAL]")
                    fifty_day_avg = st.number_input("50 Day average [OPTIONAL]")
                    total_cash_per_share = st.number_input("Cash per Share [OPTIONAL]")
                    profit_margins = st.number_input("Profit margins [OPTIONAL]")
                    volume = st.number_input("Trading Volume [OPTIONAL]")
                    add_stock_to_db_btn = st.button("Add stock to database")
                    if add_stock_to_db_btn:
                        response_add_stock_to_db = add_stock_to_db(
                            name,
                            ticker,
                            yahoo_ticker,
                            price,
                            exchange,
                            sector,
                            industry,
                            long_business_summary,
                            country,
                            website,
                            recommendation,
                            ex_dividend_date,
                            marketcap,
                            dividends,
                            dividend_yield,
                            beta,
                            fifty_two_week_high,
                            fifty_two_week_low,
                            fifty_day_avg,
                            total_cash_per_share,
                            profit_margins,
                            volume,
                        )
                        if response_add_stock_to_db is not bool:
                            st.write("Added your stock to the database")
                            st.write(response_add_stock_to_db)
    else:
        st.error("You need to be logged in to view this page.")
        st.info(
            "Please Login by selecting 'Login' on the drop down on the sidebar and logging in with your credentials."
        )


# ---- PORTFOLIO ----
st.write("---")
st.subheader("Portfolio")
portfolio_container = st.container()
with portfolio_container:
    if st.session_state.logged_in:
        portfolio_sidebar_expander = st.sidebar.expander("Portfolio Stuff")
        with portfolio_sidebar_expander:
            portfolios = get_portfolios()
            if not portfolios:
                st.session_state.logged_in = False
            portfolios.append("All")
            selected_portfolio = st.selectbox("Select which Portfolio to look at", options=portfolios)
            search_button = st.button("Confirm selected Portfolio.")
            st.sidebar.write("---")
            if selected_portfolio != "All":
                portfolio_response = get_one_portfolio(selected_portfolio[1])
            else:
                st.write("I have not implemented the combine function yet.")
            st.write("---")
            with st.form("Add stock to selected portfolio"):
                st.write("Create new Portfolio")
                portfolio_name = st.text_input("Portfolio Name")
                dividends_goal = st.number_input(
                    "Dividends Goal [OPTIONAL]", help="This is a goal on how much dividends you want to get in a year."
                )
                monetary_goal = st.number_input(
                    "Monetary Goal [OPTIONAL]", help="This is a goal on what the value of the portfolio"
                )
                submitted = st.form_submit_button("Create Portfolio")
                if submitted:
                    name, dividends_goal, monetary_goal = create_portfolio(
                        portfolio_name, dividends_goal, monetary_goal
                    )
                    if name:
                        st.success("Created portfolio successfully")
                        st.write(f"Portfolio name: {name}")
                        st.write(f"Dividends Goal: {dividends_goal}")
                        st.write(f"Monetary Goal: {monetary_goal}")
                    else:
                        st.error("Something went wrong, please try again.")
        portfolio_expander = st.expander("Portfolio Key Stats")
        with portfolio_expander:
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
            except UnboundLocalError:
                st.info("Please select a Portfolio and press the search button")
        stocks_in_portfolio_expander = st.expander("Stocks in portfolio")
        stocks_in_portfolio_df = pd.DataFrame(portfolio_response["stocks"])
        with stocks_in_portfolio_expander:
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
                filename2 = st.text_input("Name your file", key="portfolio_stocks_csv_name")
                st.download_button(
                    "Download your portfolio stocks as CSV",
                    data=save_df_as_cv(stocks_in_portfolio_df),
                    file_name=f"{filename2}.csv",
                    mime="text/csv",
                    key="portfolio_download",
                )
        r4_col1, r4_col2 = st.columns(2)
        with r4_col1:
            portfolio_industry_distrb_expander = st.expander("Industry distribution")
            with portfolio_industry_distrb_expander:
                st.plotly_chart(industry_distribution(stocks_in_portfolio_df))
            portfolio_div_distribution_expander = st.expander("Dividends vs non-dividends distribution")
            with portfolio_div_distribution_expander:
                st.plotly_chart(div_vs_nondiv_distribution(stocks_in_portfolio_df))
            portfolio_div_contrib_expander = st.expander("% Contribution towards dividends per stock.")
            with portfolio_div_contrib_expander:
                st.plotly_chart(div_contrib_distribution(stocks_in_portfolio_df, dividends))
        with r4_col2:
            portfolio_sector_distrb_expander = st.expander("Sector Distribution")
            with portfolio_sector_distrb_expander:
                st.plotly_chart(sector_distribution(stocks_in_portfolio_df))
            portfolio_stock_distrb_count_expander = st.expander("Stocks % of overall number")
            with portfolio_stock_distrb_count_expander:
                st.plotly_chart(stock_distribution_count(stocks_in_portfolio_df))
            portfolio_stock_distrb_expander = st.expander("Stocks in % of capital")
            with portfolio_stock_distrb_expander:
                st.plotly_chart(stock_distribution_percent_capital(portfolio_response["stocks"]))

        portfolio_stocks_graph_expander = st.expander("Stock price and % change over time")
        with portfolio_stocks_graph_expander:
            adjusted_check = st.checkbox("Adjusted", key="portfolio_adjusted")
            period_selected = st.selectbox(
                "Period",
                options=["1d", "5d", "7d", "60d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
                index=11,
            )
            interval_selected = st.selectbox(
                "Interval",
                options=["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"],
                index=8,
            )
            history_df = get_historical_data(
                symbol=stocks_in_portfolio_df["ticker"],
                interval=interval_selected,
                period=period_selected,
                adjusted=adjusted_check,
            )
            r5_col1, r5_col2 = st.columns(2)
            with r5_col1:
                fig = px.line(history_df, x="date", y="close", color="symbol")
                fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig)
            with r5_col2:
                history_df_pct = history_df.copy()
                history_df_pct["change %"] = (history_df_pct.groupby("symbol"))["close"].pct_change() * 100
                fig = px.line(history_df_pct, x="date", y="change %", color="symbol")
                fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig)
        r6_col1, r6_col2 = st.columns(2)
        with r6_col1:
            cagr_expander = st.expander("Cumulative Annual Growth Rate (CAGR)")
            with cagr_expander:
                st.write(
                    """Compound annual growth rate (CAGR) is the rate of returns from an investment over a period of time.
                    The calculation of CAGR is based on the presumption that all the profit will be reinvested at the end of each year."""
                )
                with st.spinner("Calculating CAGR for your stocks."):
                    combined_cagr = 0
                    for stock in stocks_in_portfolio_df["ticker"]:
                        cagr = calc_cagr(stock)
                        st.write(f"{stock} : {cagr*100:.2f}%")
                        combined_cagr += cagr
                    st.write(f"Avg. CAGR: {combined_cagr/len(stocks_in_portfolio_df)*100:.2f}%")
        with r6_col2:
            stock_volatility_expander = st.expander("Volatilie of your stocks/portfolio")
            with stock_volatility_expander:
                st.write(
                    """Volatility here refers to the rate at which the stock price rise and fall over a particular period of time. 
                    It is equivalent to the standard deviation of the daily returns. 
                    The higher the stock volatility the higher the risk of the investment. This is calculated on an anual Term"""
                )
                with st.spinner("Calculating Volatility for your stocks."):
                    combined_volatility = 0
                    for stock in stocks_in_portfolio_df["ticker"]:
                        vol = calc_volatility(stock)
                        st.write(f"{stock} : {vol*100:.2f}%")
                        combined_volatility += vol
                    st.write(f"Avg. Volatility: {combined_volatility/len(stocks_in_portfolio_df)*100:.2f}%")
    else:
        st.error("Please log in.")
