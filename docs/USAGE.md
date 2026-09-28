# Usage Guide

## Overview

This guide explains how to use the ETF Analytics Project for data ingestion, analysis, and visualization.

## 1. Data Ingestion

### Running the Update Script

The main data ingestion script is `update_database.py`. It handles downloading ETF data from Yahoo Finance and storing it in PostgreSQL.

#### Basic Usage

```bash
python update_database.py
```

This will:
1. Load ETF tickers from the ETF universe or ETF_TICKERS environment variable
2. Connect to PostgreSQL using credentials from .env
3. Initialize/update the database schema
4. Determine date range for download (full history or incremental)
5. Download raw and adjusted OHLCV data
6. Normalize, clean, and validate the data
7. UPSERT the data into the prices table
8. Print a summary of the operation

#### Command-Line Arguments

The script does not accept command-line arguments; all configuration is done through environment variables in the `.env` file.

#### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_USER` | PostgreSQL username | (required) |
| `DB_PASSWORD` | PostgreSQL password | (required) |
| `DB_HOST` | PostgreSQL host | localhost |
| `DB_PORT` | PostgreSQL port | 5432 |
| `DB_NAME` | PostgreSQL database name | finance_db |
| `ETF_TICKERS` | Comma-separated list of ETF tickers | SPY,QQQ |
| `START_DATE` | Start date for full historical download (YYYY-MM-DD) | 2015-01-01 |
| `OVERLAP_DAYS` | Days to overlap for incremental downloads | 7 |
| `YFINANCE_PROGRESS` | Show yfinance progress bar | True |

### Understanding the Update Process

#### First Run
On the first run, the script will:
- Download full history for all specified ETFs from START_DATE to yesterday
- Create the prices table if it doesn't exist
- Store both raw and adjusted prices
- Print statistics about rows downloaded and stored

#### Subsequent Runs
On subsequent runs, the script will:
- Identify the earliest date currently stored across all tickers
- Calculate a new download start date as (earliest_stored_date - OVERLAP_DAYS)
- Never go earlier than START_DATE
- Download data from the calculated start date to yesterday
- UPSERT all data, updating existing rows with any corrections from Yahoo
- This approach ensures data consistency while minimizing redundant downloads

### Verifying Data Ingestion

After running the update script, you can verify the data was stored correctly:

```bash
# Check row count
psql -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM prices;"

# Check date range for a ticker
psql -U $DB_USER -d $DB_NAME -c "SELECT MIN(date), MAX(date) FROM prices WHERE ticker = 'SPY';"

# Check table structure
psql -U $DB_USER -d $DB_NAME -c "\d prices"
```

## 2. Using the Analytics Functions

The project provides a comprehensive set of financial analytics functions that can be used in Python scripts, Jupyter notebooks, or other applications.

### Importing the Analytics Module

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from finance_analytics.analytics import (
    # Returns
    simple_returns, log_returns, cumulative_returns,
    
    # Volatility
    rolling_volatility, annualized_volatility,
    
    # Drawdown
    max_drawdown, rolling_drawdown,
    
    # Risk Metrics
    value_at_risk, conditional_value_at_risk,
    sharpe_ratio, sortino_ratio,
    
    # Market Sensitivity
    beta, alpha, correlation,
    
    # Utils
    annualize_return, validate_price_data
)
```

### Example Usage

#### Calculating Returns

```python
import pandas as pd

# Assume df is a DataFrame with date, ticker, close columns
df = pd.read_csv('price_data.csv')
df['date'] = pd.to_datetime(df['date'])

# Calculate simple returns for each ticker
df['simple_return'] = df.groupby('ticker')['close'].transform(simple_returns)

# Calculate log returns
df['log_return'] = df.groupby('ticker')['close'].transform(log_returns)

# Calculate cumulative returns (starting from 0)
df['cumulative_return'] = df.groupby('ticker')['simple_return'].transform(cumulative_returns)
```

#### Risk Analysis

```python
# Calculate VaR and CVaR for a ticker's returns
spy_returns = df[df['ticker'] == 'SPY']['simple_return'].dropna()
var_95 = value_at_risk(spy_returns, confidence_level=0.95)
cvar_95 = conditional_value_at_risk(spy_returns, confidence_level=0.95)

# Calculate Sharpe ratio (assuming 0% risk-free rate)
sharpe = sharpe_ratio(spy_returns, risk_free_rate=0.0)

# Calculate max drawdown
max_dd = max_drawdown(
    df[df['ticker'] == 'SPY']['cumulative_return']
)
```

#### Market Sensitivity

```python
# Calculate beta of QQQ vs SPY
qqq_returns = df[df['ticker'] == 'QQQ']['simple_return'].dropna()
spy_returns = df[df['ticker'] == 'SPY']['simple_return'].dropna()

