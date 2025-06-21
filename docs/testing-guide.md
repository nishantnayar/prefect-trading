# Testing Implementation Guide

## Overview

This document provides detailed implementation guidelines and specific test case examples for the Prefect Trading System. It complements the testing architecture document with practical examples and step-by-step implementation approaches.

## Component-Specific Testing Implementation

### 1. Data Sources Testing

#### Yahoo Finance Loader Tests

```python
# test/unit/data/sources/test_yahoo_finance_loader.py
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader

class TestYahooFinanceDataLoader:
    
    @pytest.fixture
    def loader(self):
        return YahooFinanceDataLoader()
    
    @pytest.fixture
    def mock_yahoo_response(self):
        """Mock Yahoo Finance API response."""
        return {
            "chart": {
                "result": [{
                    "meta": {
                        "symbol": "AAPL",
                        "regularMarketPrice": 150.25,
                        "regularMarketVolume": 50000000
                    },
                    "timestamp": [1642248000, 1642334400],
                    "indicators": {
                        "quote": [{
                            "open": [150.0, 151.0],
                            "high": [152.0, 153.0],
                            "low": [149.0, 150.5],
                            "close": [150.25, 151.75],
                            "volume": [50000000, 45000000]
                        }]
                    }
                }],
                "error": None
            }
        }
    
    def test_fetch_stock_data_success(self, loader, mock_yahoo_response):
        """Test successful stock data fetching."""
        with patch('requests.get') as mock_get:
            # Arrange
            mock_response = Mock()
            mock_response.json.return_value = mock_yahoo_response
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            # Act
            result = loader.fetch_stock_data("AAPL")
            
            # Assert
            assert result is not None
            assert result['symbol'] == "AAPL"
            assert result['price'] == 150.25
            assert result['volume'] == 50000000
            mock_get.assert_called_once()
    
    def test_fetch_stock_data_api_error(self, loader):
        """Test handling of API errors."""
        with patch('requests.get') as mock_get:
            # Arrange
            mock_get.side_effect = Exception("API Error")
            
            # Act & Assert
            with pytest.raises(Exception, match="API Error"):
                loader.fetch_stock_data("AAPL")
    
    def test_fetch_stock_data_invalid_symbol(self, loader):
        """Test handling of invalid stock symbols."""
        with patch('requests.get') as mock_get:
            # Arrange
            mock_response = Mock()
            mock_response.json.return_value = {
                "chart": {"result": None, "error": {"code": "Not Found"}}
            }
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid symbol"):
                loader.fetch_stock_data("INVALID")
    
    def test_fetch_stock_data_rate_limiting(self, loader):
        """Test rate limiting behavior."""
        with patch('requests.get') as mock_get:
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 429  # Too Many Requests
            mock_get.return_value = mock_response
            
            # Act & Assert
            with pytest.raises(Exception, match="Rate limit exceeded"):
                loader.fetch_stock_data("AAPL")
    
    def test_batch_fetch_data(self, loader, mock_yahoo_response):
        """Test batch data fetching."""
        with patch('requests.get') as mock_get:
            # Arrange
            mock_response = Mock()
            mock_response.json.return_value = mock_yahoo_response
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            symbols = ["AAPL", "GOOGL", "MSFT"]
            
            # Act
            results = loader.batch_fetch_data(symbols)
            
            # Assert
            assert len(results) == 3
            assert all(result['symbol'] in symbols for result in results)
            assert mock_get.call_count == 3
    
    def test_data_validation(self, loader):
        """Test data validation logic."""
        # Test with missing required fields
        invalid_data = {"chart": {"result": [{"meta": {}}]}}
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = invalid_data
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            with pytest.raises(ValueError, match="Missing required data"):
                loader.fetch_stock_data("AAPL")
    
    @pytest.mark.parametrize("symbol,expected_price", [
        ("AAPL", 150.25),
        ("GOOGL", 2800.75),
        ("MSFT", 300.50)
    ])
    def test_multiple_symbols(self, loader, symbol, expected_price):
        """Test fetching data for multiple symbols."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "chart": {
                    "result": [{
                        "meta": {
                            "symbol": symbol,
                            "regularMarketPrice": expected_price
                        }
                    }]
                }
            }
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = loader.fetch_stock_data(symbol)
            assert result['price'] == expected_price
```

