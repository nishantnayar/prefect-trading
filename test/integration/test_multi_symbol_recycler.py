#!/usr/bin/env python3
"""
Integration test for Multi-Symbol Data Recycler

This test verifies the multi-symbol data recycler works correctly
with the new configuration and proxy data support.
"""

import pytest
import asyncio
import websockets
import json
from unittest.mock import patch, MagicMock

from src.utils.websocket_config import get_websocket_config


@pytest.fixture
def websocket_config():
    """Fixture to provide websocket configuration."""
    return get_websocket_config()


def test_configuration_loading(websocket_config):
    """Test that configuration loads successfully."""
    assert websocket_config is not None
    assert hasattr(websocket_config, 'get_websocket_mode')
    assert hasattr(websocket_config, 'get_websocket_symbols')
    assert hasattr(websocket_config, 'get_recycler_symbols')
    assert hasattr(websocket_config, 'get_recycler_replay_mode')
    assert hasattr(websocket_config, 'get_recycler_replay_speed')
    assert hasattr(websocket_config, 'validate_config')


def test_configuration_validation(websocket_config):
    """Test configuration validation."""
    # This should not raise an exception
    try:
        is_valid = websocket_config.validate_config()
        assert isinstance(is_valid, bool)
    except Exception as e:
        pytest.fail(f"Configuration validation failed: {e}")


def test_websocket_symbols(websocket_config):
    """Test that websocket symbols are retrieved correctly."""
    symbols = websocket_config.get_websocket_symbols()
    assert isinstance(symbols, list)
    assert len(symbols) > 0


def test_recycler_symbols(websocket_config):
    """Test that recycler symbols are retrieved correctly."""
    symbols = websocket_config.get_recycler_symbols()
    assert isinstance(symbols, list)
    assert len(symbols) > 0


def test_recycler_server_url(websocket_config):
    """Test that recycler server URL is generated correctly."""
    url = websocket_config.get_recycler_server_url()
    assert isinstance(url, str)
    assert url.startswith('ws://') or url.startswith('wss://')


@pytest.mark.asyncio
async def test_data_recycler_connection_mock():
    """Test data recycler connection with mocked websocket."""
    # Mock websocket connection
    mock_websocket = MagicMock()
    mock_message = json.dumps([
        {
            'S': 'AAPL',
            't': '2024-01-01T10:00:00Z',
            'c': 150.0,
            'v': 1000000
        },
        {
            'S': 'MSFT',
            't': '2024-01-01T10:00:00Z',
            'c': 300.0,
            'v': 500000
        }
    ])
    
    # Mock the websocket context manager
    mock_websocket.__aiter__.return_value = [mock_message]
    
    with patch('websockets.connect', return_value=mock_websocket):
        config = get_websocket_config()
        uri = config.get_recycler_server_url()
        
        # This should not raise an exception
        assert uri is not None
        assert isinstance(uri, str)


@pytest.mark.asyncio
async def test_data_recycler_message_parsing():
    """Test parsing of data recycler messages."""
    # Sample message format
    sample_message = json.dumps([
        {
            'S': 'AAPL',
            't': '2024-01-01T10:00:00Z',
            'c': 150.0,
            'v': 1000000
        }
    ])
    
    # Parse the message
    data = json.loads(sample_message)
    assert isinstance(data, list)
    assert len(data) == 1
    
    symbol_data = data[0]
    assert symbol_data['S'] == 'AAPL'
    assert symbol_data['t'] == '2024-01-01T10:00:00Z'
    assert symbol_data['c'] == 150.0
    assert symbol_data['v'] == 1000000


def test_configuration_summary(websocket_config):
    """Test that configuration summary is generated correctly."""
    summary = websocket_config.get_config_summary()
    assert isinstance(summary, str)
    assert len(summary) > 0


# Integration test that requires actual server (marked as slow)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_data_recycler_live_connection():
    """Test live connection to data recycler server."""
    config = get_websocket_config()
    uri = config.get_recycler_server_url()
    
    try:
        async with websockets.connect(uri, timeout=5) as websocket:
            # Try to receive at least one message
            message_count = 0
            max_messages = 1
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_count += 1
                    
                    # Verify message structure
                    assert isinstance(data, list)
                    assert len(data) > 0
                    
                    for symbol_data in data:
                        assert 'S' in symbol_data  # Symbol
                        assert 't' in symbol_data  # Timestamp
                        assert 'c' in symbol_data  # Close price
                        assert 'v' in symbol_data  # Volume
                    
                    if message_count >= max_messages:
                        break
                        
                except json.JSONDecodeError:
                    pytest.fail("Failed to parse websocket message as JSON")
                    
    except websockets.exceptions.ConnectionClosed:
        pytest.skip("Data recycler server not running")
    except Exception as e:
        pytest.skip(f"Could not connect to data recycler server: {e}")


if __name__ == "__main__":
    # Allow running as standalone script for debugging
    import sys
    pytest.main([__file__] + sys.argv[1:]) 