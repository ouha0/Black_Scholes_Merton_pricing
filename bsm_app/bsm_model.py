import numpy as np
from scipy.stats import norm
import math

# This file will contain all the core calculations


def black_scholes(S, K, T, r, sigma, option_type='call'):
    '''
    Calculate the BSM option price for a call or option.
    Parameters:
    S (float): Current stock price 
    K (float): Strike Price
    T (float): Time to maturity in years
    r (float): risk-free rate annualized
    sigma (float): Volatility of stock annualized
    option_type (string): 'call' or 'put'

    Returns (float): returns price of the option
    '''

    # d1 and d2
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    # Price based on option type
    if option_type.lower() == 'call':
        price = (S * norm.cdf(d1, 0.0, 1.0) - K *
                 np.exp(-r * T) * norm.cdf(d2, 0.0, 1.0))
    elif option_type.lower() == 'put':
        price = (K * np.exp(-r * T) * norm.cdf(-d2, 0.0, 1.0) -
                 S * norm.cdf(-d1, 0.0, 1.0))
    else:
        raise ValueError("Invalid option type. Choose 'call' or 'put'")

    return price

# --- The Greeks (functions) ---


def delta(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    if option_type.lower() == 'call':
        return norm.cdf(d1, 0.0, 1.0)
    elif option_type.lower() == 'put':
        return norm.cdf(d1, 0.0, 1.0) - 1
    else:
        raise ValueError("Invalid Option type. Choose 'call' or 'put'")


def gamma(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    return (norm.pdf(d1, 0.0, 1.0) / (S * sigma * np.sqrt(T)))


# Vega is sensitivity of price and volatility
def vega(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    return (S * norm.pdf(d1, 0.0, 1.0) * np.sqrt(T))


def theta(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    left_term = (-S * norm.pdf(d1, 0.0, 1.0) * sigma) / (2 * np.sqrt(T))

    if (option_type.lower() == 'call'):
        right_term = -r * K * np.exp(-r * T) * norm.cdf(d2, 0.0, 1.0)
        return (left_term + right_term)
    elif (option_type.lower() == 'put'):
        right_term = r * K * np.exp(-r * T) * norm.cdf(-d2, 0.0, 1.0)
        return (left_term + right_term)
    else:
        raise ValueError("Invalid option type. Choose 'call' or 'put'")


def rho(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type.lower() == 'call':
        return (K * T * np.exp(-r * T) * norm.cdf(d2, 0.0, 1.0))
    elif option_type.lower() == 'put':
        return (-K * T * np.exp(-r * T) * norm.cdf(-d2, 0.0, 1.0))
    else:
        raise ValueError("Invalid option type. Choose 'call' or 'put'")


''' 
Solves for implied volatility; returns none
if vega is 0 (Option price insensitive to volatility)
'''


def implied_volatility(market_price, S, K, T, r, option_type='call'):
    '''
    Function to calculate the implied Volatility; No closed form solution
    , use Newton's method (Root finding technique). In some ways similar to gradient descent
    '''
    ITERATIONS = 100
    TOLERENCE = 1.0e-5  # Stop algorithm if "good enough"

    sigma = 0.5  # Intial guess

    for i in range(ITERATIONS):
        price = black_scholes(S, K, T, r, sigma, option_type)
        curr_vega = vega(S, K, T, r, sigma)

        diff = price - market_price

        # Stop if estimate good enough
        if abs(diff) < TOLERENCE:
            return sigma

        # When Vega is zero, cannot solve; option price insensitive to price change. Happens at expiry
        if abs(curr_vega) < 1e-6:
            return None

        sigma = sigma - (diff / curr_vega)

    return None
