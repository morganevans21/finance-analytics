# Data Model

## Overview

This document describes the data model used by the ETF Analytics Project, focusing on the PostgreSQL database schema and how data flows through the system.

## Core Table: prices

The central table in the data model is the `prices` table, which stores OHLCV (Open, High, Low, Close, Volume) data for ETF tickers.

### Table Definition

```sql
CREATE TABLE prices (
    date DATE NOT NULL,
    ticker VARCHAR(20) NOT NULL,

    -- Raw market prices
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,

    -- Corporate-action-adjusted prices
    adj_open DOUBLE PRECISION,
    adj_high DOUBLE PRECISION,
    adj_low DOUBLE PRECISION,
    adj_close DOUBLE PRECISION,

    -- Unadjusted trading volume
    volume BIGINT,

    PRIMARY KEY (date, ticker)
);
```

### Column Descriptions

| Column Name | Data Type | Description | Constraints |
|-------------|-----------|-------------|-------------|
| `date` | DATE | Trading date | PART OF PRIMARY KEY |
| `ticker` | VARCHAR(20) | ETF ticker symbol | PART OF PRIMARY KEY |
| `open` | DOUBLE PRECISION | Raw opening price | NULLABLE |
| `high` | DOUBLE PRECISION | Raw highest price | NULLABLE |
| `low` | DOUBLE PRECISION | Raw lowest price | NULLABLE |
| `close` | DOUBLE PRECISION | Raw closing price | NULLABLE |
| `adj_open` | DOUBLE PRECISION | Adjusted opening price | NULLABLE |
| `adj_high` | DOUBLE PRECISION | Adjusted highest price | NULLABLE |
| `adj_low` | DOUBLE PRECISION | Adjusted lowest price | NULLABLE |
| `adj_close` | DOUBLE PRECISION | Adjusted closing price | NULLABLE |
| `volume` | BIGINT | Trading volume (unadjusted) | NULLABLE |

### Key Design Points

1. **Composite Primary Key**: The combination of `date` and `ticker` forms the primary key, ensuring:
   - Only one record per ticker per trading day
   - Prevention of duplicate data entries
   - Efficient querying by ticker and date range

2. **Raw vs Adjusted Prices**: 
   - Raw prices reflect actual market prices on the trading day
   - Adjusted prices are adjusted by Yahoo Finance for corporate actions (dividends, splits)
   - Important: Do NOT apply additional adjustments to the adj_* columns as they are already adjusted

3. **Volume Storage**:
   - Volume is stored as unadjusted (raw) volume
   - Volume is not adjusted for splits/dividends in the same way prices are

4. **Data Types**:
   - DATE: Efficient storage for calendar dates
   - VARCHAR(20): Sufficient for ticker symbols (including exchange suffixes like .L)
   - DOUBLE PRECISION: 64-bit floating point for price precision
   - BIGINT: 64-bit integer for volume (can handle large volume numbers)

## Data Flow

### 1. Ingestion Pipeline

```
Yahoo Finance API → Raw Data → Validation & Cleaning → PostgreSQL prices table
```

#### Stages:
1. **Download**: Raw OHLCV and adjusted OHLC data downloaded via yfinance
2. **Normalization**: Convert to consistent format, handle missing values
3. **Cleaning**: Remove invalid rows, handle data anomalies
4. **Validation**: Ensure data quality (OHLC relationships, reasonable values)
5. **Storage**: UPSERT into prices table (INSERT ... ON CONFLICT DO UPDATE)

### 2. Data Transformation for Analytics

When data is retrieved for analysis, it typically undergoes these transformations:

```
PostgreSQL prices table → Pandas DataFrame → Calculated Metrics → Visualization/Reporting
```

#### Common Transformations:
1. **Price Selection**: Choose between raw or adjusted close based on analysis type
2. **Return Calculation**: Convert prices to returns (simple or log)
3. **Date Handling**: Ensure proper datetime indexing and sorting
4. **Ticker Grouping**: Operations typically grouped by ticker symbol
5. **Missing Data Handling**: Decide on forward-fill, drop, or interpolation strategy

