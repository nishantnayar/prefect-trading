#!/usr/bin/env python3
"""
Debug script to test UI components and data fetching.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_symbol_selector():
    """Test the symbol selector component."""
    print("🧪 Testing Symbol Selector...")
    try:
        from src.ui.components.symbol_selector import display_symbol_selector
        from src.data.sources.symbol_manager import SymbolManager
        
        # Test SymbolManager directly
        sm = SymbolManager()
        symbols = sm.get_active_symbols()
        print(f"✅ Active symbols from SymbolManager: {symbols}")
        
        # Test symbol info
        if symbols:
            symbol_info = sm.get_symbol_info(symbols[0])
            print(f"✅ Symbol info for {symbols[0]}: {symbol_info}")
        
    except Exception as e:
        print(f"❌ Error in symbol selector: {e}")

def test_market_status():
    """Test the market status component."""
    print("\n🧪 Testing Market Status...")
    try:
        from src.ui.components.market_status import display_market_status
        from src.utils.market_hours import MarketHoursManager
        
        # Test MarketHoursManager directly
        mhm = MarketHoursManager()
        is_open = mhm.is_market_open()
        print(f"✅ Market is open: {is_open}")
        
    except Exception as e:
        print(f"❌ Error in market status: {e}")

def test_news_fetching():
    """Test news article fetching."""
    print("\n🧪 Testing News Fetching...")
    try:
        from src.database.database_connectivity import DatabaseConnectivity
        from src.ui.components.date_display import format_datetime_est_to_cst
        
        db = DatabaseConnectivity()
        with db.get_session() as cursor:
            query = """
                SELECT title, source_name, url, published_at, description
                FROM news_articles
                ORDER BY published_at DESC
                LIMIT 3
            """
            cursor.execute(query)
            articles = cursor.fetchall()
            
            print(f"✅ Found {len(articles)} recent articles")
            
            for i, article in enumerate(articles):
                title, source, url, published_at, description = article
                print(f"  Article {i+1}: {title[:50]}...")
                print(f"    Source: {source}")
                print(f"    Published: {published_at}")
                print(f"    Description: {description[:100] if description else 'No description'}...")
                print()
                
    except Exception as e:
        print(f"❌ Error in news fetching: {e}")

def test_portfolio_data():
    """Test portfolio data fetching."""
    print("\n🧪 Testing Portfolio Data...")
    try:
        from src.database.database_connectivity import DatabaseConnectivity
        
        db = DatabaseConnectivity()
        with db.get_session() as cursor:
            # Check if we have any market data
            cursor.execute("SELECT COUNT(*) FROM market_data")
            market_data_count = cursor.fetchone()[0]
            print(f"✅ Market data records: {market_data_count}")
            
            # Check if we have any symbols
            cursor.execute("SELECT COUNT(*) FROM symbols WHERE is_active = true")
            active_symbols_count = cursor.fetchone()[0]
            print(f"✅ Active symbols: {active_symbols_count}")
            
            # Get some sample market data
            if market_data_count > 0:
                cursor.execute("""
                    SELECT symbol, price, volume, timestamp 
                    FROM market_data 
                    ORDER BY timestamp DESC 
                    LIMIT 5
                """)
                recent_data = cursor.fetchall()
                print(f"✅ Recent market data:")
                for data in recent_data:
                    symbol, price, volume, timestamp = data
                    print(f"  {symbol}: ${price} (vol: {volume}) at {timestamp}")
                
    except Exception as e:
        print(f"❌ Error in portfolio data: {e}")

def main():
    """Main debug function."""
    print("🔍 Debugging UI Components")
    print("=" * 50)
    
    test_symbol_selector()
    test_market_status()
    test_news_fetching()
    test_portfolio_data()
    
    print("\n✅ Debug complete!")

if __name__ == "__main__":
    main() 