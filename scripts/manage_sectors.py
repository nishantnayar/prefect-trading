#!/usr/bin/env python3
"""
Sector Management Utility

This script helps manage sector configuration and provides insights into
available sectors and their symbols. It's useful for configuring which
sectors to use for trading and analysis.
"""

import sys
import os
from pathlib import Path
import yaml
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.sources.symbol_manager import SymbolManager


def show_sector_summary():
    """Show summary of all sectors and their symbol counts."""
    print("=" * 60)
    print("SECTOR SUMMARY")
    print("=" * 60)
    
    symbol_manager = SymbolManager()
    sector_summary = symbol_manager.get_sector_summary()
    
    if not sector_summary:
        print("No sectors found in database.")
        return
    
    total_symbols = sum(sector_summary.values())
    print(f"Total symbols across all sectors: {total_symbols}")
    print()
    
    # Sort by symbol count (descending)
    sorted_sectors = sorted(sector_summary.items(), key=lambda x: x[1], reverse=True)
    
    for sector, count in sorted_sectors:
        percentage = (count / total_symbols) * 100
        print(f"{sector:<25} {count:>3} symbols ({percentage:>5.1f}%)")
    
    print()
    print("=" * 60)


def show_sector_symbols(sector: str, limit: int = 20):
    """Show symbols for a specific sector."""
    print(f"=" * 60)
    print(f"SYMBOLS FOR SECTOR: {sector.upper()}")
    print("=" * 60)
    
    symbol_manager = SymbolManager()
    symbols = symbol_manager.get_symbols_by_sector(sector)
    
    if not symbols:
        print(f"No symbols found for sector: {sector}")
        return
    
    print(f"Found {len(symbols)} symbols in {sector} sector:")
    print()
    
    # Show symbols in columns
    for i in range(0, len(symbols), 5):
        row_symbols = symbols[i:i+5]
        row_str = "  ".join(f"{symbol:<8}" for symbol in row_symbols)
        print(row_str)
    
    if len(symbols) > limit:
        print(f"\n... and {len(symbols) - limit} more symbols")
    
    print()
    print("=" * 60)


def show_current_config():
    """Show current sector configuration."""
    print("=" * 60)
    print("CURRENT SECTOR CONFIGURATION")
    print("=" * 60)
    
    symbol_manager = SymbolManager()
    active_sectors = symbol_manager.get_active_sectors()
    available_sectors = symbol_manager.get_available_sectors()
    
    print(f"Active sectors: {active_sectors}")
    print(f"Available sectors: {available_sectors}")
    print()
    
    # Show what symbols would be used with current config
    symbols = symbol_manager.get_active_symbols()
    print(f"Symbols with current active sectors: {len(symbols)}")
    if symbols:
        print(f"First 10 symbols: {symbols[:10]}")
        if len(symbols) > 10:
            print(f"... and {len(symbols) - 10} more")
    
    print()
    print("=" * 60)


def update_active_sectors(sectors: list):
    """Update the active sectors in config.yaml."""
    print(f"=" * 60)
    print(f"UPDATING ACTIVE SECTORS TO: {sectors}")
    print("=" * 60)
    
    config_path = project_root / "config" / "config.yaml"
    
    try:
        # Read current config
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update active sectors
        if 'sectors' not in config:
            config['sectors'] = {}
        
        config['sectors']['active'] = sectors
        
        # Write updated config
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Updated {config_path}")
        print(f"Active sectors set to: {sectors}")
        
        # Show what this means
        symbol_manager = SymbolManager()
        symbols = symbol_manager.get_active_symbols()
        print(f"Symbols with new configuration: {len(symbols)}")
        
    except Exception as e:
        print(f"❌ Error updating config: {e}")
    
    print()
    print("=" * 60)


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/manage_sectors.py summary                    - Show sector summary")
        print("  python scripts/manage_sectors.py symbols <sector>          - Show symbols for sector")
        print("  python scripts/manage_sectors.py config                     - Show current config")
        print("  python scripts/manage_sectors.py set-active <sector1> ...  - Set active sectors")
        print()
        print("Examples:")
        print("  python scripts/manage_sectors.py summary")
        print("  python scripts/manage_sectors.py symbols Technology")
        print("  python scripts/manage_sectors.py set-active Technology")
        print("  python scripts/manage_sectors.py set-active Technology Healthcare")
        return
    
    command = sys.argv[1].lower()
    
    if command == "summary":
        show_sector_summary()
    
    elif command == "symbols":
        if len(sys.argv) < 3:
            print("Error: Please specify a sector name")
            return
        sector = sys.argv[2]
        show_sector_symbols(sector)
    
    elif command == "config":
        show_current_config()
    
    elif command == "set-active":
        if len(sys.argv) < 3:
            print("Error: Please specify at least one sector")
            return
        sectors = sys.argv[2:]
        update_active_sectors(sectors)
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'summary', 'symbols', 'config', or 'set-active'")


if __name__ == "__main__":
    main() 