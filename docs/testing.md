# Testing Documentation

## Overview

The Prefect Trading System includes a comprehensive testing strategy with automated test execution, coverage analysis, and a dedicated Testing page in the Streamlit UI for real-time test results visualization.

> **📋 Quick Links**: [Architecture Decisions](architecture-decisions.md) | [Setup Guide](setup.md) | [Development Guide](development.md) | [UI Documentation](ui.md) | [API Documentation](api.md)

## Testing Strategy

### 1. Test Types
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **End-to-End Tests**: Complete workflow testing
- **UI Tests**: Streamlit interface testing
- **Performance Tests**: Load and stress testing

### 2. Testing Tools
- **Pytest**: Primary testing framework
- **Pytest-cov**: Coverage analysis
- **Mock**: Component isolation
- **Streamlit Testing**: UI component testing
- **Streamlit Dataframes**: Advanced table functionality for results display

### 3. Coverage Analysis
- **Line Coverage**: Statement-level coverage tracking
- **File-level Analysis**: Detailed breakdown by source files
- **Coverage Visualization**: Interactive coverage reports
- **Coverage Insights**: Automated recommendations and analysis

## Testing Page Features

### 1. Real-time Test Results
The Testing page (`src/ui/components/testing_results.py`) provides:
- **Test Execution**: Run tests directly from the UI
- **Coverage Overview**: Visual coverage metrics and insights
- **File-level Details**: Interactive Streamlit dataframes with sorting/filtering
- **Execution Logs**: Detailed stdout, stderr, and error information
- **Performance Metrics**: Test execution time and statistics

### 2. Coverage Visualization
```python
def display_coverage_overview(coverage_data: Dict):
    """
    Display overall coverage metrics with visual indicators.
    
    Features:
    - Overall coverage percentage with progress bar
    - Color-coded coverage levels (red/yellow/green)
    - Coverage distribution analysis
    - Automated insights and recommendations
    """
```

### 3. Interactive Tables
```python
def display_coverage_details(coverage_data: Dict):
    """
    Display file-level coverage in interactive Streamlit dataframes.
    
    Features:
    - Sortable columns (file name, statements, missing, coverage)
    - Color-coded coverage percentages
    - Filtering capabilities
    - Responsive table design
    - Path normalization for cross-platform compatibility
    """
```

### 4. Test Execution
```python
def run_tests_and_get_results() -> Dict:
    """
    Run tests using the run_tests.py script and return results.
    
    Features:
    - Automated test execution
    - Coverage data generation
    - JSON report creation
    - Error handling and timeout management
    """
```

## Test Structure

### 1. Test Organization
```
test/
├── conftest.py                          # Pytest configuration and fixtures
├── conftest_streamlit.py                # Streamlit-specific fixtures
├── unit/                                # Unit tests
│   ├── test_basic_functionality.py     # Basic functionality tests
│   ├── database/                       # Database tests
│   │   ├── test_database_connectivity.py
│   │   └── test_database_connectivity_comprehensive.py
│   ├── data/                           # Data source tests
│   │   ├── test_portfolio_manager.py
│   │   ├── test_portfolio_optimization.py
│   │   ├── test_symbol_analysis.py
│   │   └── test_symbol_manager_comprehensive.py
│   └── ui/                             # UI tests
│       ├── test_simple_streamlit.py
│       ├── test_home_comprehensive.py
│       ├── test_date_display_comprehensive.py
│       ├── test_market_status_comprehensive.py
│       ├── test_portfolio_comprehensive.py
│       ├── test_portfolio_direct.py
│       ├── test_portfolio_simple.py
│       ├── test_symbol_selector_comprehensive.py
│       ├── test_testing_results.py
│       └── test_debug_ui.py
├── integration/                         # Integration tests
│   ├── test_streamlit_integration.py
│   └── test_multi_symbol_recycler.py
├── e2e/                                # End-to-end tests
│   └── test_streamlit_e2e.py
└── fixtures/                           # Test fixtures
```

### 2. Streamlit Testing Fixtures

The `conftest_streamlit.py` file provides specialized fixtures for Streamlit UI testing:

#### Core Fixtures
- `mock_streamlit`: Mocks all Streamlit functions (set_page_config, sidebar, title, etc.)
- `mock_streamlit_autorefresh`: Mocks autorefresh functionality
- `mock_streamlit_option_menu`: Mocks option menu
- `streamlit_test_environment`: Sets up test environment variables

