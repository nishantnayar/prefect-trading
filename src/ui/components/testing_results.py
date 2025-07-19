"""
Testing Results Component

Displays test results and allows running tests from the UI.
Enhanced version with coverage visualization and comprehensive reporting.
"""

import streamlit as st
import subprocess
import sys
import os
import json
import re
from pathlib import Path
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple

def run_test_command(test_path=None, test_name=None):
    """Run a specific test or all tests and return results"""
    try:
        # Add project root to Python path
        project_root = Path(__file__).parent.parent.parent.parent
        python_path = sys.executable
        
        # Use the consolidated test runner
        if test_path:
            # Run specific test file
            cmd = [python_path, "scripts/run_tests.py", "--test-path", str(test_path)]
        elif test_name:
            # Run specific test by name
            cmd = [python_path, "scripts/run_tests.py", "--test-path", f"test/{test_name}"]
        else:
            # Run all tests with JSON output
            cmd = [python_path, "scripts/run_tests.py"]
        
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=300  # 5 minute timeout
        )
        
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout or '',
            'stderr': result.stderr or '',
            'returncode': result.returncode
        }
    
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Test execution timed out after 5 minutes',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Error running tests: {str(e)}',
            'returncode': -1
        }

def load_existing_test_results() -> Dict:
    """Load existing test results from JSON files"""
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
        'execution_time': 0
    }
    
    # Load test results
    if test_results_file.exists():
        try:
            with open(test_results_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
                results['test_results'] = test_data
                results['status'] = 'success'
                results['file_timestamp'] = test_data.get('timestamp', 'unknown')
                results['execution_time'] = test_data.get('execution_time', 0)
                results['stdout'] = test_data.get('stdout', '')
                results['stderr'] = test_data.get('stderr', '')
        except Exception as e:
            results['status'] = 'error'
            results['error'] = f"Error loading test results: {str(e)}"
    else:
        results['status'] = 'no_file'
        results['message'] = f"No test results file found at {test_results_file}"
    
    # Load coverage data
    if coverage_file.exists():
        try:
            with open(coverage_file, 'r', encoding='utf-8') as f:
                results['coverage_data'] = json.load(f)
        except Exception as e:
            results['coverage_error'] = str(e)
    
    return results

def parse_coverage_data(coverage_data: Dict) -> Dict:
    """Parse coverage data into a more readable format"""
    if not coverage_data:
        return {}
    
    parsed = {
        'summary': {},
        'files': [],
        'modules': {},
        'coverage_levels': {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
    }
    
    try:
        # Extract summary information
        if 'totals' in coverage_data:
            totals = coverage_data['totals']
            parsed['summary'] = {
                'lines_covered': totals.get('covered_lines', 0),
                'lines_total': totals.get('num_statements', 0),
                'coverage_percentage': totals.get('percent_covered', 0),
                'missing_lines': totals.get('missing_lines', 0),
                'coverage_display': totals.get('percent_covered_display', '0')
            }
        
        # Extract file-level coverage
        if 'files' in coverage_data:
            for file_path, file_data in coverage_data['files'].items():
                normalized_path = file_path.replace('\\', '/')
                if normalized_path.startswith('src/'):
                    summary = file_data.get('summary', {})
                    coverage_pct = summary.get('percent_covered', 0)
                    
                    file_info = {
                        'file': normalized_path,
                        'coverage_percentage': coverage_pct,
                        'lines_covered': summary.get('covered_lines', 0),
                        'lines_total': summary.get('num_statements', 0),
                        'missing_lines': summary.get('missing_lines', 0),
                        'missing_line_numbers': file_data.get('missing_lines', [])
                    }
                    parsed['files'].append(file_info)
                    
                    # Categorize by coverage level
                    if coverage_pct >= 90:
                        parsed['coverage_levels']['excellent'] += 1
                    elif coverage_pct >= 80:
                        parsed['coverage_levels']['good'] += 1
                    elif coverage_pct >= 60:
                        parsed['coverage_levels']['fair'] += 1
                    else:
                        parsed['coverage_levels']['poor'] += 1
                    
                    # Group by module
                    module = normalized_path.split('/')[1] if len(normalized_path.split('/')) > 1 else 'other'
                    if module not in parsed['modules']:
                        parsed['modules'][module] = {
                            'files': 0,
                            'covered_lines': 0,
                            'total_lines': 0
                        }
                    parsed['modules'][module]['files'] += 1
                    parsed['modules'][module]['covered_lines'] += summary.get('covered_lines', 0)
                    parsed['modules'][module]['total_lines'] += summary.get('num_statements', 0)
        
        # Calculate module coverage percentages
        for module, data in parsed['modules'].items():
            if data['total_lines'] > 0:
                data['coverage_percentage'] = (data['covered_lines'] / data['total_lines']) * 100
            else:
                data['coverage_percentage'] = 0
    
    except Exception as e:
        st.error(f"Error parsing coverage data: {e}")
    
    return parsed

def get_coverage_level(coverage_percentage: float) -> str:
    """Get coverage level description based on percentage"""
    if coverage_percentage >= 90:
        return "🟢 Excellent"
    elif coverage_percentage >= 80:
        return "🔵 Good"
    elif coverage_percentage >= 60:
        return "🟡 Fair"
    else:
        return "🔴 Poor"

def display_coverage_overview(coverage_data: Dict):
    """Display a comprehensive coverage overview"""
    if not coverage_data:
        st.warning("No coverage data available")
        return
    
    parsed_coverage = parse_coverage_data(coverage_data)
    
    if not parsed_coverage:
        st.error("Failed to parse coverage data")
        return
    
    st.subheader("📈 Code Coverage Overview")
    
    # Overall coverage metrics
    if 'summary' in parsed_coverage:
        summary = parsed_coverage['summary']
        
        # Main metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            coverage_pct = summary.get('coverage_percentage', 0)
            st.metric(
                "Overall Coverage", 
                f"{coverage_pct:.1f}%",
                delta=f"{summary.get('lines_covered', 0)}/{summary.get('lines_total', 0)} lines"
            )
        
        with col2:
            st.metric("Lines Covered", summary.get('lines_covered', 0))
        
        with col3:
            st.metric("Total Lines", summary.get('lines_total', 0))
        
        with col4:
            st.metric("Missing Lines", summary.get('missing_lines', 0))
        
        # Coverage progress bar
        if summary.get('lines_total', 0) > 0:
            coverage_ratio = summary.get('lines_covered', 0) / summary.get('lines_total', 0)
            st.progress(coverage_ratio)
            st.caption(f"Coverage Level: {get_coverage_level(coverage_ratio * 100)}")
    
    # Coverage distribution by level
    if 'coverage_levels' in parsed_coverage:
        st.subheader("📊 Coverage Distribution")
        
        levels = parsed_coverage['coverage_levels']
        total_files = sum(levels.values())
        
        if total_files > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                excellent_pct = (levels['excellent'] / total_files) * 100
                st.metric("Excellent (≥90%)", f"{levels['excellent']} files", f"{excellent_pct:.1f}%")
            
            with col2:
                good_pct = (levels['good'] / total_files) * 100
                st.metric("Good (80-89%)", f"{levels['good']} files", f"{good_pct:.1f}%")
            
            with col3:
                fair_pct = (levels['fair'] / total_files) * 100
                st.metric("Fair (60-79%)", f"{levels['fair']} files", f"{fair_pct:.1f}%")
            
            with col4:
                poor_pct = (levels['poor'] / total_files) * 100
                st.metric("Poor (<60%)", f"{levels['poor']} files", f"{poor_pct:.1f}%")

def display_coverage_details(coverage_data: Dict):
    """Display detailed coverage information"""
    if not coverage_data:
        st.warning("No coverage data available")
        return
    
    parsed_coverage = parse_coverage_data(coverage_data)
    
    if not parsed_coverage:
        st.error("Failed to parse coverage data")
        return
    
    st.subheader("📋 Detailed Coverage Report")
    
    # File-level coverage table
    if parsed_coverage.get('files'):
        files_df = pd.DataFrame(parsed_coverage['files'])
        files_df = files_df.sort_values('coverage_percentage', ascending=False)
        
        # Add coverage level column
        files_df['Coverage Level'] = files_df['coverage_percentage'].apply(get_coverage_level)
        files_df['Coverage %'] = files_df['coverage_percentage'].round(1)
        
        # Reorder columns
        files_df = files_df[['file', 'Coverage Level', 'Coverage %', 'lines_covered', 'lines_total', 'missing_lines']]
        files_df.columns = ['File', 'Level', 'Coverage %', 'Covered', 'Total', 'Missing']
        
        # Display file coverage details
        st.dataframe(files_df, use_container_width=True)
        
        # Show files that need attention
        low_coverage_files = files_df[files_df['Coverage %'] < 80]
        if not low_coverage_files.empty:
            st.subheader("⚠️ Files Needing Coverage Improvement")
            st.dataframe(low_coverage_files[['File', 'Coverage %', 'Missing']], use_container_width=True)

def display_test_summary(results: Dict):
    """Display test summary metrics"""
    if not results or not results.get('test_results'):
        st.info("No test results available")
        return
    
    test_results = results['test_results']
    
    st.subheader("📊 Test Summary")
    
    # Execution info
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        execution_time = results.get('execution_time', 0)
        st.metric("Execution Time", f"{execution_time:.2f}s")
    
    with col2:
        timestamp = test_results.get('timestamp', 'Unknown')
        if timestamp != 'Unknown':
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            st.metric("Last Run", dt.strftime('%Y-%m-%d %H:%M'))
        else:
            st.metric("Last Run", "Unknown")
    
    with col3:
        status = results.get('status', 'unknown')
        if status == 'success':
            st.success("✅ Status: Success")
        else:
            st.error("❌ Status: Failed")
    
    with col4:
        return_code = test_results.get('return_code', -1)
        st.metric("Return Code", return_code)
    
    # Test results summary
    if 'summary' in test_results:
        summary = test_results['summary']
        
        st.subheader("🧪 Test Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            passed = summary.get('passed', 0)
            st.metric("✅ Passed", passed)
        
        with col2:
            failed = summary.get('failed', 0)
            st.metric("❌ Failed", failed)
        
        with col3:
            skipped = summary.get('skipped', 0)
            st.metric("⏭️ Skipped", skipped)
        
        with col4:
            total = summary.get('total', 0)
            success_rate = (passed / total * 100) if total > 0 else 0
            st.metric("📊 Success Rate", f"{success_rate:.1f}%")

def display_test_results(test_results: Dict):
    """Display detailed test results"""
    if not test_results or 'tests' not in test_results:
        st.info("No individual test results available")
        return
    
    tests = test_results['tests']
    
    if not tests:
        st.info("No individual test results parsed from output")
        return
    
    st.subheader("📋 Test Outcomes")
    
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

def display_test_execution_logs(results: Dict):
    """Display test execution logs"""
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
        st.info("No execution logs available. Run tests to see detailed output.")

def render_testing_results():
    """Main function to render the testing results page"""
    st.markdown('<h1 class="main-header">🧪 Testing Results</h1>', unsafe_allow_html=True)
    
    # Create two columns for buttons
    col1, col2 = st.columns(2)
    
    with col1:
        # Button to refresh from existing JSON file
        if st.button("🔄 Refresh from JSON", type="primary"):
            st.rerun()
    
    with col2:
        # Button to run tests and update results
        if st.button("🚀 Run Tests & Update", type="primary"):
            with st.spinner("Running tests... This may take a few moments."):
                # Run the tests
                test_results = run_test_command()
                
                if test_results.get('success'):
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
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Coverage Overview", 
            "📋 Coverage Details",
            "🧪 Test Results", 
            "📝 Logs"
        ])
        
        with tab1:
            display_coverage_overview(results.get('coverage_data', {}))
        
        with tab2:
            display_coverage_details(results.get('coverage_data', {}))
        
        with tab3:
            display_test_results(results.get('test_results', {}))
        
        with tab4:
            display_test_execution_logs(results)
    
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
    
    # Test information section
    st.subheader("ℹ️ Test Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Available Test Categories:**")
        test_categories = {
            'All Tests': None,
            'Database Tests': 'database/',
            'Data Tests': 'data/',
            'Basic Functionality': 'test_basic_functionality.py',
            'Pair Analysis': 'test_pair_analysis.py',
            'MLflow Manager': 'test_mlflow_manager.py',
            'WebSocket Symbols': 'test_websocket_symbols.py'
        }
        
        for category, path in test_categories.items():
            if path:
                st.write(f"• **{category}**: `{path}`")
            else:
                st.write(f"• **{category}**: All tests")
    
    with col2:
        st.write("**Test Status Meanings:**")
        st.write("• ✅ **PASSED**: Test completed successfully")
        st.write("• ❌ **FAILED**: Test failed with assertions")
        st.write("• ⏭️ **SKIPPED**: Test was skipped")
        st.write("• ⚠️ **ERROR**: Test encountered an error")
    
    # Quick test status
    st.subheader("⚡ Quick Test Status")
    
    # Check if pytest is available
    try:
        import pytest
        st.success("✅ pytest is available")
    except ImportError:
        st.error("❌ pytest is not installed")
        st.info("Install pytest with: `pip install pytest`")
    
    # Check test directory
    test_dir = Path("test")
    if test_dir.exists():
        test_files = list(test_dir.rglob("test_*.py"))
        st.success(f"✅ Found {len(test_files)} test files")
    else:
        st.error("❌ Test directory not found") 