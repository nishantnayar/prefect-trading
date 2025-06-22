# Streamlit Testing Guide

This document provides comprehensive information about testing the Streamlit UI components in the trading application.

## Overview

The Streamlit testing suite includes:
- **Unit Tests**: Test individual UI components and functions
- **Integration Tests**: Test component interactions and data flow
- **End-to-End Tests**: Test complete user journeys and scenarios

## Test Structure

```
test/
├── unit/ui/                    # Unit tests for UI components
│   ├── test_streamlit_app.py   # Main app tests
│   ├── test_home_page.py       # Home page tests
│   └── test_ui_components.py   # Component tests
├── integration/                # Integration tests
│   └── test_streamlit_integration.py
├── e2e/                        # End-to-end tests
│   └── test_streamlit_e2e.py
├── conftest_streamlit.py       # Streamlit-specific fixtures
└── README_STREAMLIT_TESTS.md   # This file
```

## Running Tests

### Using the Test Runner Script

```bash
# Run all Streamlit tests
python scripts/test_streamlit.py --all

# Run specific test types
python scripts/test_streamlit.py --unit
python scripts/test_streamlit.py --integration
python scripts/test_streamlit.py --e2e

# Check dependencies and setup
python scripts/test_streamlit.py --check

# Verbose output
python scripts/test_streamlit.py --all --verbose
```

### Using Make Commands

```bash
# Run all Streamlit tests
make test-streamlit

# Run specific test types
make test-streamlit-unit
make test-streamlit-integration
make test-streamlit-e2e

# Check setup
make test-streamlit-check
```

### Using Pytest Directly

```bash
# Run all UI tests
pytest test/unit/ui/ -v

# Run integration tests
pytest test/integration/ -v

# Run E2E tests
pytest test/e2e/ -v

# Run with coverage
pytest test/unit/ui/ --cov=src.ui --cov-report=term-missing
```

## Test Categories

### Unit Tests (`test/unit/ui/`)

**Purpose**: Test individual functions and components in isolation.

**Files**:
- `test_streamlit_app.py`: Tests main application logic, routing, and configuration
- `test_home_page.py`: Tests home page rendering and display functions
- `test_ui_components.py`: Tests individual UI components (symbol selector, date display, market status)

**Key Test Areas**:
- Function return values
- Component rendering
- Error handling
- Data formatting
- User interactions

### Integration Tests (`test/integration/`)

**Purpose**: Test how components work together and data flows through the application.

**Files**:
- `test_streamlit_integration.py`: Tests complete application flows and component interactions

**Key Test Areas**:
- Component interactions
- Data flow between components
- Database integration
- Navigation flows
- Error recovery

### End-to-End Tests (`test/e2e/`)

**Purpose**: Test complete user journeys and real-world scenarios.

**Files**:
- `test_streamlit_e2e.py`: Tests complete user journeys and application behavior

**Key Test Areas**:
- Complete user workflows
- Application startup and shutdown
- Performance under load
- Error recovery scenarios
- Environment setup

## Test Fixtures

The `conftest_streamlit.py` file provides common fixtures for all Streamlit tests:

### Core Fixtures

- `mock_streamlit`: Mocks all Streamlit functions
- `mock_streamlit_autorefresh`: Mocks autorefresh functionality
- `mock_streamlit_option_menu`: Mocks option menu
- `streamlit_test_environment`: Sets up test environment variables

### Data Fixtures

- `sample_portfolio_data`: Sample portfolio information
- `sample_market_data`: Sample market data
- `sample_activity_data`: Sample trading activities
- `sample_news_data`: Sample news articles
- `ui_test_data`: Comprehensive test data

### Mock Fixtures

- `mock_database_connection`: Mocks database operations
- `mock_market_hours`: Mocks market hours functionality
- `mock_time_functions`: Mocks time-related functions
- `mock_file_operations`: Mocks file operations

## Writing New Tests

### Unit Test Example

