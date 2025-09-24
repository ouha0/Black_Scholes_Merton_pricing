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
    * Plots the "Volatility Smile" and Volatility surface, revealing market risk perceptions.

## To Add
* **Backend Database:**
    * Save and retrieve pricing scenario

## Tech Stack

* **Language:** Python
* **Frontend:** Streamlit
* **Analysis and Visualization:** Pandas, Numpy, SciPy, Plotly
* **Financial Data:** yfinance API


## How to Run Locally

### 1, Clone the Repository
```bash
git clone https://github.com/ouha0/Black_Scholes_Merton_pricing.git
cd Black_Scholes_Merton_pricing
```

### 2. Create and Activate Virtual Environment
*   **On macOS / Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
*   **On Windows:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

### 3. Install required packages from the 'requirements.txt' file
```bash
pip install -r requirements.txt

```

### 4. Run the Streamlit Application

Go to bsm_app directory and launch the Streamlit app from your terminal:
```bash
cd bsm_app
streamlit run app.py
```
The web browser should automatically open the application



## Background Information
* **Black-Scholes-Merton model:**
* ** Greeks:**
* ** Implied Volatility:**

