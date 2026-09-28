"""
Database operations for the finance analytics project.
"""

from datetime import date, timedelta
from sqlalchemy import text
from .connection import get_engine
from .schema import initialize_database_schema


def get_latest_dates(tickers):
    """
    Return the latest date currently stored for each ticker.

    A single SQL query is used rather than one query per ticker.

    Args:
        tickers (list): List of ticker symbols

    Returns:
        dict: Mapping of ticker to latest date (date object or None)
    """
    engine = get_engine()

    query = text("""
        SELECT
            ticker,
            MAX(date) AS latest_date
        FROM prices
        WHERE ticker IN :tickers
        GROUP BY ticker;
    """)

    with engine.connect() as conn:

        result = conn.execute(
            query,
            {
                "tickers": tuple(tickers)
            },
        )

        return {
            row.ticker: row.latest_date
            for row in result
        }


def determine_download_start(tickers, start_date, overlap_days):
    """
    Determine when Yahoo Finance data should be downloaded.

    First run:
        START_DATE

    Subsequent runs:
        Earliest existing ticker date minus OVERLAP_DAYS.

    The overlap allows recent historical data to be refreshed.

    Args:
        tickers (list): List of ticker symbols
        start_date (str): Earliest date for full historical download (YYYY-MM-DD)
        overlap_days (int): Number of days to overlap for incremental downloads

    Returns:
        str: Download start date in YYYY-MM-DD format
    """
    latest_dates = get_latest_dates(tickers)

    missing_tickers = [
        ticker
        for ticker in tickers
        if ticker not in latest_dates
        or latest_dates[ticker] is None
    ]

    # -----------------------------------------------------
    # First-run / missing ticker mode.
    # -----------------------------------------------------

    if missing_tickers:

        print(
            f"No existing data for "
            f"{len(missing_tickers)} ticker(s)."
        )

        if len(missing_tickers) <= 20:

            print(
                "Missing tickers: "
                + ", ".join(missing_tickers)
            )

        print(
            f"Full download starting "
            f"from {start_date}."
        )

        return start_date

    # -----------------------------------------------------
    # Incremental mode.
    # -----------------------------------------------------

    earliest_latest_date = min(
        latest_dates.values()
    )

    download_start_date = (
        earliest_latest_date
        - timedelta(days=overlap_days)
    )

    # Never go before the configured historical start.

    download_start_date = max(
        download_start_date,
        date.fromisoformat(start_date),
    )

    print(
        f"Earliest stored ticker date: "
        f"{earliest_latest_date}"
    )

    print(
        f"Refreshing the previous "
        f"{overlap_days} days."
    )

    return download_start_date.strftime("%Y-%m-%d")


def get_download_end():
    """
    Return the exclusive end date for yfinance.

    Yesterday is used so that today's potentially incomplete
    trading session is not stored as a completed daily bar.

    Returns:
        str: Download end date in YYYY-MM-DD format
    """
    yesterday = (
        date.today() - timedelta(days=1)
    )

    return yesterday.strftime("%Y-%m-%d")


def needs_download(download_start, download_end):
    """
    Check whether data needs downloading based on date range.

    Args:
        download_start (str): Start date in YYYY-MM-DD format
        download_end (str): End date in YYYY-MM-DD format (exclusive)

    Returns:
        bool: True if data needs downloading, False otherwise
    """
    return date.fromisoformat(download_start) < date.fromisoformat(download_end)


def upsert_prices(records):
    """
    UPSERT price records into the PostgreSQL database.

    Existing rows are UPDATED rather than ignored.
    This matters because Yahoo may revise historical data,
    particularly adjusted prices after corporate-action
    information changes.

    Args:
        records (list): List of dictionaries containing price data
    """
    engine = get_engine()

    insert_sql = text("""
    INSERT INTO prices (
        date,
        ticker,

        open,
        high,
        low,
        close,

        adj_open,
        adj_high,
        adj_low,
        adj_close,

        volume
    )
    VALUES (
        :date,
        :ticker,

        :open,
        :high,
        :low,
        :close,

        :adj_open,
        :adj_high,
        :adj_low,
        :adj_close,

        :volume
    )

    ON CONFLICT (date, ticker)
    DO UPDATE SET

        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,

        adj_open = EXCLUDED.adj_open,
        adj_high = EXCLUDED.adj_high,
        adj_low = EXCLUDED.adj_low,
        adj_close = EXCLUDED.adj_close,

        volume = EXCLUDED.volume;

    """)

    with engine.begin() as conn:
        conn.execute(insert_sql, records)