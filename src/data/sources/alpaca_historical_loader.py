"""
Alpaca data loader for historical and real-time market data.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import pandas as pd
from loguru import logger
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from prefect.blocks.system import Secret

from src.database.database_connectivity import DatabaseConnectivity
from src.data.sources.symbol_manager import SymbolManager

class AlpacaDataLoader:
    def __init__(self):
        self.db = DatabaseConnectivity()
        self.symbol_manager = SymbolManager()
        
        # Load Alpaca credentials from Prefect secrets
        api_key_block = Secret.load("alpaca-api-key")
        secret_key_block = Secret.load("alpaca-secret-key")
        
        api_key = api_key_block.get()
        secret_key = secret_key_block.get()
        
        # Initialize Alpaca client
        self.client = StockHistoricalDataClient(
            api_key=api_key,
            secret_key=secret_key
        )

    def get_historical_data(
        self,
        symbols: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeframe: TimeFrame = TimeFrame.Hour
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical data for given symbols.
        
        Args:
            symbols: List of stock symbols
            start_date: Start date in 'YYYY-MM-DD' format. If None, defaults to 30 days ago
            end_date: End date in 'YYYY-MM-DD' format. If None, defaults to today
            timeframe: Data timeframe (Hour by default)
        
        Returns:
            Dictionary of DataFrames with historical data for each symbol
        """
        try:
            # Set default dates if not provided
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                # For 1-minute data, limit to 7 days due to Alpaca API restrictions
                if timeframe == TimeFrame.Minute:
                    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                    logger.info("Using 7-day limit for 1-minute data due to Alpaca API restrictions")
                else:
                    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

            timeframe_name = "1-minute" if timeframe == TimeFrame.Minute else "hourly"
            logger.info(f"Fetching {timeframe_name} data for {symbols} from {start_date} to {end_date}")
            
            # Create request parameters
            request_params = StockBarsRequest(
                symbol_or_symbols=symbols,
                timeframe=timeframe,
                start=datetime.strptime(start_date, '%Y-%m-%d'),
                end=datetime.strptime(end_date, '%Y-%m-%d')
            )
            
            # Get the data
            bars = self.client.get_stock_bars(request_params)
            
            # Convert to dictionary of DataFrames
            data_dict = {}
            for symbol in symbols:
                try:
                    # Get bars for the symbol
                    symbol_bars = bars[symbol]
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
                    else:
                        logger.warning(f"No bars found for symbol {symbol}")
                except KeyError:
                    logger.warning(f"Symbol {symbol} not found in response")
                except Exception as e:
                    logger.error(f"Error processing symbol {symbol}: {str(e)}")
            
            logger.info(f"Successfully downloaded {timeframe_name} data for {symbols}")
            return data_dict

        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            raise

    def store_historical_data(self, data_dict: Dict[str, pd.DataFrame], table_name: str = "market_data"):
        """
        Store historical data in the database.
        
        Args:
            data_dict: Dictionary of DataFrames with historical data for each symbol
            table_name: Table to store data in ('market_data' or 'market_data_historical')
        """
        try:
            with self.db.get_session() as cursor:
                for symbol, df in data_dict.items():
                    # Insert data
                    for _, row in df.iterrows():
                        insert_query = f"""
                            INSERT INTO {table_name} 
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
                    
                    logger.info(f"Stored data for {symbol} in {table_name}")
            
            logger.info(f"Successfully stored all historical data in {table_name}")
            
        except Exception as e:
            logger.error(f"Error storing historical data: {str(e)}")
            raise

    def run_historical_load(self, days_back: int = None, timeframe: TimeFrame = TimeFrame.Hour):
        """
        Run a historical data load for all active symbols.
        
        Args:
            days_back: Number of days of historical data to load (not used, defaults to 30 days for hourly, 7 for minute)
            timeframe: Data timeframe (Hour by default, Minute for 1-minute data)
        """
        try:
            # Get active symbols
            symbols = self.symbol_manager.get_active_symbols()
            if not symbols:
                logger.error("No active symbols found")
                return

            # Calculate date range based on timeframe
            end_date = datetime.now()
            if timeframe == TimeFrame.Minute:
                start_date = end_date - timedelta(days=7)  # 7 days for 1-minute data
                table_name = "market_data_historical"
                logger.info("Loading 1-minute historical data (7-day limit due to Alpaca API restrictions)")
            else:
                start_date = end_date - timedelta(days=30)  # 30 days for hourly data
                table_name = "market_data"
                logger.info("Loading hourly historical data")
            
            # Get and store historical data
            data_dict = self.get_historical_data(
                symbols=symbols,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                timeframe=timeframe
            )
            
            if data_dict:
                self.store_historical_data(data_dict, table_name)
            else:
                logger.warning("No data retrieved for any symbols")
            
        except Exception as e:
            logger.error(f"Error in historical data load: {str(e)}")
            raise

    def load_1min_historical_data(self, symbols: List[str] = None, days_back: int = 7):
        """
        Load 1-minute historical data for specified symbols or all active symbols.
        
        Args:
            symbols: List of symbols to load data for. If None, loads all active symbols
            days_back: Number of days to look back (max 7 due to Alpaca API restrictions)
        """
        try:
            # Limit days_back to 7 for 1-minute data
            if days_back > 7:
                logger.warning(f"Limiting days_back to 7 for 1-minute data (Alpaca API restriction). Requested: {days_back}")
                days_back = 7
            
            # Get symbols if not provided
            if symbols is None:
                symbols = self.symbol_manager.get_active_symbols()
                if not symbols:
                    logger.error("No active symbols found")
                    return
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            logger.info(f"Loading 1-minute historical data for {len(symbols)} symbols from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
            # Get and store 1-minute data
            data_dict = self.get_historical_data(
                symbols=symbols,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                timeframe=TimeFrame.Minute
            )
            
            if data_dict:
                self.store_historical_data(data_dict, "market_data_historical")
                logger.info(f"Successfully loaded 1-minute data for {list(data_dict.keys())}")
            else:
                logger.warning("No 1-minute data retrieved for any symbols")
            
        except Exception as e:
            logger.error(f"Error loading 1-minute historical data: {str(e)}")
            raise

    def load_all_symbols_historical_data(self, timeframe: TimeFrame = TimeFrame.Hour, days_back: int = None):
        """
        Load historical data for all symbols in the symbols table.
        
        Args:
            timeframe: Data timeframe (Hour by default, Minute for 1-minute data)
            days_back: Number of days to look back (max 7 for minute data)
        """
        try:
            # Get all symbols from database
            with self.db.get_session() as cursor:
                cursor.execute("SELECT symbol FROM symbols WHERE is_active = true")
                symbols = [row[0] for row in cursor.fetchall()]
            
            if not symbols:
                logger.error("No active symbols found in database")
                return
            
            logger.info(f"Found {len(symbols)} active symbols in database")
            
            # Determine table and date range based on timeframe
            if timeframe == TimeFrame.Minute:
                if days_back is None or days_back > 7:
                    days_back = 7
                    logger.info("Using 7-day limit for 1-minute data due to Alpaca API restrictions")
                table_name = "market_data_historical"
            else:
                if days_back is None:
                    days_back = 30
                table_name = "market_data"
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            logger.info(f"Loading {timeframe} data for {len(symbols)} symbols from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
            # Process symbols in batches to avoid overwhelming the API
            batch_size = 10
            all_data = {}
            
            for i in range(0, len(symbols), batch_size):
                batch_symbols = symbols[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(symbols) + batch_size - 1)//batch_size}: {batch_symbols}")
                
                try:
                    batch_data = self.get_historical_data(
                        symbols=batch_symbols,
                        start_date=start_date.strftime('%Y-%m-%d'),
                        end_date=end_date.strftime('%Y-%m-%d'),
                        timeframe=timeframe
                    )
                    all_data.update(batch_data)
                    
                    # Store batch data immediately
                    if batch_data:
                        self.store_historical_data(batch_data, table_name)
                    
                    # Small delay between batches to respect rate limits
                    import time
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing batch {batch_symbols}: {str(e)}")
                    continue
            
            logger.info(f"Completed loading {timeframe} data. Successfully processed {len(all_data)} symbols")
            
        except Exception as e:
            logger.error(f"Error loading all symbols historical data: {str(e)}")
            raise


if __name__ == "__main__":
    # Example usage
    loader = AlpacaDataLoader()
    
    # Load hourly historical data (stored in market_data table)
    # print("Loading hourly historical data...")
    #loader.run_historical_load(timeframe=TimeFrame.Hour)
    
    # Load 1-minute historical data (stored in market_data_historical table)
    print("\nLoading 1-minute historical data...")
    loader.load_1min_historical_data()