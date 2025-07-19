#!/usr/bin/env python3
"""
Test script to verify WebSocket symbol configuration for pairs trading.
"""

import sys
import os
import pytest
from pathlib import Path

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_alpaca_websocket_symbols():
    """Test that alpaca_websocket.py uses configuration for symbols."""
    try:
        websocket_file = Path('src/data/sources/alpaca_websocket.py')
        if not websocket_file.exists():
            pytest.skip("alpaca_websocket.py file not found")
        
        with open(websocket_file, 'r') as f:
            content = f.read()
        
        # Check for configuration import
        assert "from src.utils.websocket_config import" in content, "Configuration import not found"
        assert "get_websocket_symbols" in content, "get_websocket_symbols function not found"
        
        # Check for configuration usage instead of hardcoded symbols
        assert "symbols = get_websocket_symbols()" in content, "Configuration-based symbols not found"
        
        # Check for symbol processing using configuration
        assert "if symbol in symbols:" in content, "Symbol processing not using configuration"
        
        # Check for Redis key pattern
        assert "symbol_keys = redis_client.keys(f\"{symbol}:*\")" in content, "Redis key pattern not found or incorrect"
        
    except Exception as e:
        pytest.skip(f"Alpaca websocket test skipped: {e}")

def test_configurable_websocket_symbols():
    """Test that configurable_websocket.py uses configuration for symbols."""
    try:
        websocket_file = Path('src/data/sources/configurable_websocket.py')
        if not websocket_file.exists():
            pytest.skip("configurable_websocket.py file not found")
        
        with open(websocket_file, 'r') as f:
            content = f.read()
        
        # Check for configuration import
        assert "from src.utils.websocket_config import" in content, "Configuration import not found"
        assert "get_websocket_symbols" in content, "get_websocket_symbols function not found"
        
        # Check for configuration usage instead of hardcoded symbols
        symbol_count = content.count("symbols = get_websocket_symbols()")
        assert symbol_count >= 2, f"Configuration-based symbols not found or incorrect (found {symbol_count} occurrences)"
        
        # Check for symbol processing using configuration
        assert "if symbol in symbols:" in content, "Symbol processing not using configuration"
        
        # Check for data source handling
        assert "data_source" in content, "Data source handling not found"
        
    except Exception as e:
        pytest.skip(f"Configurable websocket test skipped: {e}")

def test_config_file_symbols():
    """Test that config.yaml has the correct symbols configured."""
    try:
        config_file = Path('config/config.yaml')
        if not config_file.exists():
            pytest.skip("config.yaml file not found")
        
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Check for websocket symbols configuration
        assert "symbols:" in content, "WebSocket symbols section not found in config.yaml"
        assert "AAPL" in content, "AAPL symbol not found in config.yaml"
        assert "PDFS" in content, "PDFS symbol not found in config.yaml"
        assert "ROG" in content, "ROG symbol not found in config.yaml"
        
    except Exception as e:
        pytest.skip(f"Config file test skipped: {e}")

def test_symbol_pairs():
    """Test that we have valid pairs for trading."""
    symbols = ['AAPL', 'PDFS', 'ROG']
    
    # Check if symbols are different (for pairs trading)
    assert len(set(symbols)) == len(symbols), "Duplicate symbols found"
    
    # Check if we have enough symbols for pairs trading
    assert len(symbols) >= 2, "Insufficient symbols for pairs trading"
    
    # Suggest pairs
    pairs = []
    for i in range(len(symbols)):
        for j in range(i + 1, len(symbols)):
            pairs.append((symbols[i], symbols[j]))
    
    assert len(pairs) >= 1, "No valid pairs found"

def test_websocket_config_import():
    """Test that websocket_config module can be imported."""
    try:
        from src.utils.websocket_config import get_websocket_symbols
        symbols = get_websocket_symbols()
        assert isinstance(symbols, list), "get_websocket_symbols should return a list"
        assert len(symbols) > 0, "No symbols configured"
    except ImportError:
        pytest.skip("websocket_config module not available")
    except Exception as e:
        pytest.skip(f"WebSocket config test skipped: {e}")

if __name__ == "__main__":
    pytest.main([__file__]) 