# Options pricing and Analysis Toolkit

A web-based financial toolkit built with Python and Streamlit for pricing European(exercise only at expiry) options using the 
Black-Scholes-Merton model and for analyzing real-world implied volatility (surfaces; not done yet) from market data. 

## Features
* **Interactive BSM Pricer:** 
    * Calculates Call and Put options prices for European options.
    * Computes and displays Greeks (Delta, Gamma, Vega, Theta, Rho).
    * Calculates and visualizes Profit and Loss (PNL)

* **Sensitivity Analysis:**
    * Generates interactive 2D heatmaps to show how options prices respond to changes in Spot Price and Volatility
* **Real-time Volatility Smile/Skew:**
    * Fetches live option chain data for any ticker using the 'yfinance' library.
    * Calculates the implied volatility for each option using the Newton-Raphson method.
    * Plots the "Volatility Smile/Skew," revealing market risk perceptions.

## To Add
* **Backend Database:**
    * Save and retrieve pricing scenario

## Tech Stack

* **Language:** Python
* **Frontend:** Streamlit
* **Analysis and Visualization:** Pandas, Numpy, SciPy, Plotly
* **Financial Data:** yfinance API


## How to Run Locally...




## Background Information 
* **Black-Scholes-Merton model:** 
* ** Greeks:** 
* ** Implied Volatility:** 