## Schema Evolution

The schema is managed by the `initialize_database_schema()` function in `src/finance_analytics/database/schema.py`. This function:

1. Checks if the `prices` table exists
2. If not, creates it with the full schema defined above
3. If it exists, compares against expected schema and adds any missing columns
4. Ensures the primary key constraint exists

This approach allows for:
- Safe initialization on new installations
- Non-disruptive schema updates when new columns are needed
- Backward compatibility with existing data

### Example Schema Change Process

If a new column were needed (e.g., dividends):

1. Add column definition to expected_columns in schema.py
2. The initialize_database_schema() function would:
   - Detect missing column on existing installations
   - Execute: ALTER TABLE prices ADD COLUMN dividends DOUBLE PRECISION;
   - Preserve all existing data
3. Update ingestion pipeline to populate the new column
4. Update analytics functions to utilize the new column if appropriate

## Indexing Strategy

### Primary Index
- **PRIMARY KEY (date, ticker)**: Automatically created with the table
- Supports efficient:
  - Lookups by specific ticker and date
  - Range scans for a ticker over time
  - Equality checks on the composite key

### Potential Additional Indexes

While the primary key covers most use cases, these additional indexes might be beneficial for specific query patterns:

```sql
-- For scanning all tickers on a specific date (less common)
CREATE INDEX idx_prices_date ON prices(date);

-- For scanning a ticker across all dates (covered by PK but might help some planners)
CREATE INDEX idx_prices_ticker ON prices(ticker);

-- For volume-based queries
CREATE INDEX idx_prices_volume ON prices(volume) WHERE volume IS NOT NULL;
```

Current usage patterns show most queries filter by ticker and date range, which the primary key handles efficiently.

## Constraints and Data Quality

### Database-Level Constraints

Currently implemented:
- **Primary Key Constraint**: Prevents duplicate (ticker, date) combinations
- **Nullable Columns**: All price and volume columns allow NULL to handle missing data

### Application-Level Validation

The application enforces additional data quality checks:

#### OHLC Relationship Validation
For raw prices (when all values present):
- `high >= max(open, close, low)`
- `low <= min(open, close, high)`

Similar relationships are validated for adjusted prices.

### Value Range Validation
- Prices: Should be positive (though theoretically could be negative in extreme scenarios)
- Volume: Should be non-negative
- Dates: Should be valid trading dates (weekdays, not exchange holidays)

## Data Characteristics

### Temporal Aspects
- **Frequency**: Daily data (trading days only)
- **Gaps**: Missing data for weekends, holidays, and non-trading days
- **Alignment**: Different tickers may have different trading calendars (especially international ETFs)
- **Adjustment Timing**: Adjusted prices reflect corporate actions on their effective dates

### Cross-Sectional Aspects
- **Currency**: Prices are in the trading currency of the listing (e.g., GBP for LSE-listed ETFs)
- **Exchange**: Ticker symbols include exchange identifiers (e.g., .L for London Stock Exchange)
- **Settlement**: Prices reflect closing auction prices where applicable

## Usage Patterns

### Common Queries

#### 1. Price Retrieval for Analysis
```sql
SELECT date, ticker, close
FROM prices
WHERE ticker = 'SPY'
  AND date >= '2023-01-01'
  AND date <= '2023-12-31'
ORDER BY date;
```

#### 2. Multi-Ticker Comparison
```sql
SELECT date,
       MAX(CASE WHEN ticker = 'SPY' THEN close END) AS spy_close,
       MAX(CASE WHEN ticker = 'QQQ' THEN close END) AS qqq_close
FROM prices
WHERE ticker IN ('SPY', 'QQQ')
  AND date >= '2023-01-01'
GROUP BY date
HAVING COUNT(DISTINCT ticker) = 2  -- Ensure both tickers have data
ORDER BY date;
```

