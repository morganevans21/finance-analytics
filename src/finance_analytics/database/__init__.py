"""
Database package for finance analytics.
"""

from .connection import get_engine
from .schema import initialize_database_schema
from .operations import (
    get_latest_dates,
    determine_download_start,
    get_download_end,
    needs_download,
    upsert_prices
)

__all__ = [
    "get_engine",
    "initialize_database_schema",
    "get_latest_dates",
    "determine_download_start",
    "get_download_end",
    "needs_download",
    "upsert_prices"
]