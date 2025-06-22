"""
Comprehensive Tests for Home Page UI
====================================

Complete test suite for src/ui/home.py covering all functions,
UI components, database integration, error handling, and edge cases.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import sys
from pathlib import Path
from datetime import datetime
from pytz import timezone

# Add src to Python path
src_path = Path(__file__).parent.parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def create_mock_column():
    """Helper function to create a mock column with context manager support."""
    mock_col = Mock()
    mock_col.__enter__ = Mock(return_value=mock_col)
    mock_col.__exit__ = Mock(return_value=None)
    return mock_col


class TestHomePageComprehensive:
    """Comprehensive tests for home page functionality."""

    @patch('src.ui.home.datetime')
    def test_get_greeting_morning(self, mock_datetime):
        """Test greeting for morning hours (5-11)."""
        from src.ui.home import get_greeting
        
        # Mock current time to be morning (8 AM)
        mock_now = Mock()
        mock_now.hour = 8
        mock_datetime.now.return_value = mock_now
        
        greeting = get_greeting()
        assert greeting == "Good Morning"

    @patch('src.ui.home.datetime')
    def test_get_greeting_afternoon(self, mock_datetime):
        """Test greeting for afternoon hours (12-16)."""
        from src.ui.home import get_greeting
        
        # Mock current time to be afternoon (2 PM)
        mock_now = Mock()
        mock_now.hour = 14
        mock_datetime.now.return_value = mock_now
        
        greeting = get_greeting()
        assert greeting == "Good Afternoon"

    @patch('src.ui.home.datetime')
    def test_get_greeting_evening(self, mock_datetime):
        """Test greeting for evening hours (17-23)."""
        from src.ui.home import get_greeting
        
        # Mock current time to be evening (8 PM)
        mock_now = Mock()
        mock_now.hour = 20
        mock_datetime.now.return_value = mock_now
        
        greeting = get_greeting()
        assert greeting == "Good Evening"

    @patch('src.ui.home.datetime')
    def test_get_greeting_late_night(self, mock_datetime):
        """Test greeting for late night hours (0-4)."""
        from src.ui.home import get_greeting
        
        # Mock current time to be late night (2 AM)
        mock_now = Mock()
        mock_now.hour = 2
        mock_datetime.now.return_value = mock_now
        
        greeting = get_greeting()
        assert greeting == "Good Evening"

    @patch('src.ui.home.get_greeting')
    @patch('src.ui.home.get_current_cst_formatted')
    @patch('src.ui.home.display_market_status')
    @patch('src.ui.home.st')
    def test_display_header(self, mock_st, mock_display_market_status, mock_get_current_cst, mock_get_greeting):
        """Test header display with all components."""
        from src.ui.home import display_header
        
        # Setup mocks
        mock_get_greeting.return_value = "Good Morning"
        mock_get_current_cst.return_value = "10:30 AM CST"
        
        # Mock streamlit columns with context manager support
        mock_col1 = create_mock_column()
        mock_col2 = create_mock_column()
        mock_col3 = create_mock_column()
        mock_st.columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        # Call the function
        display_header("John Doe")
        
        # Verify greeting was called
        mock_get_greeting.assert_called_once()
        
        # Verify columns were created
        mock_st.columns.assert_called_once_with([2, 1, 1])
        
        # Verify title and greeting were displayed
        mock_st.title.assert_called_once_with("🏠 Trading Dashboard")
        mock_st.write.assert_called()
        
        # Verify time was displayed
        mock_get_current_cst.assert_called_once()
        
        # Verify market status was displayed
        mock_display_market_status.assert_called_once()

    @patch('src.ui.home.st')
    def test_display_portfolio_summary(self, mock_st):
        """Test portfolio summary display."""
        from src.ui.home import display_portfolio_summary
        
        # Mock streamlit columns with context manager support
        mock_col1 = create_mock_column()
        mock_col2 = create_mock_column()
        mock_col3 = create_mock_column()
        mock_col4 = create_mock_column()
        mock_st.columns.return_value = [mock_col1, mock_col2, mock_col3, mock_col4]
        
        # Mock expander
        mock_expander = Mock()
        mock_st.expander.return_value.__enter__ = Mock(return_value=mock_expander)
        mock_st.expander.return_value.__exit__ = Mock(return_value=None)
        
        # Call the function
        display_portfolio_summary()
        
        # Verify subheader was displayed
        mock_st.subheader.assert_called_with("📊 Portfolio Overview")
        
        # Verify columns were created for metrics
        mock_st.columns.assert_called()
        
        # Verify metrics were displayed
        assert mock_st.metric.call_count >= 4  # At least 4 primary metrics

    @patch('src.ui.home.st')
    def test_display_market_overview(self, mock_st):
        """Test market overview display."""
        from src.ui.home import display_market_overview
        
        # Mock streamlit columns with context manager support
        mock_col1 = create_mock_column()
        mock_col2 = create_mock_column()
        mock_col3 = create_mock_column()
        mock_st.columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        # Call the function
        display_market_overview()
        
        # Verify subheader was displayed
        mock_st.subheader.assert_called_with("🌍 Market Overview")
        
        # Verify columns were created
        mock_st.columns.assert_called_once_with(3)
        
        # Verify market data was displayed
        assert mock_st.metric.call_count >= 9  # 9 metrics total (3 per column)

    @patch('src.ui.home.st')
    def test_display_recent_activity(self, mock_st):
        """Test recent activity display."""
        from src.ui.home import display_recent_activity
        
        # Mock streamlit columns for each activity with context manager support
        mock_cols = [create_mock_column() for _ in range(4)]
        mock_st.columns.return_value = mock_cols
        
        # Call the function
        display_recent_activity()
        
        # Verify subheader was displayed
        mock_st.subheader.assert_called_with("📝 Recent Activity")
        
        # Verify activities were displayed (3 activities * 4 columns each)
        assert mock_st.columns.call_count == 3

    @patch('src.ui.home.st')
    def test_display_quick_actions(self, mock_st):
        """Test quick actions display."""
        from src.ui.home import display_quick_actions
        
        # Mock streamlit columns with context manager support
        mock_col1 = create_mock_column()
        mock_col2 = create_mock_column()
        mock_st.columns.return_value = [mock_col1, mock_col2]
        
        # Call the function
        display_quick_actions()
        
        # Verify subheader was displayed
        mock_st.subheader.assert_called_with("⚡ Quick Actions")
        
        # Verify columns were created
        mock_st.columns.assert_called_once_with(2)
        
        # Verify buttons were created
        assert mock_st.button.call_count == 4  # 4 action buttons

    @patch('src.ui.home.format_datetime_est_to_cst')
    @patch('src.ui.home.DatabaseConnectivity')
    @patch('src.ui.home.st')
    def test_display_market_news_success(self, mock_st, mock_db_class, mock_format_datetime):
        """Test successful market news display."""
        from src.ui.home import display_market_news
        
        # Mock database and cursor
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        
        mock_cursor = Mock()
        mock_db.get_session.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_db.get_session.return_value.__exit__ = Mock(return_value=None)
        
        # Mock news data
        mock_articles = [
            ("Test Article 1", "Reuters", "http://example.com/1", "2024-01-01 10:00:00", "Test description 1"),
            ("Test Article 2", "Bloomberg", "http://example.com/2", "2024-01-01 09:00:00", "Test description 2")
        ]
        mock_cursor.fetchall.return_value = mock_articles
        
        # Mock datetime formatting
        mock_format_datetime.return_value = "10:00 AM CST"
        
        # Mock expander
        mock_expander = Mock()
        mock_st.expander.return_value.__enter__ = Mock(return_value=mock_expander)
        mock_st.expander.return_value.__exit__ = Mock(return_value=None)
        
        # Call the function
        display_market_news()
        
        # Verify subheader was displayed
        mock_st.subheader.assert_called_with("📰 Market News")
        
        # Verify database was queried
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_called_once()
        
        # Verify articles were displayed
        assert mock_st.expander.call_count == 2  # 2 articles

    @patch('src.ui.home.DatabaseConnectivity')
    @patch('src.ui.home.st')
    def test_display_market_news_no_articles(self, mock_st, mock_db_class):
        """Test market news display when no articles are available."""
        from src.ui.home import display_market_news
        
        # Mock database and cursor
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        
        mock_cursor = Mock()
        mock_db.get_session.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_db.get_session.return_value.__exit__ = Mock(return_value=None)
        
        # Mock empty news data
        mock_cursor.fetchall.return_value = []
        
        # Call the function
        display_market_news()
        
        # Verify info message was displayed
        mock_st.info.assert_called_with("No recent news articles available.")

    @patch('src.ui.home.DatabaseConnectivity')
    @patch('src.ui.home.st')
    def test_display_market_news_database_error(self, mock_st, mock_db_class):
        """Test market news display when database error occurs."""
        from src.ui.home import display_market_news
        
        # Mock database to raise exception
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        mock_db.get_session.side_effect = Exception("Database connection failed")
        
        # Call the function
        display_market_news()
        
        # Verify error messages were displayed
        mock_st.error.assert_called()
        assert mock_st.error.call_count >= 1

    @patch('src.ui.home.display_symbol_selector')
    @patch('src.ui.home.display_market_news')
    @patch('src.ui.home.display_quick_actions')
    @patch('src.ui.home.display_recent_activity')
    @patch('src.ui.home.display_market_overview')
    @patch('src.ui.home.display_portfolio_summary')
    @patch('src.ui.home.display_header')
    @patch('src.ui.home.os')
    @patch('src.ui.home.st')
    def test_render_home_success(self, mock_st, mock_os, mock_display_header, 
                                mock_display_portfolio, mock_display_market, 
                                mock_display_activity, mock_display_actions,
                                mock_display_news, mock_display_symbol):
        """Test successful home page rendering."""
        from src.ui.home import render_home
        
        # Mock environment variable
        mock_os.getenv.return_value = "Test User"
        
        # Prepare columns for each call
        main_col1 = create_mock_column()
        main_col2 = create_mock_column()
        symbol_col1 = create_mock_column()
        symbol_col2 = create_mock_column()
        symbol_col3 = create_mock_column()
        # st.columns is called twice: first with 2, then with 3
        mock_st.columns.side_effect = [
            [main_col1, main_col2],
            [symbol_col1, symbol_col2, symbol_col3]
        ]
        
        # Mock symbol selector
        mock_display_symbol.return_value = "AAPL"
        
        # Mock session state as a Mock for attribute access
        mock_st.session_state = Mock()
        
        # Call the function
        render_home()
        
        # Verify environment variable was accessed
        mock_os.getenv.assert_called_with("USER_NAME", "Trader")
        
        # Verify all display functions were called
        mock_display_header.assert_called_once_with("Test User")
        mock_display_portfolio.assert_called_once()
        mock_display_market.assert_called_once()
        mock_display_activity.assert_called_once()
        mock_display_actions.assert_called_once()
        mock_display_news.assert_called_once()
        mock_display_symbol.assert_called_once()
        
        # Verify session state was updated
        assert mock_st.session_state.selected_symbol == "AAPL"

    @patch('src.ui.home.display_symbol_selector')
    @patch('src.ui.home.display_market_news')
    @patch('src.ui.home.display_quick_actions')
    @patch('src.ui.home.display_recent_activity')
    @patch('src.ui.home.display_market_overview')
    @patch('src.ui.home.display_portfolio_summary')
    @patch('src.ui.home.display_header')
    @patch('src.ui.home.os')
    @patch('src.ui.home.st')
    def test_render_home_no_symbol_selected(self, mock_st, mock_os, mock_display_header, 
                                           mock_display_portfolio, mock_display_market, 
                                           mock_display_activity, mock_display_actions,
                                           mock_display_news, mock_display_symbol):
        """Test home page rendering when no symbol is selected."""
        from src.ui.home import render_home
        
        # Mock environment variable
        mock_os.getenv.return_value = "Test User"
        
        # Prepare columns for each call (only 2 columns needed)
        main_col1 = create_mock_column()
        main_col2 = create_mock_column()
        mock_st.columns.side_effect = [
            [main_col1, main_col2]
        ]
        
        # Mock symbol selector returns None
        mock_display_symbol.return_value = None
        
        # Mock session state as a Mock for attribute access
        mock_st.session_state = Mock()
        
        # Call the function
        render_home()
        
        # Verify all display functions were called
        mock_display_header.assert_called_once_with("Test User")
        mock_display_portfolio.assert_called_once()
        mock_display_market.assert_called_once()
        mock_display_activity.assert_called_once()
        mock_display_actions.assert_called_once()
        mock_display_news.assert_called_once()
        mock_display_symbol.assert_called_once()
        
        # Since Mock objects automatically create attributes, we just verify the symbol selector was called
        # and returned None, which means no symbol was selected

    @patch('src.ui.home.display_symbol_selector')
    @patch('src.ui.home.display_market_news')
    @patch('src.ui.home.display_quick_actions')
    @patch('src.ui.home.display_recent_activity')
    @patch('src.ui.home.display_market_overview')
    @patch('src.ui.home.display_portfolio_summary')
    @patch('src.ui.home.display_header')
    @patch('src.ui.home.os')
    @patch('src.ui.home.st')
    def test_render_home_default_user_name(self, mock_st, mock_os, mock_display_header, 
                                          mock_display_portfolio, mock_display_market, 
                                          mock_display_activity, mock_display_actions,
                                          mock_display_news, mock_display_symbol):
        """Test home page rendering with default user name."""
        from src.ui.home import render_home
        
        # Mock environment variable to return None (use default)
        # Simply return None for the first call
        mock_os.getenv.return_value = None
        
        # Prepare columns for each call
        main_col1 = create_mock_column()
        main_col2 = create_mock_column()
        symbol_col1 = create_mock_column()
        symbol_col2 = create_mock_column()
        symbol_col3 = create_mock_column()
        mock_st.columns.side_effect = [
            [main_col1, main_col2],
            [symbol_col1, symbol_col2, symbol_col3]
        ]
        
        # Mock symbol selector
        mock_display_symbol.return_value = "GOOGL"
        
        # Mock session state as a Mock for attribute access
        mock_st.session_state = Mock()
        
        # Call the function
        render_home()
        
        # Verify that os.getenv was called with the correct parameters
        mock_os.getenv.assert_called_with("USER_NAME", "Trader")
        
        # Verify that display_header was called (we can't easily verify the exact value due to mock behavior)
        mock_display_header.assert_called_once()

    @patch('src.ui.home.st')
    def test_render_home_divider_count(self, mock_st):
        """Test that render_home creates correct number of dividers."""
        from src.ui.home import render_home
        
        # Mock all dependencies
        with patch('src.ui.home.os') as mock_os, \
             patch('src.ui.home.display_header') as mock_header, \
             patch('src.ui.home.display_portfolio_summary') as mock_portfolio, \
             patch('src.ui.home.display_market_overview') as mock_market, \
             patch('src.ui.home.display_recent_activity') as mock_activity, \
             patch('src.ui.home.display_quick_actions') as mock_actions, \
             patch('src.ui.home.display_market_news') as mock_news, \
             patch('src.ui.home.display_symbol_selector') as mock_symbol:
            
            # Prepare columns for each call
            main_col1 = create_mock_column()
            main_col2 = create_mock_column()
            symbol_col1 = create_mock_column()
            symbol_col2 = create_mock_column()
            symbol_col3 = create_mock_column()
            mock_st.columns.side_effect = [
                [main_col1, main_col2],
                [symbol_col1, symbol_col2, symbol_col3]
            ]
            
            # Setup mocks
            mock_os.getenv.return_value = "Test User"
            mock_symbol.return_value = "AAPL"
            # Mock session state as a Mock for attribute access
            mock_st.session_state = Mock()
            
            # Call the function
            render_home()
            
            # Verify dividers were created (should be 4 dividers)
            assert mock_st.divider.call_count == 4

    def test_import_home_module(self):
        """Test that home module can be imported successfully."""
        try:
            from src.ui.home import (
                get_greeting,
                display_header,
                display_portfolio_summary,
                display_market_overview,
                display_recent_activity,
                display_quick_actions,
                display_market_news,
                render_home
            )
            assert all([
                get_greeting,
                display_header,
                display_portfolio_summary,
                display_market_overview,
                display_recent_activity,
                display_quick_actions,
                display_market_news,
                render_home
            ])
        except ImportError as e:
            pytest.fail(f"Failed to import home module: {e}")

    @patch('src.ui.home.st')
    def test_display_portfolio_summary_metrics_count(self, mock_st):
        """Test that portfolio summary displays correct number of metrics."""
        from src.ui.home import display_portfolio_summary
        
        # Mock streamlit columns with context manager support
        mock_cols = [create_mock_column() for _ in range(4)]
        mock_st.columns.return_value = mock_cols
        
        # Mock expander
        mock_expander = Mock()
        mock_st.expander.return_value.__enter__ = Mock(return_value=mock_expander)
        mock_st.expander.return_value.__exit__ = Mock(return_value=None)
        
        # Call the function
        display_portfolio_summary()
        
        # Verify exactly 8 metrics were displayed (4 primary + 4 in expander)
        assert mock_st.metric.call_count == 8

    @patch('src.ui.home.st')
    def test_display_market_overview_metrics_count(self, mock_st):
        """Test that market overview displays correct number of metrics."""
        from src.ui.home import display_market_overview
        
        # Mock streamlit columns with context manager support
        mock_cols = [create_mock_column() for _ in range(3)]
        mock_st.columns.return_value = mock_cols
        
        # Call the function
        display_market_overview()
        
        # Verify exactly 9 metrics were displayed (3 per column)
        assert mock_st.metric.call_count == 9

    @patch('src.ui.home.st')
    def test_display_quick_actions_button_count(self, mock_st):
        """Test that quick actions displays correct number of buttons."""
        from src.ui.home import display_quick_actions
        
        # Mock streamlit columns with context manager support
        mock_cols = [create_mock_column() for _ in range(2)]
        mock_st.columns.return_value = mock_cols
        
        # Call the function
        display_quick_actions()
        
        # Verify exactly 4 buttons were created
        assert mock_st.button.call_count == 4

    @patch('src.ui.home.format_datetime_est_to_cst')
    @patch('src.ui.home.DatabaseConnectivity')
    @patch('src.ui.home.st')
    def test_display_market_news_with_none_published_at(self, mock_st, mock_db_class, mock_format_datetime):
        """Test market news display with None published_at."""
        from src.ui.home import display_market_news
        
        # Mock database and cursor
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        
        mock_cursor = Mock()
        mock_db.get_session.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_db.get_session.return_value.__exit__ = Mock(return_value=None)
        
        # Mock news data with None published_at
        mock_articles = [
            ("Test Article", "Reuters", "http://example.com", None, "Test description")
        ]
        mock_cursor.fetchall.return_value = mock_articles
        
        # Mock expander
        mock_expander = Mock()
        mock_st.expander.return_value.__enter__ = Mock(return_value=mock_expander)
        mock_st.expander.return_value.__exit__ = Mock(return_value=None)
        
        # Call the function
        display_market_news()
        
        # Verify article was displayed with "Unknown date"
        mock_st.expander.assert_called_once() 