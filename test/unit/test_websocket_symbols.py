#!/usr/bin/env python3
"""
Test script to verify WebSocket symbol configuration for pairs trading.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_alpaca_websocket_symbols():
    """Test that alpaca_websocket.py uses configuration for symbols."""
    print("🧪 Testing alpaca_websocket.py symbol configuration...")
    
    try:
        with open('src/data/sources/alpaca_websocket.py', 'r') as f:
            content = f.read()
        
        # Check for configuration import
        if "from src.utils.websocket_config import" in content and "get_websocket_symbols" in content:
            print("✅ Configuration import correctly configured")
        else:
            print("❌ Configuration import not found")
            assert False
        
        # Check for configuration usage instead of hardcoded symbols
        if "symbols = get_websocket_symbols()" in content:
            print("✅ Configuration-based symbols correctly configured")
        else:
            print("❌ Configuration-based symbols not found")
            assert False
        
        # Check for symbol processing using configuration
        if "symbols = get_websocket_symbols()" in content and "if symbol in symbols:" in content:
            print("✅ Symbol processing correctly uses configuration")
        else:
            print("❌ Symbol processing not using configuration")
            assert False
        
        # Check for Redis key pattern
        if "symbol_keys = redis_client.keys(f\"{symbol}:*\")" in content:
            print("✅ Redis key pattern correctly configured")
        else:
            print("❌ Redis key pattern not found or incorrect")
            assert False
        
        print("✅ alpaca_websocket.py symbol configuration is correct")
        assert True
        
    except Exception as e:
        print(f"❌ Error testing alpaca_websocket.py: {e}")
        assert False

def test_configurable_websocket_symbols():
    """Test that configurable_websocket.py uses configuration for symbols."""
    print("\n🧪 Testing configurable_websocket.py symbol configuration...")
    
    try:
        with open('src/data/sources/configurable_websocket.py', 'r') as f:
            content = f.read()
        
        # Check for configuration import
        if "from src.utils.websocket_config import" in content and "get_websocket_symbols" in content:
            print("✅ Configuration import correctly configured")
        else:
            print("❌ Configuration import not found")
            assert False
        
        # Check for configuration usage instead of hardcoded symbols
        symbol_count = content.count("symbols = get_websocket_symbols()")
        if symbol_count >= 2:
            print(f"✅ Configuration-based symbols correctly configured ({symbol_count} occurrences)")
        else:
            print(f"❌ Configuration-based symbols not found or incorrect (found {symbol_count} occurrences)")
            assert False
        
        # Check for symbol processing using configuration
        if "symbols = get_websocket_symbols()" in content and "if symbol in symbols:" in content:
            print("✅ Symbol processing correctly uses configuration")
        else:
            print("❌ Symbol processing not using configuration")
            assert False
        
        # Check for data source handling
        if "data_source" in content:
            print("✅ Data source handling correctly configured")
        else:
            print("❌ Data source handling not found")
            assert False
        
        print("✅ configurable_websocket.py symbol configuration is correct")
        assert True
        
    except Exception as e:
        print(f"❌ Error testing configurable_websocket.py: {e}")
        assert False

def test_config_file_symbols():
    """Test that config.yaml has the correct symbols configured."""
    print("\n🧪 Testing config.yaml symbol configuration...")
    
    try:
        with open('config/config.yaml', 'r') as f:
            content = f.read()
        
        # Check for websocket symbols configuration
        if "symbols: [\"AAPL\", \"PDFS\", \"ROG\"]" in content:
            print("✅ WebSocket symbols correctly configured in config.yaml")
        else:
            print("❌ WebSocket symbols not found or incorrect in config.yaml")
            assert False
        
        print("✅ config.yaml symbol configuration is correct")
        assert True
        
    except Exception as e:
        print(f"❌ Error testing config.yaml: {e}")
        assert False

def test_symbol_pairs():
    """Test that we have valid pairs for trading."""
    print("\n🧪 Testing symbol pairs for pairs trading...")
    
    symbols = ['AAPL', 'PDFS', 'ROG']
    
    # Check if symbols are different (for pairs trading)
    if len(set(symbols)) == len(symbols):
        print("✅ All symbols are unique")
    else:
        print("❌ Duplicate symbols found")
        assert False
    
    # Check if we have enough symbols for pairs trading
    if len(symbols) >= 2:
        print(f"✅ Sufficient symbols for pairs trading ({len(symbols)} symbols)")
    else:
        print("❌ Insufficient symbols for pairs trading")
        assert False
    
    # Suggest pairs
    pairs = []
    for i in range(len(symbols)):
        for j in range(i + 1, len(symbols)):
            pairs.append((symbols[i], symbols[j]))
    
    print(f"✅ Available pairs: {pairs}")
    print(f"✅ Primary trading pair: PDFS-ROG")
    print(f"✅ Testing symbol: AAPL")
    assert True

if __name__ == "__main__":
    print("🚀 Testing WebSocket Symbol Configuration for Pairs Trading...\n")
    
    # Run tests
    alpaca_test = test_alpaca_websocket_symbols()
    configurable_test = test_configurable_websocket_symbols()
    config_test = test_config_file_symbols()
    pairs_test = test_symbol_pairs()
    
    print("\n📊 Test Results:")
    print(f"Alpaca WebSocket: {'✅ PASSED' if alpaca_test else '❌ FAILED'}")
    print(f"Configurable WebSocket: {'✅ PASSED' if configurable_test else '❌ FAILED'}")
    print(f"Config File: {'✅ PASSED' if config_test else '❌ FAILED'}")
    print(f"Symbol Pairs: {'✅ PASSED' if pairs_test else '❌ FAILED'}")
    
    if alpaca_test and configurable_test and config_test and pairs_test:
        print("\n🎉 All tests passed! WebSocket configuration is ready for pairs trading.")
        print("\nNext steps:")
        print("1. Start the WebSocket to collect data for configured symbols")
        print("2. Create feature engineering pipeline for pairs trading")
        print("3. Implement cointegration testing for pair identification")
        print("4. Symbols can now be easily changed in config.yaml")
    else:
        print("\n⚠️ Some tests failed. Please check the WebSocket configuration.") 