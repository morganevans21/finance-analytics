"""
update_database.py

Updates the PostgreSQL 'prices' table with raw and adjusted
daily OHLCV data.

Features:

    Full history on first run
    Incremental updates on later runs
    Re-downloads a rolling overlap window
    Stores BOTH raw and adjusted OHLC prices
    Stores unadjusted trading volume
    UPSERTs existing rows so corrected Yahoo data is captured
    One SQL query determines existing database coverage
    Supports single or multiple ETF tickers
    Safe against duplicate (date, ticker) rows

Database columns:
date
ticker

open
high
low
close

adj_open
adj_high
adj_low
adj_close

volume

Definitions:
open/high/low/close
    Raw historical market prices as supplied by Yahoo Finance.

adj_open/adj_high/adj_low/adj_close
    Corporate-action-adjusted prices supplied by Yahoo Finance.

volume
    Unadjusted trading volume.

IMPORTANT:
Do NOT apply another dividend or split adjustment to the
adj_* columns. They are already adjusted by yfinance.
"""

# =========================================================
# 1. IMPORT ETF UNIVERSE
# =========================================================

import sys
import os

# Add the src directory to the Python path so that we can
# import from finance_analytics.

sys.path.append(
    os.path.join(os.path.dirname(__file__), "src")
)

from finance_analytics.config import get_tickers_with_fallback

# =========================================================
# 2. CONFIGURATION
# =========================================================

from finance_analytics.config import load_config

config = load_config()

START_DATE = config["START_DATE"]
OVERLAP_DAYS = config["OVERLAP_DAYS"]
YFINANCE_PROGRESS = config["YFINANCE_PROGRESS"]

# =========================================================
# 3. GET ETF TICKERS
# =========================================================

TICKERS = get_tickers_with_fallback()

# =========================================================
# 4. CONNECT TO POSTGRESQL
# =========================================================

from finance_analytics.database.connection import get_engine
from finance_analytics.database.schema import initialize_database_schema

engine = get_engine()

print("Connected to PostgreSQL.")

# =========================================================
# 5. INITIALIZE / UPDATE DATABASE SCHEMA
# =========================================================

initialize_database_schema()

# =========================================================
# 6. GET EXISTING DATA COVERAGE
# =========================================================

from finance_analytics.database.operations import get_latest_dates

# =========================================================
# 7. DETERMINE DOWNLOAD START DATE
# =========================================================

from finance_analytics.database.operations import determine_download_start

# =========================================================
# 8. DETERMINE DOWNLOAD END DATE
# =========================================================

from finance_analytics.database.operations import get_download_end

# =========================================================
# 9. CHECK WHETHER DATA NEEDS DOWNLOADING
# =========================================================

from finance_analytics.database.operations import needs_download

download_start = determine_download_start(TICKERS, START_DATE, OVERLAP_DAYS)
download_end = get_download_end()

print()
print(
    f"Download range: "
    f"{download_start} -> {download_end}"
)
print("(End date is exclusive.)")

if not needs_download(download_start, download_end):
    print()
    print("Database is already up to date.")
    raise SystemExit(0)

# =========================================================
# 10. DOWNLOAD RAW DATA
# =========================================================

from finance_analytics.ingestion.download import download_raw_data

print()
print(
    f"Downloading RAW OHLCV data "
    f"for {len(TICKERS)} ticker(s)..."
)

raw_data = download_raw_data(
    TICKERS,
    download_start,
    download_end,
    progress=YFINANCE_PROGRESS,
)

# =========================================================
# 11. DOWNLOAD ADJUSTED DATA
# =========================================================

from finance_analytics.ingestion.download import download_adjusted_data

print()
print(
    f"Downloading ADJUSTED OHLC data "
    f"for {len(TICKERS)} ticker(s)..."
)

adjusted_data = download_adjusted_data(
    TICKERS,
    download_start,
    download_end,
    progress=YFINANCE_PROGRESS,
)

# =========================================================
# 12. CHECK DOWNLOAD RESULTS
# =========================================================

if raw_data is None or raw_data.empty:
    print()
    print("Yahoo returned no raw data.")
    raise SystemExit(0)

if adjusted_data is None or adjusted_data.empty:
    print()
    print("Yahoo returned no adjusted data.")
    raise SystemExit(0)

# =========================================================
# 13. NORMALIZE RAW DATA
# =========================================================

from finance_analytics.ingestion.normalization import normalize_yfinance_data

raw_ohlcv = normalize_yfinance_data(
    raw_data,
    TICKERS,
    include_volume=True,
)

