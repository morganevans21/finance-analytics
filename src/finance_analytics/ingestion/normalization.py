"""
Data normalization functionality for the finance analytics project.
"""

import pandas as pd


def normalize_yfinance_data(data, tickers, include_volume=False):
    """
    Convert yfinance DataFrame into a flat DataFrame.

    Handles both single-ticker and multi-ticker downloads.

    Args:
        data (pandas.DataFrame): Raw data from yfinance.download()
        tickers (list): List of ticker symbols
        include_volume (bool): Whether to include volume column

    Returns:
        pandas.DataFrame: Normalized DataFrame with Date, Ticker, and price/volume columns
    """
    if len(tickers) == 1:
        ticker = tickers[0]

        result = pd.DataFrame({
            "Date": data.index,
            "Open": data[("Open", ticker)].values,
            "High": data[("High", ticker)].values,
            "Low": data[("Low", ticker)].values,
            "Close": data[("Close", ticker)].values,
        })

        if include_volume:
            result["Volume"] = data[
                ("Volume", ticker)
            ].values

        result["Ticker"] = ticker

    else:
        result = (
            data
            .stack(
                level=1,
                future_stack=True,
            )
            .rename_axis(
                index=["Date", "Ticker"]
            )
            .reset_index()
        )

    return result