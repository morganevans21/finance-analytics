#!/usr/bin/env python3
"""
Database reset script for the ETF Analytics Project.

This script resets the database to a clean state by:
1. Dropping the existing database
2. Creating a new empty database
3. Initializing the schema
4. Optionally reloading data

WARNING: This will DELETE ALL DATA in the database.
Use with caution in development and testing environments.
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

def check_env_file():
    """Check if .env file exists."""
    env_path = Path(".env")
    if not env_path.exists():
        print_error(".env file not found. Please run setup.py first or create .env from .env.example")
        return False
    return True

def load_env_vars():
    """Load environment variables from .env file."""
    from dotenv import load_dotenv
    load_dotenv()
    return {
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD'),
        'DB_HOST': os.getenv('DB_HOST', 'localhost'),
        'DB_PORT': os.getenv('DB_PORT', '5432'),
        'DB_NAME': os.getenv('DB_NAME')
    }

def drop_database(db_params):
    """Drop the database if it exists."""
    print_status(f"Checking if database '{db_params['DB_NAME']}' exists...")

    # Connect to default postgres database to check/drop target database
    conn_params = {
        'user': db_params['DB_USER'],
        'password': db_params['DB_PASSWORD'],
        'host': db_params['DB_HOST'],
        'port': db_params['DB_PORT'],
        'dbname': 'postgres'  # Connect to default database
    }

    # Check if database exists
    check_cmd = [
        "psql",
        "-U", conn_params['user'],
        "-h", conn_params['host'],
        "-p", conn_params['port'],
        "-d", "postgres",
        "-t", "-c",
        f"SELECT 1 FROM pg_database WHERE datename = '{db_params['DB_NAME']}';"
    ]

    # Set password via environment variable for psql
    env = os.environ.copy()
    env['PGPASSWORD'] = conn_params['password']

    try:
        result = subprocess.run(check_cmd, capture_output=True, text=True, env=env)
        db_exists = '1' in result.stdout.strip()

        if db_exists:
            print_status(f"Database '{db_params['DB_NAME']}' exists. Dropping...")
            drop_cmd = [
                "psql",
                "-U", conn_params['user'],
                "-h", conn_params['host'],
                "-p", conn_params['port'],
                "-d", "postgres",
                "-c",
                f"DROP DATABASE IF EXISTS {db_params['DB_NAME']};"
            ]
            drop_result = subprocess.run(drop_cmd, capture_output=True, text=True, env=env)
            if drop_result.returncode == 0:
                print_success(f"Database '{db_params['DB_NAME']}' dropped successfully")
            else:
                print_error(f"Failed to drop database: {drop_result.stderr}")
                return False
        else:
            print_status(f"Database '{db_params['DB_NAME']}' does not exist")

        return True

    except Exception as e:
        print_error(f"Error checking/dropping database: {e}")
        return False

def create_database(db_params):
    """Create a new database."""
    print_status(f"Creating database '{db_params['DB_NAME']}'...")

    # Connect to default postgres database to create new database
    conn_params = {
        'user': db_params['DB_USER'],
        'password': db_params['DB_PASSWORD'],
        'host': db_params['DB_HOST'],
        'port': db_params['DB_PORT'],
        'dbname': 'postgres'
    }

    create_cmd = [
        "psql",
        "-U", conn_params['user'],
        "-h", conn_params['host'],
        "-p", conn_params['port'],
        "-d", "postgres",
        "-c",
        f"CREATE DATABASE {db_params['DB_NAME']};"
    ]

    # Set password via environment variable for psql
    env = os.environ.copy()
    env['PGPASSWORD'] = conn_params['password']

    try:
        result = subprocess.run(create_cmd, capture_output=True, text=True, env=env)
        if result.returncode == 0:
            print_success(f"Database '{db_params['DB_NAME']}' created successfully")
            return True
        else:
            print_error(f"Failed to create database: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"Error creating database: {e}")
        return False

def initialize_schema(db_params):
    """Initialize the database schema using project functions."""
    print_status("Initializing database schema...")

    try:
        # Add project root to Python path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))

        # Temporarily override environment variables for this session
        old_env = dict(os.environ)
        os.environ.update({
            'DB_USER': db_params['DB_USER'],
            'DB_PASSWORD': db_params['DB_PASSWORD'],
            'DB_HOST': db_params['DB_HOST'],
            'DB_PORT': db_params['DB_PORT'],
            'DB_NAME': db_params['DB_NAME']
        })

        from src.finance_analytics.database.schema import initialize_database_schema
        initialize_database_schema()

        # Restore environment
        os.environ.clear()
        os.environ.update(old_env)

        print_success("Database schema initialized successfully")
        return True
    except Exception as e:
        print_error(f"Failed to initialize database schema: {e}")
        return False

def main():
    """Main reset function."""
    print("=" * 60)
    print("ETF Analytics Project Database Reset")
    print("=" * 60)
    print_warning("THIS WILL DELETE ALL DATA IN THE DATABASE!")
    print("=" * 60)

    # Check prerequisites
    if not check_env_file():
        return 1

    # Load environment variables
    db_params = load_env_vars()
    missing_params = [k for k, v in db_params.items() if not v]
    if missing_params:
        print_error(f"Missing required environment variables: {', '.join(missing_params)}")
        print_error("Please check your .env file")
        return 1

    # Confirm with user
    print(f"Database to be reset: {db_params['DB_NAME']}")
    print(f"Host: {db_params['DB_HOST']}:{db_params['DB_PORT']}")
    print(f"User: {db_params['DB_USER']}")

    response = input("\nAre you sure you want to continue? This will DELETE ALL DATA. (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print_status("Database reset cancelled.")
        return 0

    # Track overall success
    success = True

    # Perform reset operations
    if not drop_database(db_params):
        success = False

    if success and not create_database(db_params):
        success = False

    if success and not initialize_schema(db_params):
        success = False

    # Final status
    print("\n" + "=" * 60)
    if success:
        print_success("Database reset completed successfully!")
        print_status("Next steps:")
        print("  1. Run the update script to reload data: python update_database.py")
        print("  2. Launch the dashboard: streamlit run app/streamlit_app.py")
    else:
        print_error("Database reset completed with errors!")
        print_status("Please address the errors above.")

    print("=" * 60)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())