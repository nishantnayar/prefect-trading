"""
Alpaca daily data loader for collecting previous day's market data.
"""
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
from loguru import logger
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from prefect.blocks.system import Secret
import pytz

from src.database.database_connectivity import DatabaseConnectivity
from src.data.sources.symbol_manager import SymbolManager


class AlpacaDailyLoader:
    def __init__(self):
        self.db = DatabaseConnectivity()
        self.symbol_manager = SymbolManager()
        
        # Load Alpaca credentials from Prefect secrets
        try:
            api_key = Secret.load("alpaca-api-key").get()
            secret_key = Secret.load("alpaca-secret-key").get()
            logger.info("Successfully loaded Alpaca credentials")
            # Log first few characters of API key for verification
            logger.info(f"API Key starts with: {api_key[:4]}...")
            self.is_paper_trading = api_key.startswith("PK")
            logger.info(f"Using {'paper' if self.is_paper_trading else 'live'} trading account")
        except Exception as e:
            logger.error(f"Failed to load Alpaca credentials: {str(e)}")
            raise
        
        # Initialize Alpaca client
        try:
            self.client = StockHistoricalDataClient(
                api_key=api_key,
                secret_key=secret_key
            )
            logger.info("Successfully initialized Alpaca client")
        except Exception as e:
            logger.error(f"Failed to initialize Alpaca client: {str(e)}")
            raise

    def test_api_connection(self, symbol: str = "AAPL") -> bool:
        """
        Test the API connection by fetching a small amount of data for a single symbol.
        
        Args:
            symbol: Symbol to test with (default: AAPL)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get data for the last hour
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=1)
            
            logger.info(f"Testing API connection with {symbol} from {start_date} to {end_date}")
            
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Minute,
                start=start_date,
                end=end_date
            )
            
            bars = self.client.get_stock_bars(request_params)
            
            if symbol in bars and bars[symbol]:
                logger.info(f"Successfully retrieved {len(bars[symbol])} bars for {symbol}")
                return True
            else:
                logger.warning(f"No data returned for {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"API test failed: {str(e)}")
            return False

    def get_previous_day_data(
        self,
        symbols: List[str],
        timeframe: TimeFrame = TimeFrame.Hour
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch previous day's data for given symbols.
        
        Args:
            symbols: List of stock symbols
            timeframe: Data timeframe (Hour by default)
        
        Returns:
            Dictionary of DataFrames with historical data for each symbol
        """
        try:
            # Set up Eastern timezone
            eastern = pytz.timezone("US/Eastern")
            current_time = datetime.now(eastern)
            
            # For paper trading, we need to use historical dates
            if self.is_paper_trading:
                # Set end date to current hour in ET
                end_date = current_time.replace(minute=0, second=0, microsecond=0)
                
                # If before market open (9:30 AM ET), get previous day's data
                if end_date.hour < 9 or (end_date.hour == 9 and end_date.minute < 30):
                    end_date = end_date - timedelta(days=1)
                    end_date = end_date.replace(hour=16, minute=0, second=0)  # Previous day market close
                    start_date = end_date.replace(hour=9, minute=30, second=0)  # Previous day market open
                else:
                    # If during market hours, get data from market open
                    start_date = end_date.replace(hour=9, minute=30, second=0)
                    if start_date > end_date:  # If we're in the same day
                        start_date = start_date - timedelta(days=1)  # Use previous day's market open
                
                logger.info(f"Using paper trading date range: {start_date} to {end_date}")
            else:
                # For live trading, use current market hours
                end_date = current_time.replace(minute=0, second=0, microsecond=0)
                start_date = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
                if current_time.hour < 9 or (current_time.hour == 9 and current_time.minute < 30):
                    # If before market open, get previous day's data
                    start_date = start_date - timedelta(days=1)
                    end_date = start_date.replace(hour=16, minute=0, second=0)

            logger.info(f"Current Eastern time: {current_time}")
            logger.info(f"Fetching {timeframe} data for {symbols} from {start_date} to {end_date}")
            
            # Create request parameters
            request_params = StockBarsRequest(
                symbol_or_symbols=symbols,
                timeframe=timeframe,
                start=start_date,
                end=end_date
            )
            
            # Get the data
            try:
                logger.info("Sending request to Alpaca API...")
                bars = self.client.get_stock_bars(request_params)
                logger.info("Successfully received response from Alpaca API")
                
                # Convert to dictionary of DataFrames
                data_dict = {}
                for symbol in symbols:
                    try:
                        # Get bars for the symbol
                        symbol_bars = bars.data.get(symbol, [])
                        if symbol_bars:
                            # Convert bars to DataFrame
                            df = pd.DataFrame([{
                                'timestamp': bar.timestamp,
                                'open': bar.open,
                                'high': bar.high,
                                'low': bar.low,
                                'close': bar.close,
                                'volume': bar.volume
                            } for bar in symbol_bars])
                            data_dict[symbol] = df
                            logger.info(f"Retrieved {len(df)} bars for {symbol}")
                            logger.info(f"First bar timestamp: {df['timestamp'].min()}")
                            logger.info(f"Last bar timestamp: {df['timestamp'].max()}")
                        else:
                            logger.warning(f"No bars found for symbol {symbol} - This might be due to market being closed or symbol not trading")
                    except Exception as e:
                        logger.error(f"Error processing symbol {symbol}: {str(e)}")
                
                if data_dict:
                    logger.info(f"Successfully downloaded data for {list(data_dict.keys())}")
                else:
                    logger.warning("No data retrieved for any symbols - This might be due to market being closed")
                return data_dict

            except Exception as e:
                logger.error(f"Failed to get data from Alpaca API: {str(e)}")
                raise

        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            raise

    def store_market_data(self, data_dict: Dict[str, pd.DataFrame]):
        """
        Store market data in the database.
        
        Args:
            data_dict: Dictionary of DataFrames with market data for each symbol
        """
        try:
            with self.db.get_session() as cursor:
                for symbol, df in data_dict.items():
                    # Insert data
                    for _, row in df.iterrows():
                        insert_query = """
                            INSERT INTO market_data 
                            (symbol, timestamp, open, high, low, close, volume)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (symbol, timestamp) DO UPDATE SET
                            open = EXCLUDED.open,
                            high = EXCLUDED.high,
                            low = EXCLUDED.low,
                            close = EXCLUDED.close,
                            volume = EXCLUDED.volume
                        """
                        cursor.execute(insert_query, (
                            symbol,
                            row['timestamp'],
                            float(row['open']),
                            float(row['high']),
                            float(row['low']),
                            float(row['close']),
                            int(row['volume'])
                        ))
                    
                    logger.info(f"Stored data for {symbol}")
            
            logger.info("Successfully stored all market data")
            
        except Exception as e:
            logger.error(f"Error storing market data: {str(e)}")
            raise

    def run_daily_load(self):
        """
        Run a daily data load for all active symbols.
        This method is designed to be called once per day to collect previous day's data.
        """
        try:
            # Get active symbols
            symbols = self.symbol_manager.get_active_symbols()
            if not symbols:
                logger.error("No active symbols found")
                return

            logger.info(f"Found {len(symbols)} active symbols: {symbols}")

            # Get and store previous day's data
            data_dict = self.get_previous_day_data(symbols=symbols)
            
            if data_dict:
                self.store_market_data(data_dict)
            else:
                logger.warning("No data retrieved for any symbols")
            
        except Exception as e:
            logger.error(f"Error in daily data load: {str(e)}")
            raise


if __name__ == "__main__":
    # Example usage
    loader = AlpacaDailyLoader()
    
    # Load previous day's data for all active symbols
    loader.run_daily_load()
    
    # # Or load specific symbols
    # symbols = ["AAPL"]
    # data = loader.get_previous_day_data(symbols=symbols)
    #
    # if data:
    #     # Store the data
    #     loader.store_market_data(data)
    #
    #     # Print sample data
    #     for symbol, df in data.items():
    #         print(f"\nData for {symbol}:")
    #         print(df.head())