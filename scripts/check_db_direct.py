#!/usr/bin/env python3
"""
Direct Database Schema Check

A script that sets database credentials directly for testing.
This bypasses the need for a .env file.
"""

import os
import sys
import psycopg2
from pathlib import Path
from datetime import datetime
import json

def set_database_credentials():
    """Set database credentials directly for testing."""
    # Set database credentials directly
    os.environ['DB_HOST'] = 'localhost'
    os.environ['DB_PORT'] = '5432'
    os.environ['DB_NAME'] = 'trading_system'
    os.environ['DB_USER'] = 'postgres'
    os.environ['DB_PASSWORD'] = 'nishant'
    
    print("🔧 Database credentials set directly:")
    print(f"   Host: {os.environ['DB_HOST']}")
    print(f"   Port: {os.environ['DB_PORT']}")
    print(f"   Database: {os.environ['DB_NAME']}")
    print(f"   User: {os.environ['DB_USER']}")

def get_db_connection():
    """Get database connection using environment variables."""
    # Set credentials
    set_database_credentials()
    
    # Get database credentials from environment
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'trading_system')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    
    if not db_user or not db_password:
        print("❌ Database credentials not found in environment variables.")
        return None
    
    try:
        print(f"🔌 Attempting to connect to {db_host}:{db_port}/{db_name} as {db_user}...")
        connection = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        return connection
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def check_database_schema():
    """Check and display the current database schema."""
    print("🔍 Direct Database Schema Check")
    print("="*50)
    
    # Get database connection
    connection = get_db_connection()
    if not connection:
        return 1
    
    try:
        cursor = connection.cursor()
        print("✅ Connected to database successfully!")
        
        # Get database info
        cursor.execute("SELECT current_database(), current_user, version();")
        db_info = cursor.fetchone()
        print(f"📊 Database: {db_info[0]}")
        print(f"👤 User: {db_info[1]}")
        print(f"🔧 PostgreSQL Version: {db_info[2].split(',')[0]}")
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📊 Found {len(tables)} tables in database:")
        print("-" * 30)
        
        for i, table in enumerate(tables, 1):
            print(f"{i:2d}. {table}")
        
        # Show detailed info for each table
        print(f"\n📋 DETAILED TABLE INFORMATION:")
        print("="*60)
        
        for table in tables:
            print(f"\n🔹 Table: {table}")
            print("-" * 40)
            
            # Get columns
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s
                ORDER BY ordinal_position;
            """, (table,))
            
            columns = cursor.fetchall()
            print("  Columns:")
            for col in columns:
                nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
                default = f" DEFAULT {col[3]}" if col[3] else ""
                print(f"    - {col[0]}: {col[1]} {nullable}{default}")
            
            # Get indexes
            cursor.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes 
                WHERE tablename = %s
                AND schemaname = 'public'
                ORDER BY indexname;
            """, (table,))
            
            indexes = cursor.fetchall()
            if indexes:
                print("  Indexes:")
                for idx in indexes:
                    print(f"    - {idx[0]}")
            
            # Get constraints
            cursor.execute("""
                SELECT constraint_name, constraint_type
                FROM information_schema.table_constraints 
                WHERE table_schema = 'public' 
                AND table_name = %s
                ORDER BY constraint_name;
            """, (table,))
            
            constraints = cursor.fetchall()
            if constraints:
                print("  Constraints:")
                for const in constraints:
                    print(f"    - {const[0]}: {const[1]}")
            
            # Get triggers
            cursor.execute("""
                SELECT trigger_name, event_manipulation, action_timing
                FROM information_schema.triggers 
                WHERE trigger_schema = 'public' 
                AND event_object_table = %s
                ORDER BY trigger_name;
            """, (table,))
            
            triggers = cursor.fetchall()
            if triggers:
                print("  Triggers:")
                for trig in triggers:
                    print(f"    - {trig[0]}: {trig[2]} {trig[1]}")
        
        # Show row counts for each table
        print(f"\n📈 TABLE ROW COUNTS:")
        print("="*30)
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count:,} rows")
            except Exception as e:
                print(f"  {table}: Error getting count - {e}")
        
        cursor.close()
        connection.close()
        
        print(f"\n✅ Schema check completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Error during schema check: {e}")
        if connection:
            connection.close()
        return 1

def main():
    """Main function."""
    return check_database_schema()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 