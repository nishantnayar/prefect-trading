#!/usr/bin/env python3
"""
PostgreSQL Optimization Script for Prefect Workers
This script optimizes PostgreSQL settings to handle multiple concurrent Prefect workers
and reduce the likelihood of deadlocks.
"""

import psycopg2
import sys
import os
from pathlib import Path

def run_optimization():
    """Run PostgreSQL optimization commands."""
    
    # Database connection parameters
    db_params = {
        'host': 'localhost',
        'database': 'trading_db',
        'user': 'postgres',
        'password': 'nishant'
    }
    
    # Optimization commands
    optimization_commands = [
        "ALTER SYSTEM SET max_connections = 200;",
        "ALTER SYSTEM SET deadlock_timeout = '5s';",
        "ALTER SYSTEM SET shared_buffers = '256MB';",
        "ALTER SYSTEM SET work_mem = '4MB';",
        "ALTER SYSTEM SET maintenance_work_mem = '64MB';",
        "ALTER SYSTEM SET checkpoint_completion_target = 0.9;",
        "ALTER SYSTEM SET wal_buffers = '16MB';",
        "ALTER SYSTEM SET effective_cache_size = '1GB';",
        "ALTER SYSTEM SET random_page_cost = 1.1;",
        "ALTER SYSTEM SET max_wal_size = '2GB';",
        "ALTER SYSTEM SET autovacuum_max_workers = 3;",
        "ALTER SYSTEM SET autovacuum_naptime = '10s';",
        "ALTER SYSTEM SET lock_timeout = '30s';",
        "ALTER SYSTEM SET max_prepared_transactions = 100;",
        "SELECT pg_reload_conf();"
    ]
    
    # Settings to check
    settings_to_check = [
        'max_connections',
        'deadlock_timeout',
        'shared_buffers',
        'work_mem',
        'maintenance_work_mem',
        'checkpoint_completion_target',
        'wal_buffers',
        'effective_cache_size',
        'random_page_cost',
        'max_wal_size',
        'autovacuum_max_workers',
        'autovacuum_naptime',
        'lock_timeout',
        'max_prepared_transactions'
    ]
    
    try:
        print("🔧 PostgreSQL Optimization for Prefect Workers")
        print("=" * 50)
        
        # Connect to database
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Connected to PostgreSQL successfully")
        print()
        
        # Run optimization commands
        print("Applying optimization settings...")
        for i, command in enumerate(optimization_commands, 1):
            try:
                cursor.execute(command)
                print(f"  {i:2d}. ✅ Applied: {command.split('=')[0].strip()}")
            except Exception as e:
                print(f"  {i:2d}. ⚠️  Warning: {command.split('=')[0].strip()} - {str(e)}")
        
        print()
        print("✅ All optimization settings applied")
        print()
        
        # Check current settings
        print("📊 Current PostgreSQL Settings:")
        print("-" * 40)
        
        for setting in settings_to_check:
            try:
                cursor.execute(f"SHOW {setting};")
                result = cursor.fetchone()
                if result:
                    print(f"  {setting:30} = {result[0]}")
            except Exception as e:
                print(f"  {setting:30} = Error: {str(e)}")
        
        print()
        print("🎉 PostgreSQL optimization completed successfully!")
        print()
        print("💡 These optimizations will help reduce deadlocks when running multiple Prefect workers.")
        print("   You may need to restart PostgreSQL for some settings to take full effect.")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Database connection error: {e}")
        print()
        print("💡 Make sure PostgreSQL is running and accessible with these credentials:")
        print(f"   Host: {db_params['host']}")
        print(f"   Database: {db_params['database']}")
        print(f"   User: {db_params['user']}")
        print(f"   Password: {db_params['password']}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_optimization() 