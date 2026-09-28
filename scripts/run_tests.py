#!/usr/bin/env python3
"""
Test runner script for the ETF Analytics Project.

This script provides convenient ways to run different subsets of tests:
- Unit tests only
- Integration tests only
- All tests
- Tests with coverage reporting
- Specific test modules or functions
"""

import os
import sys
import subprocess
import argparse
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

def print_header(title):
    """Print a section header."""
    print(f"\n\033[95m{'='*60}\033[0m")
    print(f"\033[95m{title}\033[0m")
    print(f"\033[95m{'='*60}\033[0m")

def main():
    """Main function."""
    print("=" * 60)
    print("ETF Analytics Project Test Runner")
    print("=" * 60)

    parser = argparse.ArgumentParser(
        description="Run tests for the ETF Analytics Project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --unit             # Run unit tests only
  python run_tests.py --integration      # Run integration tests only
  python run_tests.py --coverage         # Run all tests with coverage
  python run_tests.py --module analytics # Run tests for analytics module
  python run_tests.py --function test_simple_returns # Run specific test function
  python run_tests.py --verbose          # Verbose output
  python run_tests.py --parallel         # Run tests in parallel (if pytest-xdist installed)
        """
    )

    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run unit tests only"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run integration tests only"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--module",
        type=str,
        help="Run tests for specific module (e.g., analytics, database, universe)"
    )
    parser.add_argument(
        "--function",
        type=str,
        help="Run specific test function (requires --module)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run tests in parallel (requires pytest-xdist)"
    )
    parser.add_argument(
        "--failfast",
        action="store_true",
        help="Stop on first failure"
    )
    parser.add_argument(
        "--tb",
        type=str,
        choices=['short', 'long', 'line', 'no'],
        default='short',
        help="Traceback format (default: short)"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.function and not args.module:
        print_error("--function requires --module to be specified")
        return 1

    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]

    # Add test selection
    if args.unit:
        cmd.append("tests/unit/")
        print_status("Running unit tests...")
    elif args.integration:
        cmd.append("tests/integration/")
        print_status("Running integration tests...")
    elif args.module:
        module_path = f"tests/unit/test_{args.module}.py"
        if not Path(module_path).exists():
            # Try integration tests
            module_path = f"tests/integration/test_{args.module}_integration.py"
            if not Path(module_path).exists():
                print_error(f"Test module '{args.module}' not found in unit or integration tests")
                return 1
        cmd.append(module_path)
        print_status(f"Running tests for module: {args.module}")

        if args.function:
            # Add specific function
            cmd[-1] = f"{cmd[-1]}::{args.function}"
            print_status(f"  Function: {args.function}")
    else:
        cmd.append("tests/")
        print_status("Running all tests...")

    # Add options
    if args.coverage:
        cmd.extend(["--cov=src", "--cov-report=term-missing"])
        print_status("  Coverage reporting enabled")

    if args.verbose:
        cmd.append("-v")
        print_status("  Verbose output enabled")

    if args.parallel:
        cmd.append("-n")
        cmd.append("auto")
        print_status("  Parallel execution enabled")

    if args.failfast:
        cmd.append("-x")
        print_status("  Fail-fast enabled")

    cmd.extend(["--tb", args.tb])

    # Add current directory to Python path
    env = os.environ.copy()
    env['PYTHONPATH'] = f"{project_root}:{env.get('PYTHONPATH', '')}"

    # Print the command being run
    print_status(f"Running command: {' '.join(cmd)}")
    print("-" * 60)

    # Run the tests
    try:
        result = subprocess.run(cmd, env=env, timeout=300)  # 5 minute timeout
        return_code = result.returncode
    except subprocess.TimeoutExpired:
        print_error("Tests timed out after 5 minutes")
        return 1
    except Exception as e:
        print_error(f"Error running tests: {e}")
        return 1

    print("-" * 60)
    if return_code == 0:
        print_success("All tests passed!")
    else:
        print_error(f"Tests failed with return code: {return_code}")

    print("=" * 60)
    return return_code

if __name__ == "__main__":
    sys.exit(main())