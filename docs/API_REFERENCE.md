# API Reference

This document provides detailed information about the public APIs and functions available in the ETF Analytics Project.

## Analytics Module (`src/finance_analytics.analytics`)

The analytics module contains reusable financial calculation functions organized into submodules.

### Returns (`src/finance_analytics.analytics.returns`)

Functions for calculating various types of returns from price data.

#### simple_returns(prices)
Calculate simple (arithmetic) returns from a price series.

**Parameters:**
- `prices` (pd.Series): Price series (typically closing prices)
  
**Returns:**
- `pd.Series`: Simple returns where `r_t = P_t / P_(t-1) - 1`
  - First value is NaN (no previous price to calculate return)
  
**Example:**
```python
import pandas as pd
from finance_analytics.analytics.returns import simple_returns

prices = pd.Series([100, 110, 121, 110], 
                   index=pd.date_range('2023-01-01', periods=4))
returns = simple_returns(prices)
# Returns: [NaN, 0.1, 0.1, -0.0909...]
```

#### log_returns(prices)
Calculate logarithmic returns from a price series.

**Parameters:**
- `prices` (pd.Series): Price series
  
**Returns:**
- `pd.Series`: Log returns where `r_t = ln(P_t / P_(t-1))`
  - First value is NaN

**Example:**
```python
from finance_analytics.analytics.returns import log_returns

prices = pd.Series([100, 110, 121], 
                   index=pd.date_range('2023-01-01', periods=3))
returns = log_returns(prices)
# Returns: [NaN, ln(1.1), ln(1.1)] ≈ [NaN, 0.0953, 0.0953]
```

#### cumulative_returns(returns)
Calculate cumulative returns from a return series.

**Parameters:**
- `returns` (pd.Series): Return series (simple or log returns)
  
**Returns:**
- `pd.Series`: Cumulative returns where `CR_t = ∏(1 + r_i) - 1` from i=0 to t
  
**Example:**
```python
from finance_analytics.analytics.returns import cumulative_returns

returns = pd.Series([0.1, 0.1, -0.0909], 
                    index=pd.date_range('2023-01-02', periods=3))
cum_returns = cumulative_returns(returns)
# Returns: [0.1, 0.21, 0.1000...]
```

#### periodic_returns(returns, period)
Calculate periodic returns (e.g., monthly, yearly) from a return series.

**Parameters:**
- `returns` (pd.Series): Return series
- `period` (str): Pandas frequency string ('M' for monthly, 'Y' for yearly, etc.)
  
**Returns:**
- `pd.DataFrame`: Periodic returns with columns for each asset

### Volatility (`src/finance_analytics.analytics.volatility`)

Functions for calculating volatility and related measures.

#### rolling_volatility(returns, window=30, annualize=True)
Calculate rolling volatility of returns.

**Parameters:**
- `returns` (pd.Series): Return series
- `window` (int): Rolling window size in periods (default: 30)
- `annualize` (bool): Whether to annualize volatility (default: True)
  
**Returns:**
- `pd.Series`: Rolling volatility (annualized if annualize=True)
  
**Example:**
```python
from finance_analytics.analytics.volatility import rolling_volatility

returns = pd.Series(np.random.normal(0.0005, 0.01, 100))  # Daily returns
volatility = rolling_volatility(returns, window=20)
# Returns 20-day rolling annualized volatility
```

#### annualized_volatility(returns, period=252)
Calculate annualized volatility of returns.

**Parameters:**
- `returns` (pd.Series): Return series
- `period` (int): Number of periods in a year (default: 252 for daily returns)
  
**Returns:**
- `float`: Annualized volatility
  
**Example:**
```python
from finance_analytics.analytics.volatility import annualized_volatility

returns = pd.Series(np.random.normal(0.0005, 0.01, 252))  # One year of daily data
vol = annualized_volatility(returns)
# Approximately 0.01 * sqrt(252) ≈ 0.1587
```

#### ewma_volatility(returns, span=30, annualize=True)
Calculate exponentially weighted moving average volatility.

