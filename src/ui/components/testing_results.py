"""
Testing Results Component for Streamlit UI.

This module provides functionality to display testing results,
coverage reports, and test statistics in the Streamlit interface.
"""

import streamlit as st
import subprocess
import json
import os
import re
from pathlib import Path
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional, Tuple
import sys
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode


def run_tests_and_get_results() -> Dict:
    """
    Run tests using the run_tests.py script and return results.
    
    Returns:
        Dict containing test results, coverage data, and execution info
    """
    project_root = Path(__file__).parent.parent.parent.parent
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'test_results': {},
        'coverage_data': {},
        'execution_time': 0,
        'status': 'unknown'
    }
    
    try:
        # Run the test script
        start_time = datetime.now()
        
        cmd = [
            'python', 'scripts/run_tests.py'
        ]
        
        st.write(f"Debug: Running command: {' '.join(cmd)}")
        
        # Add timeout and better error handling
        try:
            process = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            end_time = datetime.now()
            results['execution_time'] = (end_time - start_time).total_seconds()
            results['status'] = 'success' if process.returncode == 0 else 'failed'
            results['stdout'] = process.stdout
            results['stderr'] = process.stderr
            results['return_code'] = process.returncode
            
            st.write(f"Debug: Process completed with return code: {process.returncode}")
            st.write(f"Debug: stdout length: {len(process.stdout)}")
            st.write(f"Debug: stderr length: {len(process.stderr)}")
            
        except subprocess.TimeoutExpired:
            st.write("Debug: Test script timed out, trying direct pytest execution...")
            # Fallback: run pytest directly
            return run_pytest_directly(project_root, results)
        
        # Parse test results from the JSON file
        test_results_file = project_root / 'build' / 'test_results.json'
        if test_results_file.exists():
            try:
                with open(test_results_file, 'r') as f:
                    test_data = json.load(f)
                    results['test_results'] = test_data
                    st.write(f"Debug: Test results loaded from {test_results_file}")
            except Exception as e:
                results['test_results_error'] = str(e)
                st.write(f"Debug: Error loading test results: {e}")
        else:
            st.write(f"Debug: Test results file not found: {test_results_file}")
        
        # Parse coverage data if available
        coverage_file = project_root / 'build' / 'coverage.json'
        if coverage_file.exists():
            try:
                with open(coverage_file, 'r') as f:
                    results['coverage_data'] = json.load(f)
                    st.write(f"Debug: Coverage data loaded from {coverage_file}")
            except Exception as e:
                results['coverage_error'] = str(e)
                st.write(f"Debug: Error loading coverage data: {e}")
        else:
            st.write(f"Debug: Coverage file not found: {coverage_file}")
                
    except Exception as e:
        results['status'] = 'error'
        results['error'] = str(e)
        st.write(f"Debug: Exception during test execution: {e}")
    
    return results


def run_pytest_directly(project_root: Path, results: Dict) -> Dict:
    """
    Run pytest directly as a fallback method.
    """
    st.write("Debug: Running pytest directly...")
    
    try:
        cmd = [
            sys.executable, '-m', 'pytest', 'test', '-v',
            '--cov=src', '--cov-report=term-missing'
        ]
        
        process = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8',
            errors='replace'
        )
        
        results['status'] = 'success' if process.returncode == 0 else 'failed'
        results['stdout'] = process.stdout
        results['stderr'] = process.stderr
        results['return_code'] = process.returncode
        
        st.write(f"Debug: Direct pytest completed with return code: {process.returncode}")
        
        # Create a simple test results structure
        results['test_results'] = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'passed': process.stdout.count('PASSED'),
                'failed': process.stdout.count('FAILED'),
                'skipped': process.stdout.count('SKIPPED'),
                'error': 0,
                'total': process.stdout.count('PASSED') + process.stdout.count('FAILED') + process.stdout.count('SKIPPED')
            },
            'tests': [],
            'stdout': process.stdout,
            'stderr': process.stderr
        }
        
        return results
         
    except Exception as e:
        results['status'] = 'error'
        results['error'] = f"Direct pytest failed: {str(e)}"
        st.write(f"Debug: Direct pytest exception: {e}")
        return results


