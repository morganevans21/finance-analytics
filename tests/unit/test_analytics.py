"""
Unit tests for the financial analytics module.
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Import the analytics module
import sys
sys.path.insert(0, '/home/me/projects/finance-analytics/src')

from finance_analytics.analytics import (
    simple_returns, log_returns, cumulative_returns,
    rolling_volatility, max_drawdown, sharpe_ratio,
    sortino_ratio, value_at_risk, conditional_value_at_risk,
    beta, alpha, correlation, historical_volatility
)
from finance_analytics.analytics.utils import annualize_return, annualize_volatility


class TestReturns(unittest.TestCase):
    """Test return calculation functions."""

    def setUp(self):
        """Set up test data."""
        # Create a simple price series
        self.prices = pd.Series([100, 110, 121, 110, 100],
                               index=pd.date_range('2023-01-01', periods=5))
        self.returns = pd.Series([0.1, 0.1, -0.0909, -0.0909],  # Approximately 10%, 10%, -9.09%, -9.09%
                                index=pd.date_range('2023-01-02', periods=4))

    def test_simple_returns(self):
        """Test simple returns calculation."""
        returns = simple_returns(self.prices)
        expected = pd.Series([np.nan, 0.1, 0.1, -0.0909, -0.0909],
                           index=self.prices.index)
        # Check first is NaN, then compare values
        self.assertTrue(np.isnan(returns.iloc[0]))
        np.testing.assert_array_almost_equal(
            returns.dropna().values,
            expected.dropna().values,
            decimal=4
        )

    def test_log_returns(self):
        """Test log returns calculation."""
        returns = log_returns(self.prices)
        # Log returns: ln(110/100)=ln(1.1)≈0.0953, ln(121/110)=ln(1.1)≈0.0953, etc.
        expected_values = [np.nan, np.log(1.1), np.log(1.1),
                          np.log(110/121), np.log(100/110)]
        self.assertTrue(np.isnan(returns.iloc[0]))
        np.testing.assert_array_almost_equal(
            returns.dropna().values,
            [expected_values[1], expected_values[2], expected_values[3], expected_values[4]],
            decimal=4
        )

    def test_cumulative_returns(self):
        """Test cumulative returns calculation."""
        cum_returns = cumulative_returns(self.returns)
        # Starting from 1: (1+0.1)*(1+0.1)=1.21, then * (1-0.0909)≈1.1, then * (1-0.0909)≈1.0
        # Cumulative returns: after 1st period: 0.1, after 2nd: 0.21, after 3rd: 0.1, after 4th: ~0.0
        expected_values = [0.1, 0.21, 0.1, 0.0]  # After each period
        np.testing.assert_array_almost_equal(
            cum_returns.values,
            expected_values,
            decimal=2
        )

        # Test with NaN in returns
        returns_with_nan = self.returns.copy()
        returns_with_nan.iloc[0] = np.nan
        cum_returns_with_nan = cumulative_returns(returns_with_nan)
        self.assertTrue(np.isnan(cum_returns_with_nan.iloc[0]))  # First should be NaN
        # Second value should be computed normally (treating NaN as 0)
        expected_second = (1 + 0.0) * (1 + self.returns.iloc[1]) - 1  # 0.1
        self.assertAlmostEqual(cum_returns_with_nan.iloc[1], expected_second, places=2)


class TestVolatility(unittest.TestCase):
    """Test volatility calculation functions."""

    def setUp(self):
        """Set up test data."""
        # Create returns with known volatility
        np.random.seed(42)
        self.returns = pd.Series(np.random.normal(0.001, 0.02, 100),  # Mean 0.1%, Std 2%
                                index=pd.date_range('2023-01-01', periods=100))

    def test_rolling_volatility(self):
        """Test rolling volatility calculation."""
        vol = rolling_volatility(self.returns, window=20)
        # Should be approximately 0.02 * sqrt(252) ≈ 0.317
        expected_annual_vol = 0.02 * np.sqrt(252)
        # Check that the mean of rolling vol is close to expected
        mean_vol = vol.dropna().mean()
        self.assertAlmostEqual(mean_vol, expected_annual_vol, places=1)

    def test_historical_volatility(self):
        """Test historical volatility calculation."""
        vol = historical_volatility(self.returns, annualize=True)
        expected_vol = 0.02 * np.sqrt(252)  # 2% daily vol annualized
        self.assertAlmostEqual(vol, expected_vol, places=1)


class TestDrawdown(unittest.TestCase):
    """Test drawdown calculation functions."""

    def setUp(self):
        """Set up test data with a known drawdown."""
        # Create a series that goes up then down: 100 -> 110 -> 120 -> 110 -> 100 -> 90
        # Cumulative returns from start: 0 -> 0.1 -> 0.2 -> 0.1 -> 0.0 -> -0.1
        dates = pd.date_range('2023-01-01', periods=6)
        self.cumulative_returns = pd.Series([0.0, 0.1, 0.2, 0.1, 0.0, -0.1], index=dates)

    def test_max_drawdown(self):
        """Test max drawdown calculation."""
        max_dd = max_drawdown(self.cumulative_returns)
        # Cumulative returns: [0.0, 0.1, 0.2, 0.1, 0.0, -0.1]
        # Running max: [0.0, 0.1, 0.2, 0.2, 0.2, 0.2]
        # Drawdown: [NaN, 0.0, 0.0, -0.5, -1.0, -1.5]
        # Max drawdown: -1.5
        self.assertLess(max_dd, 0)  # Should be negative
        self.assertAlmostEqual(max_dd, -1.5, places=2)


class TestRiskMetrics(unittest.TestCase):
    """Test risk metrics calculation functions."""

    def setUp(self):
        """Set up test data."""
        # Create returns with known distribution
        np.random.seed(42)
        self.returns = pd.Series(np.random.normal(0.0005, 0.01, 252),  # Daily returns for a year
                                index=pd.date_range('2023-01-01', periods=252))

    def test_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
        # With ~0.05% daily return, ~1% daily vol
        # Annual return ≈ 0.0005*252 = 0.126
        # Annual vol ≈ 0.01*sqrt(252) ≈ 0.1587
        # Sharpe ≈ 0.126/0.1587 ≈ 0.79 (assuming rf=0)
        sr = sharpe_ratio(self.returns, risk_free_rate=0.0)
        self.assertGreater(sr, 0)
        self.assertLess(sr, 2.0)  # Reasonable range

    def test_value_at_risk(self):
        """Test VaR calculation."""
        var_95 = value_at_risk(self.returns, confidence_level=0.95, method='historical')
        # For normal distribution, 95% VaR ≈ 1.645 * sigma
        # Sigma ≈ 0.01, so VaR ≈ 0.01645
        self.assertGreater(var_95, 0)  # Should be positive (representing loss)
        self.assertLess(var_95, 0.05)  # Should be reasonable

    def test_conditional_value_at_risk(self):
        """Test CVaR calculation."""
        cvar_95 = conditional_value_at_risk(self.returns, confidence_level=0.95, method='historical')
        var_95 = value_at_risk(self.returns, confidence_level=0.95, method='historical')
        # CVaR should be >= VaR for the same confidence level
        self.assertGreaterEqual(cvar_95, var_95)


class TestMarketSensitivity(unittest.TestCase):
    """Test market sensitivity calculation functions."""

    def setUp(self):
        """Set up test data with known beta."""
        np.random.seed(42)
        # Create market returns
        market_returns = pd.Series(np.random.normal(0.0005, 0.01, 200),
                                 index=pd.date_range('2023-01-01', periods=200))
        # Create asset returns with beta = 1.5 (minimize noise for test reliability)
        asset_returns = 1.5 * market_returns + np.random.normal(0, 0.001, 200)
        self.market_returns = market_returns
        self.asset_returns = asset_returns

    def test_beta(self):
        """Test beta calculation."""
        beta_val = beta(self.asset_returns, self.market_returns)
        # Should be close to 1.5
        self.assertAlmostEqual(beta_val, 1.5, places=1)

    def test_alpha(self):
        """Test alpha calculation."""
        # With no alpha in our generated data, alpha should be near zero
        alpha_val = alpha(self.asset_returns, self.market_returns)
        self.assertAlmostEqual(alpha_val, 0.0, places=1)

    def test_correlation(self):
        """Test correlation calculation."""
        corr_val = correlation(self.asset_returns, self.market_returns)
        # With beta=1.5 and low idiosyncratic vol, correlation should be high
        self.assertGreater(corr_val, 0.7)
        self.assertLessEqual(corr_val, 1.0)


if __name__ == '__main__':
    unittest.main()