**Parameters:**
- `returns` (pd.Series): Return series
- `span` (int): Span for EWMA calculation
- `annualize` (bool): Whether to annualize (default: True)
  
**Returns:**
- `pd.Series`: EWMA volatility

### Drawdown (`src/finance_analytics.analytics.drawdown`)

Functions for calculating drawdown and related measures.

#### max_drawdown(cumulative_returns)
Calculate the maximum drawdown from a cumulative return series.

**Parameters:**
- `cumulative_returns` (pd.Series): Cumulative return series (where 0 = starting point)
  
**Returns:**
- `float`: Maximum drawdown (negative value or zero)
  
**Example:**
```python
from finance_analytics.analytics.drawdown import max_drawdown

cum_returns = pd.Series([0.0, 0.1, 0.2, 0.1, -0.05, -0.15])  # Peaks at 0.2, trough at -0.15
max_dd = max_drawdown(cum_returns)
# Drawdown from peak: (-0.15 - 0.2) / (1 + 0.2) = -0.35 / 1.2 = -0.2917
```

#### rolling_drawdown(returns, window=252)
Calculate rolling drawdown from a return series.

**Parameters:**
- `returns` (pd.Series): Return series
- `window` (int): Rolling window size in periods (default: 252)
  
**Returns:**
- `pd.Series`: Rolling maximum drawdown

#### drawdown_series(cumulative_returns)
Calculate the drawdown series (current drawdown from peak) from cumulative returns.

**Parameters:**
- `cumulative_returns` (pd.Series): Cumulative return series
  
**Returns:**
- `pd.Series`: Current drawdown at each point in time

### Risk Metrics (`src/finance_analytics.analytics.risk_metrics`)

Functions for calculating risk-related metrics.

#### value_at_risk(returns, confidence_level=0.95, method='historical')
Calculate Value at Risk (VaR) at a specified confidence level.

**Parameters:**
- `returns` (pd.Series): Return series
- `confidence_level` (float): Confidence level between 0 and 1 (default: 0.95 for 95%)
- `method` (str): Calculation method ('historical', 'parametric', 'monte_carlo') (default: 'historical')
  
**Returns:**
- `float`: VaR value (positive representing loss magnitude)
  
**Example:**
```python
from finance_analytics.analytics.risk_metrics import value_at_risk

returns = pd.Series(np.random.normal(0.0005, 0.01, 252))  # Approximately 1% daily vol
var_95 = value_at_risk(returns, confidence_level=0.95)
# For normal distribution, 95% VaR ≈ 1.645 * sigma ≈ 1.645 * 0.01 = 0.01645
```

#### conditional_value_at_risk(returns, confidence_level=0.95, method='historical')
Calculate Conditional Value at Risk (CVaR, also known as Expected Shortfall).

**Parameters:**
- `returns` (pd.Series): Return series
- `confidence_level` (float): Confidence level between 0 and 1 (default: 0.95)
- `method` (str): Calculation method (default: 'historical')
  
**Returns:**
- `float`: CVaR value (positive representing expected loss beyond VaR)
  
**Note:** CVaR >= VaR for the same confidence level and method.

#### sharpe_ratio(returns, risk_free_rate=0.0, periods_per_year=252)
Calculate the Sharpe ratio (risk-adjusted return).

**Parameters:**
- `returns` (pd.Series): Return series
- `risk_free_rate` (float): Risk-free rate per period (default: 0.0)
- `periods_per_year` (int): Number of periods in a year for annualization (default: 252)
  
**Returns:**
- `float`: Sharpe ratio
  
**Formula:** `(annualized_return - annualized_risk_free_rate) / annualized_volatility`

**Example:**
```python
from finance_analytics.analytics.risk_metrics import sharpe_ratio

returns = pd.Series(np.random.normal(0.0006, 0.01, 252))  # 6bp daily return, 1% vol
sr = sharpe_ratio(returns, risk_free_rate=0.0)
# Annual return ≈ 0.0006 * 252 = 0.1512
# Annual vol ≈ 0.01 * sqrt(252) ≈ 0.1587
# SR ≈ 0.1512 / 0.1587 ≈ 0.953
```

