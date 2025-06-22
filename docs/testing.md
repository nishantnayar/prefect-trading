# Testing Documentation

## Overview

The Prefect Trading System includes a comprehensive testing strategy with automated test execution, coverage analysis, and a dedicated Testing page in the Streamlit UI for real-time test results visualization.

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
├── unit/                                # Unit tests
│   ├── test_basic_functionality.py     # Basic functionality tests
│   ├── database/                       # Database tests
│   │   ├── test_database_connectivity.py
│   │   └── test_database_connectivity_comprehensive.py
│   └── ui/                             # UI tests
│       ├── test_simple_streamlit.py
│       ├── test_home_comprehensive.py
│       ├── test_date_display_comprehensive.py
│       ├── test_market_status_comprehensive.py
│       └── test_testing_results.py
├── integration/                         # Integration tests
│   └── test_streamlit_integration.py
├── e2e/                                # End-to-end tests
│   └── test_streamlit_e2e.py
└── fixtures/                           # Test fixtures
```

### 2. Test Categories

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
- ✅ **Overall Project Coverage**: 77%
- ✅ **High Coverage Modules (100%)**:
  - Database connectivity (`src/database/database_connectivity.py`)
  - UI components (`src/ui/home.py`, `src/ui/components/date_display.py`, `src/ui/components/market_status.py`)
  - Testing results component with AgGrid integration

### 3. Modules Needing Coverage Improvement
- **Data Sources**: `symbol_manager.py` (24%), `yahoo_finance_loader.py` (13%)
- **UI Components**: `symbol_selector.py` (25%)
- **Utilities**: `market_hours.py` (30%)

## Example Test Output

```
======================================== test session starts ========================================
platform win32 -- Python 3.10.6, pytest-8.4.1, pluggy-1.6.0
collected 89 items

test/unit/test_basic_functionality.py ............... [ 15%]
test/unit/database/test_database_connectivity_comprehensive.py ........................ [ 47%]
test/unit/ui/test_date_display_comprehensive.py .............................. [ 80%]
test/unit/ui/test_market_status_comprehensive.py ............................. [100%]

======================================== 89 passed in 12.3s =========================================

---------- coverage: platform win32, python 3.10.6-final-0 -----------
Name                                                    Stmts   Miss  Cover
-------------------------------------------------------------------------
src/database/database_connectivity.py                     45      0   100%
src/ui/components/date_display.py                         35      0   100%
src/ui/components/market_status.py                        42      0   100%
src/ui/home.py                                            89      0   100%
-------------------------------------------------------------------------
TOTAL                                                    211     49    77%
```

## Best Practices

### 1. Test Development
- Write tests for all new features
- Use descriptive test names
- Group related tests in classes
- Use fixtures for common setup
- Mock external dependencies

### 2. Coverage Goals
- Aim for ≥80% coverage on critical modules
- Focus on business logic coverage
- Test error handling paths
- Include edge case testing

### 3. Test Maintenance
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

### Debug Steps
1. Check if `build/coverage.json` exists and is readable
2. Verify test execution completed successfully
3. Review console logs for parsing errors
4. Validate JSON structure manually if needed

## Future Enhancements

### Planned Features
- **Historical Tracking**: Coverage trends over time
- **Custom Thresholds**: Configurable coverage level boundaries
- **Export Options**: PDF/CSV reports
- **Integration**: CI/CD pipeline integration
- **Notifications**: Coverage drop alerts

### Potential Improvements
- **Branch Coverage**: Support for branch coverage metrics
- **Function Coverage**: Detailed function-level analysis
- **Test Impact**: Identify which tests affect which lines
- **Coverage Maps**: Visual file coverage highlighting 