#!/usr/bin/env python3
"""
Development dependencies installer for the ETF Analytics Project.

This script installs development dependencies in addition to the base requirements.
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
    print("ETF Analytics Project Development Dependencies Installer")
    print("=" * 60)

    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Check if requirements-dev.txt exists
    dev_req_path = project_root / "scripts" / "requirements-dev.txt"
    if not dev_req_path.exists():
        print_error(f"Development requirements file not found: {dev_req_path}")
        return 1

    print_status("Installing development dependencies...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(dev_req_path)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print_success("Development dependencies installed successfully")
            print(result.stdout)
        else:
            print_error("Failed to install development dependencies")
            print_error(result.stderr)
            return 1

    except Exception as e:
        print_error(f"Error installing development dependencies: {e}")
        return 1

    print_status("Development dependencies installation completed!")
    print_status("You can now use development tools like:")
    print("  - pytest for testing")
    print("  - ruff for linting")
    print("  - black for code formatting")
    print("  - mypy for type checking")
    print("  - pre-commit for pre-commit hooks")

    return 0

if __name__ == "__main__":
    sys.exit(main())