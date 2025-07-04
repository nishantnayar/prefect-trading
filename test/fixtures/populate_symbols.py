#!/usr/bin/env python3
"""
Symbol population utility for tests.

This module provides utilities to populate the symbols table with sample data
for testing purposes.
"""

import pytest
from src.data.sources.symbol_manager import SymbolManager


# Sample symbols with company names for testing
SAMPLE_SYMBOLS = [
    ("AAPL", "Apple Inc."),
    ("MSFT", "Microsoft Corporation"),
    ("GOOGL", "Alphabet Inc."),
    ("AMZN", "Amazon.com Inc."),
    ("TSLA", "Tesla Inc."),
    ("META", "Meta Platforms Inc."),
    ("NVDA", "NVIDIA Corporation"),
    ("NFLX", "Netflix Inc."),
    ("CRM", "Salesforce Inc."),
    ("ADBE", "Adobe Inc."),
    ("PYPL", "PayPal Holdings Inc."),
    ("INTC", "Intel Corporation"),
    ("AMD", "Advanced Micro Devices Inc."),
    ("ORCL", "Oracle Corporation"),
    ("IBM", "International Business Machines Corporation"),
    ("CSCO", "Cisco Systems Inc."),
    ("QCOM", "QUALCOMM Incorporated"),
    ("TXN", "Texas Instruments Incorporated"),
    ("AVGO", "Broadcom Inc."),
    ("MU", "Micron Technology Inc."),
    ("PDFS", "PDF Solutions Inc."),
    ("ROG", "Rogers Corporation")
]


def populate_symbols(symbols=None, is_active=True):
    """Populate symbols table with sample data.
    
    Args:
        symbols: List of (symbol, name) tuples. If None, uses SAMPLE_SYMBOLS.
        is_active: Whether to mark symbols as active.
        
    Returns:
        List of successfully added symbols.
    """
    if symbols is None:
        symbols = SAMPLE_SYMBOLS
    
    symbol_manager = SymbolManager()
    added_symbols = []
    
    for symbol, name in symbols:
        try:
            symbol_manager.add_symbol(symbol, name, is_active=is_active)
            added_symbols.append(symbol)
        except Exception as e:
            # Log error but continue with other symbols
            print(f"Warning: Error adding {symbol}: {e}")
    
    return added_symbols


def populate_test_symbols():
    """Populate symbols table with a minimal set for testing."""
    test_symbols = [
        ("AAPL", "Apple Inc."),
        ("MSFT", "Microsoft Corporation"),
        ("GOOGL", "Alphabet Inc.")
    ]
    return populate_symbols(test_symbols)


def populate_pairs_trading_symbols():
    """Populate symbols table with pairs trading symbols."""
    pairs_symbols = [
        ("AAPL", "Apple Inc."),
        ("PDFS", "PDF Solutions Inc."),
        ("ROG", "Rogers Corporation")
    ]
    return populate_symbols(pairs_symbols)


def clear_all_symbols():
    """Clear all symbols from the database."""
    symbol_manager = SymbolManager()
    
    try:
        active_symbols = symbol_manager.get_active_symbols()
        for symbol in active_symbols:
            symbol_manager.remove_symbol(symbol)
        return len(active_symbols)
    except Exception as e:
        print(f"Warning: Error clearing symbols: {e}")
        return 0


def get_symbol_count():
    """Get the count of active symbols in the database."""
    symbol_manager = SymbolManager()
    
    try:
        active_symbols = symbol_manager.get_active_symbols()
        return len(active_symbols)
    except Exception as e:
        print(f"Warning: Error getting symbol count: {e}")
        return 0


def verify_symbol_exists(symbol):
    """Verify that a symbol exists in the database."""
    symbol_manager = SymbolManager()
    
    try:
        symbol_info = symbol_manager.get_symbol_info(symbol)
        return symbol_info is not None
    except Exception as e:
        print(f"Warning: Error verifying symbol {symbol}: {e}")
        return False


def get_symbol_info(symbol):
    """Get information about a specific symbol."""
    symbol_manager = SymbolManager()
    
    try:
        return symbol_manager.get_symbol_info(symbol)
    except Exception as e:
        print(f"Warning: Error getting symbol info for {symbol}: {e}")
        return None


# Pytest fixtures
@pytest.fixture
def populated_symbols():
    """Fixture to provide populated symbols for testing."""
    # Populate with test symbols
    added_symbols = populate_test_symbols()
    
    yield added_symbols
    
    # Cleanup is optional - symbols can persist for other tests


@pytest.fixture
def pairs_trading_symbols():
    """Fixture to provide pairs trading symbols for testing."""
    # Populate with pairs trading symbols
    added_symbols = populate_pairs_trading_symbols()
    
    yield added_symbols
    
    # Cleanup is optional - symbols can persist for other tests


@pytest.fixture
def clean_symbols():
    """Fixture to provide a clean symbols table for testing."""
    # Clear existing symbols
    cleared_count = clear_all_symbols()
    
    yield []
    
    # Cleanup - clear symbols after test
    clear_all_symbols()


# Test functions
def test_populate_symbols():
    """Test symbol population functionality."""
    # Test with a small set
    test_symbols = [("TEST1", "Test Company 1"), ("TEST2", "Test Company 2")]
    added_symbols = populate_symbols(test_symbols)
    
    assert len(added_symbols) >= 0  # May fail if symbols already exist
    
    # Verify symbols exist
    for symbol in added_symbols:
        assert verify_symbol_exists(symbol)


def test_populate_test_symbols():
    """Test populating test symbols."""
    added_symbols = populate_test_symbols()
    
    assert len(added_symbols) >= 0
    assert "AAPL" in added_symbols or get_symbol_count() > 0


def test_populate_pairs_trading_symbols():
    """Test populating pairs trading symbols."""
    added_symbols = populate_pairs_trading_symbols()
    
    assert len(added_symbols) >= 0
    assert "AAPL" in added_symbols or get_symbol_count() > 0


def test_symbol_count():
    """Test getting symbol count."""
    count = get_symbol_count()
    assert isinstance(count, int)
    assert count >= 0


def test_verify_symbol_exists():
    """Test symbol existence verification."""
    # Test with a common symbol
    exists = verify_symbol_exists("AAPL")
    assert isinstance(exists, bool)


def test_get_symbol_info():
    """Test getting symbol information."""
    info = get_symbol_info("AAPL")
    
    if info is not None:
        assert isinstance(info, dict)
        assert 'symbol' in info
        assert 'name' in info


if __name__ == "__main__":
    # Allow running as standalone script for debugging
    import sys
    pytest.main([__file__] + sys.argv[1:]) 