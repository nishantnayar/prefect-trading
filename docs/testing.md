# Testing Guide

## Overview

This document provides comprehensive guidance for testing the Prefect Trading System. The testing strategy follows a multi-layered approach with unit tests, integration tests, and end-to-end tests to ensure system reliability and maintainability.

## Testing Strategy

### Test Pyramid
```
    /\
   /  \     E2E Tests (Few)
  /____\    Integration Tests (Some)
 /______\   Unit Tests (Many)
```

### Test Categories

1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test component interactions
3. **End-to-End Tests** - Test complete user workflows
4. **Performance Tests** - Test system performance under load

## Test Structure

```
test/
├── unit/                    # Unit tests
│   ├── data/               # Data layer tests
│   ├── database/           # Database tests
│   ├── ui/                 # UI component tests
│   └── utils/              # Utility function tests
├── integration/            # Integration tests
│   ├── api/                # API integration tests
│   ├── database/           # Database integration tests
│   └── workflows/          # Workflow integration tests
├── e2e/                    # End-to-end tests
│   ├── ui/                 # UI workflow tests
│   └── workflows/          # Complete workflow tests
├── fixtures/               # Test fixtures and data
└── conftest.py            # Pytest configuration
```

## Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest test/unit/test_database.py

# Run specific test function
pytest test/unit/test_database.py::test_connection
```

### Test Categories
```bash
# Run only unit tests
pytest test/unit/

# Run only integration tests
pytest test/integration/

# Run only e2e tests
pytest test/e2e/

# Run tests with specific markers
pytest -m "slow"
pytest -m "not slow"
```

### Coverage Reports
```bash
# Generate coverage report
pytest --cov=src --cov-report=html tests/

# Generate coverage report in terminal
pytest --cov=src --cov-report=term-missing tests/

# Generate XML coverage report
pytest --cov=src --cov-report=xml tests/
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
    unit: marks tests as unit tests
```

### Test Fixtures (`conftest.py`)
```python
import pytest
from unittest.mock import Mock, patch
from src.database.database_connectivity import DatabaseConnectivity

@pytest.fixture
def mock_db():
    """Mock database connection for testing."""
    with patch('src.database.database_connectivity.DatabaseConnectivity') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def sample_market_data():
    """Sample market data for testing."""
    return {
        'symbol': 'AAPL',
        'price': 150.0,
        'volume': 1000000,
        'timestamp': '2024-01-01T09:30:00Z'
    }

@pytest.fixture
def sample_news_data():
    """Sample news data for testing."""
    return {
        'title': 'Test News Article',
        'content': 'This is a test news article.',
        'source': 'Test Source',
        'published_at': '2024-01-01T10:00:00Z'
    }
```

## Unit Testing

### Data Layer Tests
```python
# test/unit/data/test_yahoo_finance_loader.py
import pytest
from unittest.mock import Mock, patch
from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader

