"""
Data merging functionality for the finance analytics project.
"""

import pandas as pd


def merge_raw_adjusted(raw_ohlcv, adjusted_ohlc):
    """
    Merge raw OHLCV data with adjusted OHLC data.

    Args:
        raw_ohlcv (pandas.DataFrame): Normalized raw OHLCV data
        adjusted_ohlc (pandas.DataFrame): Normalized adjusted OHLC data

    Returns:
        pandas.DataFrame: Merged DataFrame containing both raw and adjusted data
    """
    ohlcv_data = pd.merge(
        raw_ohlcv,
        adjusted_ohlc,
        on=[
            "Date",
            "Ticker",
        ],
        how="inner",
    )

    return ohlcv_data


def rename_columns(raw_ohlcv, adjusted_ohlc):
    """
    Rename columns to match database schema.

    Args:
        raw_ohlcv (pandas.DataFrame): Normalized raw OHLCV data
        adjusted_ohlc (pandas.DataFrame): Normalized adjusted OHLC data

    Returns:
        tuple: (renamed_raw_ohlcv, renamed_adjusted_ohlc)
    """
    # Rename raw columns
    raw_ohlcv.rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        },
        inplace=True,
    )

    # Rename adjusted columns
    adjusted_ohlc.rename(
        columns={
            "Open": "adj_open",
            "High": "adj_high",
            "Low": "adj_low",
            "Close": "adj_close",
        },
        inplace=True,
    )

    return raw_ohlcv, adjusted_ohlc


def select_required_columns(raw_ohlcv, adjusted_ohlc):
    """
    Select only the required columns for storage.

    Args:
        raw_ohlcv (pandas.DataFrame): Normalized raw OHLCV data with renamed columns
        adjusted_ohlc (pandas.DataFrame): Normalized adjusted OHLC data with renamed columns

    Returns:
        tuple: (selected_raw_ohlcv, selected_adjusted_ohlc)
    """
    raw_ohlcv = raw_ohlcv[
        [
            "Date",
            "Ticker",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
    ].copy()

    adjusted_ohlc = adjusted_ohlc[
        [
            "Date",
            "Ticker",
            "adj_open",
            "adj_high",
            "adj_low",
            "adj_close",
        ]
    ].copy()

    return raw_ohlcv, adjusted_ohlc