#### sortino_ratio(returns, target_return=0.0, periods_per_year=252)
Calculate the Sortino ratio (downside risk-adjusted return).

**Parameters:**
- `returns` (pd.Series): Return series
- `target_return` (float): Minimum acceptable return per period (default: 0.0)
- `periods_per_year` (int): Number of periods in a year (default: 252)
  
**Returns:**
- `float`: Sortino ratio
  
**Note:** Similar to Sharpe ratio but only considers downside deviation below target_return.

### Market Sensitivity (`src/finance_analytics.analytics.market_sensitivity`)

Functions for calculating market sensitivity and related measures.

#### beta(asset_returns, market_returns)
Calculate beta (sensitivity to market movements).

**Parameters:**
- `asset_returns` (pd.Series): Return series of the asset
- `market_returns` (pd.Series): Return series of the market benchmark
  
**Returns:**
- `float`: Beta coefficient
  
**Note:** Returns should be aligned by date/index for accurate calculation.
  
**Example:**
```python
from finance_analytics.analytics.market_sensitivity import beta

# Assume we have aligned returns data
asset_returns = pd.Series([0.01, 0.02, -0.01, 0.015])
market_returns = pd.Series([0.005, 0.01, -0.005, 0.01])
beta_val = beta(asset_returns, market_returns)
# Should be approximately 2.0 since asset moves ~2x market
```

#### alpha(asset_returns, market_returns, risk_free_rate=0.0)
Calculate alpha (excess return after adjusting for beta).

**Parameters:**
- `asset_returns` (pd.Series): Return series of the asset
- `market_returns` (pd.Series): Return series of the market benchmark
- `risk_free_rate` (float): Risk-free rate per period (default: 0.0)
  
**Returns:**
- `float`: Alpha coefficient
  
**Note:** Represents the intercept in the CAPM regression: 
  `asset_return = alpha + beta * market_return + epsilon`

#### correlation(asset_returns, benchmark_returns)
Calculate correlation between two return series.

**Parameters:**
- `asset_returns` (pd.Series): First return series
- `benchmark_returns` (pd.Series): Second return series (typically market)
  
**Returns:**
- `float`: Correlation coefficient (-1 to 1)
  
**Example:**
```python
from finance_analytics.analytics.market_sensitivity import correlation

returns_a = pd.Series([0.01, 0.02, -0.01, 0.015])
returns_b = pd.Series([0.005, 0.01, -0.005, 0.01])
corr = correlation(returns_a, returns_b)
# Should be high positive since returns move together
```

#### rolling_correlation(asset_returns, benchmark_returns, window=90)
Calculate rolling correlation between two return series.

**Parameters:**
- `asset_returns` (pd.Series): First return series
- `benchmark_returns` (pd.Series): Second return series
- `window` (int): Rolling window size (default: 90)
  
**Returns:**
- `pd.Series`: Rolling correlation coefficient

### Utility Functions (`src/finance_analytics.analytics.utils`)

Helper functions supporting the analytics module.

#### annualize_return(return_per_period, periods_per_year)
Convert a periodic return to an annualized return.

**Parameters:**
- `return_per_period` (float): Return per period
- `periods_per_year` (int): Number of periods in a year
  
**Returns:**
- `float`: Annualized return
  
**Formula:** `(1 + return_per_period) ^ periods_per_year - 1`

#### annualize_volatility(volatility_per_period, periods_per_year)
Convert a periodic volatility to an annualized volatility.

**Parameters:**
- `volatility_per_period` (float): Volatility per period
- `periods_per_year` (int): Number of periods in a year
  
**Returns:**
- `float`: Annualized volatility
  
**Formula:** `volatility_per_period * sqrt(periods_per_year)`

#### validate_price_data(df)
Validate that a DataFrame contains proper OHLC price data.

**Parameters:**
- `df` (pd.DataFrame): DataFrame with price data
  
