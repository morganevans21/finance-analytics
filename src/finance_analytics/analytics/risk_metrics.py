"""
Risk metrics calculations for financial analytics.
"""

import pandas as pd
import numpy as np
from typing import Union, Tuple, Optional
from pandas import Series
from .utils import validate_price_data, annualize_return
from .returns import simple_returns, excess_returns
from .drawdown import max_drawdown
from .volatility import historical_volatility


def value_at_risk(returns: Series,
                  confidence_level: float = 0.95,
                  method: str = 'historical') -> float:
    """
    Calculate Value at Risk (VaR) at a specified confidence level.

    Args:
        returns: Series of simple returns
        confidence_level: Confidence level (default 0.95 for 95% VaR)
        method: Calculation method ('historical', 'parametric', 'modified')

    Returns:
        VaR as a positive float (representing loss)
    """
    if returns.empty:
        return np.nan

    # Remove NaN values
    returns_clean = returns.dropna()
    if returns_clean.empty:
        return np.nan

    if method == 'historical':
        # Historical VaR: percentile of returns
        var = np.percentile(returns_clean, (1 - confidence_level) * 100)
        return -var  # Return as positive loss
    elif method == 'parametric':
        # Parametric VaR: assumes normal distribution
        mu = returns_clean.mean()
        sigma = returns_clean.std()
        from scipy import stats
        var = mu + sigma * stats.norm.ppf(1 - confidence_level)
        return -var
    elif method == 'modified':
        # Modified VaR: incorporates skewness and kurtosis (Cornish-Fisher expansion)
        # This is a simplified version
        mu = returns_clean.mean()
        sigma = returns_clean.std()
        skewness = returns_clean.skew()
        kurtosis = returns_clean.kurtosis()
        from scipy import stats
        z = stats.norm.ppf(1 - confidence_level)
        # Cornish-Fisher expansion
        z_cf = z + (z**2 - 1) * skewness / 6 + \
               (z**3 - 3*z) * (kurtosis - 3) / 24 - \
               (2*z**3 - 5*z) * (skewness**2) / 36
        var = mu + sigma * z_cf
        return -var
    else:
        raise ValueError(f"Unknown method: {method}. Use 'historical', 'parametric', or 'modified'")


def conditional_value_at_risk(returns: Series,
                              confidence_level: float = 0.95,
                              method: str = 'historical') -> float:
    """
    Calculate Conditional Value at Risk (CVaR) also known as Expected Shortfall.

    CVaR is the expected return given that the return is below the VaR threshold.

    Args:
        returns: Series of simple returns
        confidence_level: Confidence level (default 0.95 for 95% CVaR)
        method: Calculation method ('historical', 'parametric')

    Returns:
        CVaR as a positive float (representing expected loss)
    """
    if returns.empty:
        return np.nan

    returns_clean = returns.dropna()
    if returns_clean.empty:
        return np.nan

    if method == 'historical':
        # Historical CVaR: mean of returns below VaR threshold
        var_threshold = np.percentile(returns_clean, (1 - confidence_level) * 100)
        cvar = returns_clean[returns_clean <= var_threshold].mean()
        return -cvar  # Return as positive loss
    elif method == 'parametric':
        # Parametric CVaR assuming normal distribution
        mu = returns_clean.mean()
        sigma = returns_clean.std()
        from scipy import stats
        alpha = 1 - confidence_level
        var = mu + sigma * stats.norm.ppf(alpha)
        # CVaR for normal distribution
        cvar = mu - sigma * stats.norm.pdf(stats.norm.ppf(alpha)) / alpha
        return -cvar
    else:
        raise ValueError(f"Unknown method: {method}. Use 'historical' or 'parametric'")


