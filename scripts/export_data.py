#!/usr/bin/env python3
"""
Data export script for the ETF Analytics Project.

This script exports data from the database to various formats for analysis,
sharing, or backup purposes.
"""

import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

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

def check_env_file():
    """Check if .env file exists."""
    env_path = Path(".env")
    if not env_path.exists():
        print_error(".env file not found. Please run setup.py first or create .env from .env.example")
        return False
    return True

def main():
    """Main function."""
    print("=" * 60)
    print("ETF Analytics Project Data Export Tool")
    print("=" * 60)

    # Check prerequisites
    if not check_env_file():
        return 1

    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Add project root to Python path
    sys.path.insert(0, str(project_root))

    # Set up argument parser
    import argparse
    parser = argparse.ArgumentParser(
        description="Export data from the ETF Analytics database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python export_data.py --format csv --output data.csv
  python export_data.py --format json --tickers SPY,QQQ --start 2023-01-01
  python export_data.py --format excel --output spy_data.xlsx --ticker SPY
        """
    )

    parser.add_argument(
        "--format",
        choices=['csv', 'json', 'excel', 'parquet', 'sql'],
        default='csv',
        help="Output format (default: csv)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (required for csv, json, excel, parquet)"
    )
    parser.add_argument(
        "--ticker",
        type=str,
        help="Filter by specific ticker (e.g., SPY)"
    )
    parser.add_argument(
        "--tickers",
        type=str,
        help="Filter by comma-separated list of tickers (e.g., SPY,QQQ,VTI)"
    )
    parser.add_argument(
        "--start",
        type=str,
        help="Start date for export (YYYY-MM-DD format)"
    )
    parser.add_argument(
        "--end",
        type=str,
        help="End date for export (YYYY-MM-DD format)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of rows to export"
    )
    parser.add_argument(
        "--adjusted",
        action="store_true",
        help="Export adjusted prices instead of raw prices"
    )
    parser.add_argument(
        "--include-volume",
        action="store_true",
        help="Include volume column in export"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.format in ['csv', 'json', 'excel', 'parquet'] and not args.output:
        print_error(f"--output is required for {args.format} format")
        return 1

    if args.ticker and args.tickers:
        print_error("Cannot specify both --ticker and --tickers")
        return 1

    try:
        # Import database functions
        from src.finance_analytics.database.connection import get_engine
        from sqlalchemy import text

        # Get engine
        engine = get_engine()

        # Build query
        select_cols = [
            "date",
            "ticker",
            "open",
            "high",
            "low",
            "close"
        ]

        if args.adjusted:
            select_cols = [
                "date",
                "ticker",
                "adj_open as open",
                "adj_high as high",
                "adj_low as low",
                "adj_close as close"
            ]

        if args.include_volume:
            select_cols.append("volume")

        query = f"""
        SELECT {', '.join(select_cols)}
        FROM prices
        WHERE 1=1
        """

        params = {}

        # Add ticker filters
        if args.ticker:
            query += " AND ticker = :ticker"
            params['ticker'] = args.ticker.upper()

        if args.tickers:
            ticker_list = [t.strip().upper() for t in args.tickers.split(',') if t.strip()]
            if ticker_list:
                placeholders = ', '.join([f':ticker_{i}' for i in range(len(ticker_list))])
                query += f" AND ticker IN ({placeholders})"
                for i, ticker in enumerate(ticker_list):
                    params[f'ticker_{i}'] = ticker

        # Add date filters
        if args.start:
            try:
                datetime.strptime(args.start, '%Y-%m-%d')
                query += " AND date >= :start_date"
                params['start_date'] = args.start
            except ValueError:
                print_error("Invalid start date format. Use YYYY-MM-DD")
                return 1

        if args.end:
            try:
                datetime.strptime(args.end, '%Y-%m-%d')
                query += " AND date <= :end_date"
                params['end_date'] = args.end
            except ValueError:
                print_error("Invalid end date format. Use YYYY-MM-DD")
                return 1

        # Add ordering and limit
        query += " ORDER BY date ASC, ticker ASC"

        if args.limit:
            if args.limit <= 0:
                print_error("Limit must be a positive integer")
                return 1
            query += " LIMIT :limit"
            params['limit'] = args.limit

        print_status(f"Executing query: {query}")
        print_status(f"With parameters: {params}")

        # Execute query and load into DataFrame
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())

        if df.empty:
            print_warning("No data found matching the specified criteria")
            return 1

        print_success(f"Retrieved {len(df)} rows of data")

        # Convert date column to proper datetime if present
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        # Export based on format
        output_path = Path(args.output)

        if args.format == 'csv':
            df.to_csv(output_path, index=False)
            print_success(f"Data exported to CSV: {output_path}")

        elif args.format == 'json':
            df.to_json(output_path, orient='records', date_format='iso')
            print_success(f"Data exported to JSON: {output_path}")

        elif args.format == 'excel':
            df.to_excel(output_path, index=False, engine='openpyxl')
            print_success(f"Data exported to Excel: {output_path}")

        elif args.format == 'parquet':
            try:
                df.to_parquet(output_path, index=False)
                print_success(f"Data exported to Parquet: {output_path}")
            except Exception as e:
                print_error(f"Failed to export to Parquet: {e}")
                print_warning("You may need to install pyarrow or fastparquet: pip install pyarrow")
                return 1

        elif args.format == 'sql':
            # Generate SQL INSERT statements
            try:
                with open(output_path, 'w') as f:
                    f.write("-- Exported from ETF Analytics Project\n")
                    f.write(f"-- Exported on: {datetime.now().isoformat()}\n\n")

                    # Group by ticker for more readable output
                    for ticker, group in df.groupby('ticker'):
                        f.write(f"-- Data for ticker: {ticker}\n")
                        for _, row in group.iterrows():
                            # Build INSERT statement
                            columns = ', '.join([f'"{col}"' for col in df.columns])
                            values = ', '.join([
                                f"'{str(val)}'" if isinstance(val, str) and val not in (None, '') else
                                f'NULL' if pd.isna(val) or val is None or val == '' else
                                str(val)
                                for val in row.values
                            ])
                            f.write(f"INSERT INTO prices ({columns}) VALUES ({values});\n")
                        f.write("\n")

                print_success(f"Data exported as SQL INSERT statements: {output_path}")
            except Exception as e:
                print_error(f"Failed to export to SQL: {e}")
                return 1

        # Show preview of exported data
        print_header("EXPORT PREVIEW")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst 5 rows:")
        print(df.head().to_string(index=False))

        if len(df) > 5:
            print("\nLast 5 rows:")
            print(df.tail().to_string(index=False))

        print("=" * 60)
        print_status("Data export completed successfully!")
        print("=" * 60)
        return 0

    except Exception as e:
        print_error(f"Error exporting data: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())