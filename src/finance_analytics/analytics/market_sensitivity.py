"""
Market sensitivity calculations for financial analytics.
"""

import pandas as pd
import numpy as np
from typing import Union, Tuple, Optional
from pandas import Series, DataFrame
from .utils import align_series, safe_divide
from .returns import simple_returns, excess_returns
from .volatility import historical_volatility


def beta(returns: Series,
         market_returns: Series,
         risk_free_rate: Union[float, Series] = 0.0) -> float:
    """
    Calculate beta (systematic risk) using linear regression.

    Formula: β = Cov(Ri, Rm) / Var(Rm)
    Where Ri is asset excess returns, Rm is market excess returns

    Args:
        returns: Series of asset simple returns
        market_returns: Series of market simple returns
        risk_free_rate: Risk-free rate (constant or series)

    Returns:
        Beta coefficient
    """
    if returns.empty or market_returns.empty:
        return np.nan

    # Align the series
    aligned_returns, aligned_market = align_series(returns, market_returns)
    if len(aligned_returns) < 2:
        return np.nan

    # Calculate excess returns
    asset_excess = excess_returns(aligned_returns, risk_free_rate)
    market_excess = excess_returns(aligned_market, risk_free_rate)

    # Remove any remaining NaN values
    valid_data = pd.concat([asset_excess, market_excess], axis=1).dropna()
    if len(valid_data) < 2:
        return np.nan

    asset_excess_clean = valid_data.iloc[:, 0]
    market_excess_clean = valid_data.iloc[:, 1]

    # Calculate beta using covariance formula
    covariance = np.cov(asset_excess_clean, market_excess_clean)[0, 1]
    market_variance = np.var(market_excess_clean)

    if market_variance == 0:
        return np.nan

    beta_coeff = covariance / market_variance
    return beta_coeff


def alpha(returns: Series,
          market_returns: Series,
          risk_free_rate: Union[float, Series] = 0.0) -> float:
    """
    Calculate alpha (excess return) using CAPM.

    Formula: α = Ri - [Rf + β(Rm - Rf)]
    Where Ri is asset return, Rf is risk-free rate, Rm is market return

    Args:
        returns: Series of asset simple returns
        market_returns: Series of market simple returns
        risk_free_rate: Risk-free rate (constant or series)

    Returns:
        Alpha as average excess return not explained by beta
    """
    if returns.empty or market_returns.empty:
        return np.nan

    # Calculate beta
    beta_coeff = beta(returns, market_returns, risk_free_rate)
    if np.isnan(beta_coeff):
        return np.nan

    # Align the series
    aligned_returns, aligned_market = align_series(returns, market_returns)
    if len(aligned_returns) < 2:
        return np.nan

    # Calculate average returns
    mean_asset = aligned_returns.mean()
    mean_market = aligned_market.mean()

    # Handle risk-free rate
    if isinstance(risk_free_rate, (int, float)):
        mean_rf = risk_free_rate
    else:
        _, aligned_rf = align_series(aligned_returns, risk_free_rate)
        mean_rf = aligned_rf.mean()

    # CAPM formula: Expected return = Rf + β(Rm - Rf)
    expected_return = mean_rf + beta_coeff * (mean_market - mean_rf)
    alpha_value = mean_asset - expected_return

    return alpha_value


def correlation(returns1: Series,
                returns2: Series,
                method: str = 'pearson') -> float:
    """
    Calculate correlation between two return series.

    Args:
        returns1: First return series
        returns2: Second return series
        method: Correlation method ('pearson', 'spearman', 'kendall')

    Returns:
        Correlation coefficient
    """
    if returns1.empty or returns2.empty:
        return np.nan

    # Align the series
    aligned1, aligned2 = align_series(returns1, returns2)
    if len(aligned1) < 2:
        return np.nan

    if method == 'pearson':
        return aligned1.corr(aligned2, method='pearson')
    elif method == 'spearman':
        return aligned1.corr(aligned2, method='spearman')
    elif method == 'kendall':
        return aligned1.corr(aligned2, method='kendall')
    else:
        raise ValueError(f"Unknown correlation method: {method}")