#### Alpaca Daily Loader Tests

```python
# test/unit/data/sources/test_alpaca_daily_loader.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from src.data.sources.alpaca_daily_loader import AlpacaDailyLoader

class TestAlpacaDailyLoader:
    
    @pytest.fixture
    def loader(self):
        return AlpacaDailyLoader()
    
    @pytest.fixture
    def mock_alpaca_bars(self):
        """Mock Alpaca bars data."""
        return {
            "AAPL": [
                {
                    "t": "2024-01-15T09:30:00Z",
                    "o": 150.0,
                    "h": 152.0,
                    "l": 149.0,
                    "c": 150.25,
                    "v": 50000000
                }
            ]
        }
    
    def test_fetch_daily_data_success(self, loader, mock_alpaca_bars):
        """Test successful daily data fetching."""
        with patch('alpaca.data.historical.StockHistoricalDataClient') as mock_client:
            # Arrange
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance
            mock_client_instance.get_bars.return_value = mock_alpaca_bars
            
            # Act
            result = loader.fetch_daily_data("AAPL")
            
            # Assert
            assert result is not None
            assert "AAPL" in result
            mock_client_instance.get_bars.assert_called_once()
    
    def test_fetch_daily_data_api_error(self, loader):
        """Test handling of Alpaca API errors."""
        with patch('alpaca.data.historical.StockHistoricalDataClient') as mock_client:
            # Arrange
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance
            mock_client_instance.get_bars.side_effect = Exception("API Error")
            
            # Act & Assert
            with pytest.raises(Exception, match="API Error"):
                loader.fetch_daily_data("AAPL")
    
    def test_rate_limiting_behavior(self, loader):
        """Test rate limiting implementation."""
        with patch('alpaca.data.historical.StockHistoricalDataClient') as mock_client:
            # Arrange
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance
            mock_client_instance.get_bars.side_effect = [
                Exception("Rate limit exceeded"),
                {"AAPL": []}  # Success on retry
            ]
            
            # Act
            result = loader.fetch_daily_data("AAPL")
            
            # Assert
            assert result is not None
            assert mock_client_instance.get_bars.call_count == 2
    
    def test_data_transformation(self, loader, mock_alpaca_bars):
        """Test data transformation logic."""
        with patch('alpaca.data.historical.StockHistoricalDataClient') as mock_client:
            # Arrange
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance
            mock_client_instance.get_bars.return_value = mock_alpaca_bars
            
            # Act
            result = loader.fetch_daily_data("AAPL")
            
            # Assert
            transformed_data = result["AAPL"][0]
            assert "timestamp" in transformed_data
            assert "open" in transformed_data
            assert "high" in transformed_data
            assert "low" in transformed_data
            assert "close" in transformed_data
            assert "volume" in transformed_data
```

### 2. Database Testing

#### Database Connectivity Tests

