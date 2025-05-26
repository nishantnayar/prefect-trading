"""
Yahoo Finance data loader for company information.
"""
import yfinance as yf
import pandas as pd
import time
from loguru import logger
from sqlalchemy import text
import random
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from src.database.database_connectivity import DatabaseConnectivity
from src.data.symbol_manager import SymbolManager


class YahooFinanceDataLoader:
    def __init__(self):
        self.db = DatabaseConnectivity()
        self.rate_limit_delay = 2  # Base delay between requests in seconds
        self.max_retries = 3  # Maximum number of retries for failed requests
        self.raw_data = []  # List to store raw ticker info
        self.columns_printed = False  # Flag to track if columns have been printed
        self.logger = logger  # Use loguru logger instead of Prefect

    def _get_ticker_info_with_retry(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get ticker info with retry logic and rate limiting."""
        for attempt in range(self.max_retries):
            try:
                # Add random jitter to avoid synchronized requests
                jitter = random.uniform(0.5, 1.5)
                time.sleep(self.rate_limit_delay * jitter)

                # Get ticker info
                ticker = yf.Ticker(symbol)
                ticker_info = ticker.info

                # Store raw data for inspection
                ticker_info['symbol'] = symbol
                self.raw_data.append(ticker_info)

                # Extract company officers data before removing it
                company_officers = ticker_info.get('companyOfficers', [])
                if company_officers:
                    self.store_company_officers(symbol, company_officers)

                # Remove fields that are not in our database schema
                ticker_info.pop('companyOfficers', None)
                ticker_info.pop('underlyingSymbol', None)  # Remove underlyingSymbol field
                ticker_info.pop('firstTradeDateEpochUtc', None)  # Remove firstTradeDateEpochUtc field
                ticker_info.pop('timeZoneFullName', None)  # Remove timeZoneFullName field
                ticker_info.pop('timeZoneShortName', None)  # Remove timeZoneShortName field
                ticker_info.pop('gmtOffSetMilliseconds', None)  # Remove gmtOffSetMilliseconds field
                ticker_info.pop('uuid', None)  # Remove uuid field
                ticker_info.pop('industrySymbol', None)  # Remove industrySymbol field

                # Add symbol to the info dictionary
                ticker_info['symbol'] = symbol

                # Convert any non-serializable values to strings
                for key, value in ticker_info.items():
                    if isinstance(value, (dict, list)):
                        ticker_info[key] = str(value)

                return ticker_info

            except Exception as e:
                if "429" in str(e):  # Rate limit error
                    wait_time = (attempt + 1) * 5  # Exponential backoff
                    self.logger.warning(f"Rate limited for {symbol}, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Error loading data for {symbol} (attempt {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt == self.max_retries - 1:
                    self.logger.error(f"Failed to get data for {symbol} after {self.max_retries} attempts")
                    return None

        return None

    def store_company_officers(self, symbol: str, officers: List[Dict[str, Any]]):
        """Store company officers information in the database."""
        if not officers:
            return

        try:
            with self.db.get_session() as cursor:
                # First, delete existing officers for this symbol
                delete_stmt = "DELETE FROM yahoo_company_officers WHERE symbol = %s"
                cursor.execute(delete_stmt, (symbol,))
                
                # Insert new officers
                for officer in officers:
                    insert_stmt = """
                        INSERT INTO yahoo_company_officers 
                        (symbol, name, title, age, year_born, fiscal_year, total_pay, exercised_value, unexercised_value)
                        VALUES 
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(insert_stmt, (
                        symbol,
                        officer.get('name'),
                        officer.get('title'),
                        officer.get('age'),
                        officer.get('yearBorn'),
                        officer.get('fiscalYear'),
                        officer.get('totalPay'),
                        officer.get('exercisedValue'),
                        officer.get('unexercisedValue')
                    ))
            
            self.logger.info(f"Stored {len(officers)} company officers for {symbol}")
            
        except Exception as e:
            self.logger.error(f"Error storing company officers for {symbol}: {e}")
            raise

    def load_ticker_info_chunk(self, stock_symbols):
        # List to store processed data for the current chunk
        ticker_info_list = []

        for symbol in stock_symbols:
            info = self._get_ticker_info_with_retry(symbol)
            if info:
                ticker_info_list.append(info)
                self.logger.info(f"Successfully received data for {symbol}")

        return ticker_info_list

    def store_company_info(self, company_info_list):
        """Store company information in the database."""
        if not company_info_list:
            return

        try:
            with self.db.get_session() as cursor:
                for info in company_info_list:
                    try:
                        # Create dynamic SQL statement based on available fields
                        fields = list(info.keys())
                        # Quote fields that start with numbers or contain uppercase letters
                        quoted_fields = []
                        for field in fields:
                            if field[0].isdigit() or any(c.isupper() for c in field):
                                quoted_fields.append(f'"{field}"')
                            else:
                                quoted_fields.append(field)
                        placeholders = ['%s'] * len(fields)
                        
                        # Create the INSERT statement
                        insert_stmt = f"""
                            INSERT INTO yahoo_company_info ({', '.join(quoted_fields)})
                            VALUES ({', '.join(placeholders)})
                            ON CONFLICT (symbol) DO UPDATE SET
                        """
                        
                        # Create the UPDATE part of the statement
                        update_parts = []
                        for field in fields:
                            if field != 'symbol':  # Skip symbol in UPDATE part
                                quoted_field = f'"{field}"' if field[0].isdigit() or any(c.isupper() for c in field) else field
                                update_parts.append(f"{quoted_field} = COALESCE(EXCLUDED.{quoted_field}, yahoo_company_info.{quoted_field})")
                        
                        insert_stmt += ', '.join(update_parts)
                        insert_stmt += ", updated_at = CURRENT_TIMESTAMP"
                        
                        # Execute the statement
                        cursor.execute(insert_stmt, [info[field] for field in fields])
                        self.logger.info(f"Stored company info for {info['symbol']}")
                        
                    except Exception as e:
                        self.logger.error(f"Error storing company info for {info['symbol']}: {e}")
                        raise

            self.logger.info("Successfully committed company information to database")
        except Exception as e:
            self.logger.error(f"Error in database transaction: {e}")
            raise

    def load_ticker_info(self, stock_symbols):
        # Process stocks in smaller chunks to avoid rate limits
        chunk_size = 50  # Reduced from 200 to 50
        for i in range(0, len(stock_symbols), chunk_size):
            chunk_symbols = stock_symbols[i:i + chunk_size]
            self.logger.info(f"Processing chunk {i // chunk_size + 1} containing {len(chunk_symbols)} symbols...")

            # Load ticker info for the current chunk
            company_info_list = self.load_ticker_info_chunk(chunk_symbols)

            # Store the company information
            if company_info_list:
                self.store_company_info(company_info_list)

            # Sleep between chunks to respect rate limits
            if i + chunk_size < len(stock_symbols):
                sleep_time = 30  # 30 seconds between chunks
                self.logger.info(f"Sleeping for {sleep_time} seconds before processing the next chunk...")
                time.sleep(sleep_time)

    def run(self):
        # Get active symbols from SymbolManager
        symbol_manager = SymbolManager()
        stock_symbols = symbol_manager.get_active_symbols()

        if not stock_symbols:
            self.logger.error("No active symbols found in the database.")
            return

        # Load ticker info
        self.load_ticker_info(stock_symbols)
        self.logger.info("Yahoo company data loading completed.")

    def get_historical_data(
        self,
        tickers: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch historical data for given tickers.
        
        Args:
            tickers: List of stock tickers
            start_date: Start date in 'YYYY-MM-DD' format. If None, defaults to 1 year ago
            end_date: End date in 'YYYY-MM-DD' format. If None, defaults to today
            interval: Data interval ('1d' for daily, '1h' for hourly, etc.)
        
        Returns:
            DataFrame with historical data
        """
        try:
            # Set default dates if not provided
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

            self.logger.info(f"Fetching data for {tickers} from {start_date} to {end_date}")
            
            # Download data
            data = yf.download(
                tickers=tickers,
                start=start_date,
                end=end_date,
                interval=interval,
                group_by='ticker'
            )

            if data.empty:
                self.logger.warning(f"No data found for tickers: {tickers}")
                return pd.DataFrame()

            # Reset index to make Date a column
            data = data.reset_index()
            
            # If multiple tickers, reshape the data
            if len(tickers) > 1:
                # Flatten multi-level columns
                data.columns = [f"{col[0]}_{col[1]}" if col[1] != '' else col[0] 
                              for col in data.columns]
            
            self.logger.info(f"Successfully downloaded data for {tickers}")
            return data

        except Exception as e:
            self.logger.error(f"Error fetching data: {str(e)}")
            raise

    def get_stock_info(self, ticker: str) -> dict:
        """
        Get basic information about a stock.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary containing stock information
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract relevant information
            relevant_info = {
                'symbol': ticker,
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'current_price': info.get('currentPrice', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 0)
            }
            
            return relevant_info
            
        except Exception as e:
            self.logger.error(f"Error fetching stock info for {ticker}: {str(e)}")
            raise


if __name__ == "__main__":
    # Create an instance of the YahooFinanceDataLoader and run it
    loader = YahooFinanceDataLoader()
    loader.run()

    # Save the raw data to CSV for inspection
    if loader.raw_data:
        raw_df = pd.DataFrame(loader.raw_data)
        raw_df.to_csv("yahoo_raw_data.csv", index=False)
        print("\nRaw ticker info saved to yahoo_raw_data.csv")

    # Example 1: Get historical data for multiple stocks
    tickers = ["AAPL", "MSFT", "GOOGL"]
    historical_data = loader.get_historical_data(tickers)
    print("\nHistorical Data:")
    print(historical_data.head())
    
    # Example 2: Get stock information
    stock_info = loader.get_stock_info("AAPL")
    print("\nStock Information:")
    print(stock_info)