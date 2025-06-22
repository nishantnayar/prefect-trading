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
        
        # Extract file-level coverage and categorize by coverage level
        if 'files' in coverage_data:
            for file_path, file_data in coverage_data['files'].items():
                normalized_path = file_path.replace('\\', '/')
                if normalized_path.startswith('src/'):
                    summary = file_data.get('summary', {})
                    coverage_pct = summary.get('percent_covered', 0)
                    
                    file_info = {
                        'file': normalized_path,
                        'lines_covered': summary.get('covered_lines', 0),
                        'lines_total': summary.get('num_statements', 0),
                        'coverage_percentage': coverage_pct,
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
                            'total_lines': 0,
                            'covered_lines': 0,
                            'coverage_percentage': 0
                        }
                    
                    parsed['modules'][module]['files'] += 1
                    parsed['modules'][module]['total_lines'] += summary.get('num_statements', 0)
                    parsed['modules'][module]['covered_lines'] += summary.get('covered_lines', 0)
                    
            # Calculate module-level coverage percentages
            for module in parsed['modules']:
                module_data = parsed['modules'][module]
                if module_data['total_lines'] > 0:
                    module_data['coverage_percentage'] = (
                        module_data['covered_lines'] / module_data['total_lines'] * 100
                    )
                    
    except Exception as e:
        st.error(f"Error parsing coverage data: {e}")
        return {}
    
    return parsed


def display_coverage_overview(coverage_data: Dict):
    """
    Display a comprehensive coverage overview with multiple visualizations.
    
    Args:
        coverage_data: Coverage data dictionary
    """
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
        
        # Coverage progress bar with color coding
        if summary.get('lines_total', 0) > 0:
            coverage_ratio = summary.get('lines_covered', 0) / summary.get('lines_total', 0)
            
            # Color code based on coverage level
            if coverage_ratio >= 0.9:
                color = "green"
            elif coverage_ratio >= 0.8:
                color = "blue"
            elif coverage_ratio >= 0.6:
                color = "orange"
            else:
                color = "red"
            
            st.progress(coverage_ratio)
            st.caption(f"Coverage Level: {get_coverage_level(coverage_ratio)}")
    
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
    
    # Module-level coverage
    if 'modules' in parsed_coverage and parsed_coverage['modules']:
        st.subheader("📁 Module Coverage")
        
        modules_data = []
        for module, data in parsed_coverage['modules'].items():
            modules_data.append({
                'Module': module.title(),
                'Files': data['files'],
                'Coverage %': round(data['coverage_percentage'], 1),
                'Lines Covered': data['covered_lines'],
                'Total Lines': data['total_lines']
            })
        
        if modules_data:
            modules_df = pd.DataFrame(modules_data)
            modules_df = modules_df.sort_values('Coverage %', ascending=False)
            
            # Configure AgGrid for modules
            gb_modules = GridOptionsBuilder.from_dataframe(modules_df)
            gb_modules.configure_default_column(
                sortable=True,
                filterable=True,
                resizable=True,
                editable=False
            )
            gb_modules.configure_column("Module", width=150, pinned="left")
            gb_modules.configure_column("Files", width=80, type=["numericColumn", "numberColumnFilter"])
            gb_modules.configure_column("Coverage %", width=120, type=["numericColumn", "numberColumnFilter"])
            gb_modules.configure_column("Lines Covered", width=120, type=["numericColumn", "numberColumnFilter"])
            gb_modules.configure_column("Total Lines", width=120, type=["numericColumn", "numberColumnFilter"])
            
            grid_options_modules = gb_modules.build()
            
            AgGrid(
                modules_df,
                gridOptions=grid_options_modules,
                data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                theme="streamlit"
            )


