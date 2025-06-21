#!/usr/bin/env python3
"""
Prefect Trading System - Test Runner
====================================

A comprehensive test runner with multiple options for running different types of tests.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def print_banner():
    """Print the test runner banner."""
    print("Prefect Trading System - Test Runner")
    print("====================================")
    print()


def setup_environment():
    """Set up test environment variables."""
    env_vars = {
        'TESTING': 'true',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'test_trading_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
    
    print("Environment variables set for testing.")


def check_pytest():
    """Check if pytest is installed."""
    try:
        result = subprocess.run([sys.executable, '-m', 'pytest', '--version'], 
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print(f"✓ {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ pytest is not installed. Please install it first:")
        print("pip install pytest pytest-cov")
        return False


def run_tests(test_path, test_name, with_coverage=False):
    """Run tests with the specified path and name."""
    print(f"Running {test_name}...")
    
    # Ensure we're in the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Build pytest command
    cmd = [sys.executable, '-m', 'pytest', test_path, '-v']
    
    if with_coverage:
        cmd.extend(['--cov=src', '--cov-report=term-missing'])
    
    try:
        result = subprocess.run(cmd, check=True, cwd=project_root)
        print(f"✓ {test_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {test_name} failed with exit code {e.returncode}")
        return False


def run_quick_tests():
    """Run the quick test suite."""
    print("Running quick test suite...")
    
    tests = [
        ("test/unit/test_basic_functionality.py", "Basic Tests"),
        ("test/unit/database/test_database_connectivity.py", "Database Tests")
    ]
    
    success = True
    for test_path, test_name in tests:
        if not run_tests(test_path, test_name):
            success = False
    
    return success


def run_all_tests():
    """Run all tests with coverage."""
    print("Running complete test suite...")
    return run_tests("test/", "Complete Test Suite", with_coverage=True)


def main():
    """Main function to handle command line arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Prefect Trading System Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_tests.py          # Run all tests with coverage
  python scripts/run_tests.py quick    # Run quick test suite
  python scripts/run_tests.py unit     # Run unit tests only
  python scripts/run_tests.py data     # Run data source tests only
        """
    )
    
    parser.add_argument(
        'test_type',
        nargs='?',
        default='all',
        choices=['basic', 'unit', 'database', 'integration', 'e2e', 'coverage', 'quick', 'all'],
        help='Type of tests to run'
    )
    
    args = parser.parse_args()
    
    print_banner()
    setup_environment()
    
    if not check_pytest():
        sys.exit(1)
    
    print()
    
    # Run tests based on the specified type
    success = True
    
    if args.test_type == 'basic':
        print("Running basic functionality tests...")
        success = run_tests("test/unit/test_basic_functionality.py", "Basic Functionality Tests")
    
    elif args.test_type == 'unit':
        print("Running all unit tests...")
        success = run_tests("test/unit/", "Unit Tests")
    
    elif args.test_type == 'database':
        print("Running database tests...")
        success = run_tests("test/unit/database/", "Database Tests")
    
    elif args.test_type == 'integration':
        print("Running integration tests...")
        success = run_tests("test/integration/", "Integration Tests")
    
    elif args.test_type == 'e2e':
        print("Running end-to-end tests...")
        success = run_tests("test/e2e/", "E2E Tests")
    
    elif args.test_type == 'coverage':
        print("Running all tests with coverage...")
        success = run_tests("test/", "All Tests with Coverage", with_coverage=True)
    
    elif args.test_type == 'quick':
        success = run_quick_tests()
    
    elif args.test_type == 'all':
        success = run_all_tests()
    
    print()
    if success:
        print("✓ Test execution completed successfully!")
    else:
        print("✗ Test execution completed with failures.")
        sys.exit(1)


if __name__ == "__main__":
    main() 