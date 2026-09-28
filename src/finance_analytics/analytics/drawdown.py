"""
Drawdown calculations for financial analytics.
"""

import pandas as pd
import numpy as np
from typing import Union, Tuple
from pandas import Series, DataFrame


def drawdown_series(cumulative_returns: Series) -> Series:
    """
    Calculate the drawdown series from cumulative returns.

    Formula: DD_t = (Cumulative_t / RunningMax_t) - 1
    Where Drawdown is negative or zero (0 = peak, negative = drawdown)

    Args:
        cumulative_returns: Series of cumulative returns (e.g., from cumulative_returns function)

    Returns:
        Series of drawdown values (negative or zero)
    """
    if cumulative_returns.empty:
        return cumulative_returns.copy()

    # Calculate running maximum
    running_max = cumulative_returns.cummax()
    # Calculate drawdown
    drawdown = (cumulative_returns / running_max) - 1

    return drawdown


def max_drawdown(cumulative_returns: Series) -> float:
    """
    Calculate the maximum drawdown (largest peak-to-trough decline).

    Args:
        cumulative_returns: Series of cumulative returns

    Returns:
        Maximum drawdown as a negative float (0 if no drawdown)
    """
    if cumulative_returns.empty:
        return np.nan

    dd_series = drawdown_series(cumulative_returns)
    return dd_series.min()  # Most negative value


def rolling_drawdown(returns: Series,
                     window: int = 252,
                     min_periods: Optional[int] = None) -> Series:
    """
    Calculate rolling maximum drawdown over a specified window.

    Args:
        returns: Series of simple returns
        window: Rolling window size in periods (default 252 = ~1 year)
        min_periods: Minimum number of observations required (default window//2 if None)

    Returns:
        Series of rolling maximum drawdown values
    """
    if min_periods is None:
        min_periods = max(2, window // 2)

    # Calculate cumulative returns
    cum_returns = (1 + returns.fillna(0)).cumprod()

    # Calculate rolling drawdown
    def rolling_dd(x):
        if len(x) < 2:
            return np.nan
        cum_x = (1 + pd.Series(x)).cumprod()
        dd_series = (cum_x / cum_x.cummax()) - 1
        return dd_series.min()

    rolling_dd_result = returns.rolling(
        window=window,
        min_periods=min_periods
    ).apply(rolling_dd, raw=False)

    return rolling_dd_result


def underwater_series(cumulative_returns: Series) -> Series:
    """
    Calculate the underwater series (duration of drawdown).

    The underwater value represents how far below the peak we are.
    0 = at peak, negative = in drawdown, more negative = deeper drawdown.

    Args:
        cumulative_returns: Series of cumulative returns

    Returns:
        Series of underwater values (same as drawdown series)
    """
    return drawdown_series(cumulative_returns)


def max_drawdown_duration(cumulative_returns: Series) -> int:
    """
    Calculate the maximum duration of a drawdown period.

    Args:
        cumulative_returns: Series of cumulative returns

    Returns:
        Maximum number of consecutive periods in drawdown
    """
    if cumulative_returns.empty:
        return 0

    dd_series = drawdown_series(cumulative_returns)
    # In drawdown when < 0, not in drawdown when >= 0
    in_drawdown = dd_series < 0

    # Find consecutive periods
    max_duration = 0
    current_duration = 0

    for is_dd in in_drawdown:
        if is_dd:
            current_duration += 1
            max_duration = max(max_duration, current_duration)
        else:
            current_duration = 0

    return max_duration


def recovery_time(cumulative_returns: Series) -> Tuple[int, Optional[pd.Timestamp]]:
    """
    Calculate the time to recover from the maximum drawdown.

    Args:
        cumulative_returns: Series of cumulative returns with DatetimeIndex

    Returns:
        Tuple of (recovery_periods, recovery_date)
        recovery_periods: Number of periods from trough to recovery
        recovery_date: Date when recovery occurred (None if not recovered)
    """
    if cumulative_returns.empty or not isinstance(cumulative_returns.index, pd.DatetimeIndex):
        return 0, None

    dd_series = drawdown_series(cumulative_returns)
    # Find the trough (most negative drawdown)
    trough_idx = dd_series.idxmin()
    trough_value = cumulative_returns.loc[trough_idx]

    # Find subsequent peaks that exceed the trough value
    subsequent = cumulative_returns.loc[trough_idx:]
    recovery_mask = subsequent >= trough_value

    if recovery_mask.any():
        recovery_idx = recovery_mask.idxmax()  # First True value
        recovery_date = recovery_idx
        # Calculate periods between trough and recovery
        # This is approximate - for exact period count we'd need frequency info
        recovery_periods = len(cumulative_returns.loc[trough_idx:recovery_date]) - 1
        return recovery_periods, recovery_date
    else:
        # Not recovered
        return len(cumulative_returns) - cumulative_returns.index.get_loc(trough_idx) - 1, None