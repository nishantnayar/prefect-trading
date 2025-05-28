import asyncio
import websockets
import json
import time
import redis
import logging
from dotenv import load_dotenv
import os

# Load environment variables
dotenv_path = r"D:\PythonProjects\StockTrading\src\config\.env"
load_dotenv(dotenv_path)

# Fetch API credentials from environment variables
API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")

# Validate API credentials
if not API_KEY or not API_SECRET:
    raise ValueError("API_KEY or API_SECRET not found in environment variables.")

# Setup Alpaca WebSocket
ws_url = "wss://stream.data.alpaca.markets/v2/iex"  # IEX WebSocket URL

# Setup Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Check Redis connection
try:
    redis_client.ping()
    logging.info("Connected to Redis successfully.")
except redis.ConnectionError:
    logging.error("Failed to connect to Redis. Make sure Redis is running.")
    exit(1)


# Function to handle WebSocket connection and process messages
async def ohlc_data_handler():
    while True:
        try:
            async with websockets.connect(ws_url, ping_interval=20, ping_timeout=20) as websocket:
                # Authenticate with Alpaca
                auth_message = {
                    "action": "auth",
                    "key": API_KEY,
                    "secret": API_SECRET
                }
                await websocket.send(json.dumps(auth_message))
                logging.info("Authenticated with Alpaca WebSocket")

                # Wait for authentication response
                auth_response = await websocket.recv()
                logging.info(f"Authentication response: {auth_response}")

                # Check if authentication was successful
                if '"T":"success"' not in auth_response:
                    logging.error("Authentication failed. Check your API key and secret.")
                    time.sleep(5)  # Wait before retrying
                    continue

                # Subscribe to real-time data for the stock symbols
                symbols = ['CDNS', 'AMAT', 'KLAC', 'GRMN', 'LRCX', 'RMBS', 'TTMI', 'AAPL', 'MSFT']  # Example symbols
                subscribe_message = {
                    "action": "subscribe",
                    "bars": symbols
                }
                await websocket.send(json.dumps(subscribe_message))
                logging.info(f"Subscribed to symbols: {symbols}")

                # Wait for subscription response
                subscribe_response = await websocket.recv()
                logging.info(f"Subscription response: {subscribe_response}")

                while True:
                    # Receive incoming data
                    message = await websocket.recv()
                    logging.info(f"Raw WebSocket message: {message}")  # Log raw message for debugging

                    data = json.loads(message)

                    # Check if data is a list (each item is an individual bar)
                    if isinstance(data, list):
                        for ohlc in data:
                            symbol = ohlc.get('S')  # Adjusted key for symbol
                            if symbol:
                                ohlc_data = {
                                    "open": str(ohlc['o']),
                                    "high": str(ohlc['h']),
                                    "low": str(ohlc['l']),
                                    "close": str(ohlc['c']),
                                    "volume": str(ohlc['v']),
                                    "timestamp": str(ohlc['t'])  # Ensure timestamp is a string
                                }
                                # Use the timestamp as the key in Redis
                                redis_key = f"{symbol}:{ohlc_data['timestamp']}"
                                logging.debug(f"Storing OHLC data with key: {redis_key}, data: {ohlc_data}")

                                # Save the OHLC data into Redis using hset
                                result = redis_client.hset(name=redis_key, mapping=ohlc_data)
                                # if result:
                                #     logging.info(f"Successfully inserted OHLC data for {symbol} into Redis.")
                                # else:
                                #     logging.warning(f"No new data inserted for {symbol}. Result: {result}")
                    else:
                        logging.warning("Received unexpected message format: %s", data)

        except websockets.exceptions.ConnectionClosedError as e:
            logging.error(f"Connection closed with error: {e}. Reconnecting...")
            time.sleep(5)  # Wait for 5 seconds before reconnecting
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}. Reconnecting...")
            time.sleep(5)
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}. Reconnecting...")
            time.sleep(5)


# Run the WebSocket client
if __name__ == "__main__":
    logging.info("Starting Alpaca WebSocket client...")
    asyncio.run(ohlc_data_handler())
