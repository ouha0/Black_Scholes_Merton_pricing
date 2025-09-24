import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import bsm_model as bsm
from datetime import datetime
import plotly.graph_objects as go
from scipy.interpolate import griddata

st.set_page_config(layout="wide")
st.title("Implied Volatility Surface")

# --- DATA FETCHING FUNCTIONS ---
# Caching only works for standard data objects, like data frames


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


@st.cache_data(ttl='1h')
def generate_surface_data(ticker, r, min_volume, min_open_interest):
    '''
    Fetches all option data, caclulates IV and returns interpolated grid data
    '''
    S = get_stock_price(ticker)
    expirations = get_expiration_dates(ticker)

    # Stock price / expirations not retrieved
    if not S or not expirations:
        return None, None, None

    all_options_list = []
    for expiry in expirations:
        expiry_date = pd.to_datetime(expiry)
        today = pd.to_datetime('today').normalize()
        days_to_expiry = (expiry_date - today).days

        if days_to_expiry < 2:
            continue
        T = days_to_expiry / 365.25

        calls, puts = get_option_chain_for_date(ticker, expiry)
        for option_type_df in [calls, puts]:
            # Skip current iteration if empty
            if option_type_df is None or option_type_df.empty:
                continue

            df = option_type_df.copy()  # shallow copy

            # Filtering low liquidity data; market price is either midpoint of ask and bid
            # or fall back on last price
            df = df[(df['volume'] >= min_volume) & (
                df['openInterest'] >= min_open_interest)]
            df['marketPrice'] = np.where((df['bid'] > 0) & (
                df['ask'] > 0), (df['bid'] + df['ask']) / 2, df['lastPrice'])
            df = df[df['marketPrice'] > 0]

            if df.empty:
                continue

            option_type = 'call' if 'C' in df['contractSymbol'].iloc[0] else 'put'
            df['IV'] = df.apply(lambda row: bsm.implied_volatility(row['marketPrice'], S, row['strike'], T, r, option_type), axis=1
                                )
            df['T'] = T
            # Define moneyness as strike price / stock price (normalize)
            df['Moneyness'] = df['strike'] / S
            all_options_list.append(df[['Moneyness', 'T', 'IV']].dropna())

    if not all_options_list:
        return None, None, None
    master_df = pd.concat(all_options_list)

    if master_df.empty:
        return None, None, None

    # --- Create smart grid and interpolate ---
    x_min, x_max = 0.75, 1.25  # Analyse moneyness in 25ITM - 25OTM
    y_min, y_max = master_df['T'].min(), master_df['T'].max()

    # Create a uniform grid (evenly spread) of (x, y) points to plot volatility surface
# cartesion product of the two sets
    grid_x, grid_y = np.meshgrid(
        np.linspace(x_min, x_max, 100),
        np.linspace(y_min, y_max, 50)
    )

    points = master_df[['Moneyness', 'T']].values
    values = master_df['IV'].values

    # Interpolation using grid x and grid y
    grid_z_raw = griddata(points, values, (grid_x, grid_y), method='linear')
    # if cubic method is used, IV may become negative
    grid_z = np.maximum(grid_z_raw, 0)

    return grid_x, grid_y, grid_z


# --- USER INTERFACE (Display) ---
ticker = st.text_input("Enter a Ticker (e.g., SPY, AAPL, NVDA)", "NVDA")


