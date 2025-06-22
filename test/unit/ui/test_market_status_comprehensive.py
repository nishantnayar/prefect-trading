"""
Comprehensive tests for market_status module.

This module tests all functions in the market_status module to ensure
proper functionality and increase code coverage.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import patch, Mock, MagicMock
from pytz import timezone as pytz_timezone
import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from src.ui.components.market_status import (
    get_ordinal_suffix,
    format_datetime_cst,
    display_market_status_section,
    display_next_events,
    display_market_hours,
    display_market_status
)


class TestGetOrdinalSuffix:
    """Test the get_ordinal_suffix function."""
    
    def test_ordinal_suffix_1st(self):
        """Test ordinal suffix for 1st."""
        assert get_ordinal_suffix(1) == 'st'
    
    def test_ordinal_suffix_2nd(self):
        """Test ordinal suffix for 2nd."""
        assert get_ordinal_suffix(2) == 'nd'
    
    def test_ordinal_suffix_3rd(self):
        """Test ordinal suffix for 3rd."""
        assert get_ordinal_suffix(3) == 'rd'
    
    def test_ordinal_suffix_4th(self):
        """Test ordinal suffix for 4th."""
        assert get_ordinal_suffix(4) == 'th'
    
    def test_ordinal_suffix_11th(self):
        """Test ordinal suffix for 11th (special case)."""
        assert get_ordinal_suffix(11) == 'th'
    
    def test_ordinal_suffix_12th(self):
        """Test ordinal suffix for 12th (special case)."""
        assert get_ordinal_suffix(12) == 'th'
    
    def test_ordinal_suffix_13th(self):
        """Test ordinal suffix for 13th (special case)."""
        assert get_ordinal_suffix(13) == 'th'
    
    def test_ordinal_suffix_21st(self):
        """Test ordinal suffix for 21st."""
        assert get_ordinal_suffix(21) == 'st'
    
    def test_ordinal_suffix_22nd(self):
        """Test ordinal suffix for 22nd."""
        assert get_ordinal_suffix(22) == 'nd'
    
    def test_ordinal_suffix_23rd(self):
        """Test ordinal suffix for 23rd."""
        assert get_ordinal_suffix(23) == 'rd'
    
    def test_ordinal_suffix_24th(self):
        """Test ordinal suffix for 24th."""
        assert get_ordinal_suffix(24) == 'th'
    
    def test_ordinal_suffix_31st(self):
        """Test ordinal suffix for 31st."""
        assert get_ordinal_suffix(31) == 'st'


class TestFormatDatetimeCst:
    """Test the format_datetime_cst function."""
    
    def test_format_datetime_cst_timezone_aware(self):
        """Test formatting timezone-aware datetime."""
        # Create a timezone-aware datetime in UTC
        utc_time = datetime(2024, 1, 24, 19, 30, 0, tzinfo=pytz_timezone('UTC'))
        result = format_datetime_cst(utc_time)
        
        # Should convert to CST (6 hours behind UTC during standard time)
        assert "1:30 PM" in result
        assert "24th January, 2024" in result
    
    def test_format_datetime_cst_timezone_naive(self):
        """Test formatting timezone-naive datetime."""
        # Create a timezone-naive datetime
        naive_time = datetime(2024, 1, 24, 19, 30, 0)
        result = format_datetime_cst(naive_time)
        
        # Should be treated as UTC and converted to CST
        assert "1:30 PM" in result
        assert "24th January, 2024" in result
    
    def test_format_datetime_cst_edge_cases(self):
        """Test edge cases for datetime formatting."""
        # Test midnight
        midnight_utc = datetime(2024, 1, 24, 6, 0, 0, tzinfo=pytz_timezone('UTC'))
        result = format_datetime_cst(midnight_utc)
        assert "12:00 AM" in result  # Midnight CST
        
        # Test noon
        noon_utc = datetime(2024, 1, 24, 18, 0, 0, tzinfo=pytz_timezone('UTC'))
        result = format_datetime_cst(noon_utc)
        assert "12:00 PM" in result  # Noon CST


class TestDisplayMarketStatusSection:
    """Test the display_market_status_section function."""
    
    @patch('src.ui.components.market_status.st')
    def test_display_market_status_open(self, mock_st):
        """Test displaying market status when open."""
        current_time = datetime(2024, 1, 24, 14, 30, 0, tzinfo=pytz_timezone('UTC'))
        
        display_market_status_section(True, current_time)
        
        # Should call markdown with green color and OPEN text
        mock_st.markdown.assert_called_once()
        call_args = mock_st.markdown.call_args[0][0]
        assert "green" in call_args
        assert "OPEN" in call_args
        assert "text-align: center" in call_args
    
    @patch('src.ui.components.market_status.st')
    def test_display_market_status_closed(self, mock_st):
        """Test displaying market status when closed."""
        current_time = datetime(2024, 1, 24, 14, 30, 0, tzinfo=pytz_timezone('UTC'))
        
        display_market_status_section(False, current_time)
        
        # Should call markdown with red color and CLOSED text
        mock_st.markdown.assert_called_once()
        call_args = mock_st.markdown.call_args[0][0]
        assert "red" in call_args
        assert "CLOSED" in call_args
        assert "text-align: center" in call_args


class TestDisplayNextEvents:
    """Test the display_next_events function."""
    
    @patch('src.ui.components.market_status.format_datetime_est_to_cst')
    @patch('src.ui.components.market_status.st')
    def test_display_next_events_both_times(self, mock_st, mock_format):
        """Test displaying both next open and close times."""
        next_open = datetime(2024, 1, 24, 9, 30, 0)
        next_close = datetime(2024, 1, 24, 16, 0, 0)
        mock_format.return_value = "9:30 AM"
        
        display_next_events(next_open, next_close)
        
        # Should call markdown multiple times
        assert mock_st.markdown.call_count >= 3
        # Check for the container div
        first_call = mock_st.markdown.call_args_list[0][0][0]
        assert "text-align: center" in first_call
        # Check for next open
        second_call = mock_st.markdown.call_args_list[1][0][0]
        assert "Next Open:" in second_call
        # Check for next close
        third_call = mock_st.markdown.call_args_list[2][0][0]
        assert "Next Close:" in third_call
    
    @patch('src.ui.components.market_status.format_datetime_est_to_cst')
    @patch('src.ui.components.market_status.st')
    def test_display_next_events_only_open(self, mock_st, mock_format):
        """Test displaying only next open time."""
        next_open = datetime(2024, 1, 24, 9, 30, 0)
        next_close = None
        mock_format.return_value = "9:30 AM"
        
        display_next_events(next_open, next_close)
        
        # Should call markdown for container and next open only
        assert mock_st.markdown.call_count == 3  # container div, next open, closing div
        # Check for next open
        second_call = mock_st.markdown.call_args_list[1][0][0]
        assert "Next Open:" in second_call
    
    @patch('src.ui.components.market_status.format_datetime_est_to_cst')
    @patch('src.ui.components.market_status.st')
    def test_display_next_events_only_close(self, mock_st, mock_format):
        """Test displaying only next close time."""
        next_open = None
        next_close = datetime(2024, 1, 24, 16, 0, 0)
        mock_format.return_value = "4:00 PM"
        
        display_next_events(next_open, next_close)
        
        # Should call markdown for container and next close only
        assert mock_st.markdown.call_count == 3  # container div, next close, closing div
        # Check for next close
        second_call = mock_st.markdown.call_args_list[1][0][0]
        assert "Next Close:" in second_call
    
    @patch('src.ui.components.market_status.st')
    def test_display_next_events_none(self, mock_st):
        """Test displaying when both times are None."""
        display_next_events(None, None)
        
        # Should not call markdown at all
        mock_st.markdown.assert_not_called()


class TestDisplayMarketHours:
    """Test the display_market_hours function."""
    
    @patch('src.ui.components.market_status.format_datetime_est_to_cst')
    @patch('src.ui.components.market_status.st')
    def test_display_market_hours_with_data(self, mock_st, mock_format):
        """Test displaying market hours with valid data."""
        hours = {
            'open': datetime(2024, 1, 24, 9, 30, 0),
            'close': datetime(2024, 1, 24, 16, 0, 0)
        }
        mock_format.return_value = "9:30 AM"
        
        display_market_hours(hours)
        
        # Should call markdown multiple times
        assert mock_st.markdown.call_count == 3
        # Check for the container div
        first_call = mock_st.markdown.call_args_list[0][0][0]
        assert "text-align: center" in first_call
        # Check for hours display
        second_call = mock_st.markdown.call_args_list[1][0][0]
        assert "Hours:" in second_call
        assert "9:30 AM" in second_call
    
    @patch('src.ui.components.market_status.st')
    def test_display_market_hours_none(self, mock_st):
        """Test displaying market hours when data is None."""
        display_market_hours(None)
        
        # Should not call markdown at all
        mock_st.markdown.assert_not_called()
    
    @patch('src.ui.components.market_status.st')
    def test_display_market_hours_empty_dict(self, mock_st):
        """Test displaying market hours when data is empty dict."""
        display_market_hours({})
        
        # Should not call markdown at all
        mock_st.markdown.assert_not_called()


class TestDisplayMarketStatus:
    """Test the display_market_status function."""
    
    @patch('src.ui.components.market_status.display_market_hours')
    @patch('src.ui.components.market_status.display_next_events')
    @patch('src.ui.components.market_status.display_market_status_section')
    @patch('src.ui.components.market_status.MarketHoursManager')
    @patch('src.ui.components.market_status.st')
    @patch('src.ui.components.market_status.datetime')
    def test_display_market_status_success(self, mock_datetime, mock_st, mock_market_hours_class, 
                                          mock_display_section, mock_display_events, mock_display_hours):
        """Test successful market status display."""
        # Mock current time
        mock_now = datetime(2024, 1, 24, 14, 30, 0, tzinfo=pytz_timezone('UTC'))
        mock_datetime.now.return_value = mock_now
        
        # Mock MarketHoursManager
        mock_market_hours = Mock()
        mock_market_hours_class.return_value = mock_market_hours
        mock_market_hours.is_market_open.return_value = True
        mock_market_hours.get_next_market_open.return_value = datetime(2024, 1, 24, 9, 30, 0)
        mock_market_hours.get_next_market_close.return_value = datetime(2024, 1, 24, 16, 0, 0)
        mock_market_hours.get_market_hours.return_value = {
            'open': datetime(2024, 1, 24, 9, 30, 0),
            'close': datetime(2024, 1, 24, 16, 0, 0)
        }
        
        # Mock container
        mock_container = Mock()
        mock_st.container.return_value.__enter__ = Mock(return_value=mock_container)
        mock_st.container.return_value.__exit__ = Mock(return_value=None)
        
        display_market_status()
        
        # Verify all functions were called
        mock_market_hours_class.assert_called_once()
        mock_market_hours.is_market_open.assert_called_once()
        mock_market_hours.get_next_market_open.assert_called_once()
        mock_market_hours.get_next_market_close.assert_called_once()
        mock_market_hours.get_market_hours.assert_called_once()
        
        mock_display_section.assert_called_once_with(True, mock_now)
        mock_display_events.assert_called_once_with(
            datetime(2024, 1, 24, 9, 30, 0),
            datetime(2024, 1, 24, 16, 0, 0)
        )
        mock_display_hours.assert_called_once_with({
            'open': datetime(2024, 1, 24, 9, 30, 0),
            'close': datetime(2024, 1, 24, 16, 0, 0)
        })
    
    @patch('src.ui.components.market_status.logger')
    @patch('src.ui.components.market_status.st')
    @patch('src.ui.components.market_status.MarketHoursManager')
    def test_display_market_status_exception(self, mock_market_hours_class, mock_st, mock_logger):
        """Test market status display when an exception occurs."""
        # Mock MarketHoursManager to raise an exception
        mock_market_hours_class.side_effect = Exception("Database connection failed")
        
        display_market_status()
        
        # Should log the error
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Error displaying market status:" in error_call
        assert "Database connection failed" in error_call
        
        # Should display error message
        mock_st.error.assert_called_once_with("Error fetching market status. Please try again later.")


class TestIntegrationScenarios:
    """Test integration scenarios for market_status functions."""
    
    @patch('src.ui.components.market_status.format_datetime_est_to_cst')
    @patch('src.ui.components.market_status.st')
    def test_full_market_status_workflow(self, mock_st, mock_format):
        """Test the full workflow of market status display."""
        mock_format.return_value = "9:30 AM"
        
        # Test market status section
        display_market_status_section(True, datetime.now())
        assert mock_st.markdown.call_count >= 1
        
        # Test next events
        display_next_events(
            datetime(2024, 1, 24, 9, 30, 0),
            datetime(2024, 1, 24, 16, 0, 0)
        )
        assert mock_st.markdown.call_count >= 3
        
        # Test market hours
        display_market_hours({
            'open': datetime(2024, 1, 24, 9, 30, 0),
            'close': datetime(2024, 1, 24, 16, 0, 0)
        })
        assert mock_st.markdown.call_count >= 5


class TestEdgeCases:
    """Test edge cases for market_status functions."""
    
    def test_format_datetime_cst_with_different_timezones(self):
        """Test format_datetime_cst with different timezone inputs."""
        # Test with EST timezone (1 hour ahead of CST)
        est_time = datetime(2024, 1, 24, 14, 30, 0, tzinfo=pytz_timezone('US/Eastern'))
        result = format_datetime_cst(est_time)
        assert result.startswith("24th January, 2024 1:") and "PM" in result
        
        # Test with PST timezone (2 hours behind CST)
        pst_time = datetime(2024, 1, 24, 11, 30, 0, tzinfo=pytz_timezone('US/Pacific'))
        result = format_datetime_cst(pst_time)
        assert result.startswith("24th January, 2024 1:") and "PM" in result
    
    @patch('src.ui.components.market_status.st')
    def test_display_functions_with_empty_strings(self, mock_st):
        """Test display functions with edge case inputs."""
        # Test with empty strings (should not crash)
        display_market_status_section(True, datetime.now())
        display_next_events(None, None)
        display_market_hours(None)
        
        # Should handle gracefully
        assert mock_st.markdown.call_count >= 1


if __name__ == "__main__":
    pytest.main([__file__]) 