class TestYahooFinanceDataLoader:
    
    def test_initialization(self):
        """Test YahooFinanceDataLoader initialization."""
        loader = YahooFinanceDataLoader()
        assert loader is not None
        assert hasattr(loader, 'run')
    
    @patch('src.data.sources.yahoo_finance_loader.requests.get')
    def test_fetch_data_success(self, mock_get):
        """Test successful data fetching."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_get.return_value = mock_response
        
        loader = YahooFinanceDataLoader()
        result = loader.fetch_data('AAPL')
        
        assert result == {'data': 'test'}
        mock_get.assert_called_once()
    
    @patch('src.data.sources.yahoo_finance_loader.requests.get')
    def test_fetch_data_error(self, mock_get):
        """Test error handling in data fetching."""
        mock_get.side_effect = Exception("Network error")
        
        loader = YahooFinanceDataLoader()
        with pytest.raises(Exception):
            loader.fetch_data('AAPL')
```

### Database Tests
```python
# test/unit/database/test_database_connectivity.py
import pytest
from unittest.mock import Mock, patch
from src.database.database_connectivity import DatabaseConnectivity

class TestDatabaseConnectivity:
    
    def test_connection_initialization(self):
        """Test database connection initialization."""
        with patch('src.database.database_connectivity.create_engine') as mock_engine:
            db = DatabaseConnectivity()
            assert db is not None
            mock_engine.assert_called_once()
    
    def test_execute_query_success(self, mock_db):
        """Test successful query execution."""
        mock_db.execute.return_value = [{'result': 'test'}]
        
        result = mock_db.execute_query("SELECT * FROM test")
        assert result == [{'result': 'test'}]
        mock_db.execute.assert_called_once()
    
    def test_execute_query_error(self, mock_db):
        """Test error handling in query execution."""
        mock_db.execute.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            mock_db.execute_query("SELECT * FROM test")
```

### UI Component Tests
```python
# test/unit/ui/test_components.py
import pytest
import streamlit as st
from src.ui.components.market_status import MarketStatus

class TestMarketStatus:
    
    def test_market_status_initialization(self):
        """Test MarketStatus component initialization."""
        component = MarketStatus()
        assert component is not None
    
    def test_market_status_display(self):
        """Test market status display."""
        # Mock Streamlit components
        with patch('streamlit.container') as mock_container:
            component = MarketStatus()
            component.display()
            mock_container.assert_called()
```

## Integration Testing

### API Integration Tests
```python
# test/integration/api/test_alpaca_integration.py
import pytest
from src.data.sources.alpaca_daily_loader import AlpacaDailyLoader

class TestAlpacaIntegration:
    
    @pytest.mark.integration
    def test_alpaca_connection(self):
        """Test Alpaca API connection."""
        loader = AlpacaDailyLoader()
        # Test actual API connection (requires valid credentials)
        assert loader.client is not None
    
    @pytest.mark.integration
    def test_market_data_fetch(self):
        """Test market data fetching from Alpaca."""
        loader = AlpacaDailyLoader()
        data = loader.fetch_market_data('AAPL')
        assert data is not None
        assert 'symbol' in data
        assert 'price' in data
```

### Database Integration Tests
```python
# test/integration/database/test_data_persistence.py
import pytest
from src.database.database_connectivity import DatabaseConnectivity
from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader

class TestDataPersistence:
    
    @pytest.mark.integration
    def test_data_storage(self):
        """Test data storage in database."""
        db = DatabaseConnectivity()
        loader = YahooFinanceDataLoader()
        
        # Fetch and store data
        data = loader.fetch_data('AAPL')
        result = db.store_market_data(data)
        
        assert result is True
        
        # Verify data was stored
        stored_data = db.get_market_data('AAPL')
        assert stored_data is not None
        assert stored_data['symbol'] == 'AAPL'
```

## End-to-End Testing

### UI Workflow Tests
```python
# test/e2e/ui/test_dashboard_workflow.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestDashboardWorkflow:
    
    @pytest.fixture(autouse=True)
    def setup_driver(self):
        """Setup web driver for UI testing."""
        self.driver = webdriver.Chrome()
        yield
        self.driver.quit()
    
    @pytest.mark.e2e
    def test_dashboard_load(self):
        """Test dashboard loads correctly."""
        self.driver.get("http://localhost:8501")
        
        # Wait for page to load
        wait = WebDriverWait(self.driver, 10)
        title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        
        assert "Trading System" in title.text
    
    @pytest.mark.e2e
    def test_symbol_selection(self):
        """Test symbol selection functionality."""
        self.driver.get("http://localhost:8501")
        
        # Find and click symbol selector
        symbol_input = self.driver.find_element(By.ID, "symbol-input")
        symbol_input.send_keys("AAPL")
        
        # Verify symbol is selected
        selected_symbol = self.driver.find_element(By.CLASS_NAME, "selected-symbol")
        assert "AAPL" in selected_symbol.text
```

### Workflow Tests
```python
# test/e2e/workflows/test_complete_workflow.py
import pytest
from main import hourly_process_flow, eod_process_flow

class TestCompleteWorkflow:
    
    @pytest.mark.e2e
    def test_hourly_workflow(self):
        """Test complete hourly workflow."""
        # Run hourly workflow
        result = hourly_process_flow()
        
        # Verify workflow completed successfully
        assert result is not None
        
        # Verify data was collected and stored
        # This would check the database for new data
        db = DatabaseConnectivity()
        recent_data = db.get_recent_market_data()
        assert len(recent_data) > 0
    
    @pytest.mark.e2e
    def test_eod_workflow(self):
        """Test complete end-of-day workflow."""
        # Run EOD workflow
        result = eod_process_flow()
        
        # Verify workflow completed successfully
        assert result is not None
        
        # Verify daily data was processed
        db = DatabaseConnectivity()
        daily_summary = db.get_daily_summary()
        assert daily_summary is not None
```

## Performance Testing

### Load Testing
```python
# test/performance/test_load.py
import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader

class TestLoadPerformance:
    
    @pytest.mark.slow
    def test_concurrent_data_fetching(self):
        """Test concurrent data fetching performance."""
        loader = YahooFinanceDataLoader()
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(loader.fetch_data, symbol) for symbol in symbols]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify all requests completed
        assert len(results) == len(symbols)
        
        # Verify performance (should complete within 10 seconds)
        assert duration < 10.0
    
    @pytest.mark.slow
    def test_database_performance(self):
        """Test database query performance."""
        db = DatabaseConnectivity()
        
        start_time = time.time()
        
        # Execute multiple queries
        for _ in range(100):
            db.execute_query("SELECT * FROM market_data LIMIT 1")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify performance (should complete within 5 seconds)
        assert duration < 5.0
```

## Test Data Management

### Fixtures and Factories
```python
# test/fixtures/data_factories.py
import factory
from datetime import datetime, timezone
from src.database.models import MarketData, NewsArticle

class MarketDataFactory(factory.Factory):
    class Meta:
        model = MarketData
    
    symbol = factory.Sequence(lambda n: f"SYMBOL{n}")
    price = factory.Faker('pyfloat', left_digits=3, right_digits=2, positive=True)
    volume = factory.Faker('pyint', min_value=1000, max_value=1000000)
    timestamp = factory.LazyFunction(lambda: datetime.now(timezone.utc))

class NewsArticleFactory(factory.Factory):
    class Meta:
        model = NewsArticle
    
    title = factory.Faker('sentence')
    content = factory.Faker('paragraph')
    source = factory.Faker('company')
    published_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
```

### Test Database Setup
```python
# test/fixtures/database.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def test_session(test_engine):
    """Create test database session."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