if ticker:
    S = get_stock_price(ticker)
    expiries = get_expiration_dates(ticker)

    if S and expiries:
        st.header(f"{ticker.upper()} Current Price: ${S:.2f}")

        # Display: Choose expiry and slide to desired risk-free rate
        st.sidebar.header("Calculation Parameters")

        r = st.sidebar.slider("Risk-Free Rate(r)", 0.0,
                              0.2, 0.05, 0.001, format="%.3f")
        st.sidebar.markdown("---")
        st.sidebar.header("Data Filtering")
        min_volume = st.sidebar.number_input("Minimum Volume", value=10)
        min_open_interest = st.sidebar.number_input(
            "Minimum Open Interest", value=20)

        view_choice = st.radio(
            "Select View", ("2D Volatility Smile", "3D Volatility Surface"), horizontal=True)

        if view_choice == "2D Volatility Smile":
            selected_expiry = st.sidebar.selectbox(
                "Select an Expiry Date", expiries)

            if selected_expiry:
                calls, puts = get_option_chain_for_date(
                    ticker, selected_expiry)

                # --- Calculate Time to Maturity ---
                # Convert to proper python datetime object; get maturity using current day
                expiry_date = pd.to_datetime(selected_expiry)
                today = pd.to_datetime('today').normalize()
                days_to_expiry = (expiry_date - today).days

                # When days to expiry is very soon. (T is too close to zero; not reliable)
                if days_to_expiry < 1:
                    st.warning("The selected expiry is within 1 day. ")
                else:
                    T = days_to_expiry / 365.25  # annualized

                # --- Calculate Implied Vol and Plot ---
                st.subheader(f"Volatility Smile for {selected_expiry} expiry")

                results_df_calls, results_df_puts = None, None

                # --- Calls ---
                if calls is not None and not calls.empty:
                    # Create a copy to modify; allows calls_df to be cached
                    calls_df = calls.copy()
                    # Keep call options that have some volume
                    calls_df = calls_df[calls_df['volume'] > min_volume]
                    calls_df = calls_df[calls_df['openInterest']
                                        > min_open_interest]
                    # estimate option price; Use last price when market is not open
                    calls_df['marketPrice'] = np.where(
                        (calls_df['bid'] > 0) & (calls_df['ask'] > 0),
                        (calls_df['bid'] + calls_df['ask']) / 2,
                        calls_df['lastPrice']
                    )
                    # Filter out options without bid and ask
                    calls_df = calls_df[calls_df['marketPrice'] > 0]

                    calls_df['impliedVolatility'] = calls_df.apply(
                        lambda row: bsm.implied_volatility(row['marketPrice'], S, row['strike'], T, r, 'call'), axis=1
                    )
                    # Remove rows where 'implied Volatility' is missing
                    results_df_calls = calls_df.dropna(
                        subset=['impliedVolatility'])

                # --- Put ---
                if puts is not None and not puts.empty:
                    puts_df = puts.copy()
                    puts_df = puts_df[puts_df['volume'] > min_volume]
                    puts_df = puts_df[puts_df['openInterest']
                                      > min_open_interest]
                    puts_df['marketPrice'] = np.where(
                        (puts_df['bid'] > 0) & (puts_df['ask'] > 0),
                        (puts_df['bid'] + puts_df['ask']) / 2,
                        puts_df['lastPrice']
                    )

                    puts_df = puts_df[puts_df['marketPrice'] > 0]
                    puts_df['impliedVolatility'] = puts_df.apply(
                        lambda row: bsm.implied_volatility(row['marketPrice'], S, row['strike'], T, r, 'put'), axis=1
                    )

                    results_df_puts = puts_df.dropna(
                        subset=['impliedVolatility'])

                # --- Create IV Plot ---
                # Outliers of the IV Graph may be lack of liquidity? Especially when using lastPrice
                fig = go.Figure()

                if results_df_calls is not None and not results_df_calls.empty:
                    fig.add_trace(go.Scatter(
                        x=results_df_calls['strike'],
                        y=results_df_calls['impliedVolatility'],
                        mode='markers', name='Calls',
                        marker=dict(color='blue')
                    ))

                if results_df_puts is not None and not results_df_puts.empty:
                    fig.add_trace(go.Scatter(
                        x=results_df_puts['strike'],
                        y=results_df_puts['impliedVolatility'],
                        mode='markers', name='Puts',
                        marker=dict(color='red')
                    ))

                fig.update_layout(
                    title=(f"Implied Volatility Smile for "
                           f"{ticker.upper()} @ {selected_expiry}"),
                    xaxis_title="Strike Price ($)",
                    yaxis_title="Implied Volatility (σ)",
                    yaxis_tickformat=".0%",
                    legend_title="Option Type"
                )
                st.plotly_chart(fig, use_container_width=True)

        elif view_choice == "3D Volatility Surface":
            st.subheader("3D Implied Volatility Surface")
            with st.spinner("Generating 3D surface... This may take a while on the first run."):
                grid_x, grid_y, grid_z = generate_surface_data(
                    ticker, r, min_volume, min_open_interest)

                if grid_x is not None:
                    # Construct the surface
                    fig = go.Figure(data=[go.Surface(
                        x=grid_x,
                        y=grid_y,
                        z=grid_z,
                        colorscale='viridis',
                        # display as percentage
                        colorbar=dict(title='Implied Volatility',
                                      tickformat=".0%"),
                        cmin=np.nanmin(grid_z),
                        cmax=np.nanmax(grid_z)
                    )])

                    # Graph naming
                    fig.update_layout(
                        title=(f"Implied Volatility Surface for"
                               f"{ticker.upper()}"),
                        scene=dict(
                            xaxis_title='Moneyness (K/S)',
                            yaxis_title='Time to Maturity (Years)',
                            zaxis_title='Implied Volatility (σ)',
                            zaxis=dict(tickformat=".0%")
                        ),
                        width=900, height=800
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Could not generate the 3D surface...")

            # Check Raw data for reference
            # st.subheader("Raw Option Chain Data")
            # col1, col2 = st.columns(2)
            # with col1:
            #    st.write("Call Options")
            #    st.dataframe(calls, use_container_width=True, height=500)
            # with col2:
            #    st.write("Put Options")
            #    st.dataframe(puts, use_container_width=True, height=500)

    else:
        st.error(f"Could not fetch data for ticker"
                 f"{ticker}. Check the ticker symbol.")
