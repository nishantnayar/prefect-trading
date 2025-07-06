"""
Portfolio Manager for Alpaca Trading System

This module provides comprehensive portfolio management functionality including:
- Account information and balance
- Current positions
- Portfolio performance metrics
- Risk analysis
- Trading history
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import pandas as pd
from loguru import logger
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from prefect.blocks.system import Secret
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv('config/.env', override=True)


class PortfolioManager:
    """Manages portfolio data and metrics using Alpaca API."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implement singleton pattern to prevent multiple initializations."""
        if cls._instance is None:
            cls._instance = super(PortfolioManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the portfolio manager with Alpaca API clients."""
        # Only initialize once
        if self._initialized:
            return
            
        try:
            # Load Alpaca credentials
            api_key = Secret.load("alpaca-api-key").get()
            secret_key = Secret.load("alpaca-secret-key").get()
            
            # Initialize trading client
            self.trading_client = TradingClient(
                api_key=api_key,
                secret_key=secret_key,
                paper=True  # Use paper trading by default
            )
            
            # Initialize data client for historical data
            self.data_client = StockHistoricalDataClient(
                api_key=api_key,
                secret_key=secret_key
            )
            
            # Initialize cache
            self._cache = {}
            self._cache_timestamps = {}
            self._cache_duration = 30  # Cache for 30 seconds
            
            self._initialized = True
            logger.info("Portfolio Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Portfolio Manager: {str(e)}")
            raise
    
    def _get_cached_data(self, key: str):
        """Get data from cache if it's still valid."""
        if key in self._cache and key in self._cache_timestamps:
            timestamp = self._cache_timestamps[key]
            
            # Use shorter cache duration for orders
            cache_duration = 10 if key.startswith('orders_') else self._cache_duration
            
            if datetime.now() - timestamp < timedelta(seconds=cache_duration):
                logger.debug(f"Cache HIT for key: {key}")
                return self._cache[key]
            else:
                logger.debug(f"Cache EXPIRED for key: {key}")
        else:
            logger.debug(f"Cache MISS for key: {key}")
        return None
    
    def _set_cached_data(self, key: str, data):
        """Store data in cache with current timestamp."""
        self._cache[key] = data
        self._cache_timestamps[key] = datetime.now()
        logger.debug(f"Cache SET for key: {key}")
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Portfolio Manager cache cleared")
    
    def get_cache_stats(self):
        """Get cache statistics for monitoring."""
        return {
            'cache_size': len(self._cache),
            'cached_keys': list(self._cache.keys()),
            'cache_duration': self._cache_duration
        }
    
    def get_account_info(self) -> Dict:
        """Get account information from Alpaca.
        
        Returns:
            Dict containing account information
        """
        # Check cache first
        cached_data = self._get_cached_data('account_info')
        if cached_data:
            return cached_data
            
        def safe_float(val):
            try:
                return float(val) if val is not None else 0.0
            except Exception:
                return 0.0
        try:
            account = self.trading_client.get_account()
            
            # Create a safe dictionary with fallback values for missing attributes
            account_info = {
                'id': getattr(account, 'id', 'unknown'),
                'account_number': getattr(account, 'account_number', 'unknown'),
                'status': getattr(account, 'status', 'unknown'),
                'currency': getattr(account, 'currency', 'USD'),
                'buying_power': safe_float(getattr(account, 'buying_power', 0)),
                'regt_buying_power': safe_float(getattr(account, 'regt_buying_power', 0)),
                'daytrading_buying_power': safe_float(getattr(account, 'daytrading_buying_power', 0)),
                'non_marginable_buying_power': safe_float(getattr(account, 'non_marginable_buying_power', 0)),
                'cash': safe_float(getattr(account, 'cash', 0)),
                'accrued_fees': safe_float(getattr(account, 'accrued_fees', 0)),
                'portfolio_value': safe_float(getattr(account, 'portfolio_value', 0)),
                'pattern_day_trader': getattr(account, 'pattern_day_trader', False),
                'trading_blocked': getattr(account, 'trading_blocked', False),
                'transfers_blocked': getattr(account, 'transfers_blocked', False),
                'account_blocked': getattr(account, 'account_blocked', False),
                'created_at': getattr(account, 'created_at', None),
                'trade_suspended_by_user': getattr(account, 'trade_suspended_by_user', False),
                'multiplier': getattr(account, 'multiplier', 1),
                'shorting_enabled': getattr(account, 'shorting_enabled', False),
                'equity': safe_float(getattr(account, 'equity', 0)),
                'last_equity': safe_float(getattr(account, 'last_equity', 0)),
                'long_market_value': safe_float(getattr(account, 'long_market_value', 0)),
                'short_market_value': safe_float(getattr(account, 'short_market_value', 0)),
                'initial_margin': safe_float(getattr(account, 'initial_margin', 0)),
                'maintenance_margin': safe_float(getattr(account, 'maintenance_margin', 0)),
                'last_maintenance_margin': safe_float(getattr(account, 'last_maintenance_margin', 0)),
                'sma': safe_float(getattr(account, 'sma', 0)),
                'daytrade_count': getattr(account, 'daytrade_count', 0)
            }
            
            # Handle optional attributes that might not exist
            try:
                account_info['transfer_out'] = safe_float(getattr(account, 'transfer_out', 0))
            except AttributeError:
                account_info['transfer_out'] = 0.0
                
            try:
                account_info['pending_transfer_out'] = safe_float(getattr(account, 'pending_transfer_out', 0))
            except AttributeError:
                account_info['pending_transfer_out'] = 0.0
            
            logger.info(f"Successfully retrieved account info for account {account_info['id']}")
            
            # Cache the result
            self._set_cached_data('account_info', account_info)
            return account_info
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error fetching account info: {error_msg}")
            
            # Check if it's an authentication error
            if "forbidden" in error_msg.lower() or "403" in error_msg:
                logger.error("🔐 Authentication Error: Your Alpaca API credentials appear to be invalid or expired.")
                logger.error("   Please regenerate your API keys in the Alpaca dashboard and update your credentials.")
                logger.error("   Visit: https://app.alpaca.markets/ -> Account -> API Keys")
            elif "unauthorized" in error_msg.lower() or "401" in error_msg:
                logger.error("🔐 Unauthorized Error: Check your API key and secret key.")
            elif "rate limit" in error_msg.lower():
                logger.error("⏱️  Rate limit exceeded. Please wait before making more requests.")
            
            return {}
    
    def get_positions(self) -> List[Dict]:
        """Get current positions from Alpaca.
        
        Returns:
            List of dictionaries containing position information
        """
        # Check cache first
        cached_data = self._get_cached_data('positions')
        if cached_data:
            return cached_data
            
        try:
            positions = self.trading_client.get_all_positions()
            
            position_list = []
            for position in positions:
                position_data = {
                    'symbol': position.symbol,
                    'qty': float(position.qty),
                    'side': position.side,
                    'market_value': float(position.market_value),
                    'cost_basis': float(position.cost_basis),
                    'unrealized_pl': float(position.unrealized_pl),
                    'unrealized_plpc': float(position.unrealized_plpc),
                    'unrealized_intraday_pl': float(position.unrealized_intraday_pl),
                    'unrealized_intraday_plpc': float(position.unrealized_intraday_plpc),
                    'current_price': float(position.current_price),
                    'lastday_price': float(position.lastday_price),
                    'change_today': float(position.change_today)
                }
                position_list.append(position_data)
            
            # Cache the result
            self._set_cached_data('positions', position_list)
            return position_list
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error fetching positions: {error_msg}")
            
            # Check if it's an authentication error
            if "forbidden" in error_msg.lower() or "403" in error_msg:
                logger.error("🔐 Authentication Error: Your Alpaca API credentials appear to be invalid or expired.")
                logger.error("   Please regenerate your API keys in the Alpaca dashboard and update your credentials.")
                logger.error("   Visit: https://app.alpaca.markets/ -> Account -> API Keys")
            elif "unauthorized" in error_msg.lower() or "401" in error_msg:
                logger.error("🔐 Unauthorized Error: Check your API key and secret key.")
            elif "rate limit" in error_msg.lower():
                logger.error("⏱️  Rate limit exceeded. Please wait before making more requests.")
            
            return []
    
    def get_orders(self, status: str = "all") -> List[Dict]:
        """Get orders from Alpaca.
        
        Args:
            status: Order status filter ("all", "open", "closed")
            
        Returns:
            List of dictionaries containing order information
        """
        # Check cache first
        cache_key = f'orders_{status}'
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            logger.info(f"Returning cached orders for status: {status}")
            return cached_data
            
        try:
            logger.info(f"Attempting to fetch orders with status: {status}")
            
            # Simplified request construction, removing date filters for now.
            # The API defaults to the last 90 days.
            request_params = GetOrdersRequest(limit=500)

            if status == "open":
                request_params.status = QueryOrderStatus.OPEN
                logger.info("Fetching open orders.")
            elif status == "closed":
                request_params.status = QueryOrderStatus.CLOSED
                logger.info("Fetching closed orders.")
            else: # "all"
                request_params.status = QueryOrderStatus.ALL
                logger.info("Fetching all orders.")
            
            logger.info(f"Calling trading_client.get_orders with params: {request_params}")
            orders = self.trading_client.get_orders(filter=request_params)
            logger.info(f"Received response from get_orders: {type(orders)} with length: {len(orders) if hasattr(orders, '__len__') else 'unknown'}")
            
            order_list = []
            for order in orders:
                try:
                    order_data = {
                        'id': order.id,
                        'symbol': order.symbol,
                        'qty': float(order.qty) if order.qty else 0,
                        'side': order.side,
                        'type': order.type,
                        'time_in_force': order.time_in_force,
                        'status': order.status,
                        'filled_at': order.filled_at,
                        'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else 0,
                        'filled_qty': float(order.filled_qty) if order.filled_qty else 0,
                        'submitted_at': order.submitted_at,
                        'limit_price': float(order.limit_price) if order.limit_price else 0,
                        'stop_price': float(order.stop_price) if order.stop_price else 0
                    }
                    order_list.append(order_data)
                except Exception as e:
                    logger.warning(f"Error processing order {getattr(order, 'id', 'unknown')}: {str(e)}")
                    continue
            
            logger.info(f"Successfully retrieved {len(order_list)} orders with status {status}")
            
            # Cache the result
            self._set_cached_data(cache_key, order_list)
            return order_list
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error fetching orders: {error_msg}")
            logger.error(f"Exception type: {type(e).__name__}")
            
            # Check if it's an authentication error
            if "forbidden" in error_msg.lower() or "403" in error_msg:
                logger.error("🔐 Authentication Error: Your Alpaca API credentials appear to be invalid or expired.")
                logger.error("   Please regenerate your API keys in the Alpaca dashboard and update your credentials.")
                logger.error("   Visit: https://app.alpaca.markets/ -> Account -> API Keys")
            elif "unauthorized" in error_msg.lower() or "401" in error_msg:
                logger.error("🔐 Unauthorized Error: Check your API key and secret key.")
            elif "rate limit" in error_msg.lower():
                logger.error("⏱️  Rate limit exceeded. Please wait before making more requests.")
            else:
                logger.error("Full traceback:")
                logger.error(traceback.format_exc())
            
            return []
    
    def calculate_portfolio_metrics(self) -> Dict:
        """Calculate comprehensive portfolio metrics.
        
        Returns:
            Dict containing portfolio metrics
        """
        # Check cache first
        cached_data = self._get_cached_data('portfolio_metrics')
        if cached_data:
            logger.info("Returning cached portfolio metrics")
            return cached_data
            
        try:
            account = self.get_account_info()
            positions = self.get_positions()
            
            if not account:
                return {}
            
            # Basic metrics
            total_value = account.get('portfolio_value', 0)
            cash = account.get('cash', 0)
            equity = account.get('equity', 0)
            buying_power = account.get('buying_power', 0)
            
            # Position metrics
            total_positions = len(positions)
            total_market_value = sum(pos.get('market_value', 0) for pos in positions)
            total_unrealized_pl = sum(pos.get('unrealized_pl', 0) for pos in positions)
            
            # Calculate daily P&L (simplified - you might want to store historical data)
            daily_pnl = total_unrealized_pl  # This is simplified
            
            # Calculate win rate from recent orders
            recent_orders = self.get_orders("closed")
            if recent_orders:
                profitable_trades = sum(1 for order in recent_orders 
                                      if order.get('filled_avg_price', 0) > 0)
                win_rate = (profitable_trades / len(recent_orders)) * 100
            else:
                win_rate = 0
            
            # Risk metrics
            margin_used = account.get('initial_margin', 0)
            margin_ratio = (margin_used / total_value * 100) if total_value > 0 else 0
            
            # Calculate average trade size
            if recent_orders:
                avg_trade_size = sum(order.get('filled_qty', 0) * order.get('filled_avg_price', 0) 
                                   for order in recent_orders) / len(recent_orders)
            else:
                avg_trade_size = 0
            
            metrics_data = {
                'total_value': total_value,
                'cash': cash,
                'equity': equity,
                'buying_power': buying_power,
                'total_positions': total_positions,
                'total_market_value': total_market_value,
                'total_unrealized_pl': total_unrealized_pl,
                'daily_pnl': daily_pnl,
                'win_rate': win_rate,
                'margin_used': margin_used,
                'margin_ratio': margin_ratio,
                'avg_trade_size': avg_trade_size,
                'account_status': account.get('status', 'unknown'),
                'pattern_day_trader': account.get('pattern_day_trader', False),
                'trading_blocked': account.get('trading_blocked', False)
            }
            
            # Cache the result
            self._set_cached_data('portfolio_metrics', metrics_data)
            return metrics_data
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {str(e)}")
            return {}
    
    def get_position_performance(self, symbol: str, days: int = 30) -> Dict:
        """Get performance data for a specific position.
        
        Args:
            symbol: Stock symbol
            days: Number of days to look back
            
        Returns:
            Dict containing performance metrics
        """
        try:
            # Get historical data for the symbol
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=start_date,
                end=end_date
            )
            
            bars = self.data_client.get_stock_bars(request_params)
            
            if symbol not in bars or not bars[symbol]:
                return {}
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'timestamp': bar.timestamp,
                'open': bar.open,
                'high': bar.high,
                'low': bar.low,
                'close': bar.close,
                'volume': bar.volume
            } for bar in bars[symbol]])
            
            if df.empty:
                return {}
            
            # Calculate performance metrics
            current_price = df['close'].iloc[-1]
            start_price = df['close'].iloc[0]
            price_change = current_price - start_price
            price_change_pct = (price_change / start_price) * 100
            
            # Calculate volatility
            daily_returns = df['close'].pct_change().dropna()
            volatility = daily_returns.std() * (252 ** 0.5) * 100  # Annualized volatility
            
            # Get position info
            positions = self.get_positions()
            position = next((pos for pos in positions if pos['symbol'] == symbol), None)
            
            if position:
                position_value = position['market_value']
                unrealized_pl = position['unrealized_pl']
                unrealized_pl_pct = position['unrealized_plpc'] * 100
            else:
                position_value = 0
                unrealized_pl = 0
                unrealized_pl_pct = 0
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'start_price': start_price,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'volatility': volatility,
                'position_value': position_value,
                'unrealized_pl': unrealized_pl,
                'unrealized_pl_pct': unrealized_pl_pct,
                'volume_avg': df['volume'].mean(),
                'high_30d': df['high'].max(),
                'low_30d': df['low'].min()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance for {symbol}: {str(e)}")
            return {}
    
    def get_portfolio_summary(self) -> Dict:
        """Get a comprehensive portfolio summary for the dashboard.
        
        Returns:
            Dict containing portfolio summary data
        """
        # Check cache first
        cached_data = self._get_cached_data('portfolio_summary')
        if cached_data:
            logger.info("Returning cached portfolio summary")
            return cached_data
            
        try:
            metrics = self.calculate_portfolio_metrics()
            positions = self.get_positions()
            recent_orders = self.get_orders("closed")[:10]  # Last 10 orders
            
            # Calculate additional metrics
            if positions:
                # Top positions by value
                top_positions = sorted(positions, key=lambda x: x.get('market_value', 0), reverse=True)[:5]
                
                # Calculate sector allocation (simplified)
                total_position_value = sum(pos.get('market_value', 0) for pos in positions)
                position_allocation = []
                
                for pos in positions:
                    allocation_pct = (pos.get('market_value', 0) / total_position_value * 100) if total_position_value > 0 else 0
                    position_allocation.append({
                        'symbol': pos['symbol'],
                        'allocation_pct': allocation_pct,
                        'market_value': pos['market_value'],
                        'unrealized_pl': pos['unrealized_pl']
                    })
            else:
                top_positions = []
                position_allocation = []
            
            # Format recent activity
            recent_activity = []
            for order in recent_orders:
                if order.get('filled_at'):
                    activity = {
                        'action': order['side'].upper(),
                        'symbol': order['symbol'],
                        'shares': order['filled_qty'],
                        'price': order['filled_avg_price'],
                        'time': order['filled_at'].strftime('%I:%M %p') if order['filled_at'] else 'N/A'
                    }
                    recent_activity.append(activity)
            
            summary_data = {
                'metrics': metrics,
                'positions': positions,
                'top_positions': top_positions,
                'position_allocation': position_allocation,
                'recent_activity': recent_activity,
                'total_positions': len(positions),
                'last_updated': datetime.now().isoformat()
            }
            
            # Cache the result
            self._set_cached_data('portfolio_summary', summary_data)
            return summary_data
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {str(e)}")
            return {}


# Example usage and testing
if __name__ == "__main__":
    try:
        portfolio_manager = PortfolioManager()
        
        # Test account info
        print("Account Info:")
        account_info = portfolio_manager.get_account_info()
        print(f"Portfolio Value: ${account_info.get('portfolio_value', 0):,.2f}")
        print(f"Cash: ${account_info.get('cash', 0):,.2f}")
        print(f"Buying Power: ${account_info.get('buying_power', 0):,.2f}")
        
        # Test positions
        print("\nPositions:")
        positions = portfolio_manager.get_positions()
        for pos in positions:
            print(f"{pos['symbol']}: {pos['qty']} shares @ ${pos['current_price']:.2f}")
        
        # Test portfolio metrics
        print("\nPortfolio Metrics:")
        metrics = portfolio_manager.calculate_portfolio_metrics()
        print(f"Total Value: ${metrics.get('total_value', 0):,.2f}")
        print(f"Daily P&L: ${metrics.get('daily_pnl', 0):,.2f}")
        print(f"Win Rate: {metrics.get('win_rate', 0):.1f}%")
        
    except Exception as e:
        print(f"Error: {str(e)}") 