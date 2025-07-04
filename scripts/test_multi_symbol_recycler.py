#!/usr/bin/env python3
"""
Test Multi-Symbol Data Recycler

This script tests the multi-symbol data recycler to ensure it works correctly
with the new configuration and proxy data support.
"""

import sys
import asyncio
import websockets
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.websocket_config import get_websocket_config

async def test_data_recycler():
    """Test the data recycler by connecting and receiving a few messages"""
    config = get_websocket_config()
    
    print("=== Testing Multi-Symbol Data Recycler ===")
    print(f"Configuration: {config.get_config_summary()}")
    print()
    
    # Connect to the data recycler
    uri = config.get_recycler_server_url()
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            print()
            
            # Receive a few messages to test
            message_count = 0
            max_messages = 3
            
            print(f"Receiving {max_messages} messages...")
            print()
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_count += 1
                    
                    print(f"Message {message_count}:")
                    print(f"  Raw message: {message[:200]}...")
                    print(f"  Parsed data: {len(data)} symbol(s)")
                    
                    # Check each symbol in the message
                    for symbol_data in data:
                        symbol = symbol_data.get('S', 'Unknown')
                        timestamp = symbol_data.get('t', 'Unknown')
                        close_price = symbol_data.get('c', 'Unknown')
                        volume = symbol_data.get('v', 'Unknown')
                        
                        print(f"    {symbol}: Close=${close_price}, Volume={volume}, Time={timestamp}")
                    
                    print()
                    
                    if message_count >= max_messages:
                        print(f"✅ Received {max_messages} messages successfully!")
                        print("✅ Multi-symbol data recycler is working correctly!")
                        break
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse message: {e}")
                    break
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    break
                    
    except ConnectionRefusedError:
        print("❌ Connection refused. Is the data recycler server running?")
        print("   Start it with: python -m src.data.sources.data_recycler_server")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

def test_configuration():
    """Test the configuration loading"""
    print("=== Testing Configuration ===")
    
    try:
        config = get_websocket_config()
        
        print("✅ Configuration loaded successfully")
        print(f"Mode: {config.get_websocket_mode()}")
        print(f"Symbols: {config.get_websocket_symbols()}")
        print(f"Recycler symbols: {config.get_recycler_symbols()}")
        print(f"Replay mode: {config.get_recycler_replay_mode()}")
        print(f"Replay speed: {config.get_recycler_replay_speed()}")
        
        if config.validate_config():
            print("✅ Configuration validation passed")
        else:
            print("❌ Configuration validation failed")
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")

def main():
    """Main test function"""
    print("Multi-Symbol Data Recycler Test")
    print("=" * 40)
    print()
    
    # Test configuration first
    test_configuration()
    print()
    
    # Test data recycler connection
    asyncio.run(test_data_recycler())
    
    print()
    print("Test completed!")

if __name__ == "__main__":
    main() 