# Testing Architecture & Strategy

## Overview

This document outlines the comprehensive testing strategy for the Prefect Trading System. Our testing approach follows the testing pyramid model with a focus on maintainable, reliable, and fast feedback loops.

## Testing Philosophy

- **Fast Feedback**: Unit tests provide immediate feedback during development
- **Reliable**: Tests are deterministic and don't depend on external services
- **Maintainable**: Tests are well-organized and easy to understand
- **Comprehensive**: Coverage includes all critical paths and edge cases
- **Automated**: All tests run automatically in CI/CD pipeline

## Testing Pyramid

```
┌─────────────────────────────────────┐
│           E2E Tests                 │  ← 10% - Critical user journeys
│         (Slow, Expensive)           │
├─────────────────────────────────────┤
│         Integration Tests           │  ← 20% - Component interactions
│        (Medium, Moderate)           │
├─────────────────────────────────────┤
│         Unit Tests                  │  ← 70% - Isolated components
│         (Fast, Cheap)               │
└─────────────────────────────────────┘
```

## Test Categories

### 1. Unit Tests (70% of test suite)

**Purpose**: Test individual components in isolation with mocked dependencies.

**Coverage Areas**:
- Data source loaders (Yahoo Finance, Alpaca, News API)
- Database operations and connectivity
- Utility functions and helpers
- Data transformation and validation logic
- Error handling and edge cases

**Characteristics**:
- Fast execution (< 1 second per test)
- No external dependencies
- Mocked external APIs and databases
- High code coverage (90%+)

### 2. Integration Tests (20% of test suite)

**Purpose**: Test component interactions and data flow between modules.

**Coverage Areas**:
- Data pipeline integration (source → processing → storage)
- Prefect flow orchestration and task dependencies
- Database migration and schema validation
- API integration with real external services (in test environment)
- WebSocket data streaming and persistence

**Characteristics**:
- Medium execution time (1-10 seconds per test)
- Real database (test instance)
- Mocked external APIs
- Test actual data flow between components

### 3. End-to-End Tests (10% of test suite)

**Purpose**: Test complete user workflows and system behavior.

**Coverage Areas**:
- Complete data ingestion workflows
- Streamlit UI functionality and user interactions
- Full system integration with real external services
- Performance and load testing scenarios
- Error recovery and system resilience

**Characteristics**:
- Slow execution (10+ seconds per test)
- Real external services (test environment)
- Full system stack
- Critical user journey validation

## Test Infrastructure

### Directory Structure

```
test/
├── conftest.py              # Pytest configuration and shared fixtures
├── unit/                    # Unit tests
│   ├── data/
│   │   ├── sources/
│   │   │   ├── test_yahoo_finance_loader.py
│   │   │   ├── test_alpaca_daily_loader.py
│   │   │   ├── test_news_loader.py
│   │   │   └── test_symbol_manager.py
│   │   └── websocket/
│   │       └── test_alpaca_websocket.py
│   ├── database/
│   │   ├── test_database_connectivity.py
│   │   └── test_migrations.py
│   └── utils/
│       └── test_market_hours.py
├── integration/             # Integration tests
│   ├── flows/
│   │   ├── test_hourly_process_flow.py
│   │   ├── test_eod_process_flow.py
│   │   └── test_websocket_flow.py
│   ├── pipelines/
│   │   ├── test_data_pipeline.py
│   │   └── test_persistence_pipeline.py
│   └── database/
│       ├── test_data_integrity.py
│       └── test_migration_integration.py
├── e2e/                     # End-to-end tests
│   ├── workflows/
│   │   ├── test_complete_data_workflow.py
│   │   └── test_error_recovery.py
│   └── ui/
│       ├── test_dashboard_functionality.py
│       └── test_user_interactions.py
├── fixtures/                # Test data and mocks
│   ├── mock_data/
│   │   ├── yahoo_finance_responses.json
│   │   ├── alpaca_responses.json
│   │   └── news_responses.json
│   ├── test_db/
│   │   ├── schema.sql
│   │   └── seed_data.sql
│   └── api_responses/
│       ├── yahoo_finance/
│       ├── alpaca/
│       └── news_api/
└── utils/                   # Test utilities
    ├── mock_apis.py
    ├── test_db_setup.py
    ├── assertions.py
    └── test_helpers.py
```