**Returns:**
- `bool`: True if data passes basic validation checks
  
**Checks:**
- Required columns exist: 'open', 'high', 'low', 'close'
- Numeric columns contain numeric data
- Date column (if present) is datetime-like
- Basic OHLC relationships: high >= low, high >= open, high >= close, low <= open, low <= close

#### align_series(series1, series2)
Align two pandas Series by their index (typically date), keeping only common dates.

**Parameters:**
- `series1` (pd.Series): First time series
- `series2` (pd.Series): Second time series
  
**Returns:**
- `tuple`: (aligned_series1, aligned_series2) with matching indices
  
**Example:**
```python
from finance_analytics.analytics.utils import align_series

s1 = pd.Series([1, 2, 3], index=['2023-01-01', '2023-01-02', '2023-01-04'])
s2 = pd.Series([4, 5, 6], index=['2023-01-02', '2023-01-03', '2023-01-04'])
aligned_s1, aligned_s2 = align_series(s1, s2)
# Both series will have index ['2023-01-02', '2023-01-04']
# aligned_s1: [2, 3]
# aligned_s2: [4, 6]
```

## Database Module (`src/finance_analytics.database`)

Functions for interacting with the PostgreSQL database.

### Connection (`src/finance_analytics.database.connection`)

#### get_engine()
Get a SQLAlchemy engine for connecting to the PostgreSQL database.

**Parameters:**
- None (reads connection parameters from environment variables)
  
**Returns:**
- `sqlalchemy.engine.Engine`: SQLAlchemy engine object
  
**Environment Variables:**
- DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

**Example:**
```python
from src.finance_analytics.database.connection import get_engine

engine = get_engine()
# Use engine for pandas read_sql or SQLAlchemy operations
```

### Schema (`src/finance_analytics.database.schema`)

#### initialize_database_schema()
Initialize or update the PostgreSQL database schema for the prices table.

**Parameters:**
- None
  
**Returns:**
- None
  
**Side Effects:**
- Creates prices table if it doesn't exist
- Adds missing columns if table exists but schema is outdated
- Ensures primary key constraint exists
  
**Example:**
```python
from src.finance_analytics.database.schema import initialize_database_schema

initialize_database_schema()
# Database is now ready for use
```

### Operations (`src/finance_analytics.database.operations`)

Functions for common database operations.

#### get_latest_dates(tickers)
Get the most recent date for which data exists for each ticker.

**Parameters:**
- `tickers` (list): List of ticker symbols
  
**Returns:**
- `dict`: Mapping of ticker to latest date (date object or None if no data)
  
**Example:**
```python
from src.finance_analytics.database.operations import get_latest_dates

latest = get_latest_dates(['SPY', 'QQQ', 'VTI'])
# Returns: {'SPY': date(2023, 6, 15), 'QQQ': date(2023, 6, 15), 'VTI': None}
```

#### determine_download_start(tickers, start_date, overlap_days)
Determine the start date for downloading data.

**Parameters:**
- `tickers` (list): List of ticker symbols
- `start_date` (str): Start date for full historical download (YYYY-MM-DD)
- `overlap_days` (int): Number of days to overlap for incremental downloads
  
**Returns:**
- `str`: Download start date in YYYY-MM-DD format
  
**Logic:**
- If any ticker has no existing data: return start_date (full download)
- Otherwise: return (earliest_existing_date - overlap_days), but not earlier than start_date

#### get_download_end()
Get the end date for downloading data (yesterday).

**Parameters:**
- None
  
**Returns:**
- `str`: Download end date in YYYY-MM-DD format (yesterday)
  
**Note:** Uses yesterday to avoid downloading potentially incomplete today's data.

#### needs_download(download_start, download_end)
Check if data needs to be downloaded based on date range.

**Parameters:**
- `download_start` (str): Start date in YYYY-MM-DD format
- `download_end` (str): End date in YYYY-MM-DD format (exclusive)
  
**Returns:**
- `bool`: True if download_start < download_end, False otherwise

#### upsert_prices(records)
Upsert price records into the PostgreSQL database.