#### Data Fixtures
- `sample_portfolio_data`: Sample portfolio information
- `sample_market_data`: Sample market data
- `sample_activity_data`: Sample trading activities
- `sample_news_data`: Sample news articles
- `ui_test_data`: Comprehensive test data

#### Mock Fixtures
- `mock_database_connection`: Mocks database operations
- `mock_market_hours`: Mocks market hours functionality
- `mock_time_functions`: Mocks time-related functions
- `mock_file_operations`: Mocks file operations

### 3. Test Categories

#### Basic Functionality Tests
- ✅ Import verification
- ✅ Environment variable setup
- ✅ Mock fixture functionality
- ✅ Data structure validation
- ✅ Error handling patterns
- ✅ Utility function validation

#### Database Connectivity Tests
- ✅ Class and method existence
- ✅ Connection and query operations
- ✅ Error handling patterns
- ✅ Transaction management
- ✅ Credential validation logic
- ✅ Comprehensive database operations (100% coverage)

#### UI Component Tests
- ✅ Component rendering with mocked Streamlit functions
- ✅ User interaction patterns
- ✅ Data display functionality
- ✅ Responsive design elements
- ✅ Timezone conversions and date formatting
- ✅ Market status display and indicators
- ✅ Error handling and edge cases

#### Comprehensive Test Suites
- ✅ **Date Display**: 30 tests covering timezone conversions, formatting, and edge cases
- ✅ **Market Status**: 29 tests covering UI components, market indicators, and display functions
- ✅ **Home Dashboard**: Complete coverage of dashboard functionality and components
- ✅ **Database Connectivity**: Full coverage of all database operations and error handling
- ✅ **Testing Results**: Coverage of the testing results component and Streamlit dataframe integration

## Running Tests

### 1. Automated Test Runner
```bash
# Run all tests with coverage (default)
python scripts/run_tests.py

# Run comprehensive test suites
python -m pytest test/unit/ui/test_market_status_comprehensive.py test/unit/ui/test_home_comprehensive.py test/unit/database/test_database_connectivity_comprehensive.py test/unit/ui/test_date_display_comprehensive.py --cov=src --cov-report=json:build/coverage.json --cov-report=term-missing

# Run quick test suite (basic + database)
python scripts/run_tests.py quick

# Run only basic tests
python scripts/run_tests.py basic

# Run only database tests
python scripts/run_tests.py database

# Run Streamlit UI tests
python scripts/run_tests.py simple

# Get help with all options
python scripts/run_tests.py --help

### 2. Testing Streamlined Workflows

#### Start-of-Day Flow Testing
```bash
# Test the streamlined start-of-day flow
python -c "from main import start_of_day_flow; start_of_day_flow()"

# Test individual components
python -c "from src.flows.preprocessing_flows import daily_preprocessing_flow; daily_preprocessing_flow()"
python -c "from src.flows.training_flows import complete_training_flow; complete_training_flow()"
```

#### Configuration Loading Testing
```bash
# Test the new config loader
python -c "from src.utils.config_loader import get_variance_stability_config; print(get_variance_stability_config())"
python -c "from src.utils.config_loader import get_sectors_config; print(get_sectors_config())"
```

#### Unicode Compatibility Testing
```bash
# Verify no Unicode characters in print statements
grep -r "print.*[^\x00-\x7F]" src/ --include="*.py" | grep -v "config_loader.py"
```
```

### 2. Individual Test Files
```bash
# Basic functionality tests
pytest test/unit/test_basic_functionality.py -v

# Database connectivity tests
pytest test/unit/database/test_database_connectivity.py -v

# Comprehensive UI tests
pytest test/unit/ui/test_market_status_comprehensive.py -v
pytest test/unit/ui/test_date_display_comprehensive.py -v
pytest test/unit/ui/test_home_comprehensive.py -v

# Streamlit UI tests
pytest test/unit/ui/test_simple_streamlit.py -v

# Testing results component tests
pytest test/unit/ui/test_testing_results.py -v
```

### 3. Coverage Reports
```bash
# Terminal coverage report
pytest test/ -v --cov=src --cov-report=term-missing

# HTML coverage report
pytest test/ -v --cov=src --cov-report=html

# JSON coverage report (for UI display)
pytest test/ -v --cov=src --cov-report=json:build/coverage.json
```

## Testing Results UI

### Overview

The Testing Results page is a dedicated section in the Streamlit UI that allows users to:

- Run tests directly from the UI
- View test execution results and statistics
- Analyze code coverage reports
- Monitor test performance and trends
- Access detailed execution logs

