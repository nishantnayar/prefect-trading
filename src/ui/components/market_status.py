"""
Market Status Component

This module provides a compact and efficient way to display market status information.
It shows whether the market is open or closed, next market events, and current market hours.
All times are displayed in Central Time (CST).

The display is optimized to take minimal vertical space while maintaining readability
and providing all essential information at a glance.
"""

from datetime import datetime, timezone
import streamlit as st
from loguru import logger
from pytz import timezone as pytz_timezone
from typing import Optional, Dict, Any

from src.utils.market_hours import MarketHoursManager
from src.ui.components.date_display import format_datetime_est_to_cst


def get_ordinal_suffix(day):
    """Return ordinal suffix for a day (st, nd, rd, th)"""
    if 11 <= day <= 13:
        return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')


def format_datetime_cst(dt):
    """Format datetime in CST as '24th May, 2025 8:08 PM'"""
    cst_zone = pytz_timezone('America/Chicago')

    # Handle both timezone-naive and timezone-aware datetimes
    if dt.tzinfo is None:
        dt = pytz_timezone('UTC').localize(dt)

    cst_time = dt.astimezone(cst_zone)

    # Get components for custom formatting
    day = cst_time.day
    suffix = get_ordinal_suffix(day)
    month = cst_time.strftime("%B")
    year = cst_time.year
    hour = cst_time.strftime("%I").lstrip("0") or "12"  # Remove leading zero
    minute = cst_time.strftime("%M")
    ampm = cst_time.strftime("%p")

    return f"{day}{suffix} {month}, {year} {hour}:{minute} {ampm}"


def display_market_status_section(is_open: bool, current_time: datetime) -> None:
    """Display a compact market status indicator.
    
    Shows whether the market is open or closed using color-coded text.
    Green for open, red for closed.
    
    Args:
        is_open: Whether the market is currently open
        current_time: Current time in UTC
    """
    status_color = "green" if is_open else "red"
    status_text = "OPEN" if is_open else "CLOSED"
    
    st.markdown(f"""
        <div style='text-align: center;'>
            <span style='color: {status_color}; font-weight: bold;'>{status_text}</span>
        </div>
    """, unsafe_allow_html=True)


def display_next_events(next_open: Optional[datetime], next_close: Optional[datetime]) -> None:
    """Display next market events in a compact format.
    
    Shows the next market open and close times in a centered layout.
    Times are displayed in CST.
    
    Args:
        next_open: Next market open time
        next_close: Next market close time
    """
    if next_open or next_close:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        if next_open:
            st.markdown(f"**Next Open:** {format_datetime_est_to_cst(next_open)}")
        if next_close:
            st.markdown(f"**Next Close:** {format_datetime_est_to_cst(next_close)}")
        st.markdown("</div>", unsafe_allow_html=True)


def display_market_hours(hours: Optional[Dict[str, datetime]]) -> None:
    """Display today's market hours in a single line.
    
    Shows market open and close times in a compact, centered format.
    Times are displayed in CST.
    
    Args:
        hours: Dictionary containing market open and close times
    """
    if hours:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown(f"**Hours:** {format_datetime_est_to_cst(hours['open'])} - {format_datetime_est_to_cst(hours['close'])}")
        st.markdown("</div>", unsafe_allow_html=True)


def display_market_status() -> None:
    """Display a compact market status section with all essential information.
    
    This is the main function that combines all market status information into a single,
    space-efficient display. It shows:
    - Current market status (open/closed)
    - Next market events (open/close)
    - Today's market hours
    
    All times are displayed in Central Time (CST).
    The display is optimized to take minimal vertical space while maintaining readability.
    """
    try:
        market_hours = MarketHoursManager()
        current_time = datetime.now(timezone.utc)
        
        # Create a single container for all market status information
        with st.container():
            display_market_status_section(
                market_hours.is_market_open(),
                current_time
            )
            
            display_next_events(
                market_hours.get_next_market_open(),
                market_hours.get_next_market_close()
            )
            
            display_market_hours(market_hours.get_market_hours())

    except Exception as e:
        logger.error(f"Error displaying market status: {e}")
        st.error("Error fetching market status. Please try again later.")