```

## Continuous Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:12
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      env:
        DB_HOST: localhost
        DB_PORT: 5432
        DB_NAME: test_db
        DB_USER: postgres
        DB_PASSWORD: postgres
      run: |
        pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

## Best Practices

### Test Organization
1. **Group related tests** in classes
2. **Use descriptive test names** that explain the scenario
3. **Follow AAA pattern**: Arrange, Act, Assert
4. **Keep tests independent** and isolated
5. **Use appropriate fixtures** for common setup

### Test Data
1. **Use factories** for creating test data
2. **Avoid hardcoded values** in tests
3. **Clean up test data** after tests
4. **Use realistic data** that matches production

### Performance
1. **Mock external services** in unit tests
2. **Use test databases** for integration tests
3. **Run slow tests separately** from fast tests
4. **Monitor test execution time**

### Maintenance
1. **Update tests** when code changes
2. **Review test coverage** regularly
3. **Refactor tests** to reduce duplication
4. **Document complex test scenarios**

## Troubleshooting

### Common Issues
1. **Database connection errors**: Check test database configuration
2. **API rate limiting**: Use mocks for external API calls
3. **Test isolation**: Ensure tests don't interfere with each other
4. **Environment variables**: Set up test environment properly

### Debugging Tests
```bash
# Run tests with debug output
pytest -s -v

# Run specific test with debugger
pytest --pdb test_file.py::test_function

# Run tests with logging
pytest --log-cli-level=DEBUG
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Factory Boy Documentation](https://factoryboy.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Selenium Documentation](https://selenium-python.readthedocs.io/) 