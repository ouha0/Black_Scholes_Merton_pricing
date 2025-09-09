import streamlit as st
import yfinance as yf
import pandas as pd
import bsm_model as bsm

st.set_page_config(layout="wide")
st.title("Implied Volatility Surface")

# --- DATA FETCHING FUNCTIONS ---


@st.cache_data(ttl='1h')  # Cache for 1 hour
def get_stock_price(ticker):
    """Gets the latest stock price."""
    try:
        return yf.Ticker(ticker).history(period='1d')['Close'].iloc[0]
    except Exception as e:
        st.error(f"Could not fetch stock price for {ticker}: {e}")
        return None


@st.cache_data(ttl='1h')
def get_expiration_dates(ticker):
    """Gets available option expiration dates."""
    try:
        return yf.Ticker(ticker).options
    except Exception as e:
        st.error(f"Could not fetch expiration dates for {ticker}: {e}")
        return None


@st.cache_data(ttl='1h')
def get_option_chain_for_date(ticker, expiry_date):
    """Get full option chain for a specific expiration date."""
    try:
        chain = yf.Ticker(ticker).option_chain(expiry_date)
        return chain.calls, chain.puts
    except Exception as e:
        st.error(
            f"Could not fetch option chain for {ticker} on {expiry_date}: {e}")
        return None, None


# --- USER INTERFACE (Display) ---
ticker = st.text_input("Enter a Ticker (e.g., SPY, AAPL, NVDA)", "SPY")

if ticker:
    S = get_stock_price(ticker)
    expirations = get_expiration_dates(ticker)

    if S and expirations:
        st.header(f"{ticker.upper()} Current Price: ${S:.2f}")

        # --- Display the raw data tables (check for now) ---
        st.subheader("Raw Option Chain Data")

        selected_expiry = st.selectbox(
            "Select an Expiration Date", expirations)

        if selected_expiry:
            calls, puts = get_option_chain_for_date(ticker, selected_expiry)

            if calls is not None and not calls.empty:  # get_option_chain successful and call options exist
                st.info(f"Displaying data for {selected_expiry}")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("Call Options")
                    st.dataframe(calls, use_container_width=True, height=500)
                with col2:
                    st.write("Put Options")
                    st.dataframe(puts, use_container_width=True, height=500)

            else:
                st.warning(
                    f"Could not fetch option data for {selected_expiry}.")

    else:
        st.error(
            f"Could not fetch data for ticker '{ticker}'. Check the ticker symbol.")