### Features

#### 🧪 Test Execution
- **One-click test execution**: Run all tests with a single button click
- **Real-time progress**: See test execution progress with spinner indicators
- **Execution time tracking**: Monitor how long tests take to complete
- **Status reporting**: Clear success/failure status indicators

#### 📊 Coverage Analysis
- **Overall coverage metrics**: View total lines covered, coverage percentage, and missing lines
- **File-level coverage**: Detailed breakdown of coverage by individual files
- **Visual indicators**: Color-coded coverage levels (green for ≥80%, yellow for ≥60%, red for <60%)
- **Progress bars**: Visual representation of coverage ratios

#### 📋 Test Results Details
- **Test outcome summary**: Counts of passed, failed, skipped, and error tests
- **Individual test results**: Detailed view of each test with status indicators
- **Grouped results**: Tests organized by outcome for easy analysis
- **Expandable sections**: Collapsible sections for different test categories

#### 📝 Execution Logs
- **Standard output**: View complete test execution output
- **Error logs**: Access detailed error information
- **Execution errors**: See any issues with test execution itself
- **Raw data access**: JSON format of all test data for debugging

### Navigation

The Testing Results page is accessible through the main navigation sidebar:

1. Open the Streamlit app
2. Click on the "Testing" tab in the sidebar (flask icon)
3. The Testing Results page will load

### Usage

#### Running Tests

1. Navigate to the Testing Results page
2. Click the "🔄 Run Tests & Refresh Results" button
3. Wait for the tests to complete (this may take several minutes)
4. View the results in the various tabs

#### Viewing Results

The results are displayed in four main sections:

1. **📊 Coverage**: Code coverage statistics and file-level breakdown
2. **🧪 Test Results**: Individual test outcomes and summary statistics
3. **📝 Logs**: Execution logs and error information
4. **📋 Raw Data**: Complete JSON data for advanced analysis

#### Understanding the Metrics

##### Test Execution Summary
- **Status**: Overall test execution status (Success/Failed/Error/Timeout)
- **Execution Time**: Total time taken to run all tests
- **Total Tests**: Number of tests executed
- **Coverage**: Overall code coverage percentage

##### Coverage Details
- **Lines Covered**: Number of code lines executed by tests
- **Lines Total**: Total number of code lines in the project
- **Coverage %**: Percentage of code covered by tests
- **Missing Lines**: Number of lines not covered by tests

##### Test Results
- **Passed**: Tests that completed successfully
- **Failed**: Tests that failed during execution
- **Skipped**: Tests that were skipped (e.g., due to missing dependencies)
- **Errors**: Tests that encountered errors during execution

### Technical Implementation

#### Components

The Testing Results feature consists of several components:

- **`testing_results.py`**: Main component for rendering the testing results page
- **`test_testing_results.py`**: Unit tests for the testing results component
- **Integration with `streamlit_app.py`**: Navigation and routing integration

#### Dependencies

The feature uses the following dependencies:
- `pytest`: For test execution
- `pytest-cov`: For coverage reporting
- `pandas`: For data manipulation and display
- `streamlit`: For UI components

#### File Structure

```
src/ui/components/
├── testing_results.py          # Main testing results component
└── ...

test/unit/ui/
├── test_testing_results.py     # Unit tests for testing results
└── ...
```

#### Configuration

##### Test Execution

The test execution is configured through the `pytest.ini` file and uses the following command:

```bash
python -m pytest test/ --cov=src --cov-report=json:coverage.json --cov-report=term-missing -v
```

##### Coverage Reporting

Coverage reports are generated in JSON format and stored in the project root as `coverage.json`.

##### Timeout Settings

Test execution has a 5-minute timeout to prevent hanging processes.

## Coverage Display System

### Overview

The coverage display system provides a unified, robust way to visualize code coverage data across multiple dimensions:

- **Overall Coverage Metrics**: High-level coverage statistics
- **Coverage Distribution**: Breakdown by coverage levels (Excellent, Good, Fair, Poor)
- **Module-Level Analysis**: Coverage grouped by project modules
- **File-Level Details**: Individual file coverage with missing line information
- **Insights & Recommendations**: AI-powered analysis and improvement suggestions

### Key Features

#### 1. Unified Data Format
- **Normalized Coverage Data**: Consistent JSON structure regardless of source
- **Path Normalization**: Cross-platform file path handling
- **Error Handling**: Graceful degradation when data is missing or malformed

