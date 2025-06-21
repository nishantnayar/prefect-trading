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
        api_key = Secret.load("alpaca-api-key").get()
        secret_key = Secret.load("alpaca-secret-key").get()
        
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
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

            logger.info(f"Fetching hourly data for {symbols} from {start_date} to {end_date}")
            
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
            
            logger.info(f"Successfully downloaded hourly data for {symbols}")
            return data_dict

        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            raise

    def store_historical_data(self, data_dict: Dict[str, pd.DataFrame]):
        """
        Store historical data in the database.
        
        Args:
            data_dict: Dictionary of DataFrames with historical data for each symbol
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
            
            logger.info("Successfully stored all historical data")
            
        except Exception as e:
            logger.error(f"Error storing historical data: {str(e)}")
            raise

    def run_historical_load(self, days_back: int = None):
        """
        Run a historical data load for all active symbols.
        
        Args:
            days_back: Number of days of historical data to load (not used, defaults to 30 days)
        """
        try:
            # Get active symbols
            symbols = self.symbol_manager.get_active_symbols()
            if not symbols:
                logger.error("No active symbols found")
                return

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)  # Default to 30 days
            
            # Get and store historical data
            data_dict = self.get_historical_data(
                symbols=symbols,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            
            if data_dict:
                self.store_historical_data(data_dict)
            else:
                logger.warning("No data retrieved for any symbols")
            
        except Exception as e:
            logger.error(f"Error in historical data load: {str(e)}")
            raise


if __name__ == "__main__":
    # Example usage
    loader = AlpacaDataLoader()
    
    # Load historical data for all active symbols
    loader.run_historical_load()
    
    # # Or load specific symbols for a custom date range
    # symbols = ["AAPL", "MSFT", "GOOGL"]
    # data = loader.get_historical_data(
    #     symbols=symbols,
    #     start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
    #     end_date=datetime.now().strftime('%Y-%m-%d')
    # )
    
    # if data:
    #     # Store the data
    #     loader.store_historical_data(data)
    #
    #     # Print sample data
    #     for symbol, df in data.items():
    #         print(f"\nHourly data for {symbol}:")
    #         print(df.head())