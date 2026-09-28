"""
Volatility calculations for financial analytics.
"""

import pandas as pd
import numpy as np
from typing import Union, Optional
from pandas import Series, DataFrame
from .utils import annualize_volatility, validate_price_data


def rolling_returns(prices: Union[Series, DataFrame],
                    window: int,
                    price_col: str = 'close',
                    log_returns: bool = False) -> Series:
    """
    Calculate rolling returns over a specified window.

    Args:
        prices: Series or DataFrame containing price data
        window: Rolling window size
        price_col: Column name if prices is DataFrame (default 'close')
        log_returns: If True, calculate log returns; otherwise simple returns

    Returns:
        Series of rolling returns
    """
    if isinstance(prices, DataFrame):
        if price_col not in prices.columns:
            raise ValueError(f"Column '{price_col}' not found in DataFrame")
        price_series = prices[price_col]
    else:
        price_series = prices

    if log_returns:
        returns = np.log(price_series / price_series.shift(1))
    else:
        returns = price_series.pct_change()

    # Calculate rolling sum of returns (for simple returns this is not geometrically correct)
    # For volatility calculation, we actually want rolling standard deviation of returns
    return returns


def rolling_volatility(returns: Series,
                       window: int = 30,
                       periods_per_year: int = 252,
                       min_periods: Optional[int] = None) -> Series:
    """
    Calculate rolling volatility (standard deviation of returns).

    Args:
        returns: Series of simple or log returns
        window: Rolling window size in periods
        periods_per_year: Number of periods in a year for annualization (default 252)
        min_periods: Minimum number of observations required (default window//2 if None)

    Returns:
        Series of annualized rolling volatility
    """
    if min_periods is None:
        min_periods = max(2, window // 2)

    # Calculate rolling standard deviation
    rolling_std = returns.rolling(window=window, min_periods=min_periods).std()
    # Annualize
    annualized_vol = rolling_std * np.sqrt(periods_per_year)

    return annualized_vol


def exponentially_weighted_volatility(returns: Series,
                                      span: int = 30,
                                      periods_per_year: int = 252) -> Series:
    """
    Calculate exponentially weighted moving average (EWMA) volatility.

    Args:
        returns: Series of simple or log returns
        span: Span for EWMA calculation
        periods_per_year: Number of periods in a year for annualization (default 252)

    Returns:
        Series of annualized EWMA volatility
    """
    # Calculate EWMA of returns (mean)
    ewma_mean = returns.ewm(span=span).mean()
    # Calculate EWMA of squared returns
    ewma_var = returns.ewm(span=span).var()
    # Volatility is sqrt of variance
    ewma_vol = np.sqrt(ewma_var)
    # Annualize
    annualized_vol = ewma_vol * np.sqrt(periods_per_year)

    return annualized_vol


def historical_volatility(returns: Series,
                          periods_per_year: int = 252,
                          annualize: bool = True) -> float:
    """
    Calculate historical volatility (standard deviation of returns).

    Args:
        returns: Series of simple or log returns
        periods_per_year: Number of periods in a year for annualization (default 252)
        annualize: If True, return annualized volatility; otherwise period volatility

    Returns:
        Historical volatility (annualized if annualize=True)
    """
    if returns.empty:
        return np.nan

    vol = returns.std()
    if annualize:
        vol = vol * np.sqrt(periods_per_year)

    return vol


def Parkinson_volatility(high: Series,
                         low: Series,
                         periods_per_year: int = 252) -> Series:
    """
    Calculate Parkinson's volatility estimator using high-low prices.

    More efficient than close-to-close volatility, especially for diffusion processes.

    Formula: σ = sqrt((1/(4n*ln(2))) * Σ(ln(H_i/L_i)^2))

    Args:
        high: Series of high prices
        low: Series of low prices
        periods_per_year: Number of periods in a year for annualization (default 252)

    Returns:
        Series of annualized Parkinson volatility
    """
    # Calculate log of high/low ratio
    log_hl_ratio = np.log(high / low)
    # Square it
    log_hl_squared = log_hl_ratio ** 2
    # Calculate rolling mean (we'll use a default window, but this function returns instantaneous)
    # For instantaneous estimate:
    vol_instantaneous = np.sqrt(log_hl_squared / (4 * np.log(2)))
    # Annualize
    annualized_vol = vol_instantaneous * np.sqrt(periods_per_year)

    return annualized_vol


def Garman_Klass_volatility(open_price: Series,
                            high: Series,
                            low: Series,
                            close: Series,
                            periods_per_year: int = 252) -> Series:
    """
    Calculate Garman-Klass volatility estimator using OHLC prices.

    More efficient than close-to-close volatility.

    Formula: σ = sqrt(0.5 * ln(H/L)^2 - (2*ln(2)-1) * ln(C/O)^2)

    Args:
        open_price: Series of opening prices
        high: Series of high prices
        low: Series of low prices
        close: Series of closing prices
        periods_per_year: Number of periods in a year for annualization (default 252)

    Returns:
        Series of annualized Garman-Klass volatility
    """
    # Calculate components
    ln_hl = np.log(high / low)
    ln_co = np.log(close / open_price)

    # Garman-Klass formula
    vol_squared = 0.5 * ln_hl ** 2 - (2 * np.log(2) - 1) * ln_co ** 2
    # Ensure non-negative (can happen due to estimation error)
    vol_squared = np.maximum(vol_squared, 0)
    vol = np.sqrt(vol_squared)
    # Annualize
    annualized_vol = vol * np.sqrt(periods_per_year)

    return annualized_vol