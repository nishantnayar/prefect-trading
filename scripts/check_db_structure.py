#!/usr/bin/env python3
"""
Check database table structure.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.database.database_connectivity import DatabaseConnectivity

def check_table_structure():
    """Check the structure of key tables."""
    db = DatabaseConnectivity()
    
    with db.get_session() as cursor:
        # Check market_data table
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'market_data' 
            ORDER BY ordinal_position
        """)
        market_data_columns = cursor.fetchall()
        print("Market data table columns:")
        for col in market_data_columns:
            print(f"  {col[0]}: {col[1]}")
        
        print()
        
        # Check symbols table
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'symbols' 
            ORDER BY ordinal_position
        """)
        symbols_columns = cursor.fetchall()
        print("Symbols table columns:")
        for col in symbols_columns:
            print(f"  {col[0]}: {col[1]}")
        
        print()
        
        # Check news_articles table
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'news_articles' 
            ORDER BY ordinal_position
        """)
        news_columns = cursor.fetchall()
        print("News articles table columns:")
        for col in news_columns:
            print(f"  {col[0]}: {col[1]}")
        
        print()
        
        # Check yahoo_company_officers table
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'yahoo_company_officers' 
            ORDER BY ordinal_position
        """)
        officers_columns = cursor.fetchall()
        print("Yahoo company officers table columns:")
        for col in officers_columns:
            print(f"  {col[0]}: {col[1]}")
        
        print()
        
        # Check yahoo_company_info table
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'yahoo_company_info' 
            ORDER BY ordinal_position
        """)
        company_info_columns = cursor.fetchall()
        print("Yahoo company info table columns:")
        for col in company_info_columns:
            print(f"  {col[0]}: {col[1]}")
        
        print()

if __name__ == "__main__":
    check_table_structure() 