"""
update_database.py
-------------------
Updates the PostgreSQL 'prices' table with:
- Full history on first run
- Incremental updates on later runs

Tickers: SPY, QQQ
Start date: 2015-01-01
"""

import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# ---------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------

TICKERS = ["SPY", "QQQ"]
START_DATE = "2015-01-01"

# Load environment variables from .env file
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ---------------------------------------------------------
# 2. CONNECT TO DATABASE
# ---------------------------------------------------------

engine = create_engine(DATABASE_URL)
print("Connected to PostgreSQL.")

# ---------------------------------------------------------
# 3. DETERMINE WHAT DATES NEED TO BE DOWNLOADED
# ---------------------------------------------------------

def get_last_date_in_db(ticker):
    """Return the max(date) in SQL for a given ticker."""
    query = text("""
        SELECT MAX(date) 
        FROM prices
        WHERE ticker = :ticker;
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"ticker": ticker}).scalar()
        return result  # datetime.date or None


def determine_download_range():
    """Determine start date for download (incremental)."""
    latest_dates = []

    for ticker in TICKERS:
        last_date = get_last_date_in_db(ticker)
        if last_date is None:
            print(f"No data found for {ticker} — full download will be used.")
            return START_DATE  # full-history mode
        else:
            latest_dates.append(last_date)

    # Incremental: earliest missing day across all tickers
    next_date = min(latest_dates) + timedelta(days=1)
    return next_date.strftime("%Y-%m-%d")


download_start = determine_download_range()
download_end = datetime.today().strftime("%Y-%m-%d")

print(f"\nDownloading price data from {download_start} to {download_end} ...")

if download_start > download_end:
    print("\nDatabase already fully up to date. No download needed.\n")
    exit()

# ---------------------------------------------------------
# 4. DOWNLOAD DATA FROM YAHOO FINANCE
# ---------------------------------------------------------

data = yf.download(
    TICKERS,
    start=download_start,
    end=download_end,
    auto_adjust=True
)

price_data = data["Close"].reset_index()
price_data = price_data.melt(
    id_vars="Date",
    var_name="Ticker",
    value_name="Close"
)

# remove rows with NaN (weekends/holidays)
price_data.dropna(subset=["Close"], inplace=True)

print(f"\nDownloaded {len(price_data)} rows.")
print(price_data.head())

# ---------------------------------------------------------
# 5. INSERT INTO POSTGRESQL (DUPLICATE SAFE)
# ---------------------------------------------------------

with engine.connect() as conn:
    # PostgreSQL UPSERT
    insert_sql = text("""
        INSERT INTO prices (date, ticker, close)
        VALUES (:date, :ticker, :close)
        ON CONFLICT (date, ticker) DO NOTHING;
    """)

    rows_inserted = 0

    for _, row in price_data.iterrows():
        result = conn.execute(insert_sql, {
            "date": row["Date"],
            "ticker": row["Ticker"],
            "close": row["Close"],
        })
        rows_inserted += result.rowcount

    conn.commit()

print(f"\nINSERT COMPLETE — {rows_inserted} new rows added.")
print("Database update finished successfully.\n")
