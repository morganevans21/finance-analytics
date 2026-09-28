"""
Utility functions for financial analytics calculations.
"""

import pandas as pd
import numpy as np
from typing import Union, Tuple, Optional
from pandas import Series, DataFrame


def annualize_return(return_series: Series, periods_per_year: int = 252) -> float:
    """
    Annualize a return series assuming geometric compounding.

    Args:
        return_series: Series of simple returns (not log returns)
        periods_per_year: Number of periods in a year (default 252 for daily)

    Returns:
        Annualized return as a float
    """
    if return_series.empty:
        return np.nan

    # Calculate cumulative return
    cum_return = (1 + return_series).prod() - 1
    # Annualize
    n_periods = len(return_series)
    annualized = (1 + cum_return) ** (periods_per_year / n_periods) - 1

    return annualized


def annualize_volatility(volatility: float, periods_per_year: int = 252) -> float:
    """
    Annualize volatility (standard deviation of returns).

    Args:
        volatility: Volatility to annualize (typically std of periodic returns)
        periods_per_year: Number of periods in a year (default 252 for daily)

    Returns:
        Annualized volatility
    """
    return volatility * np.sqrt(periods_per_year)


def validate_price_data(df: DataFrame, price_col: str = 'close') -> bool:
    """
    Validate price data for financial calculations.

    Args:
        df: DataFrame with price data
        price_col: Column name containing price data

    Returns:
        True if data is valid, False otherwise
    """
    if df.empty:
        return False

    if price_col not in df.columns:
        return False

    # Check for sufficient data points
    if len(df) < 2:
        return False

    # Check for positive prices
    if (df[price_col] <= 0).any():
        return False

    # Check for excessive missing values
    if df[price_col].isnull().sum() > len(df) * 0.1:  # More than 10% missing
        return False

    return True


def align_series(*series: Series) -> Tuple[Series, ...]:
    """
    Align multiple series by their index, dropping NaN values.

    Args:
        *series: Variable number of pandas Series to align

    Returns:
        Tuple of aligned series with NaN values dropped
    """
    if not series:
        return tuple()

    # Combine all series into a DataFrame
    combined = pd.concat(series, axis=1)
    # Drop rows with any NaN values
    combined_clean = combined.dropna()

    # Return individual series (columns of the DataFrame)
    return tuple(combined_clean[col] for col in combined_clean.columns)


def safe_divide(numerator: Union[float, Series],
                denominator: Union[float, Series]) -> Union[float, Series]:
    """
    Safely divide two values or series, handling division by zero.

    Args:
        numerator: Numerator value or series
        denominator: Denominator value or series

    Returns:
        Result of division, with np.where(denominator == 0, np.nan, numerator/denominator)
    """
    if isinstance(numerator, pd.Series) or isinstance(denominator, pd.Series):
        return np.where(denominator == 0, np.nan, numerator / denominator)
    else:
        return np.nan if denominator == 0 else numerator / denominator