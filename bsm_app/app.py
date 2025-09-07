import streamlit as st
import bsm_model as bsm  # import bsm model

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
S = st.sidebar.number_input("Spot Price (S)", min_value=0.1, value=100.0, step=1.0)
K = st.sidebar.number_input("Strike Price (K)", min_value=0.1, value=100.0, step=1.0)
T = st.sidebar.number_input("Time to Maturity (T in years)", min_value=0.01, value=1.0, step=0.01)
r = st.sidebar.slider("Risk-Free Rate (r)", 0.0, 0.2, 0.05, 0.001, format="%.3f")
sigma = st.sidebar.slider("Volatility (σ)", 0.01, 1.0, 0.2, 0.01)
purchase_price = st.sidebar.number_input("Purchase Price", min_value=0.0, value=10.0, step=0.1)