### Test Configuration

#### pytest.ini
```ini
[tool:pytest]
testpaths = test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml:coverage.xml
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    api: Tests requiring external APIs
    database: Tests requiring database
```

#### conftest.py
```python
import pytest
import asyncio
from unittest.mock import Mock, patch
from src.database.database_connectivity import DatabaseConnectivity

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_db():
    """Create test database connection."""
    # Implementation for test database setup
    pass

@pytest.fixture
def mock_yahoo_api():
    """Mock Yahoo Finance API responses."""
    with patch('src.data.sources.yahoo_finance_loader.requests.get') as mock_get:
        # Setup mock responses
        yield mock_get

@pytest.fixture
def mock_alpaca_api():
    """Mock Alpaca API responses."""
    with patch('src.data.sources.alpaca_daily_loader.AlpacaAPI') as mock_api:
        # Setup mock responses
        yield mock_api
```

## Testing Strategy by Component

### Data Sources Testing

#### Yahoo Finance Loader
```python
# test/unit/data/sources/test_yahoo_finance_loader.py
import pytest
from unittest.mock import Mock, patch
from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader

class TestYahooFinanceDataLoader:
    
    @pytest.fixture
    def loader(self):
        return YahooFinanceDataLoader()
    
    def test_fetch_stock_data_success(self, loader, mock_yahoo_api):
        """Test successful stock data fetching."""
        # Arrange
        mock_yahoo_api.return_value.json.return_value = {
            "chart": {"result": [{"meta": {}, "timestamp": [], "indicators": {}}]}
        }
        
        # Act
        result = loader.fetch_stock_data("AAPL")
        
        # Assert
        assert result is not None
        mock_yahoo_api.assert_called_once()
    
    def test_fetch_stock_data_api_error(self, loader, mock_yahoo_api):
        """Test handling of API errors."""
        # Arrange
        mock_yahoo_api.side_effect = Exception("API Error")
        
        # Act & Assert
        with pytest.raises(Exception):
            loader.fetch_stock_data("AAPL")
    
    def test_data_validation(self, loader):
        """Test data validation logic."""
        # Test various data validation scenarios
        pass
```

#### Alpaca Daily Loader
```python
# test/unit/data/sources/test_alpaca_daily_loader.py
import pytest
from unittest.mock import Mock, patch
from src.data.sources.alpaca_daily_loader import AlpacaDailyLoader

class TestAlpacaDailyLoader:
    
    def test_daily_data_loading(self, mock_alpaca_api):
        """Test daily data loading functionality."""
        # Test implementation
        pass
    
    def test_rate_limiting(self, mock_alpaca_api):
        """Test rate limiting behavior."""
        # Test implementation
        pass
```

### Database Testing

#### Database Connectivity
```python
# test/unit/database/test_database_connectivity.py
import pytest
from src.database.database_connectivity import DatabaseConnectivity

class TestDatabaseConnectivity:
    
    def test_connection_establishment(self, test_db):
        """Test database connection establishment."""
        # Test implementation
        pass
    
    def test_connection_pooling(self, test_db):
        """Test connection pooling functionality."""
        # Test implementation
        pass
    
    def test_error_handling(self, test_db):
        """Test database error handling."""
        # Test implementation
        pass
```

### Prefect Flows Testing

#### Flow Orchestration
```python
# test/integration/flows/test_hourly_process_flow.py
import pytest
from prefect import flow
from main import hourly_process_flow

class TestHourlyProcessFlow:
    
    @pytest.mark.integration
    def test_flow_execution_order(self, mock_apis, test_db):
        """Test that flow tasks execute in correct order."""
        # Test implementation
        pass
    
    @pytest.mark.integration
    def test_flow_error_handling(self, mock_apis, test_db):
        """Test flow error handling and retry logic."""
        # Test implementation
        pass
```