def display_coverage_details(coverage_data: Dict):
    """
    Display detailed coverage information with file-level breakdown.
    
    Args:
        coverage_data: Coverage data dictionary
    """
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
        files_df = files_df[['file', 'Coverage Level', 'Coverage %', 'lines_covered', 'lines_total', 'missing_lines', 'missing_line_numbers']]
        files_df.columns = ['File', 'Level', 'Coverage %', 'Covered', 'Total', 'Missing', 'Missing Lines']
        
        # Configure AgGrid options
        gb = GridOptionsBuilder.from_dataframe(files_df)
        gb.configure_default_column(
            sortable=True,
            filterable=True,
            resizable=True,
            editable=False
        )
        gb.configure_column("File", width=300, pinned="left")
        gb.configure_column("Level", width=100)
        gb.configure_column("Coverage %", width=100, type=["numericColumn", "numberColumnFilter"])
        gb.configure_column("Covered", width=80, type=["numericColumn", "numberColumnFilter"])
        gb.configure_column("Total", width=80, type=["numericColumn", "numberColumnFilter"])
        gb.configure_column("Missing", width=80, type=["numericColumn", "numberColumnFilter"])
        gb.configure_column("Missing Lines", width=200)
        
        grid_options = gb.build()
        
        # Display the AgGrid
        grid_response = AgGrid(
            files_df,
            gridOptions=grid_options,
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            theme="streamlit"
        )
        
        # Show files that need attention
        low_coverage_files = files_df[files_df['Coverage %'] < 80]
        if not low_coverage_files.empty:
            st.subheader("⚠️ Files Needing Coverage Improvement")
            st.dataframe(low_coverage_files[['File', 'Coverage %', 'Missing']], use_container_width=True)


def get_coverage_level(coverage_percentage: float) -> str:
    """
    Get coverage level description based on percentage.
    
    Args:
        coverage_percentage: Coverage percentage (0-100)
        
    Returns:
        Coverage level description
    """
    if coverage_percentage >= 90:
        return "🟢 Excellent"
    elif coverage_percentage >= 80:
        return "🔵 Good"
    elif coverage_percentage >= 60:
        return "🟡 Fair"
    else:
        return "🔴 Poor"


def display_coverage_insights(coverage_data: Dict):
    """
    Display insights and recommendations based on coverage data.
    
    Args:
        coverage_data: Coverage data dictionary
    """
    if not coverage_data:
        return
    
    parsed_coverage = parse_coverage_data(coverage_data)
    
    if not parsed_coverage:
        return
    
    st.subheader("💡 Coverage Insights & Recommendations")
    
    insights = []
    recommendations = []
    
    # Analyze overall coverage
    if 'summary' in parsed_coverage:
        summary = parsed_coverage['summary']
        coverage_pct = summary.get('coverage_percentage', 0)
        
        if coverage_pct >= 90:
            insights.append("🎉 Excellent overall coverage! Your codebase is well-tested.")
        elif coverage_pct >= 80:
            insights.append("👍 Good coverage! Consider improving coverage in specific areas.")
        elif coverage_pct >= 60:
            insights.append("⚠️ Fair coverage. Focus on increasing coverage in critical modules.")
        else:
            insights.append("🚨 Low coverage detected. Prioritize adding tests for critical functionality.")
    
    # Analyze file distribution
    if 'coverage_levels' in parsed_coverage:
        levels = parsed_coverage['coverage_levels']
        total_files = sum(levels.values())
        
        if total_files > 0:
            poor_pct = (levels['poor'] / total_files) * 100
            if poor_pct > 20:
                insights.append(f"⚠️ {poor_pct:.1f}% of files have poor coverage (<60%)")
                recommendations.append("Focus on files with <60% coverage first")
            
            excellent_pct = (levels['excellent'] / total_files) * 100
            if excellent_pct >= 70:
                insights.append("🌟 Most files have excellent coverage!")
    
    # Module-specific insights
    if 'modules' in parsed_coverage:
        low_coverage_modules = []
        for module, data in parsed_coverage['modules'].items():
            if data['coverage_percentage'] < 70:
                low_coverage_modules.append(module)
        
        if low_coverage_modules:
            insights.append(f"📁 Modules needing attention: {', '.join(low_coverage_modules)}")
            recommendations.append(f"Prioritize testing in: {', '.join(low_coverage_modules)}")
    
    # Display insights
    if insights:
        st.write("**Key Insights:**")
        for insight in insights:
            st.write(f"• {insight}")
    
    # Display recommendations
    if recommendations:
        st.write("**Recommendations:**")
        for rec in recommendations:
            st.write(f"• {rec}")
    
    # Coverage improvement tips
    st.write("**General Tips:**")
    st.write("• Focus on critical business logic and error handling paths")
    st.write("• Test edge cases and boundary conditions")
    st.write("• Consider integration tests for complex workflows")
    st.write("• Use parameterized tests to cover multiple scenarios")


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
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Coverage Overview", 
            "📋 Coverage Details",
            "🧪 Test Results", 
            "📝 Logs"
        ])
        
        with tab1:
            display_coverage_overview(results.get('coverage_data', {}))
            display_coverage_insights(results.get('coverage_data', {}))
        
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