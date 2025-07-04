#!/usr/bin/env python3
"""
Test script for symbol analysis functionality.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.data.sources.symbol_manager import SymbolManager
from src.database.database_connectivity import DatabaseConnectivity

def test_symbol_manager():
    """Test symbol manager functionality."""
    print("Testing SymbolManager...")
    
    symbol_manager = SymbolManager()
    
    # Get active symbols
    active_symbols = symbol_manager.get_active_symbols()
    print(f"Active symbols: {len(active_symbols)}")
    print(f"First 5 symbols: {active_symbols[:5]}")
    
    # Get symbol info for AAPL
    if 'AAPL' in active_symbols:
        symbol_info = symbol_manager.get_symbol_info('AAPL')
        print(f"AAPL info: {symbol_info}")
    
    return active_symbols

def test_database_queries():
    """Test database queries used in symbol analysis."""
    print("\nTesting database queries...")
    
    db = DatabaseConnectivity()
    
    # Test market data query
    with db.get_session() as cursor:
        cursor.execute("""
            SELECT 
                COUNT(*) as data_points,
                MIN(timestamp) as first_data,
                MAX(timestamp) as last_data,
                AVG(close) as avg_price,
                MAX(close) as max_price,
                MIN(close) as min_price,
                AVG(volume) as avg_volume
            FROM market_data 
            WHERE symbol = 'AAPL'
        """)
        
        market_summary = cursor.fetchone()
        if market_summary:
            print(f"Market data summary for AAPL:")
            print(f"  Data points: {market_summary[0]}")
            print(f"  First data: {market_summary[1]}")
            print(f"  Last data: {market_summary[2]}")
            print(f"  Avg price: ${market_summary[3]:.2f}" if market_summary[3] else "  Avg price: N/A")
            print(f"  Max price: ${market_summary[4]:.2f}" if market_summary[4] else "  Max price: N/A")
            print(f"  Min price: ${market_summary[5]:.2f}" if market_summary[5] else "  Min price: N/A")
            print(f"  Avg volume: {market_summary[6]:,.0f}" if market_summary[6] else "  Avg volume: N/A")
        else:
            print("No market data found for AAPL")
    
    # Test company info query
    with db.get_session() as cursor:
        cursor.execute("""
            SELECT 
                "longName",
                sector,
                industry,
                "marketCap",
                "currentPrice"
            FROM yahoo_company_info 
            WHERE symbol = 'AAPL'
        """)
        
        company_info = cursor.fetchone()
        if company_info:
            print(f"\nCompany info for AAPL:")
            print(f"  Name: {company_info[0]}")
            print(f"  Sector: {company_info[1]}")
            print(f"  Industry: {company_info[2]}")
            print(f"  Market Cap: ${company_info[3]:,.0f}" if company_info[3] else "  Market Cap: N/A")
            print(f"  Current Price: ${company_info[4]:.2f}" if company_info[4] else "  Current Price: N/A")
        else:
            print("No company info found for AAPL")
    
    # Test news query
    with db.get_session() as cursor:
        cursor.execute("""
            SELECT 
                title,
                source_name,
                published_at
            FROM news_articles 
            WHERE title ILIKE '%AAPL%' OR description ILIKE '%AAPL%'
            ORDER BY published_at DESC
            LIMIT 3
        """)
        
        news = cursor.fetchall()
        if news:
            print(f"\nRecent news for AAPL:")
            for article in news:
                print(f"  - {article[0]} ({article[1]}, {article[2]})")
        else:
            print("No news found for AAPL")

def main():
    """Main test function."""
    print("=== Symbol Analysis Test ===\n")
    
    try:
        # Test symbol manager
        active_symbols = test_symbol_manager()
        
        # Test database queries
        test_database_queries()
        
        print(f"\n✅ All tests completed successfully!")
        print(f"Found {len(active_symbols)} active symbols in database")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 