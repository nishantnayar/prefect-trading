#!/usr/bin/env python3
"""
Prefect Trading System - Simple Test Runner
==========================================

A minimal test runner for Streamlit UI components.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def print_banner():
    print("Prefect Trading System - Simple Test Runner")
    print("==========================================")
    print()


def setup_environment():
    os.environ['TESTING'] = 'true'
    print("Environment variable TESTING set for testing.")


def check_pytest():
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


def run_simple_tests():
    """Run the simple Streamlit UI tests."""
    print("Running simple Streamlit UI tests...")
    project_root = Path(__file__).parent.parent
    test_path = project_root / "test" / "unit" / "ui" / "test_simple_streamlit.py"
    cmd = [
        sys.executable, '-m', 'pytest', str(test_path), '-v',
        '--cov=src/ui', '--cov-report=term-missing', '--cov-report=html:htmlcov', '--cov-fail-under=20'
    ]
    try:
        result = subprocess.run(cmd, check=True, cwd=project_root)
        print("✓ Simple Streamlit UI tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Simple Streamlit UI tests failed with exit code {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Prefect Trading System Simple Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_tests.py          # Run all simple Streamlit UI tests
  python scripts/run_tests.py simple   # Run simple Streamlit UI tests
        """
    )
    parser.add_argument(
        'test_type', nargs='?', default='simple', choices=['simple'],
        help='Type of tests to run (only "simple" is supported)'
    )
    args = parser.parse_args()

    print_banner()
    setup_environment()
    if not check_pytest():
        sys.exit(1)
    print()
    success = run_simple_tests()
    print()
    if success:
        print("✓ Test execution completed successfully!")
    else:
        print("✗ Test execution completed with failures.")
        sys.exit(1)


if __name__ == "__main__":
    main() 