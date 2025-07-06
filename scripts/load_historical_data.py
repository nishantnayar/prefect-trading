#!/usr/bin/env python3
"""
Script to load historical market data for all symbols.

This script:
1. Runs the database migration to create market_data_historical table
2. Loads 1-minute historical data for all active symbols
3. Provides options for different timeframes and date ranges
"""

import sys
import os
import argparse
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.database.database_connectivity import DatabaseConnectivity
from src.data.sources.alpaca_historical_loader import AlpacaDataLoader
from alpaca.data.timeframe import TimeFrame
from loguru import logger


def run_migration():
    """Run the migration to create market_data_historical table."""
    try:
        db = DatabaseConnectivity()
        
        # Read migration file
        migration_file = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'migrations', 
            '010_create_market_data_historical.sql'
        )
        
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        with db.get_session() as cursor:
            cursor.execute(migration_sql)
            logger.info("Successfully created market_data_historical table")
            
    except Exception as e:
        logger.error(f"Error running migration: {str(e)}")
        raise


def load_historical_data(timeframe='hour', days_back=None, symbols=None):
    """
    Load historical data for symbols.
    
    Args:
        timeframe: 'hour' or 'minute'
        days_back: Number of days to look back
        symbols: List of specific symbols to load (None for all active symbols)
    """
    try:
        loader = AlpacaDataLoader()
        
        # Convert timeframe string to TimeFrame enum
        if timeframe == 'minute':
            tf = TimeFrame.Minute
            if days_back is None or days_back > 7:
                days_back = 7
                logger.info("Using 7-day limit for 1-minute data due to Alpaca API restrictions")
        else:
            tf = TimeFrame.Hour
            if days_back is None:
                days_back = 30
        
        logger.info(f"Loading {timeframe} data for {days_back} days")
        
        if symbols:
            # Load data for specific symbols
            if timeframe == 'minute':
                loader.load_1min_historical_data(symbols=symbols, days_back=days_back)
            else:
                data = loader.get_historical_data(
                    symbols=symbols,
                    start_date=(datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d'),
                    end_date=datetime.now().strftime('%Y-%m-%d'),
                    timeframe=tf
                )
                if data:
                    table_name = "market_data_historical" if timeframe == 'minute' else "market_data"
                    loader.store_historical_data(data, table_name)
        else:
            # Load data for all symbols
            if timeframe == 'minute':
                # Use the dedicated method for 1-minute data
                loader.load_1min_historical_data(days_back=days_back)
            else:
                # Use the general method for hourly data
                loader.load_all_symbols_historical_data(timeframe=tf, days_back=days_back)
            
    except Exception as e:
        logger.error(f"Error loading historical data: {str(e)}")
        raise


def main():
    parser = argparse.ArgumentParser(description='Load historical market data')
    parser.add_argument('--timeframe', choices=['hour', 'minute'], default='hour',
                       help='Data timeframe (default: hour)')
    parser.add_argument('--days', type=int, 
                       help='Number of days to look back (max 7 for minute data)')
    parser.add_argument('--symbols', nargs='+', 
                       help='Specific symbols to load (default: all active symbols)')
    parser.add_argument('--migrate-only', action='store_true',
                       help='Only run migration, skip data loading')
    
    args = parser.parse_args()
    
    try:
        # Run migration first
        logger.info("Running database migration...")
        run_migration()
        
        if args.migrate_only:
            logger.info("Migration completed. Skipping data loading.")
            return
        
        # Load historical data
        logger.info("Loading historical data...")
        load_historical_data(
            timeframe=args.timeframe,
            days_back=args.days,
            symbols=args.symbols
        )
        
        logger.info("Historical data loading completed successfully!")
        
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 