def parse_coverage_data(coverage_data: Dict) -> Dict:
    """
    Parse coverage data into a more readable format.
    
    Args:
        coverage_data: Raw coverage data from pytest-cov
        
    Returns:
        Parsed coverage information
    """
    if not coverage_data:
        return {}
    
    parsed = {
        'summary': {},
        'files': []
    }
    
    try:
        # Extract summary information
        if 'totals' in coverage_data:
            totals = coverage_data['totals']
            parsed['summary'] = {
                'lines_covered': totals.get('covered_lines', 0),
                'lines_total': totals.get('num_statements', 0),
                'coverage_percentage': totals.get('percent_covered', 0),
                'missing_lines': totals.get('missing_lines', 0)
            }
        
        # Extract file-level coverage
        if 'files' in coverage_data:
            for file_path, file_data in coverage_data['files'].items():
                normalized_path = file_path.replace('\\', '/').replace('\\', '/')
                if normalized_path.startswith('src/'):
                    parsed['files'].append({
                        'file': normalized_path,
                        'lines_covered': file_data.get('summary', {}).get('covered_lines', 0),
                        'lines_total': file_data.get('summary', {}).get('num_statements', 0),
                        'coverage_percentage': file_data.get('summary', {}).get('percent_covered', 0)
                    })
    except Exception:
        pass
    return parsed


def display_test_summary(results: Dict):
    """
    Display a summary of test results.
    
    Args:
        results: Test results dictionary
    """
    st.subheader("📊 Test Execution Summary")
    
    # Show when tests were run
    if 'file_timestamp' in results and results['file_timestamp'] != 'unknown':
        try:
            # Parse the timestamp and format it nicely
            from datetime import datetime
            timestamp = datetime.fromisoformat(results['file_timestamp'].replace('Z', '+00:00'))
            formatted_time = timestamp.strftime("%B %d, %Y at %I:%M:%S %p")
            st.info(f"🕒 **Last run:** {formatted_time}")
        except:
            st.info(f"🕒 **Last run:** {results['file_timestamp']}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_emoji = "✅" if results['status'] == 'success' else "❌"
        st.metric("Status", f"{status_emoji} {results['status'].title()}")
    
    with col2:
        execution_time = results.get('execution_time', 0)
        st.metric("Execution Time", f"{execution_time:.2f}s")
    
    with col3:
        if 'test_results' in results and 'summary' in results['test_results']:
            total_tests = results['test_results']['summary'].get('total', 0)
            st.metric("Total Tests", total_tests)
        else:
            st.metric("Total Tests", "N/A")
    
    with col4:
        if 'coverage_data' in results and results['coverage_data']:
            coverage = parse_coverage_data(results['coverage_data'])
            if 'summary' in coverage:
                coverage_pct = coverage['summary'].get('coverage_percentage', 0)
                st.metric("Coverage", f"{coverage_pct:.1f}%")
            else:
                st.metric("Coverage", "N/A")
        else:
            st.metric("Coverage", "N/A")


def display_coverage_details(coverage_data: Dict):
    """
    Display detailed coverage information.
    
    Args:
        coverage_data: Coverage data dictionary
    """
    if not coverage_data:
        st.warning("No coverage data available")
        return
    
    parsed_coverage = parse_coverage_data(coverage_data)
    
    st.subheader("📈 Code Coverage Details")
    
    # Overall coverage
    if 'summary' in parsed_coverage:
        summary = parsed_coverage['summary']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Lines Covered", 
                f"{summary.get('lines_covered', 0)} / {summary.get('lines_total', 0)}"
            )
        
        with col2:
            coverage_pct = summary.get('coverage_percentage', 0)
            st.metric("Coverage %", f"{coverage_pct:.1f}%")
        
        with col3:
            st.metric("Missing Lines", summary.get('missing_lines', 0))
        
        # Coverage progress bar
        if summary.get('lines_total', 0) > 0:
            coverage_ratio = summary.get('lines_covered', 0) / summary.get('lines_total', 0)
            st.progress(coverage_ratio)
    
    # Show summary table like pytest output (now after metrics)
    if 'files' in coverage_data:
        summary_rows = []
        for file_path, file_data in coverage_data['files'].items():
            summary = file_data.get('summary', {})
            coverage_pct = summary.get('percent_covered_display', summary.get('percent_covered', 0))
            summary_rows.append({
                "File": file_path.replace("\\", "/"),
                "Stmts": summary.get("num_statements", 0),
                "Miss": summary.get("missing_lines", 0),
                "Cover": coverage_pct,  # Keep as numeric for sorting
                "Missing": ", ".join(str(x) for x in file_data.get("missing_lines", []))
            })
        if summary_rows:
            import pandas as pd
            df = pd.DataFrame(summary_rows)
            st.subheader("📋 Coverage Summary Table")
            
            # Configure AgGrid options
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_default_column(
                sortable=True,
                filterable=True,
                resizable=True,
                editable=False
            )
            gb.configure_column("File", width=300, pinned="left")
            gb.configure_column("Stmts", width=80, type=["numericColumn", "numberColumnFilter"])
            gb.configure_column("Miss", width=80, type=["numericColumn", "numberColumnFilter"])
            gb.configure_column("Cover", header_name="Cover %", width=100, type=["numericColumn", "numberColumnFilter"])
            gb.configure_column("Missing", width=200)
            
            grid_options = gb.build()
            
            # Display the AgGrid
            grid_response = AgGrid(
                df,
                gridOptions=grid_options,
                data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                theme="streamlit"
            )

    # File-level coverage
    if parsed_coverage.get('files'):
        st.subheader("📁 File-Level Coverage")
        
        files_df = pd.DataFrame(parsed_coverage['files'])
        files_df = files_df.sort_values('coverage_percentage', ascending=False)
        
        # Configure AgGrid options for file-level coverage
        gb_files = GridOptionsBuilder.from_dataframe(files_df)
        gb_files.configure_default_column(
            sortable=True,
            filterable=True,
            resizable=True,
            editable=False
        )
        gb_files.configure_column("file", header_name="File", width=300, pinned="left")
        gb_files.configure_column("lines_covered", header_name="Lines Covered", width=120, type=["numericColumn", "numberColumnFilter"])
        gb_files.configure_column("lines_total", header_name="Total Lines", width=120, type=["numericColumn", "numberColumnFilter"])
        gb_files.configure_column("coverage_percentage", header_name="Coverage %", width=120, type=["numericColumn", "numberColumnFilter"])
        
        grid_options_files = gb_files.build()
        
        # Display the AgGrid for file-level coverage
        grid_response_files = AgGrid(
            files_df,
            gridOptions=grid_options_files,
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            theme="streamlit"
        )


