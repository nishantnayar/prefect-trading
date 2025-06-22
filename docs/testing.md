# Testing Guide

## Philosophy and Strategy

Testing is a core pillar of the Prefect Trading System. We aim for high reliability, maintainability, and confidence in every release. Our strategy is to combine unit, integration, end-to-end (E2E), performance, and UI testing, with automation and CI/CD integration.

## Test Categories
- **Unit Tests**: Isolate and test individual functions/classes.
- **Integration Tests**: Validate interactions between components (e.g., database, APIs).
- **End-to-End (E2E) Tests**: Simulate real user workflows across the system.
- **Performance Tests**: Assess speed, resource usage, and scalability.
- **UI Tests**: Automated checks for the Streamlit interface.

## Infrastructure & Configuration
- **Framework**: Pytest (with pytest-cov for coverage)
- **Directory Structure**:
  ```
  test/
  ├── unit/
  │   ├── ui/
  │   │   ├── test_date_display_comprehensive.py
  │   │   ├── test_market_status_comprehensive.py
  │   │   ├── test_home_comprehensive.py
  │   │   └── test_testing_results.py
  │   └── database/
  │       └── test_database_connectivity_comprehensive.py
  ├── integration/
  ├── e2e/
  ├── fixtures/
  └── conftest.py
  ```
- **Environment**: Use `.env` for secrets; use test databases for integration/E2E.

## Current Coverage Status

### High Coverage Modules (100%)
- **`src/ui/components/date_display.py`** - 100% coverage
  - Comprehensive test suite with 30 tests
  - Covers all functions: `get_ordinal_suffix`, `format_datetime_est_to_cst`, `get_current_cst`, `get_current_cst_formatted`, `convert_est_to_cst`
  - Includes edge cases, error handling, and timezone conversions

- **`src/ui/components/market_status.py`** - 100% coverage
  - Comprehensive test suite with 29 tests
  - Covers all functions: `get_ordinal_suffix`, `format_datetime_cst`, `display_market_status_section`, `display_next_events`, `display_market_hours`, `display_market_status`
  - Includes UI component testing with mocked Streamlit functions

- **`src/database/database_connectivity.py`** - 100% coverage
  - Comprehensive test suite covering all database operations
  - Includes connection management, query execution, and error handling

- **`src/ui/home.py`** - 100% coverage
  - Comprehensive test suite covering all UI components and functions

### Modules Needing Coverage Improvement
- **`src/data/sources/symbol_manager.py`** - 24% coverage
- **`src/ui/components/symbol_selector.py`** - 25% coverage
- **`src/utils/market_hours.py`** - 30% coverage
- **`src/ui/components/testing_results.py`** - 72% coverage

### Overall Project Coverage: 77%

## Comprehensive Test Suites

### Date Display Module (`test_date_display_comprehensive.py`)
- **30 tests** covering all functionality
- **Test Categories**:
  - Ordinal suffix generation (1st, 2nd, 3rd, 4th, 11th, 12th, 13th, 21st, 22nd, 23rd, 24th, 31st)
  - DateTime formatting with timezone conversions
  - Error handling for invalid inputs
  - Integration scenarios
  - Edge cases (midnight, noon, different timezones)

### Market Status Module (`test_market_status_comprehensive.py`)
- **29 tests** covering all functionality
- **Test Categories**:
  - Ordinal suffix generation
  - DateTime formatting in CST
  - UI component display functions
  - Market status indicators (open/closed)
  - Next events display
  - Market hours display
  - Error handling and exception scenarios

## Writing Tests
- Use descriptive names and docstrings.
- Prefer fixtures for setup/teardown.
- Use mocks for external APIs and side effects.
- Example:
  ```python
  import pytest
  from unittest.mock import patch
  from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader

  def test_initialization():
      loader = YahooFinanceDataLoader()
      assert loader is not None

  @patch('src.data.sources.yahoo_finance_loader.requests.get')
  def test_error_handling(mock_get):
      mock_get.side_effect = Exception("Network error")
      loader = YahooFinanceDataLoader()
      with pytest.raises(Exception):
          loader.fetch_data('AAPL')
  ```

## Mocking Strategies
- Use `unittest.mock` for API calls, database access, and time-based logic.
- Patch only what you need; avoid over-mocking.
- For UI components, mock Streamlit functions (`st.markdown`, `st.container`, etc.)
- For timezone-dependent tests, use `pytz_timezone` instead of `timezone`

## Performance Testing
- Use Pytest markers (e.g., `@pytest.mark.performance`).
- Measure execution time and resource usage.
- Run performance tests separately from unit/integration.

## Running Tests
- All tests: `make test`
- Unit: `make test-unit`
- Integration: `make test-integration`
- E2E: `make test-e2e`
- With coverage: `make test-coverage`
- Specific comprehensive test: `python -m pytest test/unit/ui/test_market_status_comprehensive.py`

## Coverage Generation
To generate accurate coverage reports including comprehensive tests:
```bash
python -m pytest test/unit/ui/test_market_status_comprehensive.py test/unit/ui/test_home_comprehensive.py test/unit/database/test_database_connectivity_comprehensive.py test/unit/ui/test_date_display_comprehensive.py --cov=src --cov-report=json:build/coverage.json --cov-report=term-missing
```

## CI/CD Integration
- Automated tests run on every PR and push to main.
- See `.github/workflows/deploy.yml` for pipeline details.
- Failing tests block merges.

## Coverage Goals
- **Target**: 85%+ for core modules
- **Current**: 77% overall
- **High Priority**: Increase coverage for `symbol_manager.py`, `symbol_selector.py`, and `market_hours.py`
- Use `pytest-cov` and review coverage reports in the Testing UI.

## Best Practices
- Write tests for all new features and bug fixes.
- Keep tests isolated and repeatable.
- Use fixtures for setup/teardown.
- Review and refactor tests regularly.
- For UI components, test both success and error scenarios.
- Use comprehensive test suites for complex modules.

## Troubleshooting
- **Tests not running**: Check pytest installation and test directory structure.
- **No coverage data**: Ensure `pytest-cov` is installed and used.
- **Timeouts**: Increase timeout for large suites.
- **Import errors**: Check dependencies and PYTHONPATH.
- **Deprecation warnings**: Update deprecated parameters (e.g., `fit_columns_on_grid_load` in AgGrid).

## UI Testing
- Automated via Streamlit Testing Results UI.
- Run UI tests from the Testing tab in the app.
- Review coverage, logs, and results interactively.
- Coverage data is displayed using AgGrid tables with sorting and filtering.

## Recent Improvements
- **Fixed deprecation warnings**: Removed deprecated `fit_columns_on_grid_load` parameter from AgGrid
- **Path normalization**: Fixed coverage display issues with Windows/Unix path differences
- **Comprehensive test suites**: Added extensive test coverage for UI components

## Resources
- [Pytest Documentation](https://docs.pytest.org/)
- [Prefect Docs](https://docs.prefect.io/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [AgGrid Documentation](https://pypi.org/project/streamlit-aggrid/) 