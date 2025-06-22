"""
Comprehensive test suite for the symbol_selector component.

Covers:
- Normal operation with symbols
- No active symbols
- Error handling (SymbolManager or Streamlit errors)
- UI integration with Streamlit mocks
"""

import pytest
from unittest.mock import patch, Mock

import src.ui.components.symbol_selector as symbol_selector

class TestSymbolSelectorComprehensive:
    @patch('src.ui.components.symbol_selector.st')
    @patch('src.ui.components.symbol_selector.SymbolManager')
    def test_display_symbol_selector_normal(self, mock_symbol_manager_class, mock_st):
        # Mock SymbolManager to return a list of symbols
        mock_manager = Mock()
        mock_manager.get_active_symbols.return_value = ['AAPL', 'GOOGL', 'MSFT']
        mock_symbol_manager_class.return_value = mock_manager
        # Mock selectbox to return the first symbol
        mock_st.selectbox.return_value = 'AAPL'
        result = symbol_selector.display_symbol_selector()
        mock_symbol_manager_class.assert_called_once()
        mock_manager.get_active_symbols.assert_called_once()
        mock_st.selectbox.assert_called_once_with(label='Select a Symbol', options=['AAPL', 'GOOGL', 'MSFT'], index=0)
        assert result == 'AAPL'

    @patch('src.ui.components.symbol_selector.st')
    @patch('src.ui.components.symbol_selector.SymbolManager')
    def test_display_symbol_selector_no_symbols(self, mock_symbol_manager_class, mock_st):
        # Mock SymbolManager to return an empty list
        mock_manager = Mock()
        mock_manager.get_active_symbols.return_value = []
        mock_symbol_manager_class.return_value = mock_manager
        result = symbol_selector.display_symbol_selector()
        mock_st.warning.assert_called_once_with('No active symbols found')
        assert result is None

    @patch('src.ui.components.symbol_selector.st')
    @patch('src.ui.components.symbol_selector.SymbolManager')
    def test_display_symbol_selector_symbol_manager_error(self, mock_symbol_manager_class, mock_st):
        # Mock SymbolManager to raise an exception
        mock_symbol_manager_class.side_effect = Exception('DB error')
        result = symbol_selector.display_symbol_selector()
        mock_st.error.assert_called_once_with('Error loading symbols. Please try again later.')
        assert result is None

    @patch('src.ui.components.symbol_selector.st')
    @patch('src.ui.components.symbol_selector.SymbolManager')
    def test_display_symbol_selector_get_active_symbols_error(self, mock_symbol_manager_class, mock_st):
        # Mock get_active_symbols to raise an exception
        mock_manager = Mock()
        mock_manager.get_active_symbols.side_effect = Exception('Query error')
        mock_symbol_manager_class.return_value = mock_manager
        result = symbol_selector.display_symbol_selector()
        mock_st.error.assert_called_once_with('Error loading symbols. Please try again later.')
        assert result is None

    @patch('src.ui.components.symbol_selector.st')
    @patch('src.ui.components.symbol_selector.SymbolManager')
    def test_display_symbol_selector_selectbox_error(self, mock_symbol_manager_class, mock_st):
        # Mock selectbox to raise an exception
        mock_manager = Mock()
        mock_manager.get_active_symbols.return_value = ['AAPL']
        mock_symbol_manager_class.return_value = mock_manager
        mock_st.selectbox.side_effect = Exception('UI error')
        result = symbol_selector.display_symbol_selector()
        mock_st.error.assert_called_once_with('Error loading symbols. Please try again later.')
        assert result is None

    def test_import_symbol_selector_module(self):
        try:
            import src.ui.components.symbol_selector as mod
            assert hasattr(mod, 'display_symbol_selector')
        except ImportError as e:
            pytest.fail(f"Failed to import symbol_selector: {e}") 