**Parameters:**
- `records` (list): List of dictionaries, each representing a price record
  - Each dict should have keys matching the prices table columns:
    - date, ticker, open, high, low, close, adj_open, adj_high, adj_low, adj_close, volume
  
**Returns:**
- None
  
**Operation:** INSERT ... ON CONFLICT (date, ticker) DO UPDATE SET ...
  - This updates existing rows with new data (important for capturing Yahoo corrections)

## Configuration Module (`src/finance_analytics.config`)

Functions for managing project configuration.

### load_config()
Load configuration from environment variables.

**Parameters:**
- None
  
**Returns:**
- `dict`: Configuration dictionary with keys:
  - START_DATE (str): Start date for full historical download
  - OVERLAP_DAYS (int): Days to overlap for incremental downloads
  - YFINANCE_PROGRESS (bool): Whether to show yfinance progress bar

### get_etf_tickers()
Get Yahoo Finance tickers from the ETF universe definition.

**Parameters:**
- None
  
**Returns:**
- `list`: List of Yahoo Finance ticker strings from primary listings
  
**Note:** Falls back to ETF_TICKERS environment variable if universe loading fails.

### get_tickers_with_fallback()
Get ETF tickers with fallback to environment variable.

**Parameters:**
- None
  
**Returns:**
- `list`: List of ticker symbols (from universe or ETF_TICKERS env var)
  
**Raises:**
- RuntimeError: If no tickers can be found from either source

## Universe Module (`src/finance_analytics.universe.etfs`)

Functions and definitions for the ETF research universe.

### get_all_etfs()
Get the complete research universe of ETFs.

**Parameters:**
- None
  
**Returns:**
- `tuple[ETF, ...]`: Tuple of ETF objects representing the complete universe

### get_etf_by_isin(isin)
Get a specific ETF by its ISIN.

**Parameters:**
- `isin` (str): International Securities Identification Number
  
**Returns:**
- `ETF`: The ETF object with the specified ISIN
  
**Raises:**
- `ValueError`: If no ETF with the given ISIN exists in the universe

### get_primary_listings()
Get the primary Yahoo Finance listing for every ETF in the universe.

**Parameters:**
- None
  
**Returns:**
- `tuple[Listing, ...]`: Tuple of Listing objects representing primary listings
  
**Note:** Each Listing has `.yahoo_ticker` attribute suitable for ticker extraction

## Streamlit Application (`app/streamlit_app.py`)

While not designed as a library API, the Streamlit application contains several helper functions that could be reused:

### load_prices(start_date=None, end_date=None, tickers=TICKERS)
Load price data from the PostgreSQL database.

**Parameters:**
- `start_date` (str or datetime, optional): Start date for filtering
- `end_date` (str or datetime, optional): End date for filtering
- `tickers` (list, optional): List of ticker symbols to filter by (default: from ETF_TICKERS env var)
  
**Returns:**
- `pd.DataFrame`: DataFrame with columns ['date', 'ticker', 'close']

### table_exists(table_name)
Check if a table exists in the database.

**Parameters:**
- `table_name` (str): Name of table to check
  
**Returns:**
- `bool`: True if table exists, False otherwise

### load_holdings(table_name="holdings")
Load holdings data from a specified table.

**Parameters:**
- `table_name` (str): Name of holdings table (default: "holdings")
  
**Returns:**
- `pd.DataFrame`: Holdings data

## Usage Examples

### Example 1: Complete Analysis Pipeline

