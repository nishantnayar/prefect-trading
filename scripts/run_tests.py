#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prefect Trading System - Unified Test Runner
==========================================

Runs all tests and outputs results in JSON format for Streamlit UI.
Also supports command-line usage with various options.
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


def normalize_coverage_data(coverage_data):
    """
    Normalize coverage data to ensure consistent format for UI consumption.
    
    Args:
        coverage_data: Raw coverage data from pytest-cov
        
    Returns:
        Normalized coverage data with consistent structure
    """
    if not coverage_data:
        return {}
    
    normalized = {
        'meta': coverage_data.get('meta', {}),
        'files': {},
        'totals': coverage_data.get('totals', {})
    }
    
    # Normalize file paths and ensure consistent structure
    for file_path, file_data in coverage_data.get('files', {}).items():
        # Normalize file path separators
        normalized_path = file_path.replace('\\', '/')
        
        # Ensure file data has required structure
        normalized_file_data = {
            'executed_lines': file_data.get('executed_lines', []),
            'summary': file_data.get('summary', {}),
            'missing_lines': file_data.get('missing_lines', []),
            'excluded_lines': file_data.get('excluded_lines', []),
            'functions': file_data.get('functions', {}),
            'classes': file_data.get('classes', {})
        }
        
        normalized['files'][normalized_path] = normalized_file_data
    
    return normalized


def run_all_tests():
    """Run all tests and output JSON results."""
    print("Running all tests...")
    project_root = Path(__file__).parent.parent
    test_path = project_root / "test"
    build_dir = project_root / "build"
    results_file = build_dir / "test_results.json"
    coverage_file = build_dir / "coverage.json"
    
    # Ensure build directory exists
    build_dir.mkdir(exist_ok=True)
    
    # Updated command to generate both HTML and JSON coverage reports
    cmd = [
        sys.executable, '-m', 'pytest', str(test_path), '-v',
        '--cov=src', 
        '--cov-report=term-missing', 
        '--cov-report=html:build/htmlcov',
        '--cov-report=json:build/coverage.json'
    ]
    
    try:
        # Start timing
        start_time = datetime.now()
        
        # Use UTF-8 encoding and handle encoding errors gracefully
        result = subprocess.run(
            cmd, 
            cwd=project_root, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace'  # Replace problematic characters with replacement character
        )
        
        # End timing
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Print output for user
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # Parse results and create JSON
        test_results = parse_pytest_output(result.stdout, result.stderr)
        test_results['status'] = 'success' if result.returncode == 0 else 'failed'
        test_results['return_code'] = result.returncode
        test_results['execution_time'] = execution_time
        
        # Write JSON results
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2)
        
        # Normalize and write coverage data if it exists
        if coverage_file.exists():
            try:
                with open(coverage_file, 'r', encoding='utf-8') as f:
                    coverage_data = json.load(f)
                
                # Normalize the coverage data
                normalized_coverage = normalize_coverage_data(coverage_data)
                
                # Write normalized coverage data
                with open(coverage_file, 'w', encoding='utf-8') as f:
                    json.dump(normalized_coverage, f, indent=2)
                
                print(f"Coverage data normalized and written to: {coverage_file}")
                
                # Print coverage summary
                if 'totals' in normalized_coverage:
                    totals = normalized_coverage['totals']
                    print(f"Coverage Summary: {totals.get('covered_lines', 0)}/{totals.get('num_statements', 0)} lines covered ({totals.get('percent_covered_display', '0')}%)")
                
            except Exception as e:
                print(f"Warning: Could not normalize coverage data: {e}")
        
        print(f"\nTest Summary: {test_results['summary']}")
        print(f"Execution Time: {execution_time:.2f} seconds")
        print(f"Results written to: {results_file}")
        
        return result.returncode == 0
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Tests failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"[ERROR] Error running tests: {e}")
        return False


def run_specific_tests(test_path=None, verbose=False):
    """Run specific tests and return results."""
    print(f"Running tests: {test_path or 'all tests'}")
    project_root = Path(__file__).parent.parent
    python_path = sys.executable
    
    # Build command
    cmd = [python_path, "-m", "pytest"]
    
    if test_path:
        cmd.append(str(test_path))
    else:
        cmd.append("test/")
    
    if verbose:
        cmd.extend(["-v", "--tb=long"])
    else:
        cmd.extend(["-v", "--tb=short"])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=600  # 10 minute timeout
        )
        
        return result
        
    except subprocess.TimeoutExpired:
        print("❌ Test execution timed out after 10 minutes")
        return None
    except Exception as e:
        print(f"❌ Error running tests: {str(e)}")
        return None


def display_results(result):
    """Display test results in a formatted way for command-line usage."""
    if not result:
        return
    
    print(f"Return Code: {result.returncode}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    if result.stdout:
        print("📋 Test Output:")
        print(result.stdout)
    
    if result.stderr:
        print("❌ Error Output:")
        print(result.stderr)
    
    # Summary
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")


def list_test_files():
    """List all available test files."""
    test_dir = Path("test")
    if test_dir.exists():
        test_files = list(test_dir.rglob("test_*.py"))
        print("Available test files:")
        for test_file in sorted(test_files):
            print(f"  • {test_file}")
    else:
        print("❌ Test directory not found")


def main():
    parser = argparse.ArgumentParser(
        description="Prefect Trading System Unified Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_tests.py                    # Run all tests and output JSON results
  python scripts/run_tests.py --list-tests       # List all available test files
  python scripts/run_tests.py --test-path test/database/test_database_connectivity.py  # Run specific test
  python scripts/run_tests.py --verbose          # Run with verbose output
  python scripts/run_tests.py --ui-mode          # Run tests for UI consumption
        """
    )
    
    parser.add_argument(
        "--test-path", 
        help="Path to specific test file or directory"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Show verbose output"
    )
    parser.add_argument(
        "--list-tests", 
        action="store_true", 
        help="List available test files"
    )
    parser.add_argument(
        "--ui-mode", 
        action="store_true", 
        help="Run tests optimized for UI consumption (JSON output)"
    )
    
    args = parser.parse_args()

    if args.list_tests:
        list_test_files()
        return
    
    if args.ui_mode or (not args.test_path and not args.verbose):
        # UI mode or default mode - run all tests with JSON output
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
    else:
        # Command-line mode - run specific tests with formatted output
        result = run_specific_tests(args.test_path, args.verbose)
        display_results(result)


if __name__ == "__main__":
    main() 