# Align the series by date (important for accurate beta)
aligned_data = pd.DataFrame({
    'spy': spy_returns,
    'qqq': qqq_returns
}).dropna()

beta_qqq_spy = beta(aligned_data['qqq'], aligned_data['spy'])
alpha_qqq_spy = alpha(aligned_data['qqq'], aligned_data['spy'])
correlation_qqq_spy = correlation(aligned_data['qqq'], aligned_data['spy'])
```

## 3. Using the Streamlit Dashboard

### Launching the Dashboard

```bash
streamlit run app/streamlit_app.py
```

### Dashboard Features

#### Sidebar Controls
- **Date Range Selection**: Choose start and end dates for analysis
- **Ticker Selection**: Select one or more ETFs from the available universe
- **Regression Pair**: Select two tickers for correlation and regression analysis
- **Rolling Windows**: Choose time windows for rolling metrics (30, 90, 252 days)
- **VaR Confidence**: Set confidence level for Value at Risk calculations (90-99%)

#### Main Panels

1. **Cumulative Returns Chart**
   - Shows growth of $1 invested in each selected ETF
   - Interactive Plotly chart with hover tooltips

2. **Returns Distribution and VaR/CVaR**
   - Histogram of daily returns for each ETF
   - VaR and CVaR metrics displayed as statistics
   - Vertical line indicating VaR threshold on histogram

3. **Rolling Metrics**
   - Rolling volatility (annualized) for selected windows
   - Rolling Sharpe ratio (assuming 0% risk-free rate)
   - Separate charts for each metric

4. **Rolling Correlation**
   - Shows rolling correlation between the two selected tickers
   - Multiple windows can be viewed simultaneously

5. **Yearly Volatility and Max Drawdown**
   - Tabular display of annualized volatility by year and ticker
   - Tabular display of maximum drawdown by year and ticker

6. **Simple Linear Regressions**
   - OLS regression results showing beta and alpha
   - Scatter plot with regression line
   - Available for each direction (ETF1 ~ ETF2 and ETF2 ~ ETF1)

7. **Holdings Analysis** (Conditional)
   - Appears only if a holdings table exists in the database
   - Shows top holdings, sector breakdown, and concentration metrics

### Interpreting the Results

#### Returns Charts
- **Cumulative Returns**: Shows total return over time, assuming reinvestment of dividends (when using adjusted prices)
- Higher final value indicates better performance over the selected period

#### Risk Metrics
- **VaR (Value at Risk)**: Estimated maximum loss over a given time period at a specific confidence level
  - Example: 95% VaR of -0.02 means there's a 95% chance the daily loss won't exceed 2%
- **CVaR (Conditional VaR)**: Expected loss given that the loss exceeds the VaR threshold
  - Provides insight into tail risk beyond VaR
- **Sharpe Ratio**: Risk-adjusted return measure (return per unit of risk)
  - Higher values indicate better risk-adjusted performance
  - Typically: <1 = poor, 1-2 = good, >2 = excellent
- **Sortino Ratio**: Similar to Sharpe but only considers downside volatility
- **Max Drawdown**: Largest peak-to-trough decline during the period
  - Measures worst-case scenario for an investor who bought at the peak and sold at the trough

#### Rolling Metrics
- **Rolling Volatility**: Shows how volatility changes over time
  - Helps identify regimes of high/low market stress
- **Rolling Sharpe**: Shows how risk-adjusted performance evolves
  - Can reveal periods of skill or luck in performance

#### Correlation Analysis
- **Rolling Correlation**: Shows how the relationship between two ETFs changes over time
  - Stable correlations suggest consistent relationship
  - Changing correlations may indicate regime shifts or changing market dynamics

#### Regression Analysis
- **Beta**: Measures sensitivity to market movements
  - Beta = 1: Moves with the market
  - Beta > 1: More volatile than the market
  - Beta < 1: Less volatile than the market
  - Beta < 0: Moves opposite to the market
- **Alpha**: Excess return after adjusting for beta
  - Positive alpha indicates outperformance relative to beta prediction
  - Negative alpha indicates underperformance

## 4. Advanced Usage

### Custom ETF Lists

To analyze a custom set of ETFs, modify the `ETF_TICKERS` environment variable in your `.env` file:

```
ETF_TICKERS=SPY,QQQ,VTI,GLD,BND,VWO,EFA,IEUR,EPHE
```

### Changing the Historical Data Range

To change the start date for full historical downloads:

```
START_DATE=2010-01-01
```

Note: This only affects the first run or when adding new tickers. Subsequent runs use the incremental update mechanism.

### Disabling yfinance Progress Bar

For cron jobs or non-interactive usage:

```
YFINANCE_PROGRESS=False
```

### Direct Database Access

For custom applications or analysis, you can access the PostgreSQL database directly:

```python
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)

