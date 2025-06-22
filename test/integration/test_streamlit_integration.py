"""
Integration tests for the Streamlit application.

Tests the complete Streamlit application flow and component interactions.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import streamlit as st

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.ui.streamlit_app import main
from src.ui.home import render_home


class TestStreamlitIntegration:
    """Integration tests for the complete Streamlit application."""

    @patch('streamlit.set_page_config')
    @patch('streamlit.sidebar')
    @patch('streamlit_autorefresh.st_autorefresh')
    @patch('builtins.open')
    @patch('streamlit_option_menu.option_menu')
    def test_complete_app_flow_home_page(self, mock_option_menu, mock_open, 
                                       mock_autorefresh, mock_sidebar, 
                                       mock_set_page_config):
        """Test the complete application flow for the home page."""
        # Mock CSS file reading
        mock_css_content = "body { background-color: #f0f2f6; }"
        mock_open.return_value.__enter__.return_value.read.return_value = mock_css_content
        
        # Mock option menu to return Home
        mock_option_menu.return_value = "Home"
        
        # Mock all the home page components
        with patch('src.ui.home.display_header') as mock_header, \
             patch('src.ui.home.display_portfolio_summary') as mock_portfolio, \
             patch('src.ui.home.display_market_overview') as mock_market, \
             patch('src.ui.home.display_recent_activity') as mock_activity, \
             patch('src.ui.home.display_quick_actions') as mock_actions, \
             patch('src.ui.home.display_market_news') as mock_news, \
             patch('src.ui.components.symbol_selector.display_symbol_selector') as mock_symbol:
            
            # Run the main application
            main()
            
            # Verify all components were called
            mock_header.assert_called_once_with("Trader")
            mock_portfolio.assert_called_once()
            mock_market.assert_called_once()
            mock_activity.assert_called_once()
            mock_actions.assert_called_once()
            mock_news.assert_called_once()
            mock_symbol.assert_called_once()

    @patch('streamlit.set_page_config')
    @patch('streamlit.sidebar')
    @patch('streamlit.title')
    @patch('streamlit.write')
    @patch('streamlit_autorefresh.st_autorefresh')
    @patch('builtins.open')
    @patch('streamlit_option_menu.option_menu')
    def test_complete_app_flow_analysis_page(self, mock_option_menu, mock_open, 
                                           mock_autorefresh, mock_write, mock_title, 
                                           mock_sidebar, mock_set_page_config):
        """Test the complete application flow for the analysis page."""
        # Mock CSS file reading
        mock_css_content = "body { background-color: #f0f2f6; }"
        mock_open.return_value.__enter__.return_value.read.return_value = mock_css_content
        
        # Mock option menu to return Analysis
        mock_option_menu.return_value = "Analysis"
        
        # Run the main application
        main()
        
        # Verify analysis page components were called
        mock_title.assert_called_with("📊 Analysis")
        mock_write.assert_called_with("Explore data analysis and trading signals.")

    @patch('streamlit.set_page_config')
    @patch('streamlit.sidebar')
    @patch('streamlit.title')
    @patch('streamlit.write')
    @patch('streamlit_autorefresh.st_autorefresh')
    @patch('builtins.open')
    @patch('streamlit_option_menu.option_menu')
    def test_complete_app_flow_settings_page(self, mock_option_menu, mock_open, 
                                           mock_autorefresh, mock_write, mock_title, 
                                           mock_sidebar, mock_set_page_config):
        """Test the complete application flow for the settings page."""
        # Mock CSS file reading
        mock_css_content = "body { background-color: #f0f2f6; }"
        mock_open.return_value.__enter__.return_value.read.return_value = mock_css_content
        
        # Mock option menu to return Settings
        mock_option_menu.return_value = "Settings"
        
        # Run the main application
        main()
        
        # Verify settings page components were called
        mock_title.assert_called_with("⚙️ Settings")
        mock_write.assert_called_with("Configure your system preferences.")

    @patch('streamlit.set_page_config')
    @patch('streamlit.sidebar')
    @patch('streamlit_autorefresh.st_autorefresh')
    @patch('builtins.open')
    @patch('streamlit_option_menu.option_menu')
    def test_app_with_database_connection(self, mock_option_menu, mock_open, 
                                        mock_autorefresh, mock_sidebar, 
                                        mock_set_page_config):
        """Test application with database connectivity."""
        # Mock CSS file reading
        mock_css_content = "body { background-color: #f0f2f6; }"
        mock_open.return_value.__enter__.return_value.read.return_value = mock_css_content
        
        # Mock option menu to return Home
        mock_option_menu.return_value = "Home"
        
        # Mock database connectivity
        with patch('src.database.database_connectivity.DatabaseConnectivity') as mock_db_class:
            mock_db_instance = Mock()
            mock_db_class.return_value = mock_db_instance
            
            # Mock all the home page components
            with patch('src.ui.home.display_header'), \
                 patch('src.ui.home.display_portfolio_summary'), \
                 patch('src.ui.home.display_market_overview'), \
                 patch('src.ui.home.display_recent_activity'), \
                 patch('src.ui.home.display_quick_actions'), \
                 patch('src.ui.home.display_market_news'), \
                 patch('src.ui.components.symbol_selector.display_symbol_selector'):
                
                # Run the main application
                main()
                
                # Verify database was initialized
                mock_db_class.assert_called_once()

    @patch('streamlit.set_page_config')
    @patch('streamlit.sidebar')
    @patch('streamlit_autorefresh.st_autorefresh')
    @patch('builtins.open')
    @patch('streamlit_option_menu.option_menu')
    def test_app_with_market_hours_integration(self, mock_option_menu, mock_open, 
                                             mock_autorefresh, mock_sidebar, 
                                             mock_set_page_config):
        """Test application with market hours integration."""
        # Mock CSS file reading
        mock_css_content = "body { background-color: #f0f2f6; }"
        mock_open.return_value.__enter__.return_value.read.return_value = mock_css_content
        
        # Mock option menu to return Home
        mock_option_menu.return_value = "Home"
        
        # Mock market hours
        with patch('src.utils.market_hours.is_market_open', return_value=True), \
             patch('src.utils.market_hours.get_market_hours') as mock_get_hours:
            
            mock_get_hours.return_value = {
                "open": "09:30",
                "close": "16:00",
                "timezone": "US/Eastern"
            }
            
            # Mock all the home page components
            with patch('src.ui.home.display_header'), \
                 patch('src.ui.home.display_portfolio_summary'), \
                 patch('src.ui.home.display_market_overview'), \
                 patch('src.ui.home.display_recent_activity'), \
                 patch('src.ui.home.display_quick_actions'), \
                 patch('src.ui.home.display_market_news'), \
                 patch('src.ui.components.symbol_selector.display_symbol_selector'):
                
                # Run the main application
                main()
                
                # Verify market hours were checked
                mock_get_hours.assert_called()

    @patch('streamlit.set_page_config')
    @patch('streamlit.sidebar')
    @patch('streamlit_autorefresh.st_autorefresh')
    @patch('builtins.open')
    @patch('streamlit_option_menu.option_menu')
    def test_app_error_handling(self, mock_option_menu, mock_open, 
                              mock_autorefresh, mock_sidebar, 
                              mock_set_page_config):
        """Test application error handling."""
        # Mock CSS file reading to raise an exception
        mock_open.side_effect = FileNotFoundError("CSS file not found")
        
        # Mock option menu to return Home
        mock_option_menu.return_value = "Home"
        
        # Mock all the home page components
        with patch('src.ui.home.display_header'), \
             patch('src.ui.home.display_portfolio_summary'), \
             patch('src.ui.home.display_market_overview'), \
             patch('src.ui.home.display_recent_activity'), \
             patch('src.ui.home.display_quick_actions'), \
             patch('src.ui.home.display_market_news'), \
             patch('src.ui.components.symbol_selector.display_symbol_selector'):
            
            # The application should handle the CSS file error gracefully
            # and continue to run
            main()
            
            # Verify the application still tried to run
            mock_set_page_config.assert_called_once()
            mock_autorefresh.assert_called_once_with(interval=10000)

    @patch('streamlit.set_page_config')
    @patch('streamlit.sidebar')
    @patch('streamlit_autorefresh.st_autorefresh')
    @patch('builtins.open')
    @patch('streamlit_option_menu.option_menu')
    def test_app_performance_with_multiple_navigations(self, mock_option_menu, 
                                                     mock_open, mock_autorefresh, 
                                                     mock_sidebar, mock_set_page_config):
        """Test application performance with multiple navigation calls."""
        # Mock CSS file reading
        mock_css_content = "body { background-color: #f0f2f6; }"
        mock_open.return_value.__enter__.return_value.read.return_value = mock_css_content
        
        # Test multiple navigation calls
        pages = ["Home", "Analysis", "Settings", "Home"]
        
        for page in pages:
            mock_option_menu.return_value = page
            
            # Mock all the home page components
            with patch('src.ui.home.display_header'), \
                 patch('src.ui.home.display_portfolio_summary'), \
                 patch('src.ui.home.display_market_overview'), \
                 patch('src.ui.home.display_recent_activity'), \
                 patch('src.ui.home.display_quick_actions'), \
                 patch('src.ui.home.display_market_news'), \
                 patch('src.ui.components.symbol_selector.display_symbol_selector'):
                
                # Run the main application
                main()
        
        # Verify the application handled multiple calls
        assert mock_set_page_config.call_count == len(pages)
        assert mock_autorefresh.call_count == len(pages) 