def display_test_results(test_results: Dict):
    """
    Display detailed test results.
    
    Args:
        test_results: Test results dictionary
    """
    if not test_results:
        st.warning("No test results available")
        return
    
    st.subheader("🧪 Test Results Details")
    
    # Summary statistics
    if 'summary' in test_results:
        summary = test_results['summary']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Passed", summary.get('passed', 0))
        
        with col2:
            st.metric("Failed", summary.get('failed', 0))
        
        with col3:
            st.metric("Skipped", summary.get('skipped', 0))
        
        with col4:
            st.metric("Errors", summary.get('error', 0))
    
    # Test outcomes
    if 'tests' in test_results and test_results['tests']:
        st.subheader("📋 Test Outcomes")
        
        tests = test_results['tests']
        
        # Group tests by outcome
        outcomes = {}
        for test in tests:
            outcome = test.get('outcome', 'unknown')
            if outcome not in outcomes:
                outcomes[outcome] = []
            outcomes[outcome].append(test)
        
        # Display each outcome group
        for outcome, test_list in outcomes.items():
            with st.expander(f"{outcome.title()} Tests ({len(test_list)})"):
                for test in test_list:
                    test_name = test.get('name', 'Unknown Test')
                    test_file = test.get('file', 'Unknown File')
                    
                    if outcome == 'passed':
                        st.success(f"✅ {test_file}::{test_name}")
                    elif outcome == 'failed':
                        st.error(f"❌ {test_file}::{test_name}")
                    elif outcome == 'skipped':
                        st.warning(f"⏭️ {test_file}::{test_name}")
                    else:
                        st.info(f"❓ {test_file}::{test_name}")
    else:
        st.info("No individual test results parsed from output")


