"""
Configuration management for the finance analytics project.
"""

import os
from dotenv import load_dotenv


def load_config():
    """
    Load configuration from environment variables.

    Returns:
        dict: Configuration dictionary
    """
    load_dotenv()

    # Earliest date used for a full historical download.
    START_DATE = os.getenv("START_DATE", "2015-01-01")

    # Number of calendar days to deliberately overlap when
    # doing incremental downloads.
    OVERLAP_DAYS = int(os.getenv("OVERLAP_DAYS", "7"))

    # Display yfinance progress information.
    YFINANCE_PROGRESS = os.getenv("YFINANCE_PROGRESS", "True").lower() == "true"

    return {
        "START_DATE": START_DATE,
        "OVERLAP_DAYS": OVERLAP_DAYS,
        "YFINANCE_PROGRESS": YFINANCE_PROGRESS,
    }


def get_etf_tickers():
    """
    Extract Yahoo Finance tickers from the ETF universe.

    Only the primary Yahoo Finance listing for each ETF
    is used.

    Duplicates are removed while preserving order.

    Returns:
        list: List of Yahoo Finance ticker symbols
    """
    # Add the src directory to the Python path so that we can
    # import from finance_analytics.
    import sys
    sys.path.append(
        os.path.join(os.path.dirname(__file__))
    )

    from finance_analytics.universe.etfs import get_all_etfs

    etfs = get_all_etfs()

    tickers = []

    for etf in etfs:
        for listing in etf.listings:
            if listing.is_primary:
                tickers.append(
                    listing.yahoo_ticker
                )

    # Remove duplicates while preserving order.
    return list(dict.fromkeys(tickers))


def get_tickers_with_fallback():
    """
    Get ETF tickers with fallback to environment variable.

    Returns:
        list: List of ticker symbols
    """
    try:
        TICKERS = get_etf_tickers()
        print(
            f"Loaded {len(TICKERS)} tickers "
            "from ETF universe."
        )
        return TICKERS
    except Exception as exc:
        print(
            f"Warning: Could not load tickers "
            f"from ETF universe: {exc}"
        )
        print(
            "Falling back to ETF_TICKERS "
            "environment variable."
        )

        tickers_env = os.getenv(
            "ETF_TICKERS",
            "SPY,QQQ",
        )

        TICKERS = [
            ticker.strip().upper()
            for ticker in tickers_env.split(",")
            if ticker.strip()
        ]

        if not TICKERS:
            raise RuntimeError(
                "No ETF tickers were found."
            )

        return TICKERS