# Example query
import pandas as pd
query = """
SELECT date, ticker, close
FROM prices
WHERE ticker IN ('SPY', 'QQQ')
  AND date >= '2023-01-01'
ORDER BY date, ticker;
"""
df = pd.read_sql(query, engine)
```

### Integrating with Other Systems

The analytics functions are designed to be importable and usable in other Python applications:

```python
# In your custom analysis script
from finance_analytics.analytics import (
    simple_returns, rolling_volatility, max_drawdown,
    sharpe_ratio, value_at_risk
)

# Your data processing pipeline
def analyze_etf(ticker_symbol, start_date, end_date):
    # 1. Load data from database
    # 2. Calculate returns
    # 3. Compute risk metrics
    # 4. Generate report
    pass
```

## 5. Maintenance Tasks

### Resetting the Database

To completely reset the database (use with caution - this deletes all stored data):

```bash
# Drop and recreate the database
dropdb -U $DB_USER $DB_NAME
createdb -U $DB_USER $DB_NAME

# Reinitialize schema and redownload data
python -c "
from src.finance_analytics.database.connection import get_engine
from src.finance_analytics.database.schema import initialize_database_schema
engine = get_engine()
initialize_database_schema()
"
python update_database.py
```

### Checking Database Status

```bash
# Check table size and row count
psql -U $DB_USER -d $DB_NAME -c "
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE tablename = 'prices';
"

# Or for simpler stats
psql -U $DB_USER -d $DB_NAME -c "
SELECT 
    COUNT(*) as total_rows,
    COUNT(DISTINCT ticker) as unique_tickers,
    MIN(date) as earliest_date,
    MAX(date) as latest_date
FROM prices;
"
```

### Updating Dependencies

To update Python packages to their latest compatible versions:

```bash
pip list --outdated  # See outdated packages
pip install -U package_name  # Update specific package
# Or update all (be cautious with major version changes)
pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U
```

Always test thoroughly after updating dependencies, especially for financial calculation libraries.

## 6. Best Practices

### Data Quality
- Always validate data after ingestion using the built-in validation functions
- Check for missing values and unexpected outliers
- Verify OHLC relationships (High >= Low, High >= Open/Close, Low <= Open/Close)

### Reproducibility
- Use fixed random seeds when running simulations or Monte Carlo analyses
- Document the exact date range and ETF list used for analyses
- Version control your analysis scripts and notebooks

### Performance
- For large datasets, consider indexing strategies in PostgreSQL
- The analytics functions use vectorized pandas operations which are efficient
- Streamlit caching (@st.cache_data, @st.cache_resource) helps with dashboard performance

### Security
- Never commit your `.env` file with real credentials
- Use least-privilege database users for production deployments
- Consider SSL connections for remote PostgreSQL instances

## 7. Examples

### Example 1: Comparing Two ETFs

```bash
# Set ETFs to compare
echo "ETF_TICKERS=SPY,VTI" >> .env

# Update database
python update_database.py

# Launch dashboard
streamlit run app/streamlit_app.py
```

In the dashboard:
1. Select both SPY and VTI
2. View cumulative returns to see long-term performance difference
3. Check rolling correlation to see how their relationship changes
4. Run regression analysis to calculate beta and alpha
5. Examine risk metrics (VaR, CVaR, Sharpe) for risk-adjusted comparison

### Example 2: Sector Analysis

```bash
# Set sector ETFs
echo "ETF_TICKERS=XLY,XLP,XLE,XLF,XLV,XLI,XLB,XLK,XLU" >> .env

# Update database
python update_database.py

# Launch dashboard
streamlit run app/streamlit_app.py
```

In the dashboard:
1. Select all sector ETFs
2. Compare cumulative returns to see sector rotation patterns
3. Use rolling correlation to identify leading/lagging sectors
4. Analyze volatility patterns across market cycles
5. Check drawdowns during market stress periods

### Example 3: Fixed Income Analysis

```bash
# Set bond ETFs
echo "ETF_TICKERS=BND,AGG,TLT,IEI,SHY,LQD,HYG" >> .env

# Update database
python update_database.py

# Launch dashboard
streamlit run app/streamlit_app.py
```

In the dashboard:
1. Examine how different duration bond ETFs respond to interest rate changes
2. Compare nominal vs inflation-protected bond performance
3. Analyze credit spread trends via high-yield vs investment-grade ETFs
4. Check correlation patterns during different economic regimes

## 8. Getting Help

If you encounter issues or have questions:

1. **Check the Troubleshooting section** in INSTALLATION.md
2. **Review the source code** - the project is designed to be readable and well-documented
3. **Look at the test suite** in the `tests/` directory for usage examples
4. **Consult the Financial Methodology documentation** for details on calculations
5. **Create an issue** on the GitHub repository (if applicable)

Remember: This project is intended for educational and research purposes. Past performance does not guarantee future results, and all investments carry risk.