## Mocking Strategy

### External API Mocking

#### Yahoo Finance API
```python
# test/utils/mock_apis.py
import json
from pathlib import Path

class YahooFinanceAPIMock:
    """Mock Yahoo Finance API responses."""
    
    def __init__(self):
        self.responses_path = Path("test/fixtures/api_responses/yahoo_finance")
    
    def get_stock_data(self, symbol):
        """Mock stock data response."""
        response_file = self.responses_path / f"{symbol}_data.json"
        with open(response_file) as f:
            return json.load(f)
    
    def get_company_info(self, symbol):
        """Mock company info response."""
        response_file = self.responses_path / f"{symbol}_info.json"
        with open(response_file) as f:
            return json.load(f)
```

#### Alpaca API
```python
class AlpacaAPIMock:
    """Mock Alpaca API responses."""
    
    def __init__(self):
        self.responses_path = Path("test/fixtures/api_responses/alpaca")
    
    def get_bars(self, symbol, timeframe, start, end):
        """Mock market data response."""
        response_file = self.responses_path / f"{symbol}_{timeframe}.json"
        with open(response_file) as f:
            return json.load(f)
```

### Database Mocking

#### Test Database Setup
```python
# test/utils/test_db_setup.py
import pytest
import psycopg2
from src.database.database_connectivity import DatabaseConnectivity

@pytest.fixture(scope="session")
def test_database():
    """Create and manage test database."""
    # Create test database
    # Run migrations
    # Seed test data
    yield database
    # Cleanup
```

## Test Data Management

### Fixtures and Factories

#### Data Factories
```python
# test/fixtures/factories.py
import factory
from datetime import datetime, timedelta

class StockDataFactory(factory.Factory):
    """Factory for creating test stock data."""
    
    class Meta:
        model = dict
    
    symbol = factory.Sequence(lambda n: f"STOCK{n}")
    price = factory.Faker('pyfloat', left_digits=3, right_digits=2, positive=True)
    volume = factory.Faker('pyint', min_value=1000, max_value=1000000)
    timestamp = factory.LazyFunction(datetime.now)

class NewsArticleFactory(factory.Factory):
    """Factory for creating test news articles."""
    
    class Meta:
        model = dict
    
    title = factory.Faker('sentence')
    content = factory.Faker('paragraph')
    published_at = factory.Faker('date_time')
    source = factory.Faker('company')
```

### Test Data Sets

#### Market Data
```json
// test/fixtures/mock_data/market_data.json
{
  "AAPL": {
    "symbol": "AAPL",
    "price": 150.25,
    "volume": 50000000,
    "timestamp": "2024-01-15T09:30:00Z"
  },
  "GOOGL": {
    "symbol": "GOOGL",
    "price": 2800.75,
    "volume": 25000000,
    "timestamp": "2024-01-15T09:30:00Z"
  }
}
```

## Performance Testing

### Load Testing

#### Data Ingestion Performance
```python
# test/performance/test_data_ingestion.py
import pytest
import time
from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader

class TestDataIngestionPerformance:
    
    def test_large_dataset_processing(self):
        """Test processing of large datasets."""
        loader = YahooFinanceDataLoader()
        symbols = [f"STOCK{i}" for i in range(1000)]
        
        start_time = time.time()
        results = loader.batch_fetch_data(symbols)
        end_time = time.time()
        
        assert end_time - start_time < 60  # Should complete within 60 seconds
        assert len(results) == 1000
```

### Stress Testing

