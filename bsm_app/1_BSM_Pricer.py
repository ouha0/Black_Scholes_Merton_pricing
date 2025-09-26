import streamlit as st
import bsm_model as bsm  # import bsm model
import numpy as np
import plotly.graph_objects as go
import database as db
from datetime import datetime
import pandas as pd

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

# User inputs. Gets value from session state / or uses the default value
S = st.sidebar.number_input(
    "Spot Price (S)", min_value=0.1, value=st.session_state.get('S_val', 40.0),
    step=0.01)

K = st.sidebar.number_input(
    "Strike Price (K)", min_value=0.1, value=st.session_state.get('K_val', 45.0),
    step=0.01)

T = st.sidebar.number_input(
    "Time to Maturity (T in years)", min_value=0.01, value=st.session_state.get('T_val', 0.33),
    step=0.01)

r = st.sidebar.slider("Risk-Free Rate (r)", 0.0, 0.2,
                      value=st.session_state.get('r_val', 0.03),
                      step=0.001, format="%.3f")

sigma = st.sidebar.slider("Volatility (σ)", 0.01, 1.0,
                          value=st.session_state.get('sigma_val', 0.40), step=0.01)

purchase_price = st.sidebar.number_input(
    "Purchase Price", min_value=0.0, value=st.session_state.get('purchase_price', 5.0),
    step=0.01)

with st.sidebar.expander("About the Inputs"):
    st.write(
        """
        - **Spot Price (S):** The current market price of the underlying asset
        - **Strike Price(K):** The price which the option can be exercised
        - **Time to Maturity(T):** Time until the option expires (in years)
        - **Risk-free rate (r):** The theoretical return rate of an investment with zero risk
        - **Volatility (sigma):** The annualized standard deviation of the asset's returns
        """
    )

# Calculations
call_price = bsm.black_scholes(S, K, T, r, sigma, option_type='call')
put_price = bsm.black_scholes(S, K, T, r, sigma, option_type='put')
call_pnl = call_price - purchase_price
put_pnl = put_price - purchase_price


# --- Split Using Tabs for less clutter ---
tab1, tab2, tab3 = st.tabs(
    ["Price and Greeks", "Sensitivity Heatmap", "Scenario History"])


# --- Pricer and the Greeks ---
with tab1:

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

    # Calls
    call_delta = bsm.delta(S, K, T, r, sigma, 'call')
    gamma = bsm.gamma(S, K, T, r, sigma)
    vega = bsm.vega(S, K, T, r, sigma)
    call_theta = bsm.theta(S, K, T, r, sigma, 'call')
    call_rho = bsm.rho(S, K, T, r, sigma, 'call')

    # Calculate Greeks for Put
    put_delta = bsm.delta(S, K, T, r, sigma, 'put')
    # put_gamma = bsm.gamma(S, K, T, r, sigma)
    # put_vega = bsm.vega(S, K, T, r, sigma)
    put_theta = bsm.theta(S, K, T, r, sigma, 'put')
    put_rho = bsm.rho(S, K, T, r, sigma, 'put')

    # Displaying Greeks
    with row1_cols[0]:
        st.metric("Call Delta", f"{call_delta:.4f}")
        st.metric("Put Delta", f"{put_delta:.4f}")

    # Gamma and Vega same for put and call
    with row1_cols[1]:
        st.metric("Gamma", f"{gamma:.4f}")

    with row1_cols[2]:
        st.metric("Vega", f"{vega:.4f}")

    # --- Row 2: Theta, Rho ---
    with row2_cols[0]:
        st.metric("Call Theta", f"{call_theta:.4f}")
        st.metric("Put Theta", f"{put_theta:.4f}")

    with row2_cols[1]:
        st.metric("Call Rho", f"{call_rho:.4f}")
        st.metric("Put Rho", f"{put_rho:.4f}")


# --- Data generation for heatmap ---
# Evenly spaced numbers between the specified range

with tab2:

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


# tab to save bsm scenarios into database and display past scenarios
with tab3:
    st.header("Scenario History")

    # Button to trigger save scenario
    if st.button("Save Current Scenario"):
        # Make data into database format
        scenario_data = {
            "timestamp": datetime.now(),
            "S": S,
            "K": K,
            "T": T,
            "r": r,
            "sigma": sigma,
            "call_price": call_price,
            "put_price": put_price,
            "call_delta": bsm.delta(S, K, T, r, sigma, 'call'),
            "put_delta": bsm.delta(S, K, T, r, sigma, 'put'),
            "gamma": bsm.gamma(S, K, T, r, sigma),
            "vega": bsm.vega(S, K, T, r, sigma)
        }

        # Call save data from database module
        db.save_scenario(scenario_data)
        st.success("Scenario saved successfully.")

    st.markdown("---")
    # st.write("Log of saved scenarios")

    history_df = db.load_scenarios()

    # Make timestamp format more readable / user friendly
    if not history_df.empty:
        st.write("Click 'Load' to restore saved scneario's inputs onto sidebar.")

        # Display logic
        # Define columns / header
        cols = st.columns([1, 4, 2, 2, 2, 2, 2, 2, 2])  # Set width of columns
        headers = ["Load", "Timestamp", "Spot",
                   "Strike", "Time to Maturity", "Vol", "Risk-free rate", "Call Price", "Put Price"]
        for col, header in zip(cols, headers):
            col.write(f"**{header}**")

        # Iterate through scenarios and create interactive row
        for index, row in history_df.iterrows():
            cols = st.columns([1, 4, 2, 2, 2, 2, 2, 2, 2])

            # Load button for each row
            if cols[0].button("▶", key=f"load_{row['id']}"):
                st.session_state['S_val'] = row['spot_price']
                st.session_state['K_val'] = row['strike_price']
                st.session_state['T_val'] = row['time_to_maturity']
                st.session_state['r_val'] = row['risk_free_rate']
                st.session_state['sigma_val'] = row['volatility']

                st.rerun()

            # Display data for each row in other colums
            timestamp_str = pd.to_datetime(
                row['timestamp']).strftime('%Y-%m-%d %I:%M:%S %p')
            cols[1].write(timestamp_str)
            cols[2].write(f"{row['spot_price']:.2f}")
            cols[3].write(f"{row['strike_price']:.2f}")
            cols[4].write(f"{row['time_to_maturity']:.2f}")
            cols[5].write(f"{row['volatility']:.2f}")
            cols[6].write(f"{row['risk_free_rate']:.2f}")
            cols[7].write(f"{row['call_price']:.2f}")
            cols[8].write(f"{row['put_price']:.2f}")

    else:
        st.info(
            "No scenarios saved yet. Used 'Save Current Scenario' button to add scenarios to history")
