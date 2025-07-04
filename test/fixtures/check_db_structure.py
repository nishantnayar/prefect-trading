#!/usr/bin/env python3
"""
Database structure checking utility for tests.

This module provides utilities to check database table structure
and can be used in tests to verify database schema.
"""

import pytest
from src.database.database_connectivity import DatabaseConnectivity


def get_table_structure(table_name):
    """Get the structure of a specific table."""
    db = DatabaseConnectivity()
    
    try:
        with db.get_session() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, (table_name,))
            
            columns = cursor.fetchall()
            return [
                {
                    'name': col[0],
                    'type': col[1],
                    'nullable': col[2],
                    'default': col[3]
                }
                for col in columns
            ]
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


def check_table_exists(table_name):
    """Check if a table exists in the database."""
    db = DatabaseConnectivity()
    
    try:
        with db.get_session() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (table_name,))
            
            exists = cursor.fetchone()[0]
            return exists
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


def get_all_table_names():
    """Get all table names in the database."""
    db = DatabaseConnectivity()
    
    try:
        with db.get_session() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            tables = cursor.fetchall()
            return [table[0] for table in tables]
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


def check_market_data_structure():
    """Check the structure of market_data table."""
    return get_table_structure('market_data')


def check_symbols_structure():
    """Check the structure of symbols table."""
    return get_table_structure('symbols')


def check_news_articles_structure():
    """Check the structure of news_articles table."""
    return get_table_structure('news_articles')


def check_yahoo_company_info_structure():
    """Check the structure of yahoo_company_info table."""
    return get_table_structure('yahoo_company_info')


def check_yahoo_company_officers_structure():
    """Check the structure of yahoo_company_officers table."""
    return get_table_structure('yahoo_company_officers')


def verify_required_tables():
    """Verify that all required tables exist."""
    required_tables = [
        'market_data',
        'symbols',
        'news_articles',
        'yahoo_company_info',
        'yahoo_company_officers'
    ]
    
    existing_tables = get_all_table_names()
    missing_tables = [table for table in required_tables if table not in existing_tables]
    
    return {
        'all_exist': len(missing_tables) == 0,
        'missing_tables': missing_tables,
        'existing_tables': existing_tables
    }


def verify_table_columns(table_name, required_columns):
    """Verify that a table has the required columns."""
    structure = get_table_structure(table_name)
    existing_columns = [col['name'] for col in structure]
    
    missing_columns = [col for col in required_columns if col not in existing_columns]
    
    return {
        'all_exist': len(missing_columns) == 0,
        'missing_columns': missing_columns,
        'existing_columns': existing_columns
    }


# Test functions that can be used in pytest
def test_market_data_table_exists():
    """Test that market_data table exists."""
    assert check_table_exists('market_data'), "market_data table does not exist"


def test_symbols_table_exists():
    """Test that symbols table exists."""
    assert check_table_exists('symbols'), "symbols table does not exist"


def test_news_articles_table_exists():
    """Test that news_articles table exists."""
    assert check_table_exists('news_articles'), "news_articles table does not exist"


def test_yahoo_company_info_table_exists():
    """Test that yahoo_company_info table exists."""
    assert check_table_exists('yahoo_company_info'), "yahoo_company_info table does not exist"


def test_yahoo_company_officers_table_exists():
    """Test that yahoo_company_officers table exists."""
    assert check_table_exists('yahoo_company_officers'), "yahoo_company_officers table does not exist"


def test_all_required_tables_exist():
    """Test that all required tables exist."""
    result = verify_required_tables()
    assert result['all_exist'], f"Missing tables: {result['missing_tables']}"


def test_market_data_has_required_columns():
    """Test that market_data table has required columns."""
    required_columns = ['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume']
    result = verify_table_columns('market_data', required_columns)
    assert result['all_exist'], f"Missing columns in market_data: {result['missing_columns']}"


def test_symbols_has_required_columns():
    """Test that symbols table has required columns."""
    required_columns = ['symbol', 'name', 'is_active']
    result = verify_table_columns('symbols', required_columns)
    assert result['all_exist'], f"Missing columns in symbols: {result['missing_columns']}"


def test_news_articles_has_required_columns():
    """Test that news_articles table has required columns."""
    required_columns = ['title', 'source_name', 'url', 'published_at', 'description']
    result = verify_table_columns('news_articles', required_columns)
    assert result['all_exist'], f"Missing columns in news_articles: {result['missing_columns']}"


if __name__ == "__main__":
    # Allow running as standalone script for debugging
    import sys
    pytest.main([__file__] + sys.argv[1:]) 