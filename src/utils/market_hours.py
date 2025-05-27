from datetime import datetime, timezone, timedelta
from typing import Optional, Dict
from pytz import timezone as pytz_timezone
from loguru import logger
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

# Load environment variables
load_dotenv('config/.env', override=True)


class MarketHoursManager:
    """Manages market hours and status for US stock market using Alpaca API."""
    
    def __init__(self):
        self.est_zone = pytz_timezone('US/Eastern')
        self.cst_zone = pytz_timezone('US/Central')
        
        # Get API credentials
        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')
        
        # Validate credentials
        if not api_key or not secret_key:
            logger.error("Alpaca API credentials not found in environment variables")
            raise ValueError(
                "Alpaca API credentials not found. Please ensure ALPACA_API_KEY and "
                "ALPACA_SECRET_KEY are set in your .env file"
            )
        
        # Initialize Alpaca API
        try:
            self.api = TradingClient(
                api_key=api_key,
                secret_key=secret_key,
                paper=True  # Use paper trading by default
            )
            # Test the connection
            self.api.get_clock()
        except Exception as e:
            logger.error(f"Failed to initialize Alpaca API: {e}")
            raise ValueError(
                "Failed to connect to Alpaca API. Please check your credentials and internet connection."
            )
        
    def _get_current_time(self) -> datetime:
        """Get current time in UTC."""
        return datetime.now(timezone.utc)
        
    def _is_weekend(self, dt: datetime) -> bool:
        """Check if the given date is a weekend."""
        return dt.weekday() >= 5
        
    def _is_holiday(self, dt: datetime) -> bool:
        """Check if the given date is a market holiday.
        TODO: Implement holiday calendar
        """
        return False
        
    def _get_market_open_time(self, dt: datetime) -> datetime:
        """Get market open time for the given date."""
        market_open = dt.replace(hour=9, minute=30, second=0, microsecond=0)
        return self.est_zone.localize(market_open)
        
    def _get_market_close_time(self, dt: datetime) -> datetime:
        """Get market close time for the given date."""
        market_close = dt.replace(hour=16, minute=0, second=0, microsecond=0)
        return self.est_zone.localize(market_close)
        
    def is_market_open(self) -> bool:
        """Check if the market is currently open using Alpaca API."""
        try:
            clock = self.api.get_clock()
            return clock.is_open
        except Exception as e:
            logger.error(f"Error checking market status from Alpaca: {e}")
            return False
        
    def get_market_hours(self) -> Optional[Dict[str, datetime]]:
        """Get today's market hours from Alpaca API."""
        try:
            clock = self.api.get_clock()
            return {
                'open': clock.next_open,
                'close': clock.next_close
            }
        except Exception as e:
            logger.error(f"Error getting market hours from Alpaca: {e}")
            return None
        
    def get_next_market_open(self) -> Optional[datetime]:
        """Get the next market open time from Alpaca API."""
        try:
            clock = self.api.get_clock()
            return clock.next_open
        except Exception as e:
            logger.error(f"Error getting next market open from Alpaca: {e}")
            return None
        
    def get_next_market_close(self) -> Optional[datetime]:
        """Get the next market close time from Alpaca API."""
        try:
            clock = self.api.get_clock()
            return clock.next_close
        except Exception as e:
            logger.error(f"Error getting next market close from Alpaca: {e}")
            return None 