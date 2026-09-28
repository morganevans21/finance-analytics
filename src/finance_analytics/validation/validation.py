"""
Data validation functionality for the finance analytics project.
"""

import pandas as pd


def validate_data(ohlcv_data):
    """
    Validate that OHLCV data is usable for database storage.

    Args:
        ohlcv_data (pandas.DataFrame): OHLCV data to validate

    Returns:
        bool: True if data is valid, False otherwise
    """
    if ohlcv_data.empty:
        return False

    return True


def prepare_database_records(ohlcv_data):
    """
    Prepare OHLCV data for insertion into the database.

    Args:
        ohlcv_data (pandas.DataFrame): Validated OHLCV data

    Returns:
        list: List of dictionaries ready for database insertion
    """
    records = []

    for row in ohlcv_data.itertuples(index=False):
        # Nullable volume:
        # pandas NA -> Python None
        if pd.isna(row.volume):
            volume = None
        else:
            volume = int(row.volume)

        records.append(
            {
                "date": row.Date,
                "ticker": row.Ticker,

                # Raw prices
                "open": float(row.open),
                "high": float(row.high),
                "low": float(row.low),
                "close": float(row.close),

                # Adjusted prices
                "adj_open": float(
                    row.adj_open
                ),
                "adj_high": float(
                    row.adj_high
                ),
                "adj_low": float(
                    row.adj_low
                ),
                "adj_close": float(
                    row.adj_close
                ),

                # Volume
                "volume": volume,
            }
        )

    return records