def rolling_correlation(returns1: Series,
                        returns2: Series,
                        window: int = 30,
                        min_periods: Optional[int] = None,
                        method: str = 'pearson') -> Series:
    """
    Calculate rolling correlation between two return series.

    Args:
        returns1: First return series
        returns2: Second return series
        window: Rolling window size
        min_periods: Minimum number of observations required
        method: Correlation method ('pearson', 'spearman', 'kendall')

    Returns:
        Series of rolling correlation values
    """
    if min_periods is None:
        min_periods = max(2, window // 2)

    # Align the series
    aligned1, aligned2 = align_series(returns1, returns2)
    if len(aligned1) < min_periods:
        return pd.Series(index=aligned1.index, dtype=float)

    # Calculate rolling correlation
    if method == 'pearson':
        rolling_corr = aligned1.rolling(window=window, min_periods=min_periods).corr(aligned2)
    elif method == 'spearman':
        # For spearman, we need to rank the data within each window
        def spearman_rolling(x, y):
            if len(x) < 2:
                return np.nan
            return pd.Series(x).corr(pd.Series(y), method='spearman')

        # Apply rolling window with custom function
        rolling_corr = pd.Series(index=aligned1.index, dtype=float)
        for i in range(len(aligned1)):
            start_idx = max(0, i - window + 1)
            end_idx = i + 1
            if end_idx - start_idx >= min_periods:
                window_corr = spearman_rolling(
                    aligned1.iloc[start_idx:end_idx],
                    aligned2.iloc[start_idx:end_idx]
                )
                rolling_corr.iloc[i] = window_corr
    elif method == 'kendall':
        # Similar approach for kendall
        def kendall_rolling(x, y):
            if len(x) < 2:
                return np.nan
            return pd.Series(x).corr(pd.Series(y), method='kendall')

        rolling_corr = pd.Series(index=aligned1.index, dtype=float)
        for i in range(len(aligned1)):
            start_idx = max(0, i - window + 1)
            end_idx = i + 1
            if end_idx - start_idx >= min_periods:
                window_corr = kendall_rolling(
                    aligned1.iloc[start_idx:end_idx],
                    aligned2.iloc[start_idx:end_idx]
                )
                rolling_corr.iloc[i] = window_corr
    else:
        raise ValueError(f"Unknown correlation method: {method}")

    return rolling_corr


def information_ratio(returns: Series,
                      benchmark_returns: Series,
                      risk_free_rate: Union[float, Series] = 0.0) -> float:
    """
    Calculate information ratio (active return / tracking error).

    Formula: IR = (Portfolio return - Benchmark return) / StdDev(Portfolio return - Benchmark return)

    Args:
        returns: Series of portfolio returns
        benchmark_returns: Series of benchmark returns
        risk_free_rate: Risk-free rate (constant or series)

    Returns:
        Information ratio
    """
    if returns.empty or benchmark_returns.empty:
        return np.nan

    # Align the series
    aligned_returns, aligned_benchmark = align_series(returns, benchmark_returns)
    if len(aligned_returns) < 2:
        return np.nan

    # Calculate excess returns over risk-free rate
    portfolio_excess = excess_returns(aligned_returns, risk_free_rate)
    benchmark_excess = excess_returns(aligned_benchmark, risk_free_rate)

    # Calculate active return
    active_return = portfolio_excess - benchmark_excess
    active_return_clean = active_return.dropna()

    if active_return_clean.empty or len(active_return_clean) < 2:
        return np.nan

    # Information ratio = mean(active return) / std(active return)
    mean_active = active_return_clean.mean()
    std_active = active_return_clean.std()

    if std_active == 0:
        return np.inf if mean_active > 0 else (-np.inf if mean_active < 0 else np.nan)

    return mean_active / std_active


def tracking_error(returns: Series,
                   benchmark_returns: Series,
                   risk_free_rate: Union[float, Series] = 0.0,
                   periods_per_year: int = 252,
                   annualize: bool = True) -> float:
    """
    Calculate tracking error (standard deviation of active returns).

    Args:
        returns: Series of portfolio returns
        benchmark_returns: Series of benchmark returns
        risk_free_rate: Risk-free rate (constant or series)
        periods_per_year: Number of periods in a year for annualization (default 252)
        annualize: If True, return annualized tracking error

    Returns:
        Tracking error
    """
    if returns.empty or benchmark_returns.empty:
        return np.nan

    # Align the series
    aligned_returns, aligned_benchmark = align_series(returns, benchmark_returns)
    if len(aligned_returns) < 2:
        return np.nan

    # Calculate excess returns over risk-free rate
    portfolio_excess = excess_returns(aligned_returns, risk_free_rate)
    benchmark_excess = excess_returns(aligned_benchmark, risk_free_rate)

    # Calculate active return
    active_return = portfolio_excess - benchmark_excess
    active_return_clean = active_return.dropna()

    if active_return_clean.empty:
        return np.nan

    # Tracking error = std(active return)
    te = active_return_clean.std()

    if annualize:
        te = te * np.sqrt(periods_per_year)

    return te


def treynor_ratio(returns: Series,
                  market_returns: Series,
                  risk_free_rate: Union[float, Series] = 0.0,
                  periods_per_year: int = 252) -> float:
    """
    Calculate Treynor ratio (excess return per unit of systematic risk).

    Formula: TR = (Portfolio excess return) / Beta

    Args:
        returns: Series of portfolio returns
        market_returns: Series of market returns
        risk_free_rate: Risk-free rate (constant or series)
        periods_per_year: Number of periods in a year for annualization (default 252)

    Returns:
        Treynor ratio
    """
    if returns.empty or market_returns.empty:
        return np.nan

    # Calculate portfolio excess return (annualized)
    portfolio_excess = excess_returns(returns, risk_free_rate)
    annualized_excess = annualize_return(portfolio_excess, periods_per_year)

    # Calculate beta
    beta_coeff = beta(returns, market_returns, risk_free_rate)

    if beta_coeff == 0:
        return np.inf if annualized_excess > 0 else (-np.inf if annualized_excess < 0 else np.nan)

    return annualized_excess / beta_coeff