```python
# test/unit/database/test_database_connectivity.py
import pytest
import psycopg2
from unittest.mock import Mock, patch, MagicMock
from src.database.database_connectivity import DatabaseConnectivity

class TestDatabaseConnectivity:
    
    @pytest.fixture
    def db_connectivity(self):
        return DatabaseConnectivity()
    
    def test_connection_establishment(self, db_connectivity):
        """Test database connection establishment."""
        with patch('psycopg2.connect') as mock_connect:
            # Arrange
            mock_connection = Mock()
            mock_connect.return_value = mock_connection
            
            # Act
            connection = db_connectivity.get_connection()
            
            # Assert
            assert connection is not None
            mock_connect.assert_called_once()
    
    def test_connection_pooling(self, db_connectivity):
        """Test connection pooling functionality."""
        with patch('psycopg2.connect') as mock_connect:
            # Arrange
            mock_connection = Mock()
            mock_connect.return_value = mock_connection
            
            # Act - Get multiple connections
            conn1 = db_connectivity.get_connection()
            conn2 = db_connectivity.get_connection()
            
            # Assert - Should reuse connections from pool
            assert conn1 is conn2
            mock_connect.assert_called_once()
    
    def test_connection_error_handling(self, db_connectivity):
        """Test database connection error handling."""
        with patch('psycopg2.connect') as mock_connect:
            # Arrange
            mock_connect.side_effect = psycopg2.OperationalError("Connection failed")
            
            # Act & Assert
            with pytest.raises(psycopg2.OperationalError):
                db_connectivity.get_connection()
    
    def test_execute_query_success(self, db_connectivity):
        """Test successful query execution."""
        with patch('psycopg2.connect') as mock_connect:
            # Arrange
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connection.cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = [{"id": 1, "name": "AAPL"}]
            mock_connect.return_value = mock_connection
            
            # Act
            result = db_connectivity.execute_query("SELECT * FROM symbols")
            
            # Assert
            assert result == [{"id": 1, "name": "AAPL"}]
            mock_cursor.execute.assert_called_once_with("SELECT * FROM symbols")
    
    def test_execute_query_error(self, db_connectivity):
        """Test query execution error handling."""
        with patch('psycopg2.connect') as mock_connect:
            # Arrange
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connection.cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = psycopg2.Error("Query failed")
            mock_connect.return_value = mock_connection
            
            # Act & Assert
            with pytest.raises(psycopg2.Error):
                db_connectivity.execute_query("SELECT * FROM invalid_table")
    
    def test_transaction_management(self, db_connectivity):
        """Test transaction management."""
        with patch('psycopg2.connect') as mock_connect:
            # Arrange
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connection.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_connection
            
            # Act
            with db_connectivity.transaction() as cursor:
                cursor.execute("INSERT INTO symbols (name) VALUES ('AAPL')")
            
            # Assert
            mock_connection.commit.assert_called_once()
            mock_cursor.execute.assert_called_once()
    
    def test_transaction_rollback_on_error(self, db_connectivity):
        """Test transaction rollback on error."""
        with patch('psycopg2.connect') as mock_connect:
            # Arrange
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connection.cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = Exception("Database error")
            mock_connect.return_value = mock_connection
            
            # Act & Assert
            with pytest.raises(Exception):
                with db_connectivity.transaction() as cursor:
                    cursor.execute("INSERT INTO symbols (name) VALUES ('AAPL')")
            
            # Assert rollback was called
            mock_connection.rollback.assert_called_once()
```

### 3. Prefect Flows Testing

#### Flow Orchestration Tests

```python
# test/integration/flows/test_hourly_process_flow.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from prefect import flow
from main import hourly_process_flow, news_data_loader_flow

class TestHourlyProcessFlow:
    
    @pytest.mark.integration
    def test_flow_execution_order(self):
        """Test that flow tasks execute in correct order."""
        with patch('src.database.database_connectivity.DatabaseConnectivity') as mock_db:
            with patch('src.data.sources.news.NewsLoader') as mock_news:
                # Arrange
                mock_db_instance = Mock()
                mock_db.return_value = mock_db_instance
                mock_news_instance = Mock()
                mock_news.return_value = mock_news_instance
                
                # Act
                result = hourly_process_flow()
                
                # Assert
                assert result is not None
                mock_news_instance.fetch_and_store_news.assert_called_once()
    
    @pytest.mark.integration
    def test_flow_error_handling(self):
        """Test flow error handling and retry logic."""
        with patch('src.database.database_connectivity.DatabaseConnectivity') as mock_db:
            with patch('src.data.sources.news.NewsLoader') as mock_news:
                # Arrange
                mock_db_instance = Mock()
                mock_db.return_value = mock_db_instance
                mock_news_instance = Mock()
                mock_news.return_value = mock_news_instance
                mock_news_instance.fetch_and_store_news.side_effect = Exception("News API error")
                
                # Act & Assert
                with pytest.raises(Exception, match="News API error"):
                    hourly_process_flow()
    
    @pytest.mark.integration
    def test_flow_dependencies(self):
        """Test flow task dependencies."""
        with patch('src.database.database_connectivity.DatabaseConnectivity') as mock_db:
            with patch('src.data.sources.news.NewsLoader') as mock_news:
                # Arrange
                mock_db_instance = Mock()
                mock_db.return_value = mock_db_instance
                mock_news_instance = Mock()
                mock_news.return_value = mock_news_instance
                
                # Act
                result = hourly_process_flow()
                
                # Assert - Database connection should be established before news loading
                mock_db.assert_called_once()
                mock_news.assert_called_once()
    
    @pytest.mark.integration
    def test_flow_logging(self):
        """Test flow logging functionality."""
        with patch('src.database.database_connectivity.DatabaseConnectivity') as mock_db:
            with patch('src.data.sources.news.NewsLoader') as mock_news:
                with patch('prefect.get_run_logger') as mock_logger:
                    # Arrange
                    mock_db_instance = Mock()
                    mock_db.return_value = mock_db_instance
                    mock_news_instance = Mock()
                    mock_news.return_value = mock_news_instance
                    mock_logger_instance = Mock()
                    mock_logger.return_value = mock_logger_instance
                    
                    # Act
                    hourly_process_flow()
                    
                    # Assert
                    mock_logger_instance.info.assert_called()
                    mock_logger_instance.error.assert_not_called()
```