#### 2. Multi-Dimensional Visualization
- **Coverage Overview**: High-level metrics with color-coded progress bars
- **Distribution Analysis**: Files categorized by coverage levels
- **Module Breakdown**: Coverage aggregated by project modules
- **Detailed File View**: Individual file coverage with missing line numbers

#### 3. Intelligent Insights
- **Coverage Level Assessment**: Automatic categorization (Excellent ≥90%, Good 80-89%, Fair 60-79%, Poor <60%)
- **Improvement Recommendations**: Actionable suggestions based on coverage patterns
- **Priority Identification**: Files and modules needing immediate attention

### Architecture

#### Data Flow
```
pytest-cov → coverage.json → normalize_coverage_data() → parse_coverage_data() → UI Components
```

#### Key Functions

##### `normalize_coverage_data(coverage_data)`
- Normalizes file paths (Windows/Unix compatibility)
- Ensures consistent data structure
- Handles missing or malformed data gracefully

##### `parse_coverage_data(coverage_data)`
- Extracts summary statistics
- Categorizes files by coverage level
- Groups files by module
- Calculates module-level coverage percentages

##### `display_coverage_overview(coverage_data)`
- Shows overall coverage metrics
- Displays coverage distribution
- Presents module-level breakdown
- Uses color-coded progress indicators

##### `display_coverage_details(coverage_data)`
- File-level coverage table
- Missing line information
- Sortable and filterable data grid
- Files needing improvement highlight

##### `display_coverage_insights(coverage_data)`
- Analyzes coverage patterns
- Provides improvement recommendations
- Identifies priority areas
- Offers general testing tips

### Coverage Levels

| Level | Range | Color | Description |
|-------|-------|-------|-------------|
| Excellent | ≥90% | 🟢 Green | Well-tested code |
| Good | 80-89% | 🔵 Blue | Adequate coverage |
| Fair | 60-79% | 🟡 Yellow | Needs improvement |
| Poor | <60% | 🔴 Red | Critical attention needed |

### UI Components

#### Coverage Overview Tab
- **Overall Coverage Metric**: Percentage with line count delta
- **Key Metrics**: Lines covered, total lines, missing lines
- **Progress Bar**: Color-coded based on coverage level
- **Distribution Metrics**: Files by coverage level
- **Module Coverage Table**: Sortable grid with coverage percentages

#### Coverage Details Tab
- **File-Level Table**: Comprehensive coverage data
- **Coverage Level Indicators**: Visual status indicators
- **Missing Line Numbers**: Specific lines needing tests
- **Low Coverage Alert**: Files below 80% coverage

#### Insights Tab
- **Key Insights**: Automated analysis of coverage patterns
- **Recommendations**: Actionable improvement suggestions
- **Priority Areas**: Modules and files needing attention
- **General Tips**: Best practices for improving coverage

### Data Structure

#### Normalized Coverage Format
```json
{
  "meta": {
    "format": 3,
    "version": "7.9.1",
    "timestamp": "2025-06-22T09:13:29.841736"
  },
  "totals": {
    "covered_lines": 380,
    "num_statements": 424,
    "percent_covered": 89.62,
    "percent_covered_display": "90",
    "missing_lines": 44
  },
  "files": {
    "src/ui/components/testing_results.py": {
      "executed_lines": [1, 2, 3, ...],
      "summary": {
        "covered_lines": 598,
        "num_statements": 598,
        "percent_covered": 100.0,
        "percent_covered_display": "100",
        "missing_lines": 0
      },
      "missing_lines": [],
      "functions": {...},
      "classes": {...}
    }
  }
}
```

#### Parsed Coverage Format
```json
{
  "summary": {
    "lines_covered": 380,
    "lines_total": 424,
    "coverage_percentage": 89.62,
    "missing_lines": 44,
    "coverage_display": "90"
  },
  "files": [
    {
      "file": "src/ui/components/testing_results.py",
      "lines_covered": 598,
      "lines_total": 598,
      "coverage_percentage": 100.0,
      "missing_lines": 0,
      "missing_line_numbers": []
    }
  ],
  "modules": {
    "ui": {
      "files": 5,
      "total_lines": 800,
      "covered_lines": 750,
      "coverage_percentage": 93.75
    }
  },
  "coverage_levels": {
    "excellent": 8,
    "good": 2,
    "fair": 1,
    "poor": 0
  }
}
```

### Error Handling

