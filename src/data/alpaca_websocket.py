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
# from dotenv import load_dotenv
import os

# Load environment variables
# dotenv_path = r"D:\PythonProjects\StockTrading\src\config\.env"
# load_dotenv(dotenv_path)

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


@task(name="WebSocket Connection Task")
async def websocket_connection():
    """
    Task to handle WebSocket connection and data processing
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
                "bars": symbols
            }
            await websocket.send(json.dumps(subscribe_message))
            logger.info(f"Subscribed to symbols: {symbols}")

            # Wait for subscription response
            subscribe_response = await websocket.recv()
            logger.info(f"Subscription response: {subscribe_response}")

            # Set a timeout for the data collection (4.5 minutes to allow for cleanup)
            end_time = time.time() + 270  # 4.5 minutes

            while time.time() < end_time:
                if not is_market_hours():
                    logger.info("Market is closed. Stopping WebSocket connection.")
                    return

                try:
                    message = await websocket.recv()
                    data = json.loads(message)

                    # Process the data
                    if isinstance(data, list):
                        for ohlc in data:
                            symbol = ohlc.get('S')
                            if symbol:
                                ohlc_data = {
                                    "open": str(ohlc['o']),
                                    "high": str(ohlc['h']),
                                    "low": str(ohlc['l']),
                                    "close": str(ohlc['c']),
                                    "volume": str(ohlc['v']),
                                    "timestamp": str(ohlc['t'])
                                }
                                redis_key = f"{symbol}:{ohlc_data['timestamp']}"
                                redis_client.hset(name=redis_key, mapping=ohlc_data)
                except websockets.exceptions.ConnectionClosedError:
                    logger.warning("WebSocket connection closed.")
                    return
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue

            logger.info("Completed 5-minute data collection window.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


@flow(name="Market Data WebSocket Flow")
def market_data_websocket_flow():
    """
    Prefect flow to manage WebSocket connection during market hours
    """
    logger = get_run_logger()

    if not is_market_hours():
        logger.info("Market is currently closed. Skipping WebSocket connection.")
        return

    try:
        # Check Redis connection
        redis_client.ping()
        logger.info("Connected to Redis successfully.")

        # Run the WebSocket connection task
        asyncio.run(websocket_connection())

    except redis.ConnectionError:
        logger.error("Failed to connect to Redis. Make sure Redis is running.")
        raise
    except Exception as e:
        logger.error(f"Error in market data WebSocket flow: {e}")
        raise


if __name__ == "__main__":
    market_data_websocket_flow()
