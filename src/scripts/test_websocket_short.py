#!/usr/bin/env python3
"""
Test script for WebSocket flow with short duration and fast persistence for testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import asyncio
import websockets
import json
import redis
import logging
from datetime import datetime, time as dt_time
import pytz
from prefect.blocks.system import Secret
from src.database.database_connectivity import DatabaseConnectivity

# Setup Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_market_hours() -> bool:
    """Check if current time is during market hours"""
    et = pytz.timezone('US/Eastern')
    current_time = datetime.now(et)
    
    if current_time.weekday() >= 5:  # Weekend
        return False
    
    market_open = dt_time(9, 30)
    market_close = dt_time(16, 0)
    current_time_et = current_time.time()
    
    return market_open <= current_time_et <= market_close

async def test_websocket_with_fast_persistence():
    """
    Test WebSocket connection with fast persistence (every 30 seconds for testing)
    """
    logger.info("🚀 Starting WebSocket test with fast persistence...")
    
    # Load API credentials
    try:
        api_key_block = await Secret.load("alpaca-api-key")
        secret_key_block = await Secret.load("alpaca-secret-key")
        API_KEY = api_key_block.get()
        API_SECRET = secret_key_block.get()
        logger.info("✅ Successfully loaded API credentials")
    except Exception as e:
        logger.error(f"❌ Failed to load API credentials: {e}")
        return

    # Setup Alpaca WebSocket
    ws_url = "wss://stream.data.alpaca.markets/v2/iex"
    
    try:
        async with websockets.connect(ws_url, ping_interval=20, ping_timeout=20) as websocket:
            # Authenticate
            auth_message = {
                "action": "auth",
                "key": API_KEY,
                "secret": API_SECRET
            }
            await websocket.send(json.dumps(auth_message))
            logger.info("✅ Authenticated with Alpaca WebSocket")

            # Wait for authentication response
            auth_response = await websocket.recv()
            if '"T":"success"' not in auth_response:
                logger.error("❌ Authentication failed")
                return

            # Subscribe to AAPL data
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
            logger.info("✅ Subscribed to AAPL bars data")

            # Wait for subscription response
            subscribe_response = await websocket.recv()
            logger.info(f"📡 Subscription response: {subscribe_response}")

            # Initialize persistence tracking (30 seconds for testing)
            last_persistence_time = datetime.now()
            persistence_interval = 30  # 30 seconds for testing (instead of 3600)

            logger.info(f"⏰ Will run persistence every {persistence_interval} seconds")
            
            # Test for 2 minutes
            start_time = datetime.now()
            test_duration = 120  # 2 minutes
            
            while (datetime.now() - start_time).total_seconds() < test_duration:
                if not is_market_hours():
                    logger.info("📅 Market is closed. Ending test.")
                    break

                # Check if it's time for persistence
                current_time = datetime.now()
                if (current_time - last_persistence_time).total_seconds() >= persistence_interval:
                    logger.info("💾 Running persistence...")
                    try:
                        from src.data.sources.alpaca_websocket import save_redis_data_to_postgres
                        save_redis_data_to_postgres()
                        last_persistence_time = current_time
                        logger.info("✅ Persistence completed")
                    except Exception as e:
                        logger.error(f"❌ Persistence failed: {e}")

                try:
                    # Set a short timeout for receiving messages
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    
                    if isinstance(data, list):
                        for ohlc in data:
                            symbol = ohlc.get('S')
                            if symbol == 'AAPL':
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
                                logger.info(f"📊 Stored AAPL data: {ohlc_data['close']} @ {ohlc_data['timestamp']}")
                                
                except asyncio.TimeoutError:
                    continue
                except websockets.exceptions.ConnectionClosedError:
                    logger.warning("⚠️ WebSocket connection closed.")
                    break
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")
                    continue

            # Final persistence run
            logger.info("🏁 Running final persistence...")
            try:
                from src.data.sources.alpaca_websocket import save_redis_data_to_postgres
                save_redis_data_to_postgres()
                logger.info("✅ Final persistence completed")
            except Exception as e:
                logger.error(f"❌ Final persistence failed: {e}")

            # Unsubscribe
            unsubscribe_message = {
                "action": "unsubscribe",
                "bars": symbols
            }
            await websocket.send(json.dumps(unsubscribe_message))
            logger.info("✅ Unsubscribed from data feed")

    except Exception as e:
        logger.error(f"❌ WebSocket test failed: {e}")

def main():
    """Main test function"""
    logger.info("🧪 Starting WebSocket with persistence test...")
    
    # Test Redis connection
    try:
        redis_client.ping()
        logger.info("✅ Redis connection successful")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        return
    
    # Test database connection
    try:
        db = DatabaseConnectivity()
        logger.info("✅ PostgreSQL connection successful")
        db.close()
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        return
    
    # Run the test
    asyncio.run(test_websocket_with_fast_persistence())
    
    # Check final state
    keys = redis_client.keys("AAPL:*")
    logger.info(f"📊 Final Redis state: {len(keys)} AAPL records remaining")
    
    logger.info("🎉 WebSocket test completed!")

if __name__ == "__main__":
    main() 