#### 3. Statistical Aggregates
```sql
SELECT 
    ticker,
    COUNT(*) as trading_days,
    AVG(close) as avg_price,
    STDDEV(close) as price_stddev,
    MIN(date) as first_date,
    MAX(date) as last_date
FROM prices
WHERE date >= '2020-01-01'
GROUP BY ticker
ORDER BY ticker;
```

#### 4. Data Completeness Check
```sql
SELECT 
    ticker,
    COUNT(*) as actual_days,
    (MAX(date) - MIN(date)) as date_range,
    ROUND(100.0 * COUNT(*) / (MAX(date) - MIN(date) + 1), 2) as pct_complete
FROM prices
GROUP BY ticker
HAVING MAX(date) >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY pct_complete;
```

## Integration with Analytics Functions

The analytics functions in `src/finance_analytics/analytics/` expect data in specific formats:

### Expected Input Format
Most analytics functions accept pandas Series or DataFrames with:
- **Index**: DatetimeIndex for time series operations
- **Columns**: Standardized naming (e.g., 'close', 'simple_return')
- **Grouping**: Operations typically performed within ticker groups

### Example: Data Preparation for Analytics
```python
import pandas as pd
from sqlalchemy import create_engine

# Load data from PostgreSQL
engine = create_engine(DATABASE_URL)
query = """
SELECT date, ticker, adj_close as close
FROM prices
WHERE ticker IN ('SPY', 'QQQ')
  AND date >= '2023-01-01'
ORDER BY date, ticker;
"""
df = pd.read_sql(query, engine)
df['date'] = pd.to_datetime(df['date'])

# Prepare for analytics: set multi-index and sort
df = df.set_index(['ticker', 'date']).sort_index()

# Example: Calculate returns for each ticker
returns = df.groupby(level='ticker')['close'].transform(simple_returns)

# Example: Calculate volatility for each ticker
volatility = df.groupby(level='ticker')['close'].transform(
    lambda x: rolling_volatility(simple_returns(x), window=30)
)
```

## Extending the Data Model

### Adding New Columns

To add new data fields (e.g., fundamentals, ESG scores, etc.):

1. **Update schema.py**: Add column to expected_columns dictionary
2. **Modify ingestion**: Update update_database.py to download and store new data
3. **Update analytics**: Add functions to utilize new data if appropriate
4. **Update dashboard**: Modify streamlit_app.py to display new metrics
5. **Schema migration**: The initialize_database_schema() function will handle adding columns to existing installations

### Example: Adding Dividend Data

```python
# In schema.py expected_columns:
"dividends": "DOUBLE PRECISION",  # Cash dividends per share

# In update_database.py:
# 1. Download dividend data via yfinance
# 2. Include in normalization and merging steps
# 3. Add to final records for UPSERT

# In analytics:
# Functions like dividend_yield, dividend_growth, etc.

# In dashboard:
# New section for dividend analysis
```

## Relationship to Other Components

### Connection to ETF Universe
The `ticker` values in the prices table correspond to the `yahoo_ticker` field in the ETF universe definitions (`src/finance_analytics/universe/etfs.py`), with the exchange suffix (e.g., .L for LSE).

### Connection to Analytics Layer
All analytics functions operate on data extracted from the prices table, transforming it as needed for specific calculations.

### Connection to Presentation Layer
The Streamlit app retrieves data from the prices table using SQL queries, then applies the same analytics functions used elsewhere in the codebase for consistency.

## Backup and Recovery

### Backup Strategy
- **Logical Backup**: Use pg_dump for schema and data
  ```bash
  pg_dump -U $DB_USER -d $DB_NAME -f finance_db_backup.sql
  ```
- **Point-in-Time Recovery**: Enable WAL archiving for PostgreSQL
- **Snapshot Backup**: For cloud providers, use snapshot/backup features

### Recovery Procedures
1. **Schema Recovery**: The initialize_database_schema() function can recreate the table structure
2. **Data Recovery**: Reload from Yahoo Finance using update_database.py (may take significant time for full history)
3. **Hybrid Approach**: Restore schema and recent data from backup, fill older data from Yahoo

## Performance Considerations

