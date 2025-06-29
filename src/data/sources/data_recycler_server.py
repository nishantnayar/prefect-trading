"""
Minimal Data Recycler WebSocket Server

Streams all historical data for AAPL from the database to any connected client,
in a single pass, with a fixed delay between messages.
"""

import asyncio
import json
import websockets
from datetime import datetime
from src.utils.data_recycler_utils import get_sample_data, get_available_date_ranges
from src.database.database_connectivity import DatabaseConnectivity
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurable parameters
SYMBOL = "AAPL"
REPLAY_DELAY_SECONDS = 60.0  # 60 seconds (1 minute) between messages to match real market data

async def fetch_all_data(symbol):
    """Fetch all historical data for the symbol from the database."""
    db = DatabaseConnectivity()
    data = []
    try:
        with db.get_session() as cursor:
            cursor.execute(
                """
                SELECT timestamp, open, high, low, close, volume
                FROM market_data
                WHERE symbol = %s
                ORDER BY timestamp
                """,
                (symbol,)
            )
            for row in cursor.fetchall():
                data.append({
                    "timestamp": row[0].isoformat(),
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4]),
                    "volume": int(row[5]),
                    "symbol": symbol
                })
    finally:
        db.close()
    return data

async def stream_data(websocket):
    logger.info(f"Client connected: {websocket.remote_address}")
    try:
        # Fetch all data for AAPL
        logger.info("Fetching data from database...")
        data = await fetch_all_data(SYMBOL)
        logger.info(f"Fetched {len(data)} records for {SYMBOL}")
        
        if not data:
            logger.warning("No data found for AAPL")
            await websocket.close()
            return
            
        logger.info("Starting to stream data...")
        for i, record in enumerate(data):
            logger.info(f"Streaming record {i+1}/{len(data)}")
            # Use current timestamp instead of historical timestamp
            current_time = datetime.now().isoformat()
            # Mimic Alpaca bar message format (as a list of dicts)
            message = json.dumps([
                {
                    "S": record["symbol"],
                    "t": current_time,  # Use current time instead of record["timestamp"]
                    "o": record["open"],
                    "h": record["high"],
                    "l": record["low"],
                    "c": record["close"],
                    "v": record["volume"]
                }
            ])
            await websocket.send(message)
            logger.info(f"Sent message {i+1} at {current_time}")
            await asyncio.sleep(REPLAY_DELAY_SECONDS)
        logger.info(f"Finished streaming data for {SYMBOL} to {websocket.remote_address}")
        await websocket.close()
    except Exception as e:
        logger.error(f"Error in stream_data: {e}")
        await websocket.close()

if __name__ == "__main__":
    logger.info("Starting minimal data recycler WebSocket server on ws://localhost:8765 ...")
    async def main():
        async with websockets.serve(stream_data, "localhost", 8765):
            await asyncio.Future()  # run forever
    asyncio.run(main()) 