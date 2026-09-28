"""
Integration tests for database operations.
"""

import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock

# Add project root to path
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

class TestDatabaseIntegration(unittest.TestCase):
    """Integration tests for database operations."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests."""
        # Load environment variables from .env file
        load_dotenv()

        # Use an in-memory SQLite database for testing to avoid
        # requiring PostgreSQL for unit tests
        # In a real integration test, you would use a test PostgreSQL database

    def setUp(self):
        """Set up before each test method."""
        pass

    def tearDown(self):
        """Clean up after each test method."""
        pass

    def test_database_connection_functions_exist(self):
        """Test that database connection functions exist and are callable."""
        # These tests would normally require a real database
        # For now, we'll just verify the functions exist
        try:
            from src.finance_analytics.database.connection import get_engine
            from src.finance_analytics.database.schema import initialize_database_schema
            from src.finance_analytics.database.operations import (
                get_latest_dates, get_download_end, needs_download, upsert_prices
            )

            # Verify functions exist
            self.assertTrue(callable(get_engine))
            self.assertTrue(callable(initialize_database_schema))
            self.assertTrue(callable(get_latest_dates))
            self.assertTrue(callable(get_download_end))
            self.assertTrue(callable(needs_download))
            self.assertTrue(callable(upsert_prices))

        except ImportError as e:
            self.skipTest(f"Database dependencies not available: {e}")

    def test_config_functions_exist(self):
        """Test that configuration functions exist."""
        try:
            from src.finance_analytics.config import load_config, get_etf_tickers, get_tickers_with_fallback

            self.assertTrue(callable(load_config))
            self.assertTrue(callable(get_etf_tickers))
            self.assertTrue(callable(get_tickers_with_fallback))

        except ImportError as e:
            self.skipTest(f"Config dependencies not available: {e}")

if __name__ == '__main__':
    unittest.main()