```python
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Import analytics functions
from finance_analytics.analytics import (
    simple_returns, rolling_volatility, max_drawdown,
    sharpe_ratio, value_at_risk, beta, alpha, correlation
)
from finance_analytics.analytics.utils import align_series, validate_price_data

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)

# Load data for two ETFs
query = """
SELECT date, ticker, adj_close as close
FROM prices
WHERE ticker IN ('SPY', 'QQQ')
  AND date >= '2022-01-01'
ORDER BY date, ticker;
"""
df = pd.read_sql(query, engine)
df['date'] = pd.to_datetime(df['date'])

# Validate data
if not validate_price_data(df):
    raise ValueError("Price data validation failed")

# Prepare data: pivot to have one column per ticker's price
price_pivot = df.pivot(index='date', columns='ticker', values='close')

# Calculate returns
returns = price_pivot.apply(simple_returns)

# Calculate volatility for each ETF
volatility = returns.apply(lambda x: rolling_volatility(x, window=30))

# Calculate max drawdown for each ETF
# First need cumulative returns
cum_returns = (1 + returns).cumprod() - 1
max_dd = cum_returns.apply(max_drawdown)

# Calculate Sharpe ratio (assuming 0% risk-free rate)
sharpe = returns.apply(lambda x: sharpe_ratio(x, risk_free_rate=0.0))

# Calculate VaR at 95% confidence
var_95 = returns.apply(lambda x: value_at_risk(x, confidence_level=0.95))

# Calculate beta of QQQ vs SPY
aligned_returns, _ = align_series(returns['QQQ'], returns['SPY'])
beta_qqq_spy = beta(aligned_returns.iloc[:, 0], aligned_returns.iloc[:, 1])

# Calculate alpha
alpha_qqq_spy = alpha(aligned_returns.iloc[:, 0], aligned_returns.iloc[:, 1])

# Calculate correlation
corr_qqq_spy = correlation(aligned_returns.iloc[:, 0], aligned_returns.iloc[:, 1])

# Results can now be used for reporting or further analysis
results = pd.DataFrame({
    'volatility_30d': volatility.iloc[-1],  # Most recent values
    'max_drawdown': max_dd,
    'sharpe_ratio': sharpe,
    'var_95': var_95,
    'beta_vs_spy': [beta_qqq_spy, np.nan],  # Beta of SPY vs itself is undefined
    'alpha_vs_spy': [alpha_qqq_spy, np.nan],
    'correlation_vs_spy': [corr_qqq_spy, 1.0]  # Correlation of SPY with itself is 1.0
}, index=['QQQ', 'SPY'])

print(results)
```

### Example 2: Using the ETF Universe

```python
from src.finance_analytics.universe.etfs import get_all_etfs, get_primary_listings
from src.finance_analytics.config import get_etf_tickers

# Method 1: Get all ETF objects with full metadata
all_etfs = get_all_etfs()
print(f"Universe contains {len(all_etfs)} ETFs")

# Find all US large-cap ETFs
us_large_cap = [etf for etf in all_etfs 
                if etf.geography == "United States" and etf.strategy == "Large Cap"]
print(f"Found {len(us_large_cap)} US large-cap ETFs")

# Method 2: Get primary listings for ticker extraction
primary_listings = get_primary_listings()
tickers = [listing.yahoo_ticker for listing in primary_listings]
print(f"Extracted {len(tickers)} Yahoo Finance tickers")

# Method 3: Use the config helper (recommended for most use cases)
tickers_from_config = get_etf_tickers()
print(f"Got {len(tickers_from_config)} tickers from config helper")

# Verify they're the same
assert set(tickers) == set(tickers_from_config)
```

### Example 3: Database Operations

```python
from src.finance_analytics.database.connection import get_engine
from src.finance_analytics.database.operations import (
    get_latest_dates, determine_download_start, get_download_end, needs_download
)
from src.finance_analytics.database.schema import initialize_database_schema

# Initialize schema (safe to call multiple times)
initialize_database_schema()

# Get engine for direct operations if needed
engine = get_engine()

# Check current data coverage
tickers = ['SPY', 'QQQ', 'VTI']
latest_dates = get_latest_dates(tickers)
print("Latest dates:", latest_dates)

# Determine what needs to be downloaded
start_date = determine_download_start(tickers, "2015-01-01", 7)
end_date = get_download_end()
print(f"Download range: {start_date} to {end_date}")

if needs_download(start_date, end_date):
    print("Data needs to be downloaded")
    # Here you would call your download and ingestion logic
else:
    print("Data is already up to date")
```