### 4. WebSocket Testing

#### WebSocket Data Streaming Tests

```python
# test/unit/data/websocket/test_alpaca_websocket.py
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.data.sources.alpaca_websocket import AlpacaWebSocket

class TestAlpacaWebSocket:
    
    @pytest.fixture
    def websocket(self):
        return AlpacaWebSocket()
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self, websocket):
        """Test WebSocket connection establishment."""
        with patch('websockets.connect') as mock_connect:
            # Arrange
            mock_websocket = AsyncMock()
            mock_connect.return_value.__aenter__.return_value = mock_websocket
            
            # Act
            await websocket.connect()
            
            # Assert
            mock_connect.assert_called_once()
            assert websocket.is_connected()
    
    @pytest.mark.asyncio
    async def test_websocket_data_reception(self, websocket):
        """Test WebSocket data reception."""
        with patch('websockets.connect') as mock_connect:
            # Arrange
            mock_websocket = AsyncMock()
            mock_websocket.recv.return_value = '{"T":"t","S":"AAPL","p":150.25,"s":100}'
            mock_connect.return_value.__aenter__.return_value = mock_websocket
            
            # Act
            await websocket.connect()
            data = await websocket.receive_data()
            
            # Assert
            assert data is not None
            assert data['symbol'] == 'AAPL'
            assert data['price'] == 150.25
    
    @pytest.mark.asyncio
    async def test_websocket_reconnection(self, websocket):
        """Test WebSocket reconnection logic."""
        with patch('websockets.connect') as mock_connect:
            # Arrange
            mock_websocket = AsyncMock()
            mock_websocket.recv.side_effect = [
                '{"T":"t","S":"AAPL","p":150.25,"s":100}',
                Exception("Connection lost"),
                '{"T":"t","S":"AAPL","p":150.50,"s":200}'
            ]
            mock_connect.return_value.__aenter__.return_value = mock_websocket
            
            # Act
            await websocket.connect()
            data1 = await websocket.receive_data()
            data2 = await websocket.receive_data()
            
            # Assert
            assert data1 is not None
            assert data2 is not None
            assert mock_connect.call_count >= 2  # Reconnection occurred
```

### 5. UI Testing

#### Streamlit Dashboard Tests

```python
# test/e2e/ui/test_dashboard_functionality.py
import pytest
import streamlit as st
from unittest.mock import Mock, patch, MagicMock
from src.ui.streamlit_app import main

class TestDashboardFunctionality:
    
    @pytest.fixture
    def mock_streamlit(self):
        """Mock Streamlit components."""
        with patch('streamlit.title') as mock_title:
            with patch('streamlit.sidebar') as mock_sidebar:
                with patch('streamlit.container') as mock_container:
                    with patch('streamlit.metric') as mock_metric:
                        with patch('streamlit.line_chart') as mock_chart:
                            yield {
                                'title': mock_title,
                                'sidebar': mock_sidebar,
                                'container': mock_container,
                                'metric': mock_metric,
                                'chart': mock_chart
                            }
    
    def test_dashboard_rendering(self, mock_streamlit):
        """Test dashboard rendering."""
        with patch('src.database.database_connectivity.DatabaseConnectivity') as mock_db:
            # Arrange
            mock_db_instance = Mock()
            mock_db_instance.execute_query.return_value = [
                {"symbol": "AAPL", "price": 150.25, "volume": 50000000}
            ]
            mock_db.return_value = mock_db_instance
            
            # Act
            main()
            
            # Assert
            mock_streamlit['title'].assert_called()
            mock_streamlit['metric'].assert_called()
    
    def test_dashboard_data_loading(self, mock_streamlit):
        """Test dashboard data loading."""
        with patch('src.database.database_connectivity.DatabaseConnectivity') as mock_db:
            # Arrange
            mock_db_instance = Mock()
            mock_db_instance.execute_query.return_value = [
                {"symbol": "AAPL", "price": 150.25},
                {"symbol": "GOOGL", "price": 2800.75}
            ]
            mock_db.return_value = mock_db_instance
            
            # Act
            main()
            
            # Assert
            mock_db_instance.execute_query.assert_called()
            assert mock_streamlit['metric'].call_count >= 2  # At least 2 metrics displayed
    
    def test_dashboard_error_handling(self, mock_streamlit):
        """Test dashboard error handling."""
        with patch('src.database.database_connectivity.DatabaseConnectivity') as mock_db:
            # Arrange
            mock_db_instance = Mock()
            mock_db_instance.execute_query.side_effect = Exception("Database error")
            mock_db.return_value = mock_db_instance
            
            with patch('streamlit.error') as mock_error:
                # Act
                main()
                
                # Assert
                mock_error.assert_called()
```

