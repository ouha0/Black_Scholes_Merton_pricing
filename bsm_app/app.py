import streamlit as st
import bsm_model as bsm  # import bsm model
import numpy as np
import plotly.graph_objects as go

# This file will contain all the frontend


# Page config
st.set_page_config(
    page_title="BSM Option Pricer",
    layout="wide"
)

# Title
st.title("Black-Scholes-Merton Option Pricer")

# Sidebar for user inputs
st.sidebar.header("Model Parameters")

# User inputs
S = st.sidebar.number_input(
    "Spot Price (S)", min_value=0.1, value=100.0, step=0.01)
K = st.sidebar.number_input(
    "Strike Price (K)", min_value=0.1, value=100.0, step=0.01)
T = st.sidebar.number_input(
    "Time to Maturity (T in years)", min_value=0.01, value=1.0, step=0.01)
r = st.sidebar.slider("Risk-Free Rate (r)", 0.0, 0.2,
                      0.05, 0.001, format="%.3f")
sigma = st.sidebar.slider("Volatility (σ)", 0.01, 1.0, 0.2, 0.01)
purchase_price = st.sidebar.number_input(
    "Purchase Price", min_value=0.0, value=10.0, step=0.01)


# Calculations
call_price = bsm.black_scholes(S, K, T, r, sigma, option_type='call')
put_price = bsm.black_scholes(S, K, T, r, sigma, option_type='put')

call_pnl = call_price - purchase_price
put_pnl = put_price - purchase_price

# Display Prices & PNL in columns
st.header("Option Prices & PNL")
col1, col2 = st.columns(2)


with col1:
    st.metric("Call Option Price", f"${call_price:.3f}")
    # Colored indicator; safety check so denominator is not 0
    st.metric("Call PNL", f"${call_pnl:.3f}",
              delta=f"{((call_price / purchase_price) - 1) * 100 if purchase_price > 0 else 0:.2f}%")

with col2:
    st.metric("Put Option Price", f"${put_price:.3f}")
    st.metric("Put PNL", f"${put_pnl:.3f}",
              delta=f"{((put_price/ purchase_price) - 1) * 100 if purchase_price > 0 else 0:.2f}%")

# The Greeks
st.header("The Greeks")

row1_cols = st.columns(3)
row2_cols = st.columns(3)

# Calculate the Greeks

call_delta = bsm.delta(S, K, T, r, sigma, 'call')
call_gamma = bsm.gamma(S, K, T, r, sigma)
call_vega = bsm.vega(S, K, T, r, sigma)
call_theta = bsm.theta(S, K, T, r, sigma, 'call')
call_rho = bsm.rho(S, K, T, r, sigma, 'call')

# Calculate Greeks for Put
put_delta = bsm.delta(S, K, T, r, sigma, 'put')
put_gamma = bsm.gamma(S, K, T, r, sigma)
put_vega = bsm.vega(S, K, T, r, sigma)
put_theta = bsm.theta(S, K, T, r, sigma, 'put')
put_rho = bsm.rho(S, K, T, r, sigma, 'put')

# Displaying Greeks
with row1_cols[0]:
    st.metric("Call Delta", f"{call_delta:.4f}")
    st.metric("Put Delta", f"{put_delta:.4f}")


with row1_cols[1]:
    st.metric("Gamma", f"{call_gamma:.4f}")

with row1_cols[2]:
    st.metric("Vega", f"{call_vega:.4f}")

# --- Row 2: Theta, Rho ---
with row2_cols[0]:
    st.metric("Call Theta", f"{call_theta:.4f}")
    st.metric("Put Theta", f"{put_theta:.4f}")

with row2_cols[1]:
    st.metric("Call Rho", f"{call_rho:.4f}")
    st.metric("Put Rho", f"{put_rho:.4f}")
