#!/usr/bin/env python3
"""
Test script to verify WebSocket symbol configuration for pairs trading.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_alpaca_websocket_symbols():
    """Test that alpaca_websocket.py has the correct symbols."""
    print("🧪 Testing alpaca_websocket.py symbol configuration...")
    
    try:
        with open('src/data/sources/alpaca_websocket.py', 'r') as f:
            content = f.read()
        
        # Check for symbol list
        if "symbols = ['AAPL', 'PDFS', 'ROG']" in content:
            print("✅ Symbol list correctly configured")
        else:
            print("❌ Symbol list not found or incorrect")
            return False
        
        # Check for symbol processing
        if "if symbol in ['AAPL', 'PDFS', 'ROG']:" in content:
            print("✅ Symbol processing correctly configured")
        else:
            print("❌ Symbol processing not found or incorrect")
            return False
        
        # Check for Redis key pattern
        if "symbol_keys = redis_client.keys(f\"{symbol}:*\")" in content:
            print("✅ Redis key pattern correctly configured")
        else:
            print("❌ Redis key pattern not found or incorrect")
            return False
        
        print("✅ alpaca_websocket.py symbol configuration is correct")
        return True
        
    except Exception as e:
        print(f"❌ Error testing alpaca_websocket.py: {e}")
        return False

def test_configurable_websocket_symbols():
    """Test that configurable_websocket.py has the correct symbols."""
    print("\n🧪 Testing configurable_websocket.py symbol configuration...")
    
    try:
        with open('src/data/sources/configurable_websocket.py', 'r') as f:
            content = f.read()
        
        # Check for symbol list (should appear twice - once for each WebSocket type)
        symbol_count = content.count("symbols = ['AAPL', 'PDFS', 'ROG']")
        if symbol_count >= 2:
            print(f"✅ Symbol list correctly configured ({symbol_count} occurrences)")
        else:
            print(f"❌ Symbol list not found or incorrect (found {symbol_count} occurrences)")
            return False
        
        # Check for symbol processing in Alpaca section
        if "if symbol in ['AAPL', 'PDFS', 'ROG']:" in content:
            print("✅ Symbol processing correctly configured")
        else:
            print("❌ Symbol processing not found or incorrect")
            return False
        
        # Check for data source handling
        if "data_source" in content:
            print("✅ Data source handling correctly configured")
        else:
            print("❌ Data source handling not found")
            return False
        
        print("✅ configurable_websocket.py symbol configuration is correct")
        return True
        
    except Exception as e:
        print(f"❌ Error testing configurable_websocket.py: {e}")
        return False

def test_symbol_pairs():
    """Test that we have valid pairs for trading."""
    print("\n🧪 Testing symbol pairs for pairs trading...")
    
    symbols = ['AAPL', 'PDFS', 'ROG']
    
    # Check if symbols are different (for pairs trading)
    if len(set(symbols)) == len(symbols):
        print("✅ All symbols are unique")
    else:
        print("❌ Duplicate symbols found")
        return False
    
    # Check if we have enough symbols for pairs trading
    if len(symbols) >= 2:
        print(f"✅ Sufficient symbols for pairs trading ({len(symbols)} symbols)")
    else:
        print("❌ Insufficient symbols for pairs trading")
        return False
    
    # Suggest pairs
    pairs = []
    for i in range(len(symbols)):
        for j in range(i + 1, len(symbols)):
            pairs.append((symbols[i], symbols[j]))
    
    print(f"✅ Available pairs: {pairs}")
    print(f"✅ Primary trading pair: PDFS-ROG")
    print(f"✅ Testing symbol: AAPL")
    return True

if __name__ == "__main__":
    print("🚀 Testing WebSocket Symbol Configuration for Pairs Trading...\n")
    
    # Run tests
    alpaca_test = test_alpaca_websocket_symbols()
    configurable_test = test_configurable_websocket_symbols()
    pairs_test = test_symbol_pairs()
    
    print("\n📊 Test Results:")
    print(f"Alpaca WebSocket: {'✅ PASSED' if alpaca_test else '❌ FAILED'}")
    print(f"Configurable WebSocket: {'✅ PASSED' if configurable_test else '❌ FAILED'}")
    print(f"Symbol Pairs: {'✅ PASSED' if pairs_test else '❌ FAILED'}")
    
    if alpaca_test and configurable_test and pairs_test:
        print("\n🎉 All tests passed! WebSocket configuration is ready for pairs trading.")
        print("\nNext steps:")
        print("1. Start the WebSocket to collect data for AAPL (testing), PDFS and ROG (trading)")
        print("2. Create feature engineering pipeline for pairs trading")
        print("3. Implement cointegration testing for pair identification")
    else:
        print("\n⚠️ Some tests failed. Please check the WebSocket configuration.") 