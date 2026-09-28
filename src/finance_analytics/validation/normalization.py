"""
Data normalization functionality for the finance analytics project.
"""

import pandas as pd


def normalize_dates(ohlcv_data):
    """
    Normalize date columns to date objects.

    Args:
        ohlcv_data (pandas.DataFrame): OHLCV data with Date column

    Returns:
        pandas.DataFrame: OHLCV data with normalized Date column
    """
    ohlcv_data_norm = ohlcv_data.copy()
    ohlcv_data_norm["Date"] = (
        pd.to_datetime(
            ohlcv_data_norm["Date"]
        ).dt.date
    )

    return ohlcv_data_norm


def normalize_tickers(ohlcv_data):
    """
    Normalize ticker strings to uppercase.

    Args:
        ohlcv_data (pandas.DataFrame): OHLCV data with Ticker column

    Returns:
        pandas.DataFrame: OHLCV data with normalized Ticker column
    """
    ohlcv_data_norm = ohlcv_data.copy()
    ohlcv_data_norm["Ticker"] = (
        ohlcv_data_norm["Ticker"]
        .astype(str)
        .str.upper()
    )

    return ohlcv_data_norm


def normalize_numeric_columns(ohlcv_data):
    """
    Normalize numeric columns to appropriate types.

    Args:
        ohlcv_data (pandas.DataFrame): OHLCV data with price and volume columns

    Returns:
        pandas.DataFrame: OHLCV data with normalized numeric columns
    """
    ohlcv_data_norm = ohlcv_data.copy()

    raw_price_columns = [
        "open",
        "high",
        "low",
        "close",
    ]

    adjusted_price_columns = [
        "adj_open",
        "adj_high",
        "adj_low",
        "adj_close",
    ]

    for column in raw_price_columns:
        ohlcv_data_norm[column] = pd.to_numeric(
            ohlcv_data_norm[column],
            errors="coerce",
        )

    for column in adjusted_price_columns:
        ohlcv_data_norm[column] = pd.to_numeric(
            ohlcv_data_norm[column],
            errors="coerce",
        )

    # Volume is deliberately nullable.
    # We do NOT convert missing volume into zero because:
    # NULL = volume unavailable/unknown
    # 0 = confirmed zero volume
    ohlcv_data_norm["volume"] = pd.to_numeric(
        ohlcv_data_norm["volume"],
        errors="coerce",
    ).astype("Int64")

    return ohlcv_data_norm