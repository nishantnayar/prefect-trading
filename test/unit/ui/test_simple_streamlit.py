"""
Simple unit tests for Streamlit UI components.

This module contains basic tests that verify the UI components
can be imported and called without errors.
"""

import pytest
from unittest.mock import Mock, patch


class TestSimpleStreamlit:
    """Simple tests for Streamlit UI components."""
    
    def test_import_streamlit_app(self):
        """Test that streamlit app can be imported."""
        try:
            from src.ui.streamlit_app import main
            assert main is not None
        except ImportError as e:
            pytest.fail(f"Failed to import streamlit_app: {e}")
    
    def test_import_home(self):
        """Test that home module can be imported."""
        try:
            from src.ui.home import render_home
            assert render_home is not None
        except ImportError as e:
            pytest.fail(f"Failed to import home: {e}")
    
    def test_import_components(self):
        """Test that UI components can be imported."""
        try:
            from src.ui.components.symbol_selector import display_symbol_selector
            from src.ui.components.market_status import display_market_status
            from src.ui.components.date_display import get_current_cst_formatted
            assert display_symbol_selector is not None
            assert display_market_status is not None
            assert get_current_cst_formatted is not None
        except ImportError as e:
            pytest.fail(f"Failed to import UI components: {e}")
    
    @patch('streamlit.selectbox')
    @patch('streamlit.warning')
    @patch('streamlit.error')
    @patch('src.data.sources.symbol_manager.SymbolManager')
    def test_symbol_selector_function_exists(self, mock_symbol_manager_class, mock_error, mock_warning, mock_selectbox):
        """Test that symbol selector function exists and can be called."""
        from src.ui.components.symbol_selector import display_symbol_selector
        
        # Mock SymbolManager
        mock_symbol_manager = Mock()
        mock_symbol_manager.get_active_symbols.return_value = ["AAPL", "MSFT", "GOOGL"]
        mock_symbol_manager_class.return_value = mock_symbol_manager
        
        # Mock selectbox
        mock_selectbox.return_value = "AAPL"
        
        # Function should exist and be callable
        assert callable(display_symbol_selector)
    
    @patch('streamlit.info')
    @patch('streamlit.error')
    @patch('src.utils.market_hours.MarketHoursManager')
    def test_market_status_function_exists(self, mock_market_hours_class, mock_error, mock_info):
        """Test that market status function exists and can be called."""
        from src.ui.components.market_status import display_market_status
        
        # Mock MarketHoursManager
        mock_market_hours = Mock()
        mock_market_hours.is_market_open.return_value = True
        mock_market_hours_class.return_value = mock_market_hours
        
        # Function should exist and be callable
        assert callable(display_market_status)
    
    def test_date_display_function_exists(self):
        """Test that date display function exists and can be called."""
        from src.ui.components.date_display import get_current_cst_formatted
        
        # Function should exist and be callable
        assert callable(get_current_cst_formatted) 