#### API Rate Limiting
```python
# test/performance/test_rate_limiting.py
import pytest
import asyncio
from src.data.sources.alpaca_daily_loader import AlpacaDailyLoader

class TestRateLimiting:
    
    @pytest.mark.asyncio
    async def test_concurrent_api_calls(self):
        """Test handling of concurrent API calls."""
        loader = AlpacaDailyLoader()
        
        # Make concurrent API calls
        tasks = [loader.fetch_data("AAPL") for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify rate limiting behavior
        assert all(not isinstance(r, Exception) for r in results)
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run unit tests
      run: |
        pytest test/unit/ -v --cov=src --cov-report=xml
    
    - name: Run integration tests
      run: |
        pytest test/integration/ -v --cov=src --cov-report=xml
    
    - name: Run E2E tests
      run: |
        pytest test/e2e/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Test Execution

### Local Development

```bash
# Run all tests
pytest

# Run specific test categories
pytest test/unit/                    # Unit tests only
pytest test/integration/             # Integration tests only
pytest test/e2e/                     # E2E tests only

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run tests in parallel
pytest -n auto

# Run specific test file
pytest test/unit/data/sources/test_yahoo_finance_loader.py

# Run tests with specific markers
pytest -m "not slow"                 # Skip slow tests
pytest -m "api"                      # Run only API tests
```

### CI/CD Pipeline

```bash
# Pre-commit hooks
pre-commit install
pre-commit run --all-files

# Automated testing
pytest test/unit/ --cov=src --cov-report=xml
pytest test/integration/ --cov=src --cov-report=xml
pytest test/e2e/ --cov=src --cov-report=xml
```

## Coverage Goals

### Code Coverage Targets

- **Unit Tests**: 90%+ line coverage
- **Integration Tests**: 80%+ critical path coverage
- **E2E Tests**: 100% user journey coverage

### Coverage Reporting

```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing

# View coverage in browser
open htmlcov/index.html
```

## Best Practices

### Test Organization

1. **AAA Pattern**: Arrange, Act, Assert
2. **Descriptive Names**: Test names should clearly describe what is being tested
3. **Single Responsibility**: Each test should test one specific behavior
4. **Test Isolation**: Tests should not depend on each other

### Mocking Guidelines

1. **Mock External Dependencies**: Always mock external APIs and databases in unit tests
2. **Use Real Dependencies**: Use real dependencies in integration tests
3. **Mock Time**: Mock time-dependent operations for deterministic tests
4. **Mock Randomness**: Use fixed seeds for reproducible tests

### Error Testing

1. **Test Error Conditions**: Always test error handling and edge cases
2. **Test Retry Logic**: Verify retry mechanisms work correctly
3. **Test Timeouts**: Test timeout handling for external services
4. **Test Invalid Data**: Test handling of malformed or invalid data

### Performance Considerations

1. **Fast Unit Tests**: Unit tests should run in milliseconds
2. **Parallel Execution**: Use pytest-xdist for parallel test execution
3. **Test Data Size**: Keep test data sets reasonable in size
4. **Database Cleanup**: Clean up test data after each test

## Monitoring and Maintenance

### Test Metrics

- **Execution Time**: Track test execution time trends
- **Coverage Trends**: Monitor code coverage over time
- **Flaky Tests**: Identify and fix unstable tests
- **Test Maintenance**: Regular review and cleanup of test code

### Test Maintenance

1. **Regular Reviews**: Review test code quality regularly
2. **Update Mocks**: Keep mock data up to date with API changes
3. **Refactor Tests**: Refactor tests when application code changes
4. **Remove Obsolete Tests**: Remove tests for removed functionality

## Troubleshooting

### Common Issues

1. **Flaky Tests**: Use retry mechanisms and proper cleanup
2. **Slow Tests**: Optimize test data and mocking strategies
3. **Coverage Gaps**: Identify and add tests for uncovered code
4. **Test Dependencies**: Ensure proper test isolation

### Debugging Tests

```bash
# Run tests with debug output
pytest -v -s

# Run specific test with debugger
pytest test_file.py::test_function -s --pdb

# Run tests with detailed logging
pytest --log-cli-level=DEBUG
```

This testing architecture provides a solid foundation for maintaining code quality and ensuring system reliability throughout the development lifecycle. 