"""
Data cleaning functionality for the finance analytics project.
"""

import pandas as pd


def clean_data(raw_ohlcv, adjusted_ohlc):
    """
    Clean raw and adjusted data by removing rows with invalid prices.

    Args:
        raw_ohlcv (pandas.DataFrame): Normalized raw OHLCV data
        adjusted_ohlc (pandas.DataFrame): Normalized adjusted OHLC data

    Returns:
        tuple: (cleaned_raw_ohlcv, cleaned_adjusted_ohlc)
    """
    # Clean raw data - remove rows with invalid prices
    raw_ohlcv_clean = raw_ohlcv.copy()
    raw_ohlcv_clean.dropna(
        subset=[
            "open",
            "high",
            "low",
            "close",
        ],
        inplace=True,
    )

    # Clean adjusted data - remove rows with invalid prices
    adjusted_ohlc_clean = adjusted_ohlc.copy()
    adjusted_ohlc_clean.dropna(
        subset=[
            "adj_open",
            "adj_high",
            "adj_low",
            "adj_close",
        ],
        inplace=True,
    )

    return raw_ohlcv_clean, adjusted_ohlc_clean


def remove_invalid_rows(ohlcv_data):
    """
    Remove rows with invalid OHLC relationships or missing values.

    Args:
        ohlcv_data (pandas.DataFrame): Merged OHLCV data

    Returns:
        pandas.DataFrame: Cleaned OHLCV data
    """
    ohlcv_data_clean = ohlcv_data.copy()
    ohlcv_data_clean.dropna(
        subset=[
            "open",
            "high",
            "low",
            "close",
            "adj_open",
            "adj_high",
            "adj_low",
            "adj_close",
        ],
        inplace=True,
    )

    return ohlcv_data_clean


def remove_duplicates(ohlcv_data):
    """
    Remove duplicate observations based on date and ticker.

    Args:
        ohlcv_data (pandas.DataFrame): OHLCV data

    Returns:
        pandas.DataFrame: Deduplicated OHLCV data
    """
    ohlcv_data_dedup = ohlcv_data.copy()
    ohlcv_data_dedup.drop_duplicates(
        subset=[
            "Date",
            "Ticker",
        ],
        keep="last",
        inplace=True,
    )

    return ohlcv_data_dedup