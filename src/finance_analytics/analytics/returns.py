"""
Return calculations for financial analytics.
"""

import pandas as pd
import numpy as np
from typing import Union, Optional
from pandas import Series, DataFrame


def simple_returns(prices: Union[Series, DataFrame],
                   price_col: str = 'close') -> Series:
    """
    Calculate simple returns from price series.

    Formula: R_t = P_t / P_{t-1} - 1

    Args:
        prices: Series or DataFrame containing price data
        price_col: Column name if prices is DataFrame (default 'close')

    Returns:
        Series of simple returns (first value will be NaN)
    """
    if isinstance(prices, DataFrame):
        if price_col not in prices.columns:
            raise ValueError(f"Column '{price_col}' not found in DataFrame")
        price_series = prices[price_col]
    else:
        price_series = prices

    return price_series.pct_change()


def log_returns(prices: Union[Series, DataFrame],
                price_col: str = 'close') -> Series:
    """
    Calculate logarithmic returns from price series.

    Formula: r_t = ln(P_t / P_{t-1})

    Args:
        prices: Series or DataFrame containing price data
        price_col: Column name if prices is DataFrame (default 'close')

    Returns:
        Series of logarithmic returns (first value will be NaN)
    """
    if isinstance(prices, DataFrame):
        if price_col not in prices.columns:
            raise ValueError(f"Column '{price_col}' not found in DataFrame")
        price_series = prices[price_col]
    else:
        price_series = prices

    return np.log(price_series / price_series.shift(1))


def cumulative_returns(returns: Series,
                       starting_value: float = 1.0) -> Series:
    """
    Calculate cumulative returns from a series of returns.

    Formula: CR_t = (1 + R_1) * (1 + R_2) * ... * (1 + R_t) * starting_value - starting_value
    Or equivalently: CR_t = starting_value * ∏(1 + R_i) - starting_value

    Args:
        returns: Series of simple returns (can contain NaN values)
        starting_value: Initial value of investment (default 1.0)

    Returns:
        Series of cumulative returns (same length as input)
    """
    # Handle NaN values: if return is NaN, treat as 0 for calculation but mark result as NaN
    # Find where returns are NaN
    nan_mask = returns.isna()

    # Fill NaN with 0 for calculation purposes
    returns_filled = returns.fillna(0)

    # Calculate cumulative returns
    cumulative = (1 + returns_filled).cumprod() * starting_value - starting_value

    # Set positions where input was NaN to NaN in output
    cumulative[nan_mask] = np.nan

    return cumulative


def periodic_returns(returns: Series,
                     period: str = 'M') -> Series:
    """
    Calculate periodic returns (e.g., monthly, quarterly) from daily returns.

    Args:
        returns: Series of simple returns with DatetimeIndex
        period: Pandas frequency string (default 'M' for month-end)

    Returns:
        Series of periodic returns
    """
    if not isinstance(returns.index, pd.DatetimeIndex):
        raise ValueError("Returns series must have DatetimeIndex for periodic returns")

    # Convert returns to cumulative returns first
    cum_returns = (1 + returns.fillna(0)).cumprod()
    # Resample to period end and calculate period returns
    period_end = cum_returns.resample(period).last()
    period_returns = period_end.pct_change()
    # First period will have NaN return (no prior period)
    return period_returns


def excess_returns(returns: Series,
                   risk_free_rate: Union[float, Series] = 0.0) -> Series:
    """
    Calculate excess returns over a risk-free rate.

    Args:
        returns: Series of investment returns
        risk_free_rate: Risk-free rate (constant or series of same length)

    Returns:
        Series of excess returns
    """
    if isinstance(risk_free_rate, (int, float)):
        return returns - risk_free_rate
    else:
        # Align the series
        aligned_returns, aligned_rf = align_series(returns, risk_free_rate)
        return aligned_returns - aligned_rf