def sharpe_ratio(returns: Series,
                 risk_free_rate: Union[float, Series] = 0.0,
                 periods_per_year: int = 252,
                 annualize: bool = True) -> float:
    """
    Calculate Sharpe ratio (risk-adjusted return).

    Formula: (Mean excess return) / (Std dev of excess return)

    Args:
        returns: Series of simple returns
        risk_free_rate: Risk-free rate (constant or series)
        periods_per_year: Number of periods in a year for annualization (default 252)
        annualize: If True, return annualized Sharpe ratio

    Returns:
        Sharpe ratio
    """
    if returns.empty:
        return np.nan

    # Calculate excess returns
    excess = excess_returns(returns, risk_free_rate)
    excess_clean = excess.dropna()

    if excess_clean.empty or len(excess_clean) < 2:
        return np.nan

    # Calculate Sharpe ratio
    mean_excess = excess_clean.mean()
    std_excess = excess_clean.std()

    if std_excess == 0:
        return np.inf if mean_excess > 0 else (-np.inf if mean_excess < 0 else np.nan)

    sharpe = mean_excess / std_excess

    if annualize:
        sharpe = sharpe * np.sqrt(periods_per_year)

    return sharpe


def sortino_ratio(returns: Series,
                  risk_free_rate: Union[float, Series] = 0.0,
                  target_return: Union[float, Series] = 0.0,
                  periods_per_year: int = 252,
                  annualize: bool = True) -> float:
    """
    Calculate Sortino ratio (risk-adjusted return using downside deviation).

    Formula: (Mean excess return) / (Downside deviation)

    Downside deviation only considers returns below the target/minimum acceptable return.

    Args:
        returns: Series of simple returns
        risk_free_rate: Risk-free rate (constant or series)
        target_return: Minimum acceptable return (constant or series)
        periods_per_year: Number of periods in a year for annualization (default 252)
        annualize: If True, return annualized Sortino ratio

    Returns:
        Sortino ratio
    """
    if returns.empty:
        return np.nan

    # Calculate excess returns over risk-free rate
    excess = excess_returns(returns, risk_free_rate)
    excess_clean = excess.dropna()

    if excess_clean.empty or len(excess_clean) < 2:
        return np.nan

    # Calculate target excess returns
    if isinstance(target_return, (int, float)):
        target_excess = excess_clean - target_return
    else:
        # Align series
        aligned_excess, aligned_target = align_series(excess_clean, target_return)
        target_excess = aligned_excess - aligned_target

    # Calculate downside deviation (only negative excess returns)
    downside_returns = target_excess[target_excess < 0]
    if downside_returns.empty:
        return np.inf if excess_clean.mean() > 0 else 0.0

    downside_deviation = np.sqrt(np.mean(downside_returns ** 2))

    if downside_deviation == 0:
        return np.inf if excess_clean.mean() > 0 else 0.0

    sortino = excess_clean.mean() / downside_deviation

    if annualize:
        sortino = sortino * np.sqrt(periods_per_year)

    return sortino


def calmar_ratio(returns: Series,
                 periods_per_year: int = 252) -> float:
    """
    Calculate Calmar ratio (annualized return / max drawdown).

    Args:
        returns: Series of simple returns
        periods_per_year: Number of periods in a year for annualization (default 252)

    Returns:
        Calmar ratio
    """
    if returns.empty:
        return np.nan

    # Calculate annualized return
    annual_return = annualize_return(returns, periods_per_year)
    # Calculate max drawdown
    cum_returns = (1 + returns.fillna(0)).cumprod()
    max_dd = max_drawdown(cum_returns)

    if max_dd == 0:
        return np.inf if annual_return > 0 else 0.0

    return annual_return / abs(max_dd)


def gain_to_pain_ratio(returns: Series) -> float:
    """
    Calculate Gain to Pain ratio (sum of positive returns / sum of absolute negative returns).

    Args:
        returns: Series of simple returns

    Returns:
        Gain to Pain ratio
    """
    if returns.empty:
        return np.nan

    returns_clean = returns.dropna()
    if returns_clean.empty:
        return np.nan

    positive_returns = returns_clean[returns_clean > 0]
    negative_returns = returns_clean[returns_clean < 0]

    if negative_returns.empty:
        return np.inf if len(positive_returns) > 0 else 0.0

    gain = positive_returns.sum()
    pain = abs(negative_returns.sum())

    if pain == 0:
        return np.inf

    return gain / pain