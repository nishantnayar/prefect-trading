"""
Comprehensive test suite for SymbolManager module.

This test suite covers all functionality of the SymbolManager class including:
- Symbol addition with various scenarios
- Symbol deactivation
- Active symbol retrieval
- Symbol information retrieval
- Symbol name updates
- Error handling and edge cases
- Database interaction patterns
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.data.sources.symbol_manager import SymbolManager


class TestSymbolManagerComprehensive:
    """Comprehensive tests for SymbolManager class."""

    def test_initialization(self):
        """Test SymbolManager initialization."""
        symbol_manager = SymbolManager()
        assert symbol_manager is not None
        assert hasattr(symbol_manager, 'db')
        assert symbol_manager.db is not None

    @patch('src.data.sources.symbol_manager.DatabaseConnectivity')
    def test_initialization_with_mock_db(self, mock_db_class):
        """Test SymbolManager initialization with mocked database."""
        mock_db_instance = Mock()
        mock_db_class.return_value = mock_db_instance
        
        symbol_manager = SymbolManager()
        
        mock_db_class.assert_called_once()
        assert symbol_manager.db == mock_db_instance

    def test_add_symbol_success(self):
        """Test successful symbol addition."""
        symbol_manager = SymbolManager()
        
        # Mock the database session and cursor
        mock_cursor = Mock()
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_cursor)
        mock_session.__exit__ = Mock(return_value=None)
        
        symbol_manager.db.get_session = Mock(return_value=mock_session)
        
        # Test adding a symbol
        symbol_manager.add_symbol("AAPL", "Apple Inc.", True)
        
        # Verify the database was called correctly
        symbol_manager.db.get_session.assert_called_once()
        mock_cursor.execute.assert_called_once()
        
        # Check the SQL query and parameters
        call_args = mock_cursor.execute.call_args
        assert "INSERT INTO symbols" in call_args[0][0]
        assert call_args[0][1] == ("AAPL", "Apple Inc.", True)

    def test_add_symbol_without_name(self):
        """Test symbol addition without providing a name."""
        symbol_manager = SymbolManager()
        
        mock_cursor = Mock()
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_cursor)
        mock_session.__exit__ = Mock(return_value=None)
        
        symbol_manager.db.get_session = Mock(return_value=mock_session)
        
        # Test adding a symbol without name
        symbol_manager.add_symbol("TSLA", is_active=True)
        
        call_args = mock_cursor.execute.call_args
        assert call_args[0][1] == ("TSLA", None, True)

    def test_add_symbol_inactive(self):
        """Test adding an inactive symbol."""
        symbol_manager = SymbolManager()
        
        mock_cursor = Mock()
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_cursor)
        mock_session.__exit__ = Mock(return_value=None)
        
        symbol_manager.db.get_session = Mock(return_value=mock_session)
        
        # Test adding an inactive symbol
        symbol_manager.add_symbol("DELISTED", "Delisted Company", False)
        
        call_args = mock_cursor.execute.call_args
        assert call_args[0][1] == ("DELISTED", "Delisted Company", False)

    def test_add_symbol_database_error(self):
        """Test symbol addition with database error."""
        symbol_manager = SymbolManager()
        
        # Mock database to raise an exception
        symbol_manager.db.get_session = Mock(side_effect=Exception("Database error"))
        
        # Test that the exception is re-raised
        with pytest.raises(Exception, match="Database error"):
            symbol_manager.add_symbol("AAPL", "Apple Inc.")

    def test_deactivate_symbol_success(self):
        """Test successful symbol deactivation."""
        symbol_manager = SymbolManager()
        
        mock_cursor = Mock()
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_cursor)
        mock_session.__exit__ = Mock(return_value=None)
        
        symbol_manager.db.get_session = Mock(return_value=mock_session)
        
        # Test deactivating a symbol
        symbol_manager.deactivate_symbol("AAPL")
        
        # Verify the database was called correctly
        symbol_manager.db.get_session.assert_called_once()
        mock_cursor.execute.assert_called_once()
        
        # Check the SQL query and parameters
        call_args = mock_cursor.execute.call_args
        assert "UPDATE symbols" in call_args[0][0]
        assert "is_active = false" in call_args[0][0]
        assert "end_date = CURRENT_TIMESTAMP" in call_args[0][0]
        assert call_args[0][1] == ("AAPL",)

    def test_deactivate_symbol_database_error(self):
        """Test symbol deactivation with database error."""
        symbol_manager = SymbolManager()
        
        # Mock database to raise an exception
        symbol_manager.db.get_session = Mock(side_effect=Exception("Database error"))
        
        # Test that the exception is re-raised
        with pytest.raises(Exception, match="Database error"):
            symbol_manager.deactivate_symbol("AAPL")

    def test_get_active_symbols_success(self):
        """Test successful retrieval of active symbols."""
        symbol_manager = SymbolManager()
        
        mock_cursor = Mock()
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_cursor)
        mock_session.__exit__ = Mock(return_value=None)
        
        symbol_manager.db.get_session = Mock(return_value=mock_session)
        
        # Mock the fetchall result
        mock_cursor.fetchall.return_value = [
            ("AAPL",),
            ("GOOGL",),
            ("MSFT",),
            ("TSLA",)
        ]
        
        # Test getting active symbols
        symbols = symbol_manager.get_active_symbols()
        
        # Verify the database was called correctly
        symbol_manager.db.get_session.assert_called_once()
        mock_cursor.execute.assert_called_once()
        
        # Check the SQL query - updated to match current implementation with JOIN
        call_args = mock_cursor.execute.call_args
        assert "SELECT DISTINCT s.symbol" in call_args[0][0]
        assert "FROM symbols s" in call_args[0][0]
        assert "JOIN yahoo_company_info y ON s.symbol = y.symbol" in call_args[0][0]
        assert "WHERE s.is_active = true" in call_args[0][0]
        assert "ORDER BY s.symbol" in call_args[0][0]
        
        # Check the result
        assert symbols == ["AAPL", "GOOGL", "MSFT", "TSLA"]
        assert len(symbols) == 4

    def test_get_active_symbols_empty_result(self):
        """Test retrieval of active symbols when none exist."""
        symbol_manager = SymbolManager()
        
        mock_cursor = Mock()
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_cursor)
        mock_session.__exit__ = Mock(return_value=None)
        
        symbol_manager.db.get_session = Mock(return_value=mock_session)
        
        # Mock empty result
        mock_cursor.fetchall.return_value = []
        
        # Test getting active symbols
        symbols = symbol_manager.get_active_symbols()
        
        # Check the result
        assert symbols == []
        assert len(symbols) == 0

    def test_get_active_symbols_database_error(self):
        """Test retrieval of active symbols with database error."""
        symbol_manager = SymbolManager()
        
        # Mock database to raise an exception
        symbol_manager.db.get_session = Mock(side_effect=Exception("Database error"))
        
        # Test that empty list is returned on error
        symbols = symbol_manager.get_active_symbols()
        
        assert symbols == []

    def test_get_symbol_info_success(self):
        """Test successful retrieval of symbol information."""
        symbol_manager = SymbolManager()
        
        mock_cursor = Mock()
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_cursor)
        mock_session.__exit__ = Mock(return_value=None)
        
        symbol_manager.db.get_session = Mock(return_value=mock_session)
        
        # Mock the cursor description and fetchone result
        mock_cursor.description = [
            ('symbol',),
            ('name',),
            ('is_active',),
            ('start_date',),
            ('end_date',),
            ('created_at',),
            ('updated_at',)
        ]
        mock_cursor.fetchone.return_value = (
            "AAPL",
            "Apple Inc.",
            True,
            datetime(2020, 1, 1),
            None,
            datetime(2020, 1, 1),
            datetime(2023, 1, 1)
        )
        
        # Test getting symbol info
        symbol_info = symbol_manager.get_symbol_info("AAPL")
        
        # Verify the database was called correctly
        symbol_manager.db.get_session.assert_called_once()
        mock_cursor.execute.assert_called_once()
        
        # Check the SQL query and parameters
        call_args = mock_cursor.execute.call_args
        assert "SELECT symbol, name, is_active" in call_args[0][0]
        assert call_args[0][1] == ("AAPL",)
        
        # Check the result
        assert symbol_info is not None
        assert symbol_info['symbol'] == "AAPL"
        assert symbol_info['name'] == "Apple Inc."
        assert symbol_info['is_active'] is True
        assert symbol_info['start_date'] == datetime(2020, 1, 1)
        assert symbol_info['end_date'] is None
        assert symbol_info['created_at'] == datetime(2020, 1, 1)
        assert symbol_info['updated_at'] == datetime(2023, 1, 1)

    def test_get_symbol_info_not_found(self):
        """Test retrieval of symbol information when symbol doesn't exist."""
        symbol_manager = SymbolManager()
        
        mock_cursor = Mock()
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_cursor)
        mock_session.__exit__ = Mock(return_value=None)
        
        symbol_manager.db.get_session = Mock(return_value=mock_session)
        
        # Mock no result found
        mock_cursor.fetchone.return_value = None
        
        # Test getting symbol info for non-existent symbol
        symbol_info = symbol_manager.get_symbol_info("NONEXISTENT")
        
        # Check the result
        assert symbol_info is None

    def test_get_symbol_info_database_error(self):
        """Test retrieval of symbol information with database error."""
        symbol_manager = SymbolManager()
        
        # Mock database to raise an exception
        symbol_manager.db.get_session = Mock(side_effect=Exception("Database error"))
        
        # Test that None is returned on error
        symbol_info = symbol_manager.get_symbol_info("AAPL")
        
        assert symbol_info is None

    def test_update_symbol_name_success(self):
        """Test successful symbol name update."""
        symbol_manager = SymbolManager()
        
        mock_cursor = Mock()
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_cursor)
        mock_session.__exit__ = Mock(return_value=None)
        
        symbol_manager.db.get_session = Mock(return_value=mock_session)
        
        # Mock that a row was affected
        mock_cursor.rowcount = 1
        
        # Test updating symbol name
        result = symbol_manager.update_symbol_name("AAPL", "Apple Inc. Updated")
        
        # Verify the database was called correctly
        symbol_manager.db.get_session.assert_called_once()
        mock_cursor.execute.assert_called_once()
        
        # Check the SQL query and parameters
        call_args = mock_cursor.execute.call_args
        assert "UPDATE symbols" in call_args[0][0]
        assert "SET name = %s" in call_args[0][0]
        assert call_args[0][1] == ("Apple Inc. Updated", "AAPL")
        
        # Check the result
        assert result is True

    def test_update_symbol_name_not_found(self):
        """Test symbol name update when symbol doesn't exist."""
        symbol_manager = SymbolManager()
        
        mock_cursor = Mock()
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_cursor)
        mock_session.__exit__ = Mock(return_value=None)
        
        symbol_manager.db.get_session = Mock(return_value=mock_session)
        
        # Mock that no row was affected
        mock_cursor.rowcount = 0
        
        # Test updating non-existent symbol name
        result = symbol_manager.update_symbol_name("NONEXISTENT", "New Name")
        
        # Check the result
        assert result is False

    def test_update_symbol_name_database_error(self):
        """Test symbol name update with database error."""
        symbol_manager = SymbolManager()
        
        # Mock database to raise an exception
        symbol_manager.db.get_session = Mock(side_effect=Exception("Database error"))
        
        # Test that False is returned on error
        result = symbol_manager.update_symbol_name("AAPL", "New Name")
        
        assert result is False

    def test_integration_scenarios(self):
        """Test integration scenarios with multiple operations."""
        symbol_manager = SymbolManager()
        
        mock_cursor = Mock()
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_cursor)
        mock_session.__exit__ = Mock(return_value=None)
        
        symbol_manager.db.get_session = Mock(return_value=mock_session)
        
        # Mock different results for different operations
        mock_cursor.fetchall.return_value = [("AAPL",), ("GOOGL",)]
        mock_cursor.fetchone.return_value = ("AAPL", "Apple Inc.", True, None, None, None, None)
        mock_cursor.rowcount = 1
        # Set description for get_symbol_info
        mock_cursor.description = [
            ('symbol',), ('name',), ('is_active',), ('start_date',), ('end_date',), ('created_at',), ('updated_at',)
        ]
        
        # Test full workflow: add, get active, get info, update, deactivate
        symbol_manager.add_symbol("AAPL", "Apple Inc.")
        active_symbols = symbol_manager.get_active_symbols()
        symbol_info = symbol_manager.get_symbol_info("AAPL")
        update_result = symbol_manager.update_symbol_name("AAPL", "Apple Inc. Updated")
        symbol_manager.deactivate_symbol("AAPL")
        
        # Verify all operations were called
        assert len(symbol_manager.db.get_session.call_args_list) == 5
        assert len(mock_cursor.execute.call_args_list) == 5
        assert active_symbols == ["AAPL", "GOOGL"]
        assert symbol_info is not None
        assert update_result is True

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        symbol_manager = SymbolManager()
        
        mock_cursor = Mock()
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_cursor)
        mock_session.__exit__ = Mock(return_value=None)
        
        symbol_manager.db.get_session = Mock(return_value=mock_session)
        
        # Test with empty string symbol
        symbol_manager.add_symbol("", "Empty Symbol")
        call_args = mock_cursor.execute.call_args
        assert call_args[0][1] == ("", "Empty Symbol", True)
        
        # Test with very long symbol name
        long_name = "A" * 1000
        symbol_manager.update_symbol_name("AAPL", long_name)
        call_args = mock_cursor.execute.call_args
        assert call_args[0][1] == (long_name, "AAPL")

    def test_error_handling_patterns(self):
        """Test various error handling patterns."""
        symbol_manager = SymbolManager()
        
        # Test with different types of exceptions
        exceptions_to_test = [
            Exception("Generic error"),
            ValueError("Value error"),
            RuntimeError("Runtime error")
        ]
        
        for exception in exceptions_to_test:
            symbol_manager.db.get_session = Mock(side_effect=exception)
            
            # Test that exceptions are properly handled
            with pytest.raises(type(exception)):
                symbol_manager.add_symbol("AAPL")
            
            with pytest.raises(type(exception)):
                symbol_manager.deactivate_symbol("AAPL")
            
            # Test that these methods return safe defaults
            assert symbol_manager.get_active_symbols() == []
            assert symbol_manager.get_symbol_info("AAPL") is None
            assert symbol_manager.update_symbol_name("AAPL", "New Name") is False

    def test_import_symbol_manager_module(self):
        """Test that the SymbolManager module can be imported correctly."""
        try:
            from src.data.sources.symbol_manager import SymbolManager
            assert SymbolManager is not None
        except ImportError as e:
            pytest.fail(f"Failed to import SymbolManager: {e}")

    def test_symbol_manager_class_structure(self):
        """Test that SymbolManager class has expected structure."""
        symbol_manager = SymbolManager()
        
        # Check that all expected methods exist
        assert hasattr(symbol_manager, 'add_symbol')
        assert hasattr(symbol_manager, 'deactivate_symbol')
        assert hasattr(symbol_manager, 'get_active_symbols')
        assert hasattr(symbol_manager, 'get_symbol_info')
        assert hasattr(symbol_manager, 'update_symbol_name')
        
        # Check that methods are callable
        assert callable(symbol_manager.add_symbol)
        assert callable(symbol_manager.deactivate_symbol)
        assert callable(symbol_manager.get_active_symbols)
        assert callable(symbol_manager.get_symbol_info)
        assert callable(symbol_manager.update_symbol_name) 