import streamlit as st
import yfinance as yf
import pandas as pd
import bsm_model as bsm


'''
Page 2 of frontend. Will include volatility surface. Clean up data from yfinance, 
Calculate IV and display it in frontend 
'''

st.set_page_config(layout="wide")

st.title("Implied Volatility Surface")

# --- Data Fetching and Cleanup ---


@st.cache_data(ttl="1h")
# Fetches stock price data from yahoo finance
def get_stock_price(ticker):
    '''Gets the latest stock price'''
    try:
        stock = yf.Ticker(ticker)

    except Exception as e:
        st.error(f"Could not fetch stock price for {ticker}:{e}")
        return None
