"""
Data Recycler Utilities

This module provides utilities to check available data ranges and statistics
for the data recycler WebSocket system.
"""

import logging
from datetime import datetime
from typing import Dict, List
from src.database.database_connectivity import DatabaseConnectivity

logger = logging.getLogger(__name__)


def get_available_date_ranges(symbol: str) -> Dict[str, any]:
    try:
        db = DatabaseConnectivity()
        with db.get_session() as cursor:
            # Try market_data first
            cursor.execute("""
                SELECT MIN(timestamp), MAX(timestamp), COUNT(*)
                FROM market_data WHERE symbol = %s
            """, (symbol,))
            result = cursor.fetchone()
            
            # If no data in market_data, try market_data_historical
            if not result or not result[0]:
                cursor.execute("""
                    SELECT MIN(timestamp), MAX(timestamp), COUNT(*)
                    FROM market_data_historical WHERE symbol = %s
                """, (symbol,))
                result = cursor.fetchone()
                data_source = 'historical'
            else:
                data_source = 'real-time'
            
            if result and result[0]:
                earliest_date = result[0]
                latest_date = result[1]
                total_records = result[2]
                date_range = (latest_date - earliest_date).days
                return {
                    'symbol': symbol,
                    'earliest_date': earliest_date.isoformat(),
                    'latest_date': latest_date.isoformat(),
                    'total_records': total_records,
                    'date_range_days': date_range,
                    'has_data': True,
                    'data_source': data_source
                }
            else:
                return {'symbol': symbol, 'has_data': False, 'message': f'No data found for symbol {symbol}'}
    except Exception as e:
        logger.error(f"Error getting date ranges for {symbol}: {e}")
        return {'symbol': symbol, 'has_data': False, 'error': str(e)}
    finally:
        if 'db' in locals():
            db.close()


def get_all_symbols_with_data() -> List[str]:
    try:
        db = DatabaseConnectivity()
        with db.get_session() as cursor:
            # Get symbols from market_data
            cursor.execute("SELECT DISTINCT symbol FROM market_data ORDER BY symbol")
            real_time_symbols = [row[0] for row in cursor.fetchall()]
            
            # Get symbols from market_data_historical
            cursor.execute("SELECT DISTINCT symbol FROM market_data_historical ORDER BY symbol")
            historical_symbols = [row[0] for row in cursor.fetchall()]
            
            # Combine and deduplicate
            all_symbols = list(set(real_time_symbols + historical_symbols))
            all_symbols.sort()
            
            logger.info(f"Found {len(all_symbols)} total symbols: {len(real_time_symbols)} real-time, {len(historical_symbols)} historical")
            return all_symbols
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        return []
    finally:
        if 'db' in locals():
            db.close()


def get_sample_data(symbol: str, limit: int = 5) -> List[Dict]:
    try:
        db = DatabaseConnectivity()
        with db.get_session() as cursor:
            # Try market_data first
            cursor.execute("""
                SELECT symbol, timestamp, open, high, low, close, volume
                FROM market_data WHERE symbol = %s ORDER BY timestamp LIMIT %s
            """, (symbol, limit))
            columns = [desc[0] for desc in cursor.description]
            records = []
            for row in cursor.fetchall():
                record = dict(zip(columns, row))
                if record['timestamp']:
                    record['timestamp'] = record['timestamp'].isoformat()
                records.append(record)
            
            # If no data in market_data, try market_data_historical
            if not records:
                cursor.execute("""
                    SELECT symbol, timestamp, open, high, low, close, volume
                    FROM market_data_historical WHERE symbol = %s ORDER BY timestamp LIMIT %s
                """, (symbol, limit))
                columns = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    record = dict(zip(columns, row))
                    if record['timestamp']:
                        record['timestamp'] = record['timestamp'].isoformat()
                    records.append(record)
            
            return records
    except Exception as e:
        logger.error(f"Error getting sample data for {symbol}: {e}")
        return []
    finally:
        if 'db' in locals():
            db.close()


def get_latest_price(symbol: str):
    """
    Get the latest price for a symbol from market_data (real-time),
    falling back to market_data_historical if not available.
    Returns a tuple: (price, source) where source is 'market_data' or 'market_data_historical'.
    """
    db = DatabaseConnectivity()
    try:
        with db.get_session() as cursor:
            # Try market_data first
            cursor.execute(
                "SELECT close FROM market_data WHERE symbol = %s ORDER BY timestamp DESC LIMIT 1",
                (symbol,)
            )
            result = cursor.fetchone()
            if result and result[0] is not None:
                return float(result[0]), 'market_data'
            # Fallback to historical
            cursor.execute(
                "SELECT close FROM market_data_historical WHERE symbol = %s ORDER BY timestamp DESC LIMIT 1",
                (symbol,)
            )
            result = cursor.fetchone()
            if result and result[0] is not None:
                return float(result[0]), 'market_data_historical'
        return None, None
    except Exception as e:
        logger.error(f"Error getting latest price for {symbol}: {e}")
        return None, None
    finally:
        db.close()


if __name__ == "__main__":
    print("=== Data Recycler Utilities Test ===\n")
    print("1. Available symbols:")
    symbols = get_all_symbols_with_data()
    print(f"   Found {len(symbols)} symbols: {symbols}\n")
    if symbols:
        symbol = symbols[0]
        print(f"2. Date range for {symbol}:")
        date_range = get_available_date_ranges(symbol)
        for key, value in date_range.items():
            print(f"   {key}: {value}")
        print()
        print(f"3. Sample data for {symbol}:")
        sample = get_sample_data(symbol, 3)
        for record in sample:
            print(f"   {record['timestamp']}: ${record['close']} (vol: {record['volume']})") 