## Test Data Management

### Mock API Responses

```python
# test/fixtures/api_responses/yahoo_finance/aapl_data.json
{
  "chart": {
    "result": [{
      "meta": {
        "symbol": "AAPL",
        "regularMarketPrice": 150.25,
        "regularMarketVolume": 50000000,
        "regularMarketTime": 1642248000
      },
      "timestamp": [1642248000, 1642334400],
      "indicators": {
        "quote": [{
          "open": [150.0, 151.0],
          "high": [152.0, 153.0],
          "low": [149.0, 150.5],
          "close": [150.25, 151.75],
          "volume": [50000000, 45000000]
        }]
      }
    }],
    "error": null
  }
}
```

```python
# test/fixtures/api_responses/alpaca/aapl_bars.json
{
  "AAPL": [
    {
      "t": "2024-01-15T09:30:00Z",
      "o": 150.0,
      "h": 152.0,
      "l": 149.0,
      "c": 150.25,
      "v": 50000000,
      "n": 1000,
      "vw": 150.125
    }
  ]
}
```

### Test Database Setup

```python
# test/utils/test_db_setup.py
import pytest
import psycopg2
from pathlib import Path

@pytest.fixture(scope="session")
def test_database():
    """Create and manage test database."""
    # Create test database
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'test_trading_db',
        'user': 'test_user',
        'password': 'test_password'
    }
    
    # Create database if it doesn't exist
    conn = psycopg2.connect(
        host=db_config['host'],
        port=db_config['port'],
        database='postgres',
        user=db_config['user'],
        password=db_config['password']
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"CREATE DATABASE {db_config['database']}")
    except psycopg2.Error:
        pass  # Database already exists
    
    cursor.close()
    conn.close()
    
    # Run migrations
    migration_files = Path("src/database/migrations/001_initial_schema").glob("*.sql")
    for migration_file in sorted(migration_files):
        with open(migration_file) as f:
            migration_sql = f.read()
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(migration_sql)
        conn.commit()
        cursor.close()
        conn.close()
    
    yield db_config
    
    # Cleanup
    conn = psycopg2.connect(
        host=db_config['host'],
        port=db_config['port'],
        database='postgres',
        user=db_config['user'],
        password=db_config['password']
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {db_config['database']}")
    cursor.close()
    conn.close()
```

## Performance Testing Implementation

### Load Testing

```python
# test/performance/test_data_ingestion_performance.py
import pytest
import time
import asyncio
from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader

class TestDataIngestionPerformance:
    
    def test_large_dataset_processing(self):
        """Test processing of large datasets."""
        loader = YahooFinanceDataLoader()
        symbols = [f"STOCK{i}" for i in range(1000)]
        
        start_time = time.time()
        results = loader.batch_fetch_data(symbols)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Performance assertions
        assert execution_time < 60  # Should complete within 60 seconds
        assert len(results) == 1000
        assert execution_time / len(symbols) < 0.1  # Less than 0.1 seconds per symbol
    
    @pytest.mark.asyncio
    async def test_concurrent_api_calls(self):
        """Test handling of concurrent API calls."""
        loader = YahooFinanceDataLoader()
        symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        
        start_time = time.time()
        
        # Make concurrent API calls
        tasks = [loader.fetch_stock_data(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance assertions
        assert execution_time < 10  # Should complete within 10 seconds
        assert all(not isinstance(r, Exception) for r in results)
        assert len(results) == len(symbols)
    
    def test_memory_usage(self):
        """Test memory usage during data processing."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        loader = YahooFinanceDataLoader()
        symbols = [f"STOCK{i}" for i in range(100)]
        
        # Process data
        results = loader.batch_fetch_data(symbols)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory assertions (in MB)
        memory_increase_mb = memory_increase / 1024 / 1024
        assert memory_increase_mb < 100  # Should not increase by more than 100MB
```

