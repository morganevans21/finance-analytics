#!/usr/bin/env python3
"""
Setup script for the ETF Analytics Project.

This script helps new developers get the project up and running by:
1. Checking prerequisites
2. Setting up the environment
3. Initializing the database
4. Running an initial data load (optional)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

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
    sys.exit(1)

def check_python_version():
    """Check that Python version is sufficient."""
    print_status("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 14):
        print_error(f"Python 3.14+ required. Found {version.major}.{version.minor}")
    else:
        print_success(f"Python {version.major}.{version.minor} is sufficient")

def check_postgres_available():
    """Check if PostgreSQL is available."""
    print_status("Checking for PostgreSQL...")
    # Check if psql command is available
    if shutil.which("psql") is None:
        print_warning("psql command not found. Please install PostgreSQL.")
        print_warning("You can still proceed, but database functions won't work until PostgreSQL is installed.")
        return False

    # Try to connect to default postgres database to see if server is running
    try:
        result = subprocess.run(
            ["psql", "-U", "postgres", "-c", "SELECT version();"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success("PostgreSQL is available and running")
            return True
        else:
            print_warning("PostgreSQL installed but server may not be running")
            print_warning("Please start PostgreSQL server before using database functions")
            return False
    except subprocess.TimeoutExpired:
        print_warning("PostgreSQL check timed out")
        return False
    except FileNotFoundError:
        print_warning("psql command not found")
        return False

def check_env_file():
    """Check if .env file exists, create from example if not."""
    print_status("Checking for environment file...")
    env_path = Path(".env")
    example_path = Path(".env.example")

    if env_path.exists():
        print_success(".env file found")
        return True
    elif example_path.exists():
        print_status("No .env found, creating from .env.example...")
        shutil.copy(example_path, env_path)
        print_success("Created .env from .env.example")
        print_warning("Please edit .env to configure your database connection")
        return True
    else:
        print_error("Neither .env nor .env.example found")
        return False

def install_dependencies():
    """Install Python dependencies."""
    print_status("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print_success("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

def initialize_database():
    """Initialize the database schema."""
    print_status("Initializing database schema...")
    try:
        # Add project root to Python path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))

        from src.finance_analytics.database.schema import initialize_database_schema
        initialize_database_schema()
        print_success("Database schema initialized successfully")
        return True
    except Exception as e:
        print_error(f"Failed to initialize database schema: {e}")
        print_warning("Make sure PostgreSQL is running and .env is configured correctly")
        return False

def load_initial_data(force=False):
    """Load initial data (optional)."""
    print_status("Checking if initial data load is needed...")

    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    try:
        from src.finance_analytics.database.operations import get_latest_dates
        from src.finance_analytics.config import get_tickers_with_fallback

        tickers = get_tickers_with_fallback()
        latest_dates = get_latest_dates(tickers)

        # Check if we have any data
        has_data = any(date is not None for date in latest_dates.values())

        if has_data and not force:
            print_success("Data already exists in database")
            print_warning("Use --force to reload initial data")
            return True
        else:
            if has_data:
                print_status("Existing data found, reloading as requested...")
            else:
                print_status("No existing data found, loading initial data...")

            # Run the update script
            print_status("Running initial data load (this may take a while)...")
            result = subprocess.run(
                [sys.executable, "update_database.py"],
                cwd=project_root,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print_success("Initial data load completed successfully")
                print(result.stdout)
                return True
            else:
                print_error("Failed to load initial data")
                print_error(result.stderr)
                return False

    except Exception as e:
        print_error(f"Failed to check/load initial data: {e}")
        return False

def main():
    """Main setup function."""
    print("=" * 60)
    print("ETF Analytics Project Setup")
    print("=" * 60)

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Setup the ETF Analytics Project")
    parser.add_argument(
        "--skip-data",
        action="store_true",
        help="Skip initial data loading"
    )
    parser.add_argument(
        "--force-data",
        action="store_true",
        help="Force reload of initial data even if data exists"
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Skip dependency installation"
    )

    args = parser.parse_args()

    # Track overall success
    success = True

    # Run setup steps
    check_python_version()
    postgres_available = check_postgres_available()

    if not check_env_file():
        success = False

    if not args.skip_deps:
        if not install_dependencies():
            success = False

    # Only proceed with database steps if env file exists
    if Path(".env").exists():
        if not initialize_database():
            success = False

        if not args.skip_data:
            if not load_initial_data(force=args.force_data):
                success = False
    else:
        print_warning("Skipping database setup due to missing .env file")

    # Final status
    print("\n" + "=" * 60)
    if success:
        print_success("Setup completed successfully!")
        print_status("Next steps:")
        print("  1. Edit .env to configure your database connection (if not already done)")
        if postgres_available:
            print("  2. Make sure PostgreSQL is running")
        print("  3. Run the update script: python update_database.py")
        print("  4. Launch the dashboard: streamlit run app/streamlit_app.py")
    else:
        print_error("Setup completed with errors!")
        print_status("Please address the errors above and re-run the setup script.")

    print("=" * 60)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())