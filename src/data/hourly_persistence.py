"""
Hourly data persistence module for saving Redis WebSocket data to PostgreSQL
"""
import redis
import logging
from datetime import datetime, timedelta
from prefect import task, get_run_logger
from src.database.database_connectivity import DatabaseConnectivity

# Setup Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@task(name="Save Redis Data to PostgreSQL")
def save_redis_data_to_postgres():
    """
    Task to save WebSocket data from Redis to PostgreSQL
    """
    logger = get_run_logger()
    
    try:
        # Initialize database connection
        db = DatabaseConnectivity()
        logger.info("Connected to PostgreSQL database")
        
        # Get all keys from Redis that match the pattern "AAPL:*"
        keys = redis_client.keys("AAPL:*")
        logger.info(f"Found {len(keys)} AAPL records in Redis")
        
        if not keys:
            logger.info("No AAPL data found in Redis to save")
            return
        
        # Prepare data for batch insertion
        data_to_insert = []
        for key in keys:
            try:
                # Get data from Redis
                ohlc_data = redis_client.hgetall(key)
                
                if ohlc_data and len(ohlc_data) == 6:  # Ensure we have all required fields
                    # Parse timestamp
                    timestamp_str = ohlc_data.get('timestamp', '')
                    if timestamp_str:
                        # Convert timestamp to datetime (assuming it's in ISO format)
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        except ValueError:
                            # If ISO format fails, try parsing as Unix timestamp
                            timestamp = datetime.fromtimestamp(float(timestamp_str) / 1000)
                        
                        # Prepare data for insertion
                        data_to_insert.append((
                            'AAPL',  # symbol
                            timestamp,  # timestamp
                            float(ohlc_data['open']),  # open
                            float(ohlc_data['high']),  # high
                            float(ohlc_data['low']),   # low
                            float(ohlc_data['close']), # close
                            int(ohlc_data['volume'])   # volume
                        ))
                        
                        # Remove the data from Redis after successful processing
                        redis_client.delete(key)
                        
            except Exception as e:
                logger.error(f"Error processing Redis key {key}: {e}")
                continue
        
        if data_to_insert:
            # Batch insert into PostgreSQL
            insert_query = """
                INSERT INTO market_data (symbol, timestamp, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, timestamp) DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume
            """
            
            with db.get_session() as cursor:
                cursor.executemany(insert_query, data_to_insert)
            
            logger.info(f"Successfully saved {len(data_to_insert)} AAPL records to PostgreSQL")
        else:
            logger.info("No valid data found to save to PostgreSQL")
            
    except Exception as e:
        logger.error(f"Error saving Redis data to PostgreSQL: {e}")
        raise
    finally:
        if 'db' in locals():
            db.close()


@task(name="Hourly Data Persistence Task")
def hourly_data_persistence():
    """
    Task that runs every hour to persist Redis data to PostgreSQL
    """
    logger = get_run_logger()
    logger.info("Starting hourly data persistence task")
    
    try:
        save_redis_data_to_postgres()
        logger.info("Hourly data persistence completed successfully")
    except Exception as e:
        logger.error(f"Hourly data persistence failed: {e}")
        raise


def run_hourly_persistence():
    """
    Standalone function to run hourly persistence (for testing or manual execution)
    """
    logger = logging.getLogger(__name__)
    logger.info("Running hourly data persistence...")
    
    try:
        save_redis_data_to_postgres()
        logger.info("Hourly data persistence completed successfully")
    except Exception as e:
        logger.error(f"Hourly data persistence failed: {e}")
        raise


if __name__ == "__main__":
    run_hourly_persistence() 