```python
import pytest
from unittest.mock import patch, Mock
from src.ui.components.symbol_selector import display_symbol_selector

class TestSymbolSelector:
    @patch('streamlit.selectbox')
    @patch('streamlit.subheader')
    def test_display_symbol_selector(self, mock_subheader, mock_selectbox):
        """Test that symbol selector displays correctly."""
        # Arrange
        mock_selectbox.return_value = "AAPL"
        
        # Act
        result = display_symbol_selector()
        
        # Assert
        assert result == "AAPL"
        mock_subheader.assert_called_once_with("📈 Symbol Selector")
        mock_selectbox.assert_called_once()
```

### Integration Test Example

```python
import pytest
from unittest.mock import patch
from src.ui.streamlit_app import main

class TestStreamlitIntegration:
    @patch('streamlit.set_page_config')
    @patch('streamlit.sidebar')
    @patch('streamlit_option_menu.option_menu')
    def test_complete_app_flow(self, mock_option_menu, mock_sidebar, mock_set_page_config):
        """Test complete application flow."""
        # Arrange
        mock_option_menu.return_value = "Home"
        
        # Act
        with patch('src.ui.home.render_home') as mock_render_home:
            main()
        
        # Assert
        mock_render_home.assert_called_once()
        mock_set_page_config.assert_called_once()
```

## Best Practices

### 1. Mock External Dependencies

Always mock external dependencies like:
- Streamlit functions
- Database connections
- API calls
- File operations

### 2. Use Descriptive Test Names

```python
def test_get_greeting_returns_morning_for_early_hours():
    """Test that greeting returns 'Good Morning' for early hours."""
    pass

def test_display_portfolio_summary_shows_correct_metrics():
    """Test that portfolio summary displays correct metrics."""
    pass
```

### 3. Follow AAA Pattern

- **Arrange**: Set up test data and mocks
- **Act**: Call the function being tested
- **Assert**: Verify the expected behavior

### 4. Test Error Scenarios

```python
def test_app_handles_missing_css_file_gracefully():
    """Test that app handles missing CSS file gracefully."""
    with patch('builtins.open', side_effect=FileNotFoundError):
        # Test that app doesn't crash
        assert main is not None
```

### 5. Use Fixtures for Common Setup

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

## Debugging Tests

### Common Issues

1. **Import Errors**: Ensure `src` is in the Python path
2. **Mock Issues**: Check that mocks are applied correctly
3. **Environment Variables**: Set required environment variables in tests

### Debug Commands

```bash
# Run tests with debug output
pytest test/unit/ui/ -v -s

# Run specific test with debug
pytest test/unit/ui/test_streamlit_app.py::TestStreamlitApp::test_main_function_runs_without_error -v -s

# Run with coverage and show missing lines
pytest test/unit/ui/ --cov=src.ui --cov-report=term-missing
```

## Continuous Integration

The Streamlit tests are integrated into the CI/CD pipeline:

- **Pre-commit**: Runs unit tests before commits
- **CI Pipeline**: Runs all tests on pull requests
- **Coverage Reports**: Generated for test coverage analysis

## Performance Testing

The E2E tests include performance benchmarks:

```python
def test_streamlit_app_performance_under_load():
    """Test Streamlit app performance under simulated load."""
    # Simulate multiple rapid navigation requests
    pages = ["Home", "Analysis", "Settings"] * 10  # 30 requests
    
    start_time = time.time()
    # Run navigation sequence
    end_time = time.time()
    
    # Verify performance is reasonable
    assert (end_time - start_time) < 5.0
```

## Contributing

When adding new Streamlit features:

1. Write unit tests for new functions
2. Add integration tests for component interactions
3. Update E2E tests for new user journeys
4. Update this documentation

## Resources

- [Streamlit Testing Documentation](https://docs.streamlit.io/library/advanced-features/testing)
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Mock Documentation](https://docs.python.org/3/library/unittest.mock.html) 