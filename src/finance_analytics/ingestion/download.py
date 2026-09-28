"""
Data download functionality for the finance analytics project.
"""

import yfinance as yf


def download_raw_data(tickers, start_date, end_date, progress=True):
    """
    Download raw OHLCV data from Yahoo Finance.

    Args:
        tickers (list): List of ticker symbols
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format (exclusive)
        progress (bool): Whether to show yfinance progress information

    Returns:
        pandas.DataFrame: Raw OHLCV data from Yahoo Finance
    """
    raw_data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        auto_adjust=False,  # False means Open/High/Low/Close are raw historical prices
        actions=False,      # We don't need Yahoo's separate actions dataframe
        progress=progress,
        group_by="column",
        threads=True,
    )

    return raw_data


def download_adjusted_data(tickers, start_date, end_date, progress=True):
    """
    Download adjusted OHLC data from Yahoo Finance.

    Args:
        tickers (list): List of ticker symbols
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format (exclusive)
        progress (bool): Whether to show yfinance progress information

    Returns:
        pandas.DataFrame: Adjusted OHLC data from Yahoo Finance
    """
    adjusted_data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        auto_adjust=True,   # True means Yahoo adjusts OHLC prices for corporate actions
        actions=False,      # We don't need Yahoo's separate actions dataframe
        progress=progress,
        group_by="column",
        threads=True,
    )

    return adjusted_data