#### Graceful Degradation
- **Missing Coverage Data**: Shows warning message
- **Malformed JSON**: Displays error with details
- **Empty Results**: Provides helpful instructions
- **Partial Data**: Shows available information

#### Debug Information
- **File Loading**: Logs file paths and loading status
- **Parsing Errors**: Shows specific error messages
- **Data Validation**: Checks for required fields
- **Fallback Options**: Alternative data sources

## Testing Philosophy

### 1. No External Dependencies
- **No real database required**: All database tests use comprehensive mocks
- **No external API calls**: No Yahoo, Alpaca, or News API tests
- **Advanced mocking**: Sophisticated mocking for UI components and external dependencies
- **Cross-platform compatibility**: Works on Windows, macOS, and Linux

### 2. Comprehensive Coverage
- **Detailed test suites**: Extensive test coverage for complex modules
- **UI testing**: Mock-based testing of Streamlit components
- **Error scenarios**: Testing of error handling and edge cases
- **Performance testing**: Test execution time and resource usage

### 3. Quality Assurance
- **Automated execution**: Tests can be run from command line or UI
- **Coverage tracking**: Real-time coverage metrics and insights
- **Continuous integration**: Automated testing in deployment pipeline
- **Documentation**: Comprehensive test documentation and examples

## Recent Improvements

### 1. Testing Results UI
- ✅ **Streamlit Dataframe Integration**: Enhanced testing results display with advanced table functionality
- ✅ **Path Normalization**: Fixed coverage display issues across different operating systems
- ✅ **Deprecation Fixes**: Removed deprecated parameters and updated dependencies
- ✅ **Enhanced Sorting**: Improved table sorting with numeric value preservation
- ✅ **Better Error Handling**: Graceful handling of missing coverage data
- ✅ **Test Execution**: Added ability to run tests directly from the UI
- ✅ **Real-time Updates**: Manual refresh capabilities for immediate data updates

### 2. AgGrid to Streamlit Refactoring (July 2025)
The testing results interface has been refactored to use Streamlit's native dataframes:

#### **Changes Made:**
- **Removed aggrid dependency**: Eliminated `streamlit-aggrid` from requirements
- **Replaced AgGrid tables**: Converted coverage tables to use `st.dataframe()` with styling
- **Simplified implementation**: Removed complex AgGrid configuration code
- **Better compatibility**: Native Streamlit components provide more reliable performance

#### **Benefits:**
- **Reduced dependencies**: No longer requires external aggrid package
- **Improved stability**: Native Streamlit components have fewer compatibility issues
- **Consistent styling**: All tables now use the same Streamlit styling and behavior
- **Easier maintenance**: Less complex code to maintain and debug

#### **Files Modified:**
- `src/ui/components/testing_results.py` - Replaced AgGrid with `st.dataframe`
- `config/requirements.txt` - Removed `streamlit-aggrid` dependency

#### **Table Functionality Preserved:**
- ✅ **Sorting**: All columns remain sortable
- ✅ **Filtering**: Data filtering capabilities maintained
- ✅ **Responsive Design**: Tables adapt to container width
- ✅ **Color Coding**: P&L and coverage percentage color coding preserved
- ✅ **Formatting**: Currency and percentage formatting maintained

### 2. Test Coverage
- ✅ **Overall Project Coverage**: 78%
- ✅ **High Coverage Modules (100%)**:
  - Database connectivity (`src/database/database_connectivity.py`)
  - Symbol manager (`src/data/sources/symbol_manager.py`)
  - UI components (`src/ui/components/date_display.py`, `src/ui/components/market_status.py`)
  - Portfolio management (`src/ui/portfolio.py` - 94%)
- ✅ **Good Coverage Modules (85%+)**:
  - Home dashboard (`src/ui/home.py` - 85%)
  - Symbol selector (`src/ui/components/symbol_selector.py` - 87%)
  - Testing results component (`src/ui/components/testing_results.py` - 75%)

### 3. Test Suite Status
- ✅ **All Tests Passing**: 309 passed, 7 skipped, 0 failed
- ✅ **Test Categories**: Unit, Integration, E2E, UI, Database, MLflow
- ✅ **Async Support**: Proper pytest-asyncio configuration
- ✅ **Mock Isolation**: Fixed test isolation issues with proper mocking
- ✅ **Environment Variables**: MLflow tracking URI configuration resolved