adjusted_ohlc = normalize_yfinance_data(
    adjusted_data,
    TICKERS,
    include_volume=False,
)

# =========================================================
# 14. RENAME RAW COLUMNS
# =========================================================

from finance_analytics.ingestion.merging import rename_columns

raw_ohlcv, adjusted_ohlc = rename_columns(raw_ohlcv, adjusted_ohlc)

# =========================================================
# 15. KEEP ONLY REQUIRED COLUMNS
# =========================================================

from finance_analytics.ingestion.merging import select_required_columns

raw_ohlcv, adjusted_ohlc = select_required_columns(raw_ohlcv, adjusted_ohlc)

# =========================================================
# 16. CLEAN RAW DATA
# =========================================================

from finance_analytics.validation.cleaning import clean_data

raw_ohlcv, adjusted_ohlc = clean_data(raw_ohlcv, adjusted_ohlc)

# =========================================================
# 17. CLEAN ADJUSTED DATA
# =========================================================

# (Already handled in clean_data function)

# =========================================================
# 18. NORMALIZE DATES
# =========================================================

from finance_analytics.validation.normalization import normalize_dates

raw_ohlcv = normalize_dates(raw_ohlcv)
adjusted_ohlc = normalize_dates(adjusted_ohlc)

# =========================================================
# 19. NORMALIZE TICKERS
# =========================================================

from finance_analytics.validation.normalization import normalize_tickers

raw_ohlcv = normalize_tickers(raw_ohlcv)
adjusted_ohlc = normalize_tickers(adjusted_ohlc)

# =========================================================
# 20. NORMALIZE NUMERIC COLUMNS
# =========================================================

from finance_analytics.validation.normalization import normalize_numeric_columns

raw_ohlcv = normalize_numeric_columns(raw_ohlcv)
adjusted_ohlc = normalize_numeric_columns(adjusted_ohlc)

# =========================================================
# 21. MERGE RAW + ADJUSTED DATA
# =========================================================

from finance_analytics.ingestion.merging import merge_raw_adjusted

ohlcv_data = merge_raw_adjusted(raw_ohlcv, adjusted_ohlc)

# =========================================================
# 22. REMOVE INVALID ROWS
# =========================================================

from finance_analytics.validation.cleaning import remove_invalid_rows

ohlcv_data = remove_invalid_rows(ohlcv_data)

# =========================================================
# 23. REMOVE DUPLICATES
# =========================================================

from finance_analytics.validation.cleaning import remove_duplicates

ohlcv_data = remove_duplicates(ohlcv_data)

# =========================================================
# 24. SORT DATA
# =========================================================

ohlcv_data.sort_values(
    [
        "Ticker",
        "Date",
    ],
    inplace=True,
)

# =========================================================
# 25. CHECK RESULT
# =========================================================

from finance_analytics.validation.validation import validate_data

if not validate_data(ohlcv_data):
    print()
    print(
        "No usable OHLCV rows were returned."
    )
    raise SystemExit(0)

print()
print(
    f"Prepared {len(ohlcv_data):,} "
    "rows for PostgreSQL."
)

print()
print("Sample:")
print(
    ohlcv_data.head(10).to_string(
        index=False
    )
)

# =========================================================
# 26. PREPARE DATABASE RECORDS
# =========================================================

from finance_analytics.validation.validation import prepare_database_records

records = prepare_database_records(ohlcv_data)

# =========================================================
# 27. UPSERT INTO POSTGRESQL
# =========================================================

from finance_analytics.database.operations import upsert_prices

# =========================================================
# 28. WRITE TO DATABASE
# =========================================================

print()
print(
    "Writing data to PostgreSQL..."
)

upsert_prices(records)

# =========================================================
# 29. FINAL REPORT
# =========================================================

unique_tickers = (
    ohlcv_data["Ticker"]
    .nunique()
)

min_date = ohlcv_data["Date"].min()
max_date = ohlcv_data["Date"].max()

print()
print("=" * 60)
print("DATABASE UPDATE COMPLETE")
print("=" * 60)

print(
    f"Rows processed: {len(records):,}"
)

print(
    f"Tickers processed: {unique_tickers:,}"
)

print(
    f"Data range: {min_date} -> {max_date}"
)

print(
    f"Overlap window: {OVERLAP_DAYS} days"
)

print(
    "Raw prices: STORED"
)

print(
    "Adjusted prices: STORED"
)

print(
    "Volume: UNADJUSTED"
)

print(
    "Existing rows: UPSERTED"
)

print("=" * 60)
print()