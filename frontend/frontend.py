import streamlit as st
import pandas as pd
import requests
import yahooquery as yq
import plotly.express as px
from decouple import config
from utils import *

st.set_page_config(layout="wide")

# --- Initialize session_states ----
if "jwt_token" not in st.session_state:
    st.session_state.jwt_token = ""
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
stocks_container = st.container()
with stocks_container:
    if st.session_state.logged_in:
        main_df = get_all_stocks()
        with st.sidebar.form("StockSearch"):
            st.sidebar.subheader("Stock Search")
            st.sidebar.write("Only enter the things you want to be filtered, there is no need to fill out all fields.")
            st.sidebar.write("---")
            exchange_cotainer = st.sidebar.container()
            all_exhanges = st.sidebar.checkbox("Select all exchanges")
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
            sector_container = st.sidebar.container()
            all_sectors = st.sidebar.checkbox("Select all Sectors")
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
            industry_container = st.sidebar.container()
            all_industries = st.sidebar.checkbox("Select all industries")
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
            country_container = st.sidebar.container()
            all_countries = st.sidebar.checkbox("Select all countries")
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
            searched_max_price = st.sidebar.number_input("Max. Price", max_value=main_df["price"].max())
            searched_market_cap = st.sidebar.number_input("Min. Marketcap", max_value=main_df["marketcap"].max())
            dividends_check = st.sidebar.checkbox("Only show Stocks with Dividends")
            searched_min_div = st.sidebar.number_input("Min. Dividends", max_value=main_df["dividends"].max())
            searched_min_div_yield = st.sidebar.number_input(
                "Min. Dividend yield", max_value=main_df["dividend_yield"].max()
            )
            searched_recommendation = st.sidebar.multiselect(
                "Recommendation", options=main_df["recommendation"].unique()
            )
            searched_50day_avg = st.sidebar.number_input("Max 50day Average", max_value=main_df["fifty_day_avg"].max())
            searched_min_cps = st.sidebar.number_input(
                "Min. Cash per share", max_value=main_df["total_cash_per_share"].max()
            )
            searched_min_profit = st.sidebar.number_input(
                "Min profit margin",
                max_value=main_df["profit_margins"].max(),
                help="1 is 100% here",
            )
            searched_min_volume = st.sidebar.number_input("Min. Volume", max_value=main_df["volume"].max())
            with st.sidebar:
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
            save_stocks_expander = st.expander("Save stocks to remember them in the Detailed Stock View")
            with save_stocks_expander:
                search_criteria = st.radio(
                    "Search criteria", options=["Ticker", "Name"], key="stocks_save_search_criteria"
                )
                if search_criteria == "Ticker":
                    select_option = filtered_df["ticker"].unique().tolist()
                elif search_criteria == "Name":
                    select_option = filtered_df["name"].unique().tolist()
                stocks_to_remember = st.multiselect(label="Select the Stocks you want to save.", options=select_option)
                if not "stocks_to_remember" in st.session_state:
                    st.session_state.stocks_to_remember = stocks_to_remember
                if "stocks_to_remember" in st.session_state:
                    pass
