#!/usr/bin/env python3
"""
Database status script for the ETF Analytics Project.

This script displays information about the current state of the database:
- Connection status
- Table existence and structure
- Row counts and date ranges
- Data completeness
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def print_status(message):
    """Print a status message with formatting."""
    print(f"\033[94m[INFO]\033[0m {message}")

def print_success(message):
    """Print a success message with formatting."""
    print(f"\033[92m[SUCCESS]\033[0m {message}")

def print_warning(message):
    """Print a warning message with formatting."""
    print(f"\033[93m[WARNING]\033[0m {message}")

def print_error(message):
    """Print an error message with formatting."""
    print(f"\033[91m[ERROR]\033[0m {message}")

def print_header(title):
    """Print a section header."""
    print(f"\n\033[95m{'='*60}\033[0m")
    print(f"\033[95m{title}\033[0m")
    print(f"\033[95m{'='*60}\033[0m")

def check_env_file():
    """Check if .env file exists."""
    env_path = Path(".env")
    if not env_path.exists():
        print_error(".env file not found. Please run setup.py first or create .env from .env.example")
        return False
    return True

def load_env_vars():
    """Load environment variables from .env file."""
    load_dotenv()
    return {
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD'),
        'DB_HOST': os.getenv('DB_HOST', 'localhost'),
        'DB_PORT': os.getenv('DB_PORT', '5432'),
        'DB_NAME': os.getenv('DB_NAME')
    }

def main():
    """Main function."""
    print("=" * 60)
    print("ETF Analytics Project Database Status")
    print("=" * 60)

    # Check prerequisites
    if not check_env_file():
        return 1

    # Load environment variables
    load_dotenv()
    db_params = {
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD'),
        'DB_HOST': os.getenv('DB_HOST', 'localhost'),
        'DB_PORT': os.getenv('DB_PORT', '5432'),
        'DB_NAME': os.getenv('DB_NAME')
    }

    missing_params = [k for k, v in db_params.items() if not v]
    if missing_params:
        print_error(f"Missing required environment variables: {', '.join(missing_params)}")
        print_error("Please check your .env file")
        return 1

    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    try:
        # Import database functions
        from src.finance_analytics.database.connection import get_engine
        from src.finance_analytics.database.operations import get_latest_dates
        from src.finance_analytics.config import get_tickers_with_fallback

        # Test connection
        print_header("CONNECTION STATUS")
        try:
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute("SELECT version();")
                version = result.fetchone()[0]
                print_success(f"Connected to PostgreSQL: {version.split()[0]} {version.split()[1]} {version.split()[2]}")
        except Exception as e:
            print_error(f"Failed to connect to database: {e}")
            return 1

        # Check if prices table exists
        print_header("TABLE STATUS")
        try:
            from sqlalchemy import text
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = 'prices'
                    );
                """))
                table_exists = result.scalar()

                if table_exists:
                    print_success("Table 'prices' exists")
                else:
                    print_warning("Table 'prices' does not exist")
                    print_warning("Run 'python update_database.py' to initialize the database")
                    return 1

        except Exception as e:
            print_error(f"Error checking table existence: {e}")
            return 1

        # Get table structure
        print_header("TABLE STRUCTURE")
        try:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    AND table_name = 'prices'
                    ORDER BY ordinal_position;
                """))
                columns = result.fetchall()

                if columns:
                    print(f"{'Column Name':<20} {'Data Type':<20} {'Nullable':<12} {'Default'}")
                    print("-" * 80)
                    for col in columns:
                        print(f"{col[0]:<20} {col[1]:<20} {col[2]:<12} {col[3] if col[3] else ''}")
                else:
                    print_warning("No columns found in prices table")

        except Exception as e:
            print_error(f"Error getting table structure: {e}")

        # Get tickers from configuration
        print_header("CONFIGURED TICKERS")
        try:
            tickers = get_tickers_with_fallback()
            print_success(f"Configured tickers ({len(tickers)}): {', '.join(tickers)}")
        except Exception as e:
            print_error(f"Error getting configured tickers: {e}")
            tickers = []

        # Get latest dates for each ticker
        print_header("DATA STATUS")
        try:
            latest_dates = get_latest_dates(tickers)

            if latest_dates:
                print(f"{'Ticker':<10} {'Latest Date':<12} {'Status'}")
                print("-" * 35)
                total_tickers = len(latest_dates)
                tickers_with_data = 0
                earliest_date = None
                latest_date = None

                for ticker, date in sorted(latest_dates.items()):
                    if date is None:
                        status = "NO DATA"
                    else:
                        status = "HAS DATA"
                        tickers_with_data += 1
                        if earliest_date is None or date < earliest_date:
                            earliest_date = date
                        if latest_date is None or date > latest_date:
                            latest_date = date
                    print(f"{ticker:<10} {str(date):<12} {status}")

                print("-" * 35)
                print_success(f"Tickers with data: {tickers_with_data}/{total_tickers}")

                if earliest_date and latest_date:
                    print_success(f"Date range: {earliest_date} to {latest_date}")

                # Calculate approximate row count
                if earliest_date and latest_date:
                    from datetime import date
                    days_diff = (latest_date - earliest_date).days
                    # Estimate trading days (approx 252 per year)
                    years = days_diff / 365.25
                    estimated_trading_days = int(years * 252)
                    estimated_rows = estimated_trading_days * tickers_with_data
                    print_info(f"Estimated row count: ~{estimated_rows:,} rows")
                    print_info(f"(Based on {tickers_with_data} tickers over {years:.1f} years)")

            else:
                print_warning("No date information available")

        except Exception as e:
            print_error(f"Error getting latest dates: {e}")

        # Get total row count
        print_header("ROW COUNTS")
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM prices;"))
                total_rows = result.scalar()
                print_success(f"Total rows in prices table: {total_rows:,}")

                if total_rows > 0:
                    # Get count by ticker
                    result = conn.execute(text("""
                        SELECT ticker, COUNT(*) as count
                        FROM prices
                        GROUP BY ticker
                        ORDER BY count DESC;
                    """))
                    ticker_counts = result.fetchall()

                    print(f"{'Ticker':<10} {'Rows':<12} {'Percentage'}")
                    print("-" * 30)
                    for ticker, count in ticker_counts:
                        percentage = (count / total_rows) * 100 if total_rows > 0 else 0
                        print(f"{ticker:<10} {count:<12} {percentage:>6.1f}%")

        except Exception as e:
            print_error(f"Error getting row counts: {e}")

        # Check for missing data patterns
        print_header("DATA QUALITY CHECKS")
        try:
            with engine.connect() as conn:
                # Check for NULL values in critical columns
                result = conn.execute(text("""
                    SELECT
                        SUM(CASE WHEN date IS NULL THEN 1 ELSE 0 END) as null_date,
                        SUM(CASE WHEN ticker IS NULL THEN 1 ELSE 0 END) as null_ticker,
                        SUM(CASE WHEN close IS NULL THEN 1 ELSE 0 END) as null_close,
                        SUM(CASE WHEN volume IS NULL THEN 1 ELSE 0 END) as null_volume
                    FROM prices;
                """))
                null_counts = result.fetchone()

                print("NULL value counts:")
                print(f"  date: {null_counts[0]}")
                print(f"  ticker: {null_counts[1]}")
                print(f"  close: {null_counts[2]}")
                print(f"  volume: {null_counts[3]}")

                if null_counts[0] == 0 and null_counts[1] == 0:
                    print_success("No NULL values in key identifier columns (date, ticker)")
                else:
                    print_warning("Found NULL values in key identifier columns")

                # Check OHLC relationships (where all values present)
                result = conn.execute(text("""
                    SELECT
                        SUM(CASE WHEN high < low THEN 1 ELSE 0 END) as high_lt_low,
                        SUM(CASE WHEN high < open THEN 1 ELSE 0 END) as high_lt_open,
                        SUM(CASE WHEN high < close THEN 1 ELSE 0 END) as high_lt_close,
                        SUM(CASE WHEN low > open THEN 1 ELSE 0 END) as low_gt_open,
                        SUM(CASE WHEN low > close THEN 1 ELSE 0 END) as low_gt_close
                    FROM prices
                    WHERE open IS NOT NULL AND high IS NOT NULL AND low IS NOT NULL AND close IS NOT NULL;
                """))
                ohlc_violations = result.fetchone()

                print("OHLC relationship violations:")
                print(f"  high < low: {ohlc_violations[0]}")
                print(f"  high < open: {ohlc_violations[1]}")
                print(f"  high < close: {ohlc_violations[2]}")
                print(f"  low > open: {ohlc_violations[3]}")
                print(f"  low > close: {ohlc_violations[4]}")

                total_violations = sum(ohlc_violations)
                if total_violations == 0:
                    print_success("No OHLC relationship violations found")
                else:
                    print_warning(f"Found {total_violations} OHLC relationship violations")

        except Exception as e:
            print_error(f"Error performing data quality checks: {e}")

    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1

    print("\n" + "=" * 60)
    print_status("Database status check completed")
    print("=" * 60)

    return 0

def print_info(message):
    """Print an informational message."""
    print(f"\033[96m[INFO]\033[0m {message}")

if __name__ == "__main__":
    sys.exit(main())