## Error Handling

### Common Exceptions

#### Analytics Functions
Most analytics functions will handle common edge cases:
- **Insufficient data**: Return NaN or raise ValueError with descriptive message
- **Non-numeric input**: Will raise TypeError or propagate pandas/numpy errors
- **Misaligned indices**: Functions that expect aligned data (like beta) may produce incorrect results if indices don't match

#### Database Operations
Database functions may raise:
- **sqlalchemy.exc.OperationalError**: For connection issues
- **sqlalchemy.exc.ProgrammingError**: For SQL syntax errors
- **ValueError**: For invalid input parameters

#### Configuration
Configuration functions may raise:
- **RuntimeError**: If required environment variables are missing and no defaults available
- **ValueError**: For invalid environment variable values (e.g., non-numeric OVERLAP_DAYS)

### Best Practices for Error Handling

1. **Validate Inputs**: Use `validate_price_data()` or similar checks before processing
2. **Handle NaN Values**: Decide how to handle missing data (drop, fill, or propagate)
3. **Check Alignment**: Use `align_series()` when combining multiple time series
4. **Use Try/Except**: Wrap database operations in try/except blocks for connection issues
5. **Log Errors**: Use Python logging module for production error tracking
6. **Provide Fallbacks**: Consider fallback values or alternative calculations when possible

## Versioning

This API reference corresponds to the current version of the ETF Analytics Project.

### Stability Guarantees
- **Stable**: Functions in the analytics module are unlikely to change signatures
- **Evolving**: Database and configuration functions may evolve as the project grows
- **Internal**: Streamlit helper functions are subject to change as the UI evolves

### Deprecation Policy
When functions are deprecated:
1. Deprecation warnings will be added using Python's `warnings` module
2. Deprecated functions will remain functional for at least one release cycle
3. Documentation will mark them as deprecated
4. Clear migration path to replacement functions will be provided

## Extending the API

### Adding New Analytics Functions
To add a new financial calculation function:

1. **Determine Appropriate Submodule**: Choose returns, volatility, drawdown, risk_metrics, market_sensitivity, or utils based on function purpose
2. **Implement Function**: Write pure function that accepts pandas Series/DataFrame and returns appropriate result
3. **Handle Edge Cases**: Consider empty inputs, insufficient data, NaN values, misaligned indices
4. **Add Tests**: Create unit tests in `tests/unit/` directory
5. **Update __init__.py**: Add function to __all__ list in the appropriate submodule's __init__.py
6. **Update Main __init__.py**: Add to __all__ in `src/finance_analytics/analytics/__init__.py` if should be publicly importable
7. **Document**: Add to this API reference with proper docstring and example

### Adding New Database Functions
To add a new database operation function:

1. **Determine Category**: Choose connection, schema, or operations based on function purpose
2. **Implement Function**: Follow existing patterns for engine/session handling
3. **Handle Transactions**: Use appropriate transaction management (engine.begin() for writes)
4. **Add Error Handling**: Include appropriate try/except blocks with meaningful error messages
5. **Add Tests**: Create integration tests in `tests/integration/` directory
6. **Document**: Add to this API reference

### Adding New Configuration Options
To add a new configuration option:

1. **Choose Name**: Select clear, descriptive name for environment variable
2. **Update load_config()**: Add to returned dictionary with appropriate default and type conversion
3. **Update .env.example**: Add line with variable name and example value
4. **Update Documentation**: Add to INSTALLATION.md and any other relevant documentation
5. **Use Consistently**: Reference through config dictionary rather than direct os.getenv() calls
6. **Document**: Add to this API reference in the Configuration Module section

## Conclusion

This API reference covers the major public interfaces of the ETF Analytics Project. The analytics module forms the core reusable component, providing pure functions that can be used across contexts (data ingestion, Streamlit dashboard, custom analysis scripts). The database and configuration modules provide infrastructure support, while the universe module defines the ETF research universe that drives the project's scope.

For the most up-to-date information, always refer to the docstrings in the source code, as they are maintained alongside the implementation.