### Storage Requirements
Approximate storage for 100 ETFs with 15 years of daily data:
- Rows: 100 tickers × 252 trading days/year × 15 years = 378,000 rows
- Size per row: ~200 bytes (estimated)
- Total size: ~75 MB (plus indexes and overhead)

### Query Performance
The primary key index provides excellent performance for:
- Single ticker date range scans: O(log n) + k where k is number of matching rows
- Latest date lookups: Efficient via index on (ticker, date DESC)
- Aggregations by ticker: Can leverage index for grouping

### Maintenance Tasks
- **Vacuuming**: Regular VACUUM/ANALYZE to maintain query planner statistics
- **Index Rebuilding**: Rarely needed with the current access pattern
- **Partitioning Consideration**: For much larger datasets (>10M rows), consider partitioning by date range

## Data Dictionary

### Sample Data

| date | ticker | open | high | low | close | adj_open | adj_high | adj_low | adj_close | volume |
|------|--------|------|------|-----|-------|----------|----------|---------|-----------|--------|
| 2023-01-03 | SPY | 375.50 | 378.25 | 374.80 | 377.45 | 375.50 | 378.25 | 374.80 | 377.45 | 45678900 |
| 2023-01-03 | QQQ | 298.50 | 301.20 | 297.80 | 300.40 | 298.50 | 301.20 | 297.80 | 300.40 | 25678900 |
| 2023-01-04 | SPY | 377.45 | 380.10 | 376.90 | 379.20 | 377.45 | 380.10 | 376.90 | 379.20 | 38945600 |

### Value Ranges (Typical)
- **Prices**: $0.01 - $1000+ (varies widely by ETF)
- **Volume**: 0 - 100M+ shares (highly variable by ticker and day)
- **Returns**: Typically -0.20 to +0.20 daily (-20% to +20%), extreme moves beyond ±0.50 rare
- **Volatility**: Annualized typically 0.10-0.80 (10%-80%) for most ETFs

## Limitations and Assumptions

### Known Limitations
1. **Currency Handling**: Prices are stored in trading currency; no automatic conversion to base currency
2. **Exchange Holidays**: Calendar differences between exchanges not automatically handled
3. **Data Source Reliance**: Reliance on Yahoo Finance data quality and availability
4. **Adjustment Methodology**: Uses Yahoo's adjustment methodology without verification
5. **Intraday Data**: Only daily data; no intraday or tick data storage

### Assumptions Made
1. **Date Uniqueness**: Assumes one trading record per ticker per date (valid for daily data)
2. **Price Validity**: Assumes prices are valid numeric values when not NULL
3. **Volume Non-Negativity**: Assumes volume is never negative
4. **Chronological Order**: Assumes dates are chronological when sorted
5. **Ticker Consistency**: Assumes ticker symbols remain constant over time (does not handle ticker changes)

## Future Enhancements

### Potential Model Extensions
1. **Separate Tables**: Split raw and adjusted prices into separate tables for different retention policies
2. **TimescaleDB**: Migrate to TimescaleDB for better time-series performance at scale
3. **Columnar Storage**: Consider columnar formats for analytical workloads
4. **Event Tracking**: Add tables for corporate actions (splits, dividends) with explicit effective dates
5. **Data Provenance**: Track source and timestamp for each data point to handle revisions

### Indexing Improvements
1. **BRIN Indexes**: For very large date ranges, consider Block Range Indexes on date column
2. **Composite Indexes**: Additional indexes for common query patterns
3. **Covering Indexes**: Indexes that include all columns needed for common queries to avoid heap access

## Security Considerations

### Data Sensitivity
- Market data is generally considered public information
- No personally identifiable information (PII) stored in the prices table
- Volume data could potentially reveal trading patterns for very large positions

### Access Controls
- Database credentials should follow least-privilege principle
- Consider read-only users for dashboard/applications that only need to query data
- Separate users for ingestion (needs INSERT/UPDATE) vs reporting (needs only SELECT)

### Compliance
- GDPR: No personal data stored, so minimal impact
- SOC 2: Standard database security controls apply
- ISO 27001: Standard infosec practices for database administration