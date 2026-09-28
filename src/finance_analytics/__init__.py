"""
Top-level package for finance analytics.
"""

# Optionally export subpackages for convenience
from . import database, ingestion, validation, universe, analytics, config

__all__ = [
    "database",
    "ingestion",
    "validation",
    "universe",
    "analytics",
    "config"
]