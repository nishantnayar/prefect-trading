"""
Configurable WebSocket Client

This module provides a WebSocket client that can connect to either:
1. Alpaca WebSocket (real market data)
2. Data Recycler Server (replayed historical data)

The client uses the same interface as the original alpaca_websocket.py
but adds configuration-based switching between data sources.
"""

import asyncio
import websockets
import json
import time
import redis
import logging
from datetime import datetime, time as dt_time
import pytz
from prefect import flow, task, get_run_logger
from prefect.blocks.system import Secret
from src.database.database_connectivity import DatabaseConnectivity
from src.utils.websocket_config import get_websocket_config, is_recycler_mode, is_alpaca_mode
import os

# Setup Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def is_market_hours() -> bool:
    """
    Check if current time is during market hours (9:30 AM - 4:00 PM ET, Monday-Friday)
    """
    et = pytz.timezone('US/Eastern')
    current_time = datetime.now(et)

    # Check if it's a weekday
    if current_time.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
        return False

    # Check if it's during market hours
    market_open = dt_time(9, 30)  # 9:30 AM
    market_close = dt_time(16, 0)  # 4:00 PM
    current_time_et = current_time.time()

    return market_open <= current_time_et <= market_close


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
                
                if ohlc_data and len(ohlc_data) >= 6:  # Ensure we have all required fields
                    # Parse timestamp
                    timestamp_str = ohlc_data.get('timestamp', '')
                    if timestamp_str:
                        # Convert timestamp to datetime (assuming it's in ISO format)
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        except ValueError:
                            # If ISO format fails, try parsing as Unix timestamp
                            timestamp = datetime.fromtimestamp(float(timestamp_str) / 1000)
                        
                        # Get data source (default to 'alpaca' for backward compatibility)
                        data_source = ohlc_data.get('data_source', 'alpaca')
                        
                        # Prepare data for insertion
                        data_to_insert.append((
                            'AAPL',  # symbol
                            timestamp,  # timestamp
                            float(ohlc_data['open']),  # open
                            float(ohlc_data['high']),  # high
                            float(ohlc_data['low']),   # low
                            float(ohlc_data['close']), # close
                            int(ohlc_data['volume']),  # volume
                            data_source  # data_source
                        ))
                        
                        # Remove the data from Redis after successful processing
                        redis_client.delete(key)
                        
            except Exception as e:
                logger.error(f"Error processing Redis key {key}: {e}")
                continue
        
        if data_to_insert:
            # Batch insert into PostgreSQL
            insert_query = """
                INSERT INTO market_data (symbol, timestamp, open, high, low, close, volume, data_source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, timestamp) DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume,
                    data_source = EXCLUDED.data_source
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


@task(name="Alpaca WebSocket Connection Task")
async def alpaca_websocket_connection():
    """
    Task to handle Alpaca WebSocket connection and data processing
    """
    logger = get_run_logger()

    # Load API credentials from Prefect secrets
    try:
        # Load secrets using Prefect's async pattern
        api_key_block = await Secret.load("alpaca-api-key")
        secret_key_block = await Secret.load("alpaca-secret-key")

        API_KEY = api_key_block.get()
        API_SECRET = secret_key_block.get()

        logger.info("Successfully loaded API credentials")
    except Exception as e:
        logger.error(f"Failed to load API credentials: {e}")
        raise

    # Setup Alpaca WebSocket
    ws_url = "wss://stream.data.alpaca.markets/v2/iex"

    try:
        async with websockets.connect(ws_url, ping_interval=20, ping_timeout=20) as websocket:
            # Authenticate with Alpaca
            auth_message = {
                "action": "auth",
                "key": API_KEY,
                "secret": API_SECRET
            }
            await websocket.send(json.dumps(auth_message))
            logger.info("Authenticated with Alpaca WebSocket")

            # Wait for authentication response
            auth_response = await websocket.recv()
            logger.info(f"Authentication response: {auth_response}")

            # Check if authentication was successful
            if '"T":"success"' not in auth_response:
                logger.error("Authentication failed. Check your API key and secret.")
                return

            # Subscribe to real-time data for the stock symbols
            symbols = ['AAPL']
            subscribe_message = {
                "action": "subscribe",
                "bars": symbols,
                "trades": [],
                "quotes": [],
                "updatedBars": [],
                "dailyBars": []
            }
            await websocket.send(json.dumps(subscribe_message))
            logger.info(f"Subscribed to AAPL bars data")

            # Wait for subscription response
            subscribe_response = await websocket.recv()
            logger.info(f"Subscription response: {subscribe_response}")

            # Initialize persistence tracking
            last_persistence_time = datetime.now()

            while True:
                if not is_market_hours():
                    logger.info("Market is closed. Closing WebSocket connection.")
                    # Send unsubscribe message before closing
                    unsubscribe_message = {
                        "action": "unsubscribe",
                        "bars": symbols
                    }
                    await websocket.send(json.dumps(unsubscribe_message))
                    logger.info("Unsubscribed from data feed")
                    return

                # Check if it's time for hourly persistence
                current_time = datetime.now()
                if (current_time - last_persistence_time).total_seconds() >= 3600:  # 1 hour
                    logger.info("Running hourly data persistence...")
                    try:
                        save_redis_data_to_postgres()
                        last_persistence_time = current_time
                        logger.info("Hourly data persistence completed")
                    except Exception as e:
                        logger.error(f"Hourly data persistence failed: {e}")

                try:
                    # Set a timeout for receiving messages
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    
                    # Process the data
                    if isinstance(data, list):
                        for ohlc in data:
                            symbol = ohlc.get('S')
                            logger.info(f"Processing symbol: {symbol}")
                            # Only process AAPL data
                            if symbol == 'AAPL':
                                ohlc_data = {
                                    "open": str(ohlc['o']),
                                    "high": str(ohlc['h']),
                                    "low": str(ohlc['l']),
                                    "close": str(ohlc['c']),
                                    "volume": str(ohlc['v']),
                                    "timestamp": str(ohlc['t']),
                                    "data_source": "alpaca"  # Mark as real Alpaca data
                                }
                                redis_key = f"{symbol}:{ohlc_data['timestamp']}"
                                logger.info(f"Storing AAPL data: {ohlc_data}")
                                assert symbol == 'AAPL', f"Attempting to store non-AAPL symbol: {symbol}"
                                redis_client.hset(name=redis_key, mapping=ohlc_data)
                            else:
                                logger.info(f"Skipping non-AAPL symbol: {symbol}")
                                
                except asyncio.TimeoutError:
                    # Timeout is expected, continue the loop
                    continue
                except websockets.exceptions.ConnectionClosedError:
                    logger.warning("WebSocket connection closed.")
                    return
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


@task(name="Recycler WebSocket Connection Task")
async def recycler_websocket_connection():
    """
    Task to handle Data Recycler WebSocket connection and data processing
    """
    logger = get_run_logger()

    # Get recycler configuration
    config = get_websocket_config()
    recycler_url = config.get_recycler_server_url()
    
    logger.info(f"Connecting to data recycler server at: {recycler_url}")

    try:
        async with websockets.connect(recycler_url) as websocket:
            logger.info("Connected to data recycler server")

            # Initialize persistence tracking
            last_persistence_time = datetime.now()
            data_received = False

            while True:
                # Check if it's time for hourly persistence
                current_time = datetime.now()
                if (current_time - last_persistence_time).total_seconds() >= 3600:  # 1 hour
                    logger.info("Running hourly data persistence...")
                    try:
                        save_redis_data_to_postgres()
                        last_persistence_time = current_time
                        logger.info("Hourly data persistence completed")
                    except Exception as e:
                        logger.error(f"Hourly data persistence failed: {e}")

                try:
                    # Set a timeout for receiving messages - increased to handle delays
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)  # 10 seconds to handle 5-second delays
                    data = json.loads(message)
                    data_received = True
                    
                    # Process the data (same format as Alpaca)
                    if isinstance(data, list):
                        for ohlc in data:
                            symbol = ohlc.get('S')
                            logger.info(f"Processing recycled symbol: {symbol}")
                            # Only process AAPL data
                            if symbol == 'AAPL':
                                ohlc_data = {
                                    "open": str(ohlc['o']),
                                    "high": str(ohlc['h']),
                                    "low": str(ohlc['l']),
                                    "close": str(ohlc['c']),
                                    "volume": str(ohlc['v']),
                                    "timestamp": str(ohlc['t']),
                                    "data_source": "recycled"  # Mark as recycled data
                                }
                                redis_key = f"{symbol}:{ohlc_data['timestamp']}"
                                logger.info(f"Storing recycled AAPL data: {ohlc_data}")
                                assert symbol == 'AAPL', f"Attempting to store non-AAPL symbol: {symbol}"
                                redis_client.hset(name=redis_key, mapping=ohlc_data)
                            else:
                                logger.info(f"Skipping non-AAPL symbol: {symbol}")
                                
                except asyncio.TimeoutError:
                    # Timeout is expected with 5-second delays, continue the loop
                    logger.debug("Timeout waiting for message (expected with 5-second delays)")
                    continue
                except websockets.exceptions.ConnectionClosedError:
                    logger.warning("Data recycler WebSocket connection closed.")
                    # Save any remaining data before exiting
                    if data_received:
                        logger.info("Saving remaining data to PostgreSQL...")
                        try:
                            save_redis_data_to_postgres()
                            logger.info("Data saved successfully")
                        except Exception as e:
                            logger.error(f"Failed to save remaining data: {e}")
                    return
                except Exception as e:
                    logger.error(f"Error processing recycled message: {e}")
                    continue

    except Exception as e:
        logger.error(f"An unexpected error occurred with recycler: {e}")
        raise


@task(name="WebSocket Connection Task")
async def websocket_connection():
    """
    Task to handle WebSocket connection based on configuration
    """
    logger = get_run_logger()
    
    # Check configuration to determine which WebSocket to use
    if is_recycler_mode():
        logger.info("Using data recycler WebSocket mode")
        await recycler_websocket_connection()
    elif is_alpaca_mode():
        logger.info("Using Alpaca WebSocket mode")
        await alpaca_websocket_connection()
    else:
        logger.error("Invalid WebSocket mode configured")
        raise ValueError("Invalid WebSocket mode. Must be 'alpaca' or 'recycler'")


@flow(name="Market Data WebSocket Flow")
def market_data_websocket_flow():
    """
    Prefect flow to manage WebSocket connection with configurable data source
    """
    logger = get_run_logger()

    # Get current configuration
    config = get_websocket_config()
    mode = config.get_websocket_mode()
    
    logger.info(f"Starting Market Data WebSocket Flow in {mode} mode")

    # For recycler mode, we don't need to check market hours
    if mode == "alpaca" and not is_market_hours():
        logger.info("Market is currently closed. Skipping WebSocket connection.")
        return

    try:
        # Check Redis connection
        redis_client.ping()
        logger.info("Connected to Redis successfully.")

        # Initialize database connection
        db = DatabaseConnectivity()
        logger.info("Connected to PostgreSQL database")

        # Run the WebSocket connection task
        asyncio.run(websocket_connection())

    except redis.ConnectionError:
        logger.error("Failed to connect to Redis. Make sure Redis is running.")
        raise
    except Exception as e:
        logger.error(f"Error in market data WebSocket flow: {e}")
        raise
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    market_data_websocket_flow() 