#!/usr/bin/env python3
"""
Application runner script for the ETF Analytics Project.

This script launches the Streamlit dashboard with proper environment setup.
"""

import os
import sys
import subprocess
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

def main():
    """Main function."""
    print("=" * 60)
    print("ETF Analytics Project Application Runner")
    print("=" * 60)

    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Check if .env file exists
    env_path = project_root / ".env"
    if not env_path.exists():
        print_warning(".env file not found")
        print_warning("Please run setup.py first or create .env from .env.example")
        print_warning("The application may not work correctly without proper database configuration")

    # Check if streamlit is available
    try:
        import streamlit
        print_success(f"Streamlit {streamlit.__version__} found")
    except ImportError:
        print_error("Streamlit not found. Please install dependencies: pip install -r requirements.txt")
        return 1

    # Check if the app file exists
    app_path = project_root / "app" / "streamlit_app.py"
    if not app_path.exists():
        print_error(f"Application file not found: {app_path}")
        return 1

    print_status("Launching Streamlit application...")
    print_status(f"App: {app_path}")
    print_status("The application will open in your default web browser")
    print_status("Press Ctrl+C to stop the application")
    print("-" * 60)

    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print_status("\nApplication stopped by user")
    except Exception as e:
        print_error(f"Error running application: {e}")
        return 1

    print("=" * 60)
    print_status("Application runner finished")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())