"""
Multi-Symbol Data Recycler WebSocket Server

Streams historical data for multiple symbols from the database to any connected client.
Supports fallback to AAPL data for symbols that don't exist in the database.
"""

import asyncio
import json
import websockets
from datetime import datetime
from typing import List, Dict, Any
from src.utils.data_recycler_utils import get_sample_data, get_available_date_ranges
from src.utils.websocket_config import get_websocket_config
from src.database.database_connectivity import DatabaseConnectivity
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurable parameters
REPLAY_DELAY_SECONDS = 60.0  # 60 seconds (1 minute) between messages to match real market data
FALLBACK_SYMBOL = "AAPL"  # Use AAPL data as fallback for missing symbols

class MultiSymbolDataRecycler:
    """Multi-symbol data recycler server"""
    
    def __init__(self):
        self.config = get_websocket_config()
        self.db = DatabaseConnectivity()
        self.symbols = self.config.get_recycler_symbols()
        self.replay_mode = self.config.get_recycler_replay_mode()
        self.replay_speed = self.config.get_recycler_replay_speed()
        self.loop_count = self.config.get_recycler_loop_count()
        
        # Validate symbols and create symbol mapping
        self.symbol_mapping = self._create_symbol_mapping()
        
    def _create_symbol_mapping(self) -> Dict[str, str]:
        """
        Create mapping of requested symbols to available symbols.
        If a symbol doesn't exist in database, map it to FALLBACK_SYMBOL.
        """
        mapping = {}
        available_symbols = self._get_available_symbols()
        
        for symbol in self.symbols:
            if symbol in available_symbols:
                mapping[symbol] = symbol  # Use actual symbol data
                logger.info(f"Symbol {symbol}: Using actual data from database")
            else:
                mapping[symbol] = FALLBACK_SYMBOL  # Use fallback data
                logger.warning(f"Symbol {symbol}: No data in database, using {FALLBACK_SYMBOL} as proxy")
        
        return mapping
    
    def _get_available_symbols(self) -> List[str]:
        """Get list of symbols that have data in the database"""
        try:
            with self.db.get_session() as cursor:
                cursor.execute(
                    "SELECT DISTINCT symbol FROM market_data ORDER BY symbol"
                )
                symbols = [row[0] for row in cursor.fetchall()]
                logger.info(f"Available symbols in database: {symbols}")
                return symbols
        except Exception as e:
            logger.error(f"Error getting available symbols: {e}")
            return [FALLBACK_SYMBOL]  # At least return fallback symbol
    
    async def fetch_all_data(self, symbol: str) -> List[Dict[str, Any]]:
        """Fetch all historical data for the symbol from the database."""
        data = []
        try:
            with self.db.get_session() as cursor:
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
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
        return data
    
    async def get_symbol_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get data for all requested symbols"""
        symbol_data = {}
        
        # Get unique symbols we need to fetch (after mapping)
        unique_symbols = set(self.symbol_mapping.values())
        
        # Fetch data for each unique symbol
        for symbol in unique_symbols:
            logger.info(f"Fetching data for {symbol}...")
            data = await self.fetch_all_data(symbol)
            symbol_data[symbol] = data
            logger.info(f"Fetched {len(data)} records for {symbol}")
        
        return symbol_data
    
    async def stream_data(self, websocket):
        """Stream data for all symbols to the connected client"""
        logger.info(f"Client connected: {websocket.remote_address}")
        logger.info(f"Requested symbols: {self.symbols}")
        logger.info(f"Symbol mapping: {self.symbol_mapping}")
        
        try:
            # Get data for all symbols
            symbol_data = await self.get_symbol_data()
            
            # Check if we have any data
            total_records = sum(len(data) for data in symbol_data.values())
            if total_records == 0:
                logger.warning("No data found for any symbol")
                await websocket.close()
                return
            
            # Calculate delay based on replay speed
            actual_delay = REPLAY_DELAY_SECONDS / self.replay_speed
            
            logger.info(f"Starting to stream data for {len(self.symbols)} symbols...")
            logger.info(f"Total records: {total_records}, Delay: {actual_delay:.2f}s")
            
            # Stream data based on replay mode
            if self.replay_mode == "single_pass":
                await self._stream_single_pass(websocket, symbol_data, actual_delay)
            elif self.replay_mode == "loop":
                await self._stream_loop(websocket, symbol_data, actual_delay)
            else:
                logger.error(f"Unsupported replay mode: {self.replay_mode}")
                await websocket.close()
                
        except Exception as e:
            logger.error(f"Error in stream_data: {e}")
            await websocket.close()
    
    async def _stream_single_pass(self, websocket, symbol_data: Dict[str, List[Dict]], delay: float):
        """Stream data once for all symbols"""
        # Get the minimum length across all symbols
        min_length = min(len(data) for data in symbol_data.values())
        
        for i in range(min_length):
            # Create message for all symbols at this timestamp
            messages = []
            for requested_symbol in self.symbols:
                actual_symbol = self.symbol_mapping[requested_symbol]
                record = symbol_data[actual_symbol][i]
                
                # Use current timestamp instead of historical timestamp
                current_time = datetime.now().isoformat()
                
                # Create message with requested symbol name but actual symbol data
                message = {
                    "S": requested_symbol,  # Use requested symbol name
                    "t": current_time,
                    "o": record["open"],
                    "h": record["high"],
                    "l": record["low"],
                    "c": record["close"],
                    "v": record["volume"]
                }
                messages.append(message)
            
            # Send all symbol data in one message
            await websocket.send(json.dumps(messages))
            logger.info(f"Sent message {i+1}/{min_length} for {len(self.symbols)} symbols at {datetime.now().isoformat()}")
            
            await asyncio.sleep(delay)
        
        logger.info(f"Finished streaming data for {len(self.symbols)} symbols")
        await websocket.close()
    
    async def _stream_loop(self, websocket, symbol_data: Dict[str, List[Dict]], delay: float):
        """Stream data in a loop"""
        loop_count = 0
        max_loops = self.loop_count if self.loop_count > 0 else float('inf')
        
        while loop_count < max_loops:
            logger.info(f"Starting loop {loop_count + 1}")
            await self._stream_single_pass(websocket, symbol_data, delay)
            loop_count += 1
            
            if loop_count < max_loops:
                logger.info(f"Restarting loop {loop_count + 1}/{max_loops}")
                # Small delay between loops
                await asyncio.sleep(5)
        
        logger.info(f"Completed {loop_count} loops")
        await websocket.close()

async def stream_data_handler(websocket, path):
    """WebSocket connection handler"""
    recycler = MultiSymbolDataRecycler()
    await recycler.stream_data(websocket)

if __name__ == "__main__":
    config = get_websocket_config()
    logger.info("Starting multi-symbol data recycler WebSocket server on ws://localhost:8765 ...")
    logger.info(f"Configuration: {config.get_config_summary()}")
    
    async def main():
        async with websockets.serve(stream_data_handler, "localhost", 8765):
            await asyncio.Future()  # run forever
    
    asyncio.run(main()) 