def display_test_execution_logs(results: Dict):
    """
    Display test execution logs.
    
    Args:
        results: Test results dictionary
    """
    st.subheader("📝 Execution Logs")
    
    has_logs = False
    
    # Show stdout
    if results.get('stdout'):
        with st.expander("Standard Output", expanded=True):
            st.code(results['stdout'], language='text')
        has_logs = True
    
    # Show stderr
    if results.get('stderr'):
        with st.expander("Standard Error"):
            st.code(results['stderr'], language='text')
        has_logs = True
    
    # Show errors
    if results.get('error'):
        with st.expander("Execution Errors"):
            st.error(results['error'])
        has_logs = True
    
    # Show message if no logs available
    if not has_logs:
        st.info("No execution logs available. The test results were loaded from a JSON file that doesn't contain stdout/stderr output.")
        st.info("To see execution logs, run tests directly from the command line: `python scripts/run_tests.py`")


def load_existing_test_results() -> Dict:
    """
    Load existing test results from the JSON file.
    
    Returns:
        Dict containing test results and metadata
    """
    project_root = Path(__file__).parent.parent.parent.parent
    test_results_file = project_root / 'build' / 'test_results.json'
    coverage_file = project_root / 'build' / 'coverage.json'
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'test_results': {},
        'coverage_data': {},
        'status': 'unknown',
        'source': 'file',
        'stdout': '',
        'stderr': '',
        'error': '',
        'execution_time': 0  # Default to 0 if not available
    }
    
    if test_results_file.exists():
        try:
            with open(test_results_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
                results['test_results'] = test_data
                results['status'] = 'success'
                results['file_timestamp'] = test_data.get('timestamp', 'unknown')
                # Load execution time from the JSON file
                results['execution_time'] = test_data.get('execution_time', 0)
                # Load execution logs from the JSON file
                results['stdout'] = test_data.get('stdout', '')
                results['stderr'] = test_data.get('stderr', '')
                results['error'] = test_data.get('error', '')
        except Exception as e:
            results['status'] = 'error'
            results['error'] = f"Error loading test results: {str(e)}"
            st.error(f"❌ Error loading test results: {e}")
    else:
        results['status'] = 'no_file'
        results['message'] = f"No test results file found at {test_results_file}"
        st.warning(f"⚠️ No test results file found. Run 'python scripts/run_tests.py' to generate results.")
    # Load coverage data if available
    if coverage_file.exists():
        try:
            with open(coverage_file, 'r', encoding='utf-8') as f:
                results['coverage_data'] = json.load(f)
        except Exception as e:
            results['coverage_error'] = str(e)
    return results


def load_coverage_data():
    """Always load the latest coverage data from disk."""
    with open("build/coverage.json", "r") as f:
        return json.load(f)


def render_testing_results():
    """
    Main function to render the testing results page.
    """
    st.title("🧪 Testing Results")
    st.markdown("---")
    
    # Create two columns for buttons
    col1, col2 = st.columns(2)
    
    with col1:
        # Button to refresh from existing JSON file
        if st.button("🔄 Refresh from JSON"):
            st.rerun()
    
    with col2:
        # Button to run tests and update results
        if st.button("🚀 Run Tests & Update"):
            with st.spinner("Running tests... This may take a few moments."):
                # Run the tests using the existing function
                test_results = run_tests_and_get_results()
                
                if test_results['status'] == 'success':
                    st.success("✅ Tests completed successfully!")
                else:
                    st.error("❌ Tests completed with errors.")
                
                # Force a rerun to show the updated results
                st.rerun()
    
    # Load existing test results
    results = load_existing_test_results()
    
    # Display summary if we have results
    if results['status'] == 'success' and results['test_results']:
        display_test_summary(results)
        
        # Create tabs for different sections
        tab1, tab2, tab3 = st.tabs([
            "📊 Coverage", 
            "🧪 Test Results", 
            "📝 Logs"
            # "📋 Raw Data"  # Commented out to simplify UI
        ])
        
        with tab1:
            display_coverage_details(results.get('coverage_data', {}))
        
        with tab2:
            display_test_results(results.get('test_results', {}))
        
        with tab3:
            display_test_execution_logs(results)
        
        # with tab4:
        #     st.subheader("🔍 Raw Test Data")
        #     st.json(results['test_results'])
    
    # Show instructions if no results
    elif results['status'] == 'no_file':
        st.info("""
        • Click "🔄 Refresh from JSON" to load existing test results
        • Click "🚀 Run Tests & Update" to run tests and generate new results
        """)
        
        st.code("python scripts/run_tests.py", language="bash")
    
    # Show error if there was a problem loading
    elif results['status'] == 'error':
        st.error("There was an error loading the test results. Please check the file and try again.") 