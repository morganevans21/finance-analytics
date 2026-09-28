-- Initial schema for the ETF Analytics Project prices table
-- This SQL represents the initial state of the database schema.
-- In the current implementation, schema management is handled by
-- src/finance_analytics/database/schema.py initialize_database_schema() function.

-- Create prices table
CREATE TABLE IF NOT EXISTS prices (
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

-- Comment on table and columns for documentation
COMMENT ON TABLE prices IS 'Stores OHLCV data for ETF tickers with both raw and adjusted prices';

COMMENT ON COLUMN prices.date IS 'Trading date';
COMMENT ON COLUMN prices.ticker IS 'ETF ticker symbol (with exchange suffix if applicable)';

COMMENT ON COLUMN prices.open IS 'Raw opening price';
COMMENT ON COLUMN prices.high IS 'Raw highest price';
COMMENT ON COLUMN prices.low IS 'Raw lowest price';
COMMENT ON COLUMN prices.close IS 'Raw closing price';

COMMENT ON COLUMN prices.adj_open IS 'Adjusted opening price (adjusted for dividends/splits by Yahoo Finance)';
COMMENT ON COLUMN prices.adj_high IS 'Adjusted highest price';
COMMENT ON COLUMN prices.adj_low IS 'Adjusted lowest price';
COMMENT ON COLUMN prices.adj_close IS 'Adjusted closing price';

COMMENT ON COLUMN prices.volume IS 'Unadjusted trading volume';

-- Indexes
-- The primary key (date, ticker) provides efficient lookup by ticker and date range
-- Additional indexes may be added based on query patterns