### 4. Recent Test Fixes
- ✅ **MLflow Manager**: Fixed environment variable substitution in YAML config
- ✅ **UI Component Tests**: Resolved mock isolation issues with `st.columns` and `st.write`
- ✅ **Database Tests**: All database connectivity tests passing with comprehensive mocking
- ✅ **Async Tests**: Proper async test configuration and execution
- ✅ **Test Isolation**: Fixed mock leakage between tests with proper reset mechanisms

## Example Test Output

```
======================================== test session starts ========================================
platform win32 -- Python 3.10.6, pytest-8.4.1, pluggy-1.6.0
collected 317 items

test/unit/test_basic_functionality.py ................ [  5%]
test/unit/test_mlflow_manager.py .. [  6%]
test/unit/test_websocket_symbols.py .... [  7%]
test/unit/ui/test_date_display_comprehensive.py .............................. [ 16%]
test/unit/ui/test_debug_ui.py ................ [ 21%]
test/unit/ui/test_home_comprehensive.py ........................ [ 30%]
test/unit/ui/test_market_status_comprehensive.py ............................. [ 39%]
test/unit/ui/test_portfolio_comprehensive.py ........................ [ 48%]
test/unit/ui/test_portfolio_direct.py ........ [ 51%]
test/unit/ui/test_portfolio_simple.py .... [ 52%]
test/unit/ui/test_simple_streamlit.py ...... [ 54%]
test/unit/ui/test_symbol_selector_comprehensive.py ................ [ 59%]
test/unit/ui/test_testing_results.py ................ [ 64%]
test/unit/data/test_portfolio_manager.py ........ [ 67%]
test/unit/data/test_portfolio_optimization.py .......... [ 71%]
test/unit/data/test_symbol_analysis.py .......... [ 76%]
test/unit/data/test_symbol_manager_comprehensive.py ................ [ 81%]
test/unit/database/test_database_connectivity_comprehensive.py ........................ [ 89%]
test/unit/database/test_database_connectivity.py ........ [ 92%]
test/unit/database/test_database_connectivity_comprehensive.py ........................ [100%]
test/integration/test_multi_symbol_recycler.py ......... [103%]
test/integration/test_streamlit_integration.py .. [104%]

======================================== 309 passed, 7 skipped in 46.76s =========================================

---------- coverage: platform win32, python 3.10.16-final-0 -----------
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/data/sources/portfolio_manager.py     249     90    64%   76-78, 105-107, 111, 131-132, 171-172, 176-177, 185-187, 225-227, 259-260, 285-287, 295-300, 311-312, 319, 342, 353, 377-379, 391-461, 498-499, 528-530, 535-559
src/data/sources/symbol_manager.py         54      0   100%
src/database/database_connectivity.py      83      0   100%
src/mlflow_manager.py                     205     88    57%   59-64, 88, 116-118, 133-134, 142-144, 174-176, 188-190, 203-205, 220, 223-225, 235-240, 253-255, 277-279, 292-299, 315-317, 328-337, 353, 373-375, 385-391, 403-422, 484-501
src/ui/components/date_display.py          39      0   100%
src/ui/components/market_status.py         52      0   100%
src/ui/components/symbol_selector.py      210     27    87%   115, 119-129, 216-218, 279-284, 308, 332-334, 382-384
src/ui/components/testing_results.py      421    107    75%   69-72, 82-86, 95-104, 113-159, 214, 216, 220, 244-246, 265-266, 300, 302, 306, 388-389, 394-395, 474, 479, 492, 494, 498, 508-509, 513, 563-564, 581, 590-592, 603-604, 628-654, 672-674, 678-680, 684-686, 730-733, 744-745, 752-753, 769, 774-784, 824-825
src/ui/home.py                            228     35    85%   38-40, 100-101, 180-192, 244-245, 261-279, 369-370, 384-385
src/ui/portfolio.py                       216     14    94%   40-42, 157-162, 202-203, 255-256, 444
src/ui/streamlit_app.py                    41      9    78%   48-52, 73, 75, 79, 86
src/utils/market_hours.py                  63     33    48%   26-27, 41-43, 49, 53, 59, 63-64, 68-69, 76-78, 82-90, 94-99, 103-108
src/utils/websocket_config.py             106     29    73%   41-43, 59, 63, 85, 96, 100, 110-111, 117-118, 122-123, 127-128, 133-135, 167-168, 174, 179, 184, 189, 194-197
---------------------------------------------------------------------
TOTAL                                    1967    432    78%
```

## Best Practices

### 1. Test Development
- Write tests for all new features
- Use descriptive test names
- Group related tests in classes
- Use fixtures for common setup
- Mock external dependencies

### 2. Streamlit Testing Best Practices

#### Mock External Dependencies
Always mock external dependencies like:
- Streamlit functions (`st.title`, `st.write`, `st.columns`, etc.)
- Database connections
- API calls
- File operations

#### Use Descriptive Test Names
```python
def test_get_greeting_returns_morning_for_early_hours():
    """Test that greeting returns 'Good Morning' for early hours."""
    pass

def test_display_portfolio_summary_shows_correct_metrics():
    """Test that portfolio summary displays correct metrics."""
    pass
```

#### Follow AAA Pattern
- **Arrange**: Set up test data and mocks
- **Act**: Call the function being tested
- **Assert**: Verify the expected behavior

#### Test Error Scenarios
```python
def test_app_handles_missing_css_file_gracefully():
    """Test that app handles missing CSS file gracefully."""
    with patch('builtins.open', side_effect=FileNotFoundError):
        # Test that app doesn't crash
        assert main is not None
```

#### Use Fixtures for Common Setup
```python
@pytest.fixture
def sample_user_data():
    return {
        "name": "Test User",
        "portfolio_value": 100000,
        "preferences": {"theme": "dark"}
    }

def test_user_dashboard(sample_user_data):
    """Test user dashboard with sample data."""
    # Use sample_user_data fixture
    pass
```

### 3. Coverage Goals
- Aim for ≥80% coverage on critical modules
- Focus on business logic coverage
- Test error handling paths
- Include edge case testing

### 4. Test Maintenance
- Keep tests up to date with code changes
- Refactor tests when code is refactored
- Remove obsolete tests
- Update test documentation

### 5. For Developers
1. **Run Tests Regularly**: Use `python scripts/run_tests.py` to generate fresh coverage data
2. **Check Coverage Levels**: Aim for ≥80% coverage on critical modules
3. **Review Insights**: Pay attention to automated recommendations
4. **Focus on Missing Lines**: Prioritize files with specific missing line numbers

### 6. For Maintainers
1. **Monitor Trends**: Track coverage changes over time
2. **Set Standards**: Define minimum coverage requirements
3. **Review Distribution**: Ensure balanced coverage across modules
4. **Update Recommendations**: Refine insight algorithms based on project needs

## Troubleshooting

### Common Issues

#### No Coverage Data
- **Cause**: Tests not run or coverage not generated
- **Solution**: Run `python scripts/run_tests.py`

#### Coverage Mismatch
- **Cause**: Different coverage tools or configurations
- **Solution**: Use unified test runner with consistent settings

#### UI Not Updating
- **Cause**: Cached data or file permissions
- **Solution**: Refresh page and check file permissions

#### Missing Files
- **Cause**: Files excluded from coverage or not in src/ directory
- **Solution**: Check coverage configuration and file paths

#### MLflow Tests Failing
- **Cause**: Invalid MLFLOW_TRACKING_URI environment variable
- **Solution**: Set `MLFLOW_TRACKING_URI=http://localhost:5000` or update config/config.yaml

#### Mock Isolation Issues
- **Cause**: Mock call counts accumulating between tests
- **Solution**: Use `mock.reset_mock()` before assertions or patch the correct functions

#### Async Test Failures
- **Cause**: Improper pytest-asyncio configuration
- **Solution**: Ensure `pytest.ini` has `--asyncio-mode=strict` and tests use proper async decorators

#### Tests not running
- **Cause**: pytest not installed or test directory doesn't exist
- **Solution**: Ensure pytest is installed and the test directory exists

#### No coverage data
- **Cause**: pytest-cov not installed or tests not generating coverage
- **Solution**: Check that pytest-cov is installed and tests are generating coverage

#### Timeout errors
- **Cause**: Large test suites may need longer timeout settings
- **Solution**: Increase timeout settings for large test suites

#### Import errors
- **Cause**: Missing required dependencies
- **Solution**: Ensure all required dependencies are installed

### Debug Steps
1. Check if `build/coverage.json` exists and is readable
2. Verify test execution completed successfully
3. Review console logs for parsing errors
4. Validate JSON structure manually if needed
5. Check the "📝 Logs" tab for detailed error information
6. View the "📋 Raw Data" tab for complete JSON output
7. Run tests manually from the command line to verify they work
8. Check the browser console for any JavaScript errors

## MLflow Integration Testing

### Testing MLflow Components
To test MLflow integration and model management:

```bash
# Ensure MLflow server is running
mlflow server --backend-store-uri postgresql://postgres:nishant@localhost/mlflow_db --default-artifact-root file:./mlruns --host 0.0.0.0 --port 5000

# Set environment variable
export MLFLOW_TRACKING_URI=http://localhost:5000

# Run MLflow-specific tests
pytest test/unit/test_mlflow_manager.py -v

# Test MLflow integration with coverage
pytest test/unit/test_mlflow_manager.py --cov=src.mlflow_manager --cov-report=term-missing
```

### MLflow Test Coverage
- **Current Coverage**: 57% (205 statements, 88 missing)
- **Test Focus**: Environment variable substitution, YAML config handling, experiment management
- **Future Improvements**: Model training workflows, artifact management, model serving

For more details on MLflow architecture and testing strategy, see [Architecture Decisions](architecture-decisions.md).

## Future Enhancements

> **📋 Centralized Registry**: All future enhancements are now tracked in the [Architecture Decisions](architecture-decisions.md#future-enhancements) for better project management and planning.

### Testing-Specific Enhancements

#### Planned Features
- **Historical Tracking**: Coverage trends over time
- **Custom Thresholds**: Configurable coverage level boundaries
- **Export Options**: PDF/CSV reports
- **Integration**: CI/CD pipeline integration
- **Notifications**: Coverage drop alerts
- **Historical data**: Store and display test results over time
- **Trend analysis**: Show coverage and test success trends
- **Test filtering**: Filter tests by category, file, or status
- **Export functionality**: Export results to PDF or CSV
- **Integration with CI/CD**: Connect to continuous integration systems
- **Performance metrics**: Track test execution time trends
- **Custom test suites**: Allow running specific test categories

#### Critical Testing Gaps to Address

##### High Priority (Critical Gaps)
- **Data Source Unit Tests**: Complete unit tests for `alpaca_websocket.py`, `alpaca_historical_loader.py`, `alpaca_daily_loader.py`, `yahoo_finance_loader.py`, `news.py`, `data_recycler_server.py`, `configurable_websocket.py`, `hourly_persistence.py`
- **Utility Module Tests**: Unit tests for `websocket_config.py`, `data_recycler_utils.py`, `market_hours.py`
- **Database Integration Tests**: Real database operation tests, migration script tests, schema validation tests
- **Error Handling Tests**: Network failures, API failures, database failures, data corruption scenarios

##### Medium Priority (Important Gaps)
- **Script Unit Tests**: Unit tests for `manage_symbols.py`, `setup_test_env.py`, `manual_save.py`
- **Performance Tests**: Load testing, memory usage, API rate limiting, database performance
- **Security Tests**: API key validation, input validation, data sanitization, authentication flows
- **Data Quality Tests**: Data validation, data completeness, data consistency, data transformation accuracy

##### Low Priority (Nice to Have)
- **Documentation Tests**: API documentation accuracy, code examples validation, README validation
- **UI Edge Case Tests**: Complex user interactions, large datasets, market holidays, responsive design
- **Cross-Platform Tests**: Different operating systems compatibility

#### Testing Infrastructure Improvements
- **Complete Coverage Tracking**: Address gaps in data source and utility module testing
- **Integration Coverage**: Track coverage for end-to-end integration tests
- **Performance Test Coverage**: Include performance and load testing in coverage metrics
- **Security Test Coverage**: Track coverage for security validation tests
- **Data Quality Test Coverage**: Monitor coverage for data validation and quality tests

#### Potential Improvements
- **Branch Coverage**: Support for branch coverage metrics
- **Function Coverage**: Detailed function-level analysis
- **Test Impact**: Identify which tests affect which lines
- **Coverage Maps**: Visual file coverage highlighting

## Contributing

To contribute to the Testing Results UI:

1. Follow the existing code style and patterns
2. Add unit tests for new functionality
3. Update this documentation for any changes
4. Test the UI thoroughly before submitting changes

## Support

For issues or questions about the Testing Results UI:

1. Check the troubleshooting section above
2. Review the logs in the "📝 Logs" tab
3. Consult the project's main documentation
4. Open an issue in the project repository

## Related Documentation

- **[Architecture Decisions](architecture-decisions.md)**: Design rationale and testing strategy decisions
- **[Development Guide](development.md)**: Development practices and testing workflows
- **[Setup Guide](setup.md)**: Test environment setup and configuration
- **[UI Documentation](ui.md)**: UI testing and component testing strategies 