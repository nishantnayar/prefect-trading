import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data.symbol_manager import SymbolManager


def add_sample_symbols(symbol_manager):
    """Add some sample trading symbols."""
    # Add some major tech stocks
    symbols = [
        ("AAPL", "Apple Inc."),
        ("MSFT", "Microsoft Corporation"),
        ("GOOGL", "Alphabet Inc."),
        ("AMZN", "Amazon.com Inc."),
        ("META", "Meta Platforms Inc.")
    ]

    for symbol, name in symbols:
        symbol_manager.add_symbol(symbol, name)
        print(f"Added symbol: {symbol} ({name})")


def list_active_symbols(symbol_manager):
    """List all active symbols."""
    symbols = symbol_manager.get_active_symbols()
    print("\nActive Symbols:")
    for symbol in symbols:
        info = symbol_manager.get_symbol_info(symbol)
        print(f"- {symbol}: {info['name'] if info else 'Unknown'}")


def deactivate_symbol(symbol_manager, symbol):
    """Deactivate a symbol."""
    symbol_manager.deactivate_symbol(symbol)
    print(f"Deactivated symbol: {symbol}")


def main():
    """Main flow to demonstrate SymbolManager functionality."""
    symbol_manager = SymbolManager()

    # Add sample symbols
    add_sample_symbols(symbol_manager)

    # List all active symbols
    list_active_symbols(symbol_manager)

    # Deactivate a symbol
    # deactivate_symbol(symbol_manager, "META")

    # List symbols again to see the change
    list_active_symbols(symbol_manager)


if __name__ == "__main__":
    main()
