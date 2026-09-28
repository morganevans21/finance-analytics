"""
Financial Analytics Module

This module contains reusable financial calculation functions for:
- Return calculations
- Volatility measures
- Drawdown analysis
- Risk metrics (VaR, CVaR, Sharpe, Sortino)
- Market sensitivity (beta, correlation)
"""

from .returns import *
from .volatility import *
from .drawdown import *
from .risk_metrics import *
from .market_sensitivity import *
from .utils import *

__all__ = [
    # Returns
    "simple_returns",
    "log_returns",
    "cumulative_returns",
    "periodic_returns",

    # Volatility
    "rolling_volatility",
    "annualized_volatility",
    "ewma_volatility",

    # Drawdown
    "max_drawdown",
    "rolling_drawdown",
    "drawdown_series",

    # Risk Metrics
    "value_at_risk",
    "conditional_value_at_risk",
    "sharpe_ratio",
    "sortino_ratio",

    # Market Sensitivity
    "beta",
    "alpha",
    "correlation",
    "rolling_correlation",

    # Utils
    "annualize_return",
    "annualize_volatility",
    "validate_price_data",
    "align_series"
]