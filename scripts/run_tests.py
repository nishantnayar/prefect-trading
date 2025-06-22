#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prefect Trading System - Unified Test Runner
==========================================

Runs all tests and outputs results in JSON format for Streamlit UI.
"""

import os
import sys
import subprocess
import argparse
import json
import re
from pathlib import Path
from datetime import datetime


def print_banner():
    print("Prefect Trading System - Unified Test Runner")
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
        print(f"[OK] {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] pytest is not installed. Please install it first:")
        print("pip install pytest pytest-cov")
        return False


def parse_pytest_output(stdout, stderr):
    """Parse pytest output to extract test results."""
    results = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'error': 0,
            'total': 0
        },
        'tests': [],
        'stdout': stdout,
        'stderr': stderr
    }
    
    # Parse test results using regex - look for the actual test result lines
    # Format: test/file/path.py::TestClass::test_method PASSED [XX%]
    test_pattern = r'([^:]+)::([^:]+)::([^:]+) ([A-Z]+) \[[^\]]*\]'
    matches = re.findall(test_pattern, stdout)
    
    for match in matches:
        file_path, class_name, test_name, status = match
        # Clean up file path - remove any leading/trailing whitespace and artifacts
        file_path = file_path.strip()
        
        # Remove common artifacts from pytest output
        file_path = re.sub(r'^.*?collecting.*?items\s*\n\s*', '', file_path)
        file_path = re.sub(r'^.*?plugins.*?\n\s*', '', file_path)
        file_path = re.sub(r'^\[\s*\d+%\]\s*', '', file_path)
        file_path = re.sub(r'^\s*\n\s*', '', file_path)
        
        # Only include if it looks like a valid test file path
        if file_path.startswith('test/') and file_path.endswith('.py'):
            test_info = {
                'file': file_path,
                'class': class_name,
                'name': test_name,
                'outcome': status.lower(),
                'nodeid': f"{file_path}::{class_name}::{test_name}"
            }
            results['tests'].append(test_info)
            
            # Update summary
            if status == 'PASSED':
                results['summary']['passed'] += 1
            elif status == 'FAILED':
                results['summary']['failed'] += 1
            elif status == 'SKIPPED':
                results['summary']['skipped'] += 1
            else:
                results['summary']['error'] += 1
    
    results['summary']['total'] = len(results['tests'])
    
    # Try to extract summary from pytest output
    summary_pattern = r'=+ (.*?) in .*? =+'
    summary_match = re.search(summary_pattern, stdout)
    if summary_match:
        results['pytest_summary'] = summary_match.group(1)
    
    return results


def run_all_tests():
    """Run all tests and output JSON results."""
    print("Running all tests...")
    project_root = Path(__file__).parent.parent
    test_path = project_root / "test"
    build_dir = project_root / "build"
    results_file = build_dir / "test_results.json"
    
    # Ensure build directory exists
    build_dir.mkdir(exist_ok=True)
    
    cmd = [
        sys.executable, '-m', 'pytest', str(test_path), '-v',
        '--cov=src', '--cov-report=term-missing', '--cov-report=html:build/htmlcov'
    ]
    
    try:
        # Use UTF-8 encoding and handle encoding errors gracefully
        result = subprocess.run(
            cmd, 
            cwd=project_root, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace'  # Replace problematic characters with replacement character
        )
        
        # Print output for user
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # Parse results and create JSON
        test_results = parse_pytest_output(result.stdout, result.stderr)
        test_results['status'] = 'success' if result.returncode == 0 else 'failed'
        test_results['return_code'] = result.returncode
        
        # Write JSON results
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2)
        
        print(f"\nTest Summary: {test_results['summary']}")
        print(f"Results written to: {results_file}")
        
        return result.returncode == 0
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Tests failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"[ERROR] Error running tests: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Prefect Trading System Unified Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_tests.py          # Run all tests and output JSON results
        """
    )
    args = parser.parse_args()

    print_banner()
    setup_environment()
    if not check_pytest():
        sys.exit(1)
    print()
    success = run_all_tests()
    print()
    if success:
        print("[SUCCESS] Test execution completed successfully!")
    else:
        print("[FAILED] Test execution completed with failures.")
        sys.exit(1)


if __name__ == "__main__":
    main() 