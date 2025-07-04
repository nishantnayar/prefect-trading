#!/usr/bin/env python3
"""
Populate symbols table with sample data for testing.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.data.sources.symbol_manager import SymbolManager

def populate_symbols():
    """Populate symbols table with sample data."""
    
    # Sample symbols with company names
    sample_symbols = [
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
    
    symbol_manager = SymbolManager()
    
    print("Populating symbols table...")
    
    for symbol, name in sample_symbols:
        try:
            symbol_manager.add_symbol(symbol, name, is_active=True)
            print(f"✅ Added {symbol} - {name}")
        except Exception as e:
            print(f"❌ Error adding {symbol}: {e}")
    
    print("\nSymbol population complete!")
    
    # Display active symbols
    active_symbols = symbol_manager.get_active_symbols()
    print(f"\nActive symbols in database: {len(active_symbols)}")
    for symbol in active_symbols:
        print(f"  - {symbol}")

if __name__ == "__main__":
    populate_symbols() 