### Stress Testing

```python
# test/performance/test_stress_conditions.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from src.data.sources.alpaca_daily_loader import AlpacaDailyLoader

class TestStressConditions:
    
    @pytest.mark.asyncio
    async def test_api_rate_limiting(self):
        """Test handling of API rate limiting."""
        loader = AlpacaDailyLoader()
        
        # Simulate rapid API calls
        tasks = []
        for i in range(50):  # Make 50 rapid calls
            tasks.append(loader.fetch_daily_data("AAPL"))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Should handle rate limiting gracefully
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        assert success_count > 0  # At least some calls should succeed
    
    def test_database_connection_pool_exhaustion(self):
        """Test database connection pool under stress."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        db = DatabaseConnectivity()
        
        # Simulate many concurrent database operations
        connections = []
        for i in range(20):
            conn = db.get_connection()
            connections.append(conn)
        
        # Should not raise connection pool exhaustion
        assert len(connections) == 20
        
        # Cleanup
        for conn in connections:
            conn.close()
    
    def test_memory_leak_detection(self):
        """Test for memory leaks during extended operation."""
        import gc
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Force garbage collection
        gc.collect()
        initial_memory = process.memory_info().rss
        
        # Simulate extended operation
        for i in range(100):
            # Create and destroy objects
            data = [{"symbol": f"STOCK{j}", "price": j * 10} for j in range(1000)]
            del data
        
        # Force garbage collection again
        gc.collect()
        final_memory = process.memory_info().rss
        
        # Memory should not increase significantly
        memory_increase = final_memory - initial_memory
        memory_increase_mb = memory_increase / 1024 / 1024
        assert memory_increase_mb < 50  # Should not increase by more than 50MB
```

## Test Execution Scripts

### Local Test Runner

```bash
#!/bin/bash
# scripts/run_tests.sh

echo "Running Prefect Trading System Tests"
echo "===================================="

# Set environment variables for testing
export TESTING=true
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=test_trading_db
export DB_USER=test_user
export DB_PASSWORD=test_password

# Run unit tests
echo "Running unit tests..."
pytest test/unit/ -v --cov=src --cov-report=term-missing

# Run integration tests
echo "Running integration tests..."
pytest test/integration/ -v --cov=src --cov-report=term-missing

# Run E2E tests
echo "Running E2E tests..."
pytest test/e2e/ -v --cov=src --cov-report=term-missing

# Generate coverage report
echo "Generating coverage report..."
pytest --cov=src --cov-report=html --cov-report=xml

echo "Tests completed!"
```

### CI/CD Test Script

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
          POSTGRES_USER: test_user
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
        pytest test/unit/ -v --cov=src --cov-report=xml --junitxml=unit-tests.xml
      env:
        TESTING: true
        DB_HOST: localhost
        DB_PORT: 5432
        DB_NAME: test_db
        DB_USER: test_user
        DB_PASSWORD: postgres
    
    - name: Run integration tests
      run: |
        pytest test/integration/ -v --cov=src --cov-report=xml --junitxml=integration-tests.xml
      env:
        TESTING: true
        DB_HOST: localhost
        DB_PORT: 5432
        DB_NAME: test_db
        DB_USER: test_user
        DB_PASSWORD: postgres
    
    - name: Run E2E tests
      run: |
        pytest test/e2e/ -v --cov=src --cov-report=xml --junitxml=e2e-tests.xml
      env:
        TESTING: true
        DB_HOST: localhost
        DB_PORT: 5432
        DB_NAME: test_db
        DB_USER: test_user
        DB_PASSWORD: postgres
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: |
          *.xml
          htmlcov/
```

This implementation guide provides comprehensive examples and practical approaches for testing each component of your Prefect trading system. The examples demonstrate proper mocking strategies, error handling, performance testing, and CI/CD integration. 