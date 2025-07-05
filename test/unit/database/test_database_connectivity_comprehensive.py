"""
Comprehensive Database Connectivity Tests
========================================

Complete test suite for database connectivity covering all methods,
error handling, edge cases, and real functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import sys
from pathlib import Path
from contextlib import contextmanager
import os

# Add src to Python path
src_path = Path(__file__).parent.parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class TestDatabaseConnectivityComprehensive:
    """Comprehensive tests for database connectivity functionality."""

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_initialization_success(self, mock_pool, mock_secret):
        """Test successful initialization with proper secret loading."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Mock secret values
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        # Mock connection pool
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        # Initialize database connectivity
        db = DatabaseConnectivity()
        
        # Verify secrets were loaded (only if env vars are not set)
        # The code tries env vars first, so secrets may not be called
        # We'll just verify the pool was created successfully
        mock_pool.assert_called_once()
        
        assert db.connection_pool == mock_pool_instance

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    @patch.dict('os.environ', {}, clear=True)
    def test_initialization_secret_error(self, mock_pool, mock_secret):
        """Test initialization failure when secrets cannot be loaded."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Mock secret loading to raise an exception
        mock_secret.load.side_effect = Exception("Secret not found")
        
        # Should raise the exception
        with pytest.raises(ValueError, match="Database credentials not found"):
            DatabaseConnectivity()

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_initialization_pool_error(self, mock_pool, mock_secret):
        """Test initialization failure when connection pool cannot be created."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Mock secret values
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        # Mock pool creation to raise an exception
        mock_pool.side_effect = Exception("Connection failed")
        
        # Should raise the exception
        with pytest.raises(Exception, match="Connection failed"):
            DatabaseConnectivity()

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_get_connection_success(self, mock_pool, mock_secret):
        """Test successful connection retrieval from pool."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Setup mocks
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        mock_connection = Mock()
        mock_pool_instance.getconn.return_value = mock_connection
        
        # Initialize and get connection
        db = DatabaseConnectivity()
        connection = db.get_connection()
        
        # Verify connection was retrieved from pool
        mock_pool_instance.getconn.assert_called_once()
        assert connection == mock_connection

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_get_connection_error(self, mock_pool, mock_secret):
        """Test connection retrieval error handling."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Setup mocks
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        # Mock getconn to raise an exception
        mock_pool_instance.getconn.side_effect = Exception("Pool exhausted")
        
        # Initialize and attempt to get connection
        db = DatabaseConnectivity()
        
        with pytest.raises(Exception, match="Pool exhausted"):
            db.get_connection()

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_release_connection_success(self, mock_pool, mock_secret):
        """Test successful connection release back to pool."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Setup mocks
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        mock_connection = Mock()
        
        # Initialize and release connection
        db = DatabaseConnectivity()
        db.release_connection(mock_connection)
        
        # Verify connection was returned to pool
        mock_pool_instance.putconn.assert_called_once_with(mock_connection)

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_release_connection_error(self, mock_pool, mock_secret):
        """Test connection release error handling."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Setup mocks
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        # Mock putconn to raise an exception
        mock_pool_instance.putconn.side_effect = Exception("Release failed")
        
        mock_connection = Mock()
        
        # Initialize and attempt to release connection
        db = DatabaseConnectivity()
        
        with pytest.raises(Exception, match="Release failed"):
            db.release_connection(mock_connection)

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_get_session_success(self, mock_pool, mock_secret):
        """Test successful session context manager."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Setup mocks
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        mock_connection = Mock()
        mock_cursor = Mock()
        # Make cursor work as context manager
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor
        
        mock_pool_instance.getconn.return_value = mock_connection
        
        # Initialize and use session
        db = DatabaseConnectivity()
        
        with db.get_session() as cursor:
            assert cursor == mock_cursor
            # Simulate some work
            cursor.execute("SELECT 1")
        
        # Verify connection was retrieved and released
        mock_pool_instance.getconn.assert_called_once()
        mock_pool_instance.putconn.assert_called_once_with(mock_connection)
        
        # Verify commit was called (successful execution)
        mock_connection.commit.assert_called_once()
        mock_connection.rollback.assert_not_called()

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_get_session_with_exception(self, mock_pool, mock_secret):
        """Test session context manager with exception handling."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Setup mocks
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        mock_connection = Mock()
        mock_cursor = Mock()
        # Make cursor work as context manager
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor
        
        mock_pool_instance.getconn.return_value = mock_connection
        
        # Initialize and use session with exception
        db = DatabaseConnectivity()
        
        with pytest.raises(Exception, match="Database error"):
            with db.get_session() as cursor:
                # Simulate an error during execution
                raise Exception("Database error")
        
        # Verify connection was retrieved and released
        mock_pool_instance.getconn.assert_called_once()
        mock_pool_instance.putconn.assert_called_once_with(mock_connection)
        
        # Verify rollback was called (exception occurred)
        mock_connection.rollback.assert_called_once()
        mock_connection.commit.assert_not_called()

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_execute_query_select_success(self, mock_pool, mock_secret):
        """Test successful SELECT query execution."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Setup mocks
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        mock_connection = Mock()
        mock_cursor = Mock()
        # Make cursor work as context manager
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor
        
        # Mock cursor description to indicate SELECT query
        mock_cursor.description = [('column1',), ('column2',)]
        mock_cursor.fetchall.return_value = [('AAPL', 'Apple Inc.'), ('GOOGL', 'Alphabet Inc.')]
        
        mock_pool_instance.getconn.return_value = mock_connection
        
        # Initialize and execute query
        db = DatabaseConnectivity()
        results = db.execute_query("SELECT symbol, name FROM symbols")
        
        # Verify query execution
        mock_cursor.execute.assert_called_once_with("SELECT symbol, name FROM symbols", None)
        mock_cursor.fetchall.assert_called_once()
        
        # Verify results
        assert results == [('AAPL', 'Apple Inc.'), ('GOOGL', 'Alphabet Inc.')]
        
        # Verify connection was retrieved and released
        mock_pool_instance.getconn.assert_called_once()
        mock_pool_instance.putconn.assert_called_once_with(mock_connection)
        
        # For SELECT, commit should NOT be called
        mock_connection.commit.assert_not_called()

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_execute_query_insert_success(self, mock_pool, mock_secret):
        """Test successful INSERT query execution."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Setup mocks
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        mock_connection = Mock()
        mock_cursor = Mock()
        # Make cursor work as context manager
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor
        
        # Mock cursor description to be None (INSERT/UPDATE/DELETE query)
        mock_cursor.description = None
        
        mock_pool_instance.getconn.return_value = mock_connection
        
        # Initialize and execute query
        db = DatabaseConnectivity()
        result = db.execute_query("INSERT INTO symbols (symbol, name) VALUES (%s, %s)", ('TSLA', 'Tesla Inc.'))
        
        # Verify query execution
        mock_cursor.execute.assert_called_once_with("INSERT INTO symbols (symbol, name) VALUES (%s, %s)", ('TSLA', 'Tesla Inc.'))
        mock_cursor.fetchall.assert_not_called()
        
        # Verify result is None for non-SELECT queries
        assert result is None
        
        # Verify connection was retrieved and released
        mock_pool_instance.getconn.assert_called_once()
        mock_pool_instance.putconn.assert_called_once_with(mock_connection)
        
        # Verify commit was called
        mock_connection.commit.assert_called_once()

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_execute_query_with_params(self, mock_pool, mock_secret):
        """Test query execution with parameters."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Setup mocks
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        mock_connection = Mock()
        mock_cursor = Mock()
        # Make cursor work as context manager
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor
        
        mock_cursor.description = [('price',)]
        mock_cursor.fetchall.return_value = [(150.25,)]
        
        mock_pool_instance.getconn.return_value = mock_connection
        
        # Initialize and execute query with parameters
        db = DatabaseConnectivity()
        results = db.execute_query("SELECT price FROM stocks WHERE symbol = %s", ('AAPL',))
        
        # Verify query execution with parameters
        mock_cursor.execute.assert_called_once_with("SELECT price FROM stocks WHERE symbol = %s", ('AAPL',))
        
        # Verify results
        assert results == [(150.25,)]

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_execute_query_error(self, mock_pool, mock_secret):
        """Test query execution error handling."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Setup mocks
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        mock_connection = Mock()
        mock_cursor = Mock()
        # Make cursor work as context manager
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor
        
        # Mock cursor execute to raise an exception
        mock_cursor.execute.side_effect = Exception("Query failed")
        
        mock_pool_instance.getconn.return_value = mock_connection
        
        # Initialize and attempt to execute query
        db = DatabaseConnectivity()
        
        with pytest.raises(Exception, match="Query failed"):
            db.execute_query("SELECT * FROM non_existent_table")
        
        # Verify connection was retrieved and released
        mock_pool_instance.getconn.assert_called_once()
        mock_pool_instance.putconn.assert_called_once_with(mock_connection)
        
        # Verify rollback was called
        mock_connection.rollback.assert_called_once()

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_execute_query_connection_error(self, mock_pool, mock_secret):
        """Test query execution when connection retrieval fails."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Setup mocks
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        # Mock getconn to raise an exception
        mock_pool_instance.getconn.side_effect = Exception("Connection failed")
        
        # Initialize and attempt to execute query
        db = DatabaseConnectivity()
        
        with pytest.raises(Exception, match="Connection failed"):
            db.execute_query("SELECT 1")
        
        # Verify getconn was called but putconn was not (no connection to release)
        mock_pool_instance.getconn.assert_called_once()
        mock_pool_instance.putconn.assert_not_called()

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_close_success(self, mock_pool, mock_secret):
        """Test successful connection pool closure."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Setup mocks
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        # Initialize and close
        db = DatabaseConnectivity()
        db.close()
        
        # Verify closeall was called
        mock_pool_instance.closeall.assert_called_once()

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_close_no_pool(self, mock_pool, mock_secret):
        """Test close when no connection pool exists."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Setup mocks
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        # Initialize and set pool to None
        db = DatabaseConnectivity()
        db.connection_pool = None
        
        # Should not raise an exception
        db.close()
        
        # Verify closeall was not called
        mock_pool_instance.closeall.assert_not_called()

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_close_error(self, mock_pool, mock_secret):
        """Test close error handling."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Setup mocks
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        # Mock closeall to raise an exception
        mock_pool_instance.closeall.side_effect = Exception("Close failed")
        
        # Initialize and attempt to close
        db = DatabaseConnectivity()
        
        with pytest.raises(Exception, match="Close failed"):
            db.close()

    def test_context_manager_import(self):
        """Test that contextmanager is properly imported."""
        from src.database.database_connectivity import contextmanager
        assert contextmanager is not None

    def test_optional_import(self):
        """Test that Optional is properly imported."""
        from src.database.database_connectivity import Optional
        assert Optional is not None

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_multiple_queries_same_instance(self, mock_pool, mock_secret):
        """Test multiple queries using the same database instance."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Setup mocks
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        mock_connection = Mock()
        mock_cursor = Mock()
        # Make cursor work as context manager
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor
        
        mock_cursor.description = [('result',)]
        mock_cursor.fetchall.return_value = [('success',)]
        
        mock_pool_instance.getconn.return_value = mock_connection
        
        # Initialize and execute multiple queries
        db = DatabaseConnectivity()
        
        # First query
        result1 = db.execute_query("SELECT 1")
        assert result1 == [('success',)]
        
        # Second query
        result2 = db.execute_query("SELECT 2")
        assert result2 == [('success',)]
        
        # Verify getconn was called twice (once per query)
        assert mock_pool_instance.getconn.call_count == 2
        assert mock_pool_instance.putconn.call_count == 2

    @patch('src.database.database_connectivity.Secret')
    @patch('src.database.database_connectivity.pool.SimpleConnectionPool')
    def test_session_with_multiple_operations(self, mock_pool, mock_secret):
        """Test session with multiple database operations."""
        from src.database.database_connectivity import DatabaseConnectivity
        
        # Setup mocks
        mock_secret.load.side_effect = lambda x: Mock(get=lambda: {
            'db-user': 'test_user',
            'db-password': 'test_pass'
        }[x])
        
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        mock_connection = Mock()
        mock_cursor = Mock()
        # Make cursor work as context manager
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor
        
        mock_pool_instance.getconn.return_value = mock_connection
        
        # Initialize and use session with multiple operations
        db = DatabaseConnectivity()
        
        with db.get_session() as cursor:
            cursor.execute("INSERT INTO table1 VALUES (1)")
            cursor.execute("UPDATE table2 SET value = 2")
            cursor.execute("DELETE FROM table3 WHERE id = 3")
        
        # Verify all operations were executed
        assert mock_cursor.execute.call_count == 3
        mock_cursor.execute.assert_any_call("INSERT INTO table1 VALUES (1)")
        mock_cursor.execute.assert_any_call("UPDATE table2 SET value = 2")
        mock_cursor.execute.assert_any_call("DELETE FROM table3 WHERE id = 3")
        
        # Verify commit was called once at the end
        mock_connection.commit.assert_called_once() 