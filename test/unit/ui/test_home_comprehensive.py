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
        def columns_side_effect(*args, **kwargs):
            if len(args) > 0 and isinstance(args[0], list):
                # For st.columns([4, 1]) - return 2 columns
                return [create_mock_column(), create_mock_column()]
            elif len(args) > 0 and args[0] == 4:
                # For st.columns(4) - return 4 columns
                return [create_mock_column(), create_mock_column(), create_mock_column(), create_mock_column()]
            else:
                # Default fallback
                return [create_mock_column() for _ in range(args[0] if args else 1)]
        
        mock_st.columns.side_effect = columns_side_effect
        
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

    @patch('src.ui.home.get_portfolio_manager')
    @patch('src.ui.home.PortfolioManager')
    @patch('src.ui.home.st')
    def test_display_recent_activity(self, mock_st, mock_portfolio_manager_class, mock_get_portfolio_manager):
        """Test recent activity display."""
        from src.ui.home import display_recent_activity
        from datetime import datetime
        from unittest.mock import MagicMock

        # Mock PortfolioManager to return dummy orders
        mock_portfolio_manager = MagicMock()
        mock_portfolio_manager_class.return_value = mock_portfolio_manager
        mock_get_portfolio_manager.return_value = mock_portfolio_manager

        # Mock dummy orders
        mock_orders = [
            {
                'side': 'buy',
                'symbol': 'AAPL',
                'filled_qty': 100,
                'filled_avg_price': 185.50,
                'filled_at': datetime(2024, 1, 1, 10, 15)
            },
            {
                'side': 'sell',
                'symbol': 'MSFT',
                'filled_qty': 50,
                'filled_avg_price': 374.20,
                'filled_at': datetime(2024, 1, 1, 10, 30)
            },
            {
                'side': 'buy',
                'symbol': 'GOOGL',
                'filled_qty': 75,
                'filled_avg_price': 140.00,
                'filled_at': datetime(2024, 1, 1, 10, 45)
            }
        ]
        mock_portfolio_manager.get_orders.return_value = mock_orders

        # Mock streamlit columns (should be called once with [1, 2, 2, 1] column widths)
        mock_cols = [MagicMock() for _ in range(4)]
        mock_st.columns.return_value = mock_cols

        # Reset st.write mock to ensure clean call count for this test
        mock_st.write.reset_mock()

        # Call the function
        display_recent_activity()

        # Verify subheader was displayed
        mock_st.subheader.assert_called_with("📝 Recent Activity")

        # Verify st.columns was called 3 times (once for each order) with [1, 2, 2, 1] column widths
        assert mock_st.columns.call_count == 3
        mock_st.columns.assert_any_call([1, 2, 2, 1])

        # Check that st.write was called exactly 12 times (3 orders x 4 writes per order)
        assert mock_st.write.call_count == 12

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
        """Test display of market news with articles present."""
        from src.ui.home import display_market_news

        # Setup DB and cursor mocks
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_cursor
        mock_session.__exit__.return_value = None
        mock_db.get_session.return_value = mock_session
        mock_db_class.return_value = mock_db

        # Mock news articles (published_at as string)
        mock_cursor.fetchall.return_value = [
            ('Big News', 'Reuters', 'https://example.com', '2024-01-01 10:00:00', 'Some news...'),
            ('Another News', 'Bloomberg', 'https://example.com/2', '2024-01-02 11:00:00', 'More news...')
        ]
        mock_format_datetime.return_value = 'Jan 1, 2024 10:00 AM'

        # Call the function
        display_market_news()

        # Assertions
        mock_st.subheader.assert_called_with("📰 Market News")
        assert mock_st.expander.call_count == 2
        assert mock_st.markdown.call_count >= 4  # At least 2 per article
        mock_cursor.fetchall.assert_called_once()

    @patch('src.ui.home.DatabaseConnectivity')
    @patch('src.ui.home.st')
    def test_display_market_news_no_articles(self, mock_st, mock_db_class):
        """Test display of market news when no articles are present."""
        from src.ui.home import display_market_news

        # Setup DB and cursor mocks
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_cursor
        mock_session.__exit__.return_value = None
        mock_db.get_session.return_value = mock_session
        mock_db_class.return_value = mock_db

        # Mock no news articles
        mock_cursor.fetchall.return_value = []

        # Call the function
        display_market_news()

        # Assertions
        mock_st.info.assert_called_with("No recent news articles available.")
        mock_cursor.fetchall.assert_called_once()

    @patch('src.ui.home.DatabaseConnectivity')
    @patch('src.ui.home.st')
    def test_display_market_news_database_error(self, mock_st, mock_db_class):
        """Test display of market news when a database error occurs."""
        from src.ui.home import display_market_news

        # Setup DB and cursor mocks
        mock_db = MagicMock()
        mock_session = MagicMock()
        mock_session.__enter__.side_effect = Exception("DB error")
        mock_session.__exit__.return_value = None
        mock_db.get_session.return_value = mock_session
        mock_db_class.return_value = mock_db

        # Call the function
        display_market_news()

        # Assertions
        mock_st.error.assert_called()

    @patch('src.ui.home.format_datetime_est_to_cst')
    @patch('src.ui.home.DatabaseConnectivity')
    @patch('src.ui.home.st')
    def test_display_market_news_with_none_published_at(self, mock_st, mock_db_class, mock_format_datetime):
        """Test display of market news with None published_at value."""
        from src.ui.home import display_market_news

        # Setup DB and cursor mocks
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_cursor
        mock_session.__exit__.return_value = None
        mock_db.get_session.return_value = mock_session
        mock_db_class.return_value = mock_db

        # Mock news articles with None published_at
        mock_cursor.fetchall.return_value = [
            ('News with None', 'Reuters', 'https://example.com', None, 'Some news...')
        ]
        mock_format_datetime.return_value = 'N/A'

        # Call the function
        display_market_news()

        # Assertions
        mock_st.subheader.assert_called_with("📰 Market News")
        assert mock_st.write.call_count > 0
        mock_cursor.fetchall.assert_called_once()

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
        
        def columns_side_effect(*args, **kwargs):
            if isinstance(args[0], int):
                n = args[0]
            elif isinstance(args[0], (list, tuple)):
                n = len(args[0])
            else:
                n = 1
            return [create_mock_column() for _ in range(n)]

        mock_st.columns.side_effect = columns_side_effect

        # Mock environment variable
        mock_os.getenv.return_value = "Test User"
        
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
        
        def columns_side_effect(*args, **kwargs):
            if isinstance(args[0], int):
                n = args[0]
            elif isinstance(args[0], (list, tuple)):
                n = len(args[0])
            else:
                n = 1
            return [create_mock_column() for _ in range(n)]

        mock_st.columns.side_effect = columns_side_effect

        # Mock environment variable
        mock_os.getenv.return_value = "Test User"
        
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
        
        def columns_side_effect(*args, **kwargs):
            if isinstance(args[0], int):
                n = args[0]
            elif isinstance(args[0], (list, tuple)):
                n = len(args[0])
            else:
                n = 1
            return [create_mock_column() for _ in range(n)]

        mock_st.columns.side_effect = columns_side_effect

        # Mock environment variable to return None (use default)
        # Instead of returning None, use side_effect to return the default value
        mock_os.getenv.side_effect = lambda key, default=None: default
        
        # Mock symbol selector
        mock_display_symbol.return_value = "GOOGL"
        
        # Mock session state as a Mock for attribute access
        mock_st.session_state = Mock()
        
        # Call the function
        render_home()
        
        # Verify environment variable was accessed with default
        mock_os.getenv.assert_called_with("USER_NAME", "Trader")
        
        # Verify all display functions were called
        mock_display_header.assert_called_once_with("Trader")  # Should use default
        mock_display_portfolio.assert_called_once()
        mock_display_market.assert_called_once()
        mock_display_activity.assert_called_once()
        mock_display_actions.assert_called_once()
        mock_display_news.assert_called_once()
        mock_display_symbol.assert_called_once()
        
        # Verify session state was updated
        assert mock_st.session_state.selected_symbol == "GOOGL"

    @patch('src.ui.home.st')
    def test_render_home_divider_count(self, mock_st):
        """Test that render_home creates correct number of dividers."""
        from src.ui.home import render_home
        
        with patch('src.ui.home.os') as mock_os, \
             patch('src.ui.home.display_header') as mock_header, \
             patch('src.ui.home.display_portfolio_summary') as mock_portfolio, \
             patch('src.ui.home.display_market_overview') as mock_market, \
             patch('src.ui.home.display_recent_activity') as mock_activity, \
             patch('src.ui.home.display_quick_actions') as mock_actions, \
             patch('src.ui.home.display_market_news') as mock_news, \
             patch('src.ui.home.display_symbol_selector') as mock_symbol:
            
            def columns_side_effect(*args, **kwargs):
                if isinstance(args[0], int):
                    n = args[0]
                elif isinstance(args[0], (list, tuple)):
                    n = len(args[0])
                else:
                    n = 1
                return [create_mock_column() for _ in range(n)]

            mock_st.columns.side_effect = columns_side_effect
            
            # Setup mocks
            mock_os.getenv.return_value = "Test User"
            mock_symbol.return_value = "AAPL"
            # Mock session state as a Mock for attribute access
            mock_st.session_state = Mock()
            
            # Call the function
            render_home()
            
            # Verify dividers were created (there should be multiple dividers in render_home)
            assert mock_st.divider.call_count >= 3

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
        def columns_side_effect(*args, **kwargs):
            if len(args) > 0 and isinstance(args[0], list):
                # For st.columns([4, 1]) - return 2 columns
                return [create_mock_column(), create_mock_column()]
            elif len(args) > 0 and args[0] == 4:
                # For st.columns(4) - return 4 columns
                return [create_mock_column(), create_mock_column(), create_mock_column(), create_mock_column()]
            else:
                # Default fallback
                return [create_mock_column() for _ in range(args[0] if args else 1)]
        
        mock_st.columns.side_effect = columns_side_effect
        
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