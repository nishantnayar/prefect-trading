#!/usr/bin/env python3
"""
Symbol Management Utility for Data Recycler

This script helps manage symbol configuration and check data availability
for the data recycler system. It's particularly useful when transitioning
from testing symbols to actual trading symbols.
"""

import sys
import os
from pathlib import Path
import yaml
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.database_connectivity import DatabaseConnectivity
from src.utils.websocket_config import get_websocket_config, reload_config


def update_config_symbols(symbols, config_path=None):
    """Update the config.yaml file with new symbols"""
    if config_path is None:
        config_path = project_root / "config" / "config.yaml"

    # Read current config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Update symbols in both websocket and recycler sections
    config['websocket']['symbols'] = symbols
    config['websocket']['recycler']['symbols'] = symbols

    # Write updated config
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    print(f"Updated config.yaml with symbols: {symbols}")


def show_current_config():
    """Show current WebSocket configuration"""
    config = get_websocket_config()
    print("\n=== Current Configuration ===")
    print(config.get_config_summary())

    # Simple data availability check
    symbols = config.get_websocket_symbols()
    print(f"\n=== Quick Data Check ===")

    db = DatabaseConnectivity()
    try:
        with db.get_session() as cursor:
            for symbol in symbols:
                cursor.execute("SELECT COUNT(*) FROM market_data WHERE symbol = %s", (symbol,))
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"✅ {symbol}: {count} records available")
                else:
                    print(f"❌ {symbol}: No data (will use AAPL as proxy)")
    finally:
        db.close()


def switch_to_pairs_trading():
    """Switch configuration to pairs trading symbols"""
    pairs_symbols = ["AAPL", "PDFS", "ROG"]
    update_config_symbols(pairs_symbols)
    print(f"\nSwitched to pairs trading symbols: {pairs_symbols}")
    print("Note: PDFS and ROG will use AAPL data as proxy until real data is available")


def switch_to_testing():
    """Switch configuration to testing symbols"""
    testing_symbols = ["AAPL"]
    update_config_symbols(testing_symbols)
    print(f"\nSwitched to testing symbols: {testing_symbols}")


def add_symbol(symbol):
    """Add a symbol to the current configuration"""
    config = get_websocket_config()
    current_symbols = config.get_websocket_symbols()

    if symbol not in current_symbols:
        new_symbols = current_symbols + [symbol]
        update_config_symbols(new_symbols)
        print(f"Added {symbol} to configuration")
    else:
        print(f"{symbol} is already in configuration")


def remove_symbol(symbol):
    """Remove a symbol from the current configuration"""
    config = get_websocket_config()
    current_symbols = config.get_websocket_symbols()

    if symbol in current_symbols:
        new_symbols = [s for s in current_symbols if s != symbol]
        update_config_symbols(new_symbols)
        print(f"Removed {symbol} from configuration")
    else:
        print(f"{symbol} is not in current configuration")


def show_help():
    """Show help information"""
    print("""
Symbol Management Utility

Usage:
    python scripts/manage_symbols.py [command] [options]

Commands:
    status              - Show current configuration and quick data check
    pairs               - Switch to pairs trading symbols (AAPL, PDFS, ROG)
    testing             - Switch to testing symbols (AAPL only)
    add <symbol>        - Add a symbol to current configuration
    remove <symbol>     - Remove a symbol from current configuration
    help                - Show this help message

Examples:
    python scripts/manage_symbols.py status
    python scripts/manage_symbols.py pairs
    python scripts/manage_symbols.py add MSFT
    python scripts/manage_symbols.py remove PDFS

Note: After collecting PDFS/ROG data on Monday, simply run 'status' to verify
data is available, then continue using the system normally.
    """)


def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_current_config()
        return

    command = sys.argv[1].lower()

    if command == "status":
        show_current_config()

    elif command == "pairs":
        switch_to_pairs_trading()
        show_current_config()

    elif command == "testing":
        switch_to_testing()
        show_current_config()

    elif command == "add" and len(sys.argv) >= 3:
        symbol = sys.argv[2].upper()
        add_symbol(symbol)
        show_current_config()

    elif command == "remove" and len(sys.argv) >= 3:
        symbol = sys.argv[2].upper()
        remove_symbol(symbol)
        show_current_config()

    elif command == "help":
        show_help()

    else:
        print("Invalid command. Use 'help' for usage information.")


if __name__ == "__main__":
    main()
