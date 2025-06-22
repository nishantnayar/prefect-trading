"""
Comprehensive tests for date_display module.

This module tests all functions in the date_display module to ensure
proper functionality and increase code coverage.
"""

import pytest
from datetime import datetime
from unittest.mock import patch, Mock
from pytz import timezone
import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from src.ui.components.date_display import (
    get_ordinal_suffix,
    format_datetime_est_to_cst,
    get_current_cst,
    get_current_cst_formatted,
    convert_est_to_cst
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


class TestFormatDatetimeEstToCst:
    """Test the format_datetime_est_to_cst function."""
    
    def test_format_datetime_with_datetime_object(self):
        """Test formatting with datetime object."""
        # Create a datetime object in EST (using January to avoid DST issues)
        est_time = datetime(2024, 1, 24, 14, 30, 0)  # 2:30 PM EST
        result = format_datetime_est_to_cst(est_time)
        
        # Should convert to CST (1 hour behind EST during standard time)
        assert "1:30 PM" in result
        assert "24th January, 2024" in result
    
    def test_format_datetime_with_string(self):
        """Test formatting with ISO format string."""
        iso_string = "2024-01-24T14:30:00"
        result = format_datetime_est_to_cst(iso_string)
        
        # Should convert to CST
        assert "1:30 PM" in result
        assert "24th January, 2024" in result
    
    def test_format_datetime_with_timezone_aware_datetime(self):
        """Test formatting with timezone-aware datetime."""
        # Create a timezone-aware datetime in UTC
        utc_time = datetime(2024, 1, 24, 19, 30, 0, tzinfo=timezone('UTC'))
        result = format_datetime_est_to_cst(utc_time)
        
        # Should convert through EST to CST
        assert "1:30 PM" in result
        assert "24th January, 2024" in result
    
    def test_format_datetime_invalid_string(self):
        """Test formatting with invalid string format."""
        with pytest.raises(ValueError, match="Invalid datetime string format"):
            format_datetime_est_to_cst("invalid-date-string")
    
    def test_format_datetime_custom_input_timezone(self):
        """Test formatting with custom input timezone."""
        # Create a datetime object and specify different input timezone
        dt = datetime(2024, 1, 24, 14, 30, 0)
        result = format_datetime_est_to_cst(dt, input_tz='US/Pacific')
        
        # Should convert from Pacific to CST (2 hours ahead during standard time)
        assert "4:30 PM" in result
        assert "24th January, 2024" in result
    
    def test_format_datetime_edge_cases(self):
        """Test edge cases for datetime formatting."""
        # Test midnight (using January to avoid DST issues)
        midnight_est = datetime(2024, 1, 24, 0, 0, 0)
        result = format_datetime_est_to_cst(midnight_est)
        assert "11:00 PM" in result  # Previous day in CST
        
        # Test noon
        noon_est = datetime(2024, 1, 24, 12, 0, 0)
        result = format_datetime_est_to_cst(noon_est)
        assert "11:00 AM" in result  # CST


class TestGetCurrentCst:
    """Test the get_current_cst function."""
    
    def test_get_current_cst(self):
        """Test getting current CST time."""
        result = get_current_cst()
        
        # Should return a timezone-aware datetime in CST
        assert result.tzinfo is not None
        # The result should be in CST timezone, but the exact zone name might vary
        assert 'Central' in str(result.tzinfo) or result.tzinfo.zone in ['US/Central', 'America/Chicago']
        
        # Should be a recent time (within the last minute)
        from datetime import datetime, timedelta
        now = datetime.now()
        assert abs((result.replace(tzinfo=None) - now).total_seconds()) < 60


class TestGetCurrentCstFormatted:
    """Test the get_current_cst_formatted function."""
    
    @patch('src.ui.components.date_display.get_current_cst')
    @patch('src.ui.components.date_display.format_datetime_est_to_cst')
    def test_get_current_cst_formatted(self, mock_format, mock_get_current):
        """Test getting formatted current CST time."""
        # Mock the current CST time
        mock_cst_time = datetime(2024, 5, 24, 13, 30, 0, tzinfo=timezone('US/Central'))
        mock_get_current.return_value = mock_cst_time
        
        # Mock the formatting function
        mock_format.return_value = "24th May, 2024 1:30 PM"
        
        result = get_current_cst_formatted()
        
        # Should call both functions
        mock_get_current.assert_called_once()
        mock_format.assert_called_once_with(mock_cst_time)
        assert result == "24th May, 2024 1:30 PM"


class TestConvertEstToCst:
    """Test the convert_est_to_cst function."""
    
    def test_convert_est_to_cst_with_datetime_object(self):
        """Test converting EST datetime to CST."""
        # Create a datetime object (assumed to be in EST)
        est_time = datetime(2024, 5, 24, 14, 30, 0)
        result = convert_est_to_cst(est_time)
        
        # Should return a timezone-aware datetime in CST
        assert result.tzinfo is not None
        assert result.tzinfo.zone == 'US/Central'
        
        # Should be 1 hour behind EST
        assert result.hour == 13  # 1:30 PM CST
    
    def test_convert_est_to_cst_with_string(self):
        """Test converting EST string to CST."""
        iso_string = "2024-05-24T14:30:00"
        result = convert_est_to_cst(iso_string)
        
        # Should return a timezone-aware datetime in CST
        assert result.tzinfo is not None
        assert result.tzinfo.zone == 'US/Central'
        
        # Should be 1 hour behind EST
        assert result.hour == 13  # 1:30 PM CST
    
    def test_convert_est_to_cst_with_timezone_aware_datetime(self):
        """Test converting timezone-aware datetime to CST."""
        # Create a timezone-aware datetime in EST (using January to avoid DST issues)
        est_time = datetime(2024, 1, 24, 14, 30, 0, tzinfo=timezone('US/Eastern'))
        result = convert_est_to_cst(est_time)
        
        # Should return a timezone-aware datetime in CST
        assert result.tzinfo is not None
        assert result.tzinfo.zone == 'US/Central'
        
        # Should be 1 hour behind EST (during standard time)
        assert result.hour == 13  # 1:30 PM CST
    
    def test_convert_est_to_cst_edge_cases(self):
        """Test edge cases for EST to CST conversion."""
        # Test midnight EST (using January to avoid DST issues)
        midnight_est = datetime(2024, 1, 24, 0, 0, 0)
        result = convert_est_to_cst(midnight_est)
        assert result.hour == 23  # 11:00 PM CST (previous day)
        
        # Test noon EST
        noon_est = datetime(2024, 1, 24, 12, 0, 0)
        result = convert_est_to_cst(noon_est)
        assert result.hour == 11  # 11:00 AM CST


class TestIntegrationScenarios:
    """Test integration scenarios for date_display functions."""
    
    def test_full_workflow_datetime_formatting(self):
        """Test the full workflow of datetime formatting."""
        # Create a datetime in EST (using January to avoid DST issues)
        est_time = datetime(2024, 1, 24, 14, 30, 0)
        
        # Convert to CST
        cst_time = convert_est_to_cst(est_time)
        
        # Format the result
        formatted = format_datetime_est_to_cst(est_time)
        
        # Verify the results are consistent
        assert cst_time.tzinfo.zone == 'US/Central'
        assert "1:30 PM" in formatted
        assert "24th January, 2024" in formatted
    
    def test_current_time_workflow(self):
        """Test the workflow of getting current formatted time."""
        with patch('src.ui.components.date_display.get_current_cst') as mock_get_current, \
             patch('src.ui.components.date_display.format_datetime_est_to_cst') as mock_format:
            
            # Mock current CST time
            mock_cst_time = datetime(2024, 5, 24, 13, 30, 0, tzinfo=timezone('US/Central'))
            mock_get_current.return_value = mock_cst_time
            mock_format.return_value = "24th May, 2024 1:30 PM"
            
            # Get formatted current time
            result = get_current_cst_formatted()
            
            # Verify the workflow
            mock_get_current.assert_called_once()
            mock_format.assert_called_once_with(mock_cst_time)
            assert result == "24th May, 2024 1:30 PM"


class TestErrorHandling:
    """Test error handling in date_display functions."""
    
    def test_format_datetime_est_to_cst_invalid_string(self):
        """Test error handling for invalid datetime string."""
        with pytest.raises(ValueError, match="Invalid datetime string format"):
            format_datetime_est_to_cst("not-a-datetime")
    
    def test_format_datetime_est_to_cst_none_input(self):
        """Test error handling for None input."""
        with pytest.raises(AttributeError):
            format_datetime_est_to_cst(None)
    
    def test_convert_est_to_cst_invalid_string(self):
        """Test error handling for invalid string in convert function."""
        with pytest.raises(ValueError):
            convert_est_to_cst("not-a-datetime")
    
    def test_convert_est_to_cst_none_input(self):
        """Test error handling for None input in convert function."""
        with pytest.raises(AttributeError):
            convert_est_to_cst(None)


if __name__ == "__main__":
    pytest.main([__file__]) 