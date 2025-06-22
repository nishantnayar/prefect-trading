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
  ├── integration/
  ├── e2e/
  ├── fixtures/
  └── conftest.py
  ```
- **Environment**: Use `.env` for secrets; use test databases for integration/E2E.

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

## CI/CD Integration
- Automated tests run on every PR and push to main.
- See `.github/workflows/deploy.yml` for pipeline details.
- Failing tests block merges.

## Coverage Goals
- Target: 85%+ for core modules.
- Use `pytest-cov` and review coverage reports in the Testing UI.

## Best Practices
- Write tests for all new features and bug fixes.
- Keep tests isolated and repeatable.
- Use fixtures for setup/teardown.
- Review and refactor tests regularly.

## Troubleshooting
- **Tests not running**: Check pytest installation and test directory structure.
- **No coverage data**: Ensure `pytest-cov` is installed and used.
- **Timeouts**: Increase timeout for large suites.
- **Import errors**: Check dependencies and PYTHONPATH.

## UI Testing
- Automated via Streamlit Testing Results UI.
- Run UI tests from the Testing tab in the app.
- Review coverage, logs, and results interactively.

## Resources
- [Pytest Documentation](https://docs.pytest.org/)
- [Prefect Docs](https://docs.prefect.io/)
- [Streamlit Docs](https://docs.streamlit.io/) 