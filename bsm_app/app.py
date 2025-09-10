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
st.markdown(
    "A tool to calculate option prices, Greeks, and visualise sensitivities")

# Sidebar for user inputs
st.sidebar.header("Model Parameters")

# User inputs
S = st.sidebar.number_input(
    "Spot Price (S)", min_value=0.1, value=40.0, step=0.01)

K = st.sidebar.number_input(
    "Strike Price (K)", min_value=0.1, value=45.0, step=0.01)

T = st.sidebar.number_input(
    "Time to Maturity (T in years)", min_value=0.01, value=0.33, step=0.01)

r = st.sidebar.slider("Risk-Free Rate (r)", 0.0, 0.2,
                      value=0.03, step=0.001, format="%.3f")

sigma = st.sidebar.slider("Volatility (σ)", 0.01, 1.0, value=0.4, step=0.01)

purchase_price = st.sidebar.number_input(
    "Purchase Price", min_value=0.0, value=5.0, step=0.01)


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
              delta=f"{((put_price / purchase_price) - 1) * 100 if purchase_price > 0 else 0:.2f}%")

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


# --- Heatmap Sentitivity Analysis ---
analysis_type = st.radio(
    "Select Analysis Type",
    ("Option Price", 'PNL'),
    horizontal=True
)


# --- Data generation for heatmap ---
# Evenly spaced numbers between the specified range
st.header("Sensitivity Analysis")

sel_col1, sel_col2 = st.columns(2)

with sel_col1:
    option_choice = st.radio(
        "Select Option Type for Heatmap",
        ('Call', 'Put'),
        horizontal=True
    )
    show_values = st.checkbox("Show values on heatmap", value=False)

with sel_col2:
    analysis_type = st.radio(
        "Select Analysis Value",
        ('Option Price', 'PNL'),
        horizontal=True,
        key='analysis_type'
    )

# Range of values
res = 15

spot_range = np.linspace(S * 0.75, S * 1.25, res)
vol_range = np.linspace(sigma * 0.5, sigma * 1.5, res)

# Emtpy grid
heatmap_data = np.zeros((len(spot_range), len(vol_range)))

# Fill in data of heatmap grid
for i, spot in enumerate(spot_range):
    for j, vol in enumerate(vol_range):
        heatmap_data[i, j] = bsm.black_scholes(
            spot, K, T, r, vol, option_choice.lower())

# Change heatmap data values if PNL heatmap
if (analysis_type == 'PNL'):
    display_data = heatmap_data - purchase_price
    colorscale = 'RdYlGn'
    chart_title = 'Call PNL sensitivity to Spot Price and Volatility'
else:
    display_data = heatmap_data
    colorscale = 'Viridis'  # Default
    chart_title = 'Call Price sensitivity to Spot Price and Volatility'

# --- Plotly for heatmap ---
fig = go.Figure(data=go.Heatmap(
    z=display_data,
    x=np.round(vol_range, 3),
    y=np.round(spot_range, 2),
    hoverongaps=False,  # Missing values
    colorscale=colorscale,
    colorbar=dict(title=analysis_type)
))

if show_values:
    fig.update_traces(
        text=display_data,
        texttemplate="%{text:.2f}"
    )

fig.update_layout(
    title=chart_title,
    xaxis_title="Volatility (σ)",
    yaxis_title="Spot Price (S)",
    autosize=False,
    width=700,
    height=700,
    margin=dict(l=50, r=50, b=100, t=100, pad=4)
)


st.plotly_chart(fig, use_container_width=True)
