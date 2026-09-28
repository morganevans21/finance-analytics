# System Architecture

## Overview

The ETF Analytics Project follows a modular architecture that separates concerns across data acquisition, storage, analytics, and presentation layers.

## Architectural Layers

### 1. Data Acquisition Layer
- **Source**: Yahoo Finance via yfinance library
- **Function**: `update_database.py` script
- **Features**:
  - Full historical download on first run
  - Incremental updates with overlap window on subsequent runs
  - Downloads both raw and adjusted OHLC prices
  - UPSERT behavior to capture data corrections from Yahoo
  - Error handling for failed ticker downloads

### 2. Data Storage Layer
- **Technology**: PostgreSQL database
- **Table**: `prices` table with schema:
  - `date` (DATE)
  - `ticker` (VARCHAR)
  - Raw OHLC: `open`, `high`, `low`, `close`
  - Adjusted OHLC: `adj_open`, `adj_high`, `adj_low`, `adj_close`
  - `volume` (BIGINT)
  - Primary key: (`date`, `ticker`) to prevent duplicates
- **Access Layer**: SQLAlchemy 2.x with connection pooling

### 3. Analytics Layer
- **Location**: `src/finance_analytics/analytics/` package
- **Modules**:
  - `returns.py`: Simple/log returns, cumulative returns
  - `volatility.py`: Rolling volatility, annualized volatility, EWMA volatility
  - `drawdown.py`: Max drawdown, rolling drawdown, drawdown series
  - `risk_metrics.py`: VaR, CVaR, Sharpe ratio, Sortino ratio
  - `market_sensitivity.py`: Beta, alpha, correlation, rolling correlation
  - `utils.py`: Helper functions for annualization, validation, series alignment
- **Design**: Pure functions that operate on pandas Series/DataFrames
- **Reusability**: Used by both update_database.py and streamlit_app.py

### 4. Presentation Layer
- **Technology**: Streamlit
- **Location**: `app/streamlit_app.py`
- **Features**:
  - Interactive date range selection
  - Ticker selection from universe
  - Returns distribution and VaR/CVaR analysis
  - Rolling metrics (volatility, Sharpe ratio)
  - Rolling correlation analysis
  - Yearly volatility and max drawdowns
  - Simple linear regressions between ETFs
  - Holdings analysis (conditional on holdings table existence)

### 5. Configuration Layer
- **Method**: Environment variables via python-dotenv
- **Variables**:
  - Database connection: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
  - Data ingestion: START_DATE, OVERLAP_DAYS, YFINANCE_PROGRESS
  - ETF selection: ETF_TICKERS (defaults to SPY,QQQ)
- **File**: `.env` (not committed) with `.env.example` template

## Data Flow

```
External Market Data (Yahoo Finance)
                │
                ▼
        [update_database.py]
                │
                ▼
   PostgreSQL Database (prices table)
                │
                ▼
    [Analytics Functions] ◄───────┐
                │                 │
                ▼                 │
    [Streamlit Dashboard]         │
                ▲                 │
                └─────────────────┘
                    Configuration
```

## Key Design Decisions

### 1. Separation of Concerns
- Data acquisition is separate from analytics and presentation
- Analytics functions are pure and reusable across contexts
- Database access is encapsulated in connection and schema modules

### 2. Idempotent Operations
- The update process is designed to be idempotent
- Uses UPSERT (INSERT ... ON CONFLICT DO UPDATE) to handle data corrections
- Overlap window ensures recent data is refreshed to catch Yahoo revisions

### 3. Raw and Adjusted Price Storage
- Both raw and Yahoo-adjusted prices are stored to support different analysis types
- Adjusted prices are NOT to be further adjusted (per Yahoo documentation)

### 4. Extensible ETF Universe
- ETF definitions are centralized in `src/finance_analytics/universe/etfs.py`
- Easy to add/remove ETFs without modifying multiple files
- Rich metadata supports research rationale and role definition

### 5. Testability
- Analytics functions are pure and easily unit-testable
- Test fixtures and sample data support reproducible testing
- Clear separation enables mocking of external dependencies

## Scalability Considerations

### Current Design
- Handles approximately 100 ETFs with 15+ years of daily data
- Dataset size: ~100 tickers × 365 days/year × 15 years ≈ 550,000 rows
- Well within PostgreSQL capabilities for a single-table design

### Potential Bottlenecks
1. **Yahoo Finance API rate limits** - Mitigated by overlap window and caching
2. **Data download time** - Parallel downloading not currently implemented
3. **Analytics computation** - Vectorized pandas operations are efficient
4. **Dashboard rendering** - Plotly charts can become slow with very large datasets

### Scaling Options
- Add connection pooling and read replicas for heavy dashboard usage
- Implement data partitioning by date range in PostgreSQL
- Add Redis caching for frequently accessed computed metrics
- Implement background job queue for heavy computations