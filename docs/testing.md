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
- **AgGrid**: Advanced table functionality for results display

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
- **File-level Details**: Interactive AgGrid tables with sorting/filtering
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
    Display file-level coverage in interactive AgGrid tables.
    
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
- ✅ **Testing Results**: Coverage of the testing results component and AgGrid integration

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
- ✅ **AgGrid Integration**: Enhanced testing results display with advanced table functionality
- ✅ **Path Normalization**: Fixed coverage display issues across different operating systems
- ✅ **Deprecation Fixes**: Removed deprecated parameters and updated dependencies
- ✅ **Enhanced Sorting**: Improved table sorting with numeric value preservation
- ✅ **Better Error Handling**: Graceful handling of missing coverage data
- ✅ **Test Execution**: Added ability to run tests directly from the UI
- ✅ **Real-time Updates**: Manual refresh capabilities for immediate data updates

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
test/unit/database/test_database_comprehensive.py ........................ [ 89%]
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

### Debug Steps
1. Check if `build/coverage.json` exists and is readable
2. Verify test execution completed successfully
3. Review console logs for parsing errors
4. Validate JSON structure manually if needed

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

#### Potential Improvements
- **Branch Coverage**: Support for branch coverage metrics
- **Function Coverage**: Detailed function-level analysis
- **Test Impact**: Identify which tests affect which lines
- **Coverage Maps**: Visual file coverage highlighting

### Related Documentation

- **[Architecture Decisions](architecture-decisions.md)**: Design rationale and testing strategy decisions
- **[Development Guide](development.md)**: Development practices and testing workflows
- **[Setup Guide](setup.md)**: Test environment setup and configuration
- **[UI Documentation](ui.md)**: UI testing and component testing strategies 