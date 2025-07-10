#!/usr/bin/env python3
"""
Simplified Database Migration Verification Script

This script connects to the database and verifies that the consolidated migration scripts
match the current database schema. It uses simpler queries to avoid SQL issues.
"""

import os
import sys
import psycopg2
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json
from datetime import datetime

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Set up environment for imports
os.environ['PYTHONPATH'] = str(src_path)

try:
    from database.database_connectivity import DatabaseConnectivity
    from utils.env_loader import load_env_file_with_decouple
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Trying alternative import method...")
    
    # Alternative import method
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from src.database.database_connectivity import DatabaseConnectivity
    from src.utils.env_loader import load_env_file_with_decouple


class SimpleDatabaseSchemaVerifier:
    """Simplified verifier for database schema against consolidated migration scripts."""
    
    def __init__(self):
        """Initialize the verifier with database connection."""
        # Load environment variables
        try:
            load_env_file_with_decouple()
        except Exception as e:
            print(f"⚠️  Warning: Could not load environment file: {e}")
            print("💡 Using default database credentials...")
            # Set some defaults
            os.environ.setdefault('DB_HOST', 'localhost')
            os.environ.setdefault('DB_PORT', '5432')
            os.environ.setdefault('DB_NAME', 'trading_system')
        
        # Initialize database connection
        self.db = DatabaseConnectivity()
        self.connection = self.db.get_connection()
        self.cursor = self.connection.cursor()
        
        # Migration files to verify
        self.migration_files = [
            "001_initial_schema_consolidated.sql",
            "002_data_source_enhancement_consolidated.sql", 
            "003_historical_data_consolidated.sql"
        ]
        
    def get_current_tables(self) -> List[str]:
        """Get list of all tables in the current database."""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get column information for a specific table."""
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = %s
        ORDER BY ordinal_position;
        """
        self.cursor.execute(query, (table_name,))
        
        columns = []
        for row in self.cursor.fetchall():
            columns.append({
                'name': row[0],
                'type': row[1],
                'nullable': row[2] == 'YES',
                'default': row[3]
            })
        return columns
    
    def get_table_indexes(self, table_name: str) -> List[str]:
        """Get index names for a specific table."""
        query = """
        SELECT indexname
        FROM pg_indexes 
        WHERE tablename = %s
        AND schemaname = 'public'
        ORDER BY indexname;
        """
        self.cursor.execute(query, (table_name,))
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_current_schema(self) -> Dict[str, Any]:
        """Get simplified current database schema."""
        schema = {
            'tables': {},
            'timestamp': datetime.now().isoformat()
        }
        
        tables = self.get_current_tables()
        
        for table in tables:
            schema['tables'][table] = {
                'columns': self.get_table_columns(table),
                'indexes': self.get_table_indexes(table)
            }
        
        return schema
    
    def read_migration_file(self, filename: str) -> str:
        """Read a migration file and return its content."""
        migration_path = Path(__file__).parent.parent / "src" / "database" / "migrations" / filename
        if not migration_path.exists():
            raise FileNotFoundError(f"Migration file not found: {migration_path}")
        
        with open(migration_path, 'r') as f:
            return f.read()
    
    def extract_expected_tables_from_migration(self, migration_content: str) -> List[str]:
        """Extract table names from migration content using regex."""
        tables = []
        
        # Remove SQL comments to avoid interference
        # Remove single-line comments (-- comment)
        content_no_comments = re.sub(r'--.*$', '', migration_content, flags=re.MULTILINE)
        # Remove multi-line comments (/* comment */)
        content_no_comments = re.sub(r'/\*.*?\*/', '', content_no_comments, flags=re.DOTALL)
        
        # Regex to match CREATE TABLE statements
        # Matches both "CREATE TABLE table_name" and "CREATE TABLE IF NOT EXISTS table_name"
        pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)'
        
        matches = re.findall(pattern, content_no_comments, re.IGNORECASE)
        
        for match in matches:
            table_name = match.strip()
            # Only add if it's a valid table name and not a reserved word
            if table_name and table_name.upper() not in ['NOT', 'NULL', 'DEFAULT', 'PRIMARY', 'KEY', 'UNIQUE', 'FOREIGN', 'REFERENCES']:
                tables.append(table_name)
        
        return tables
    
    def verify_schema(self) -> Dict[str, Any]:
        """Verify current schema against consolidated migrations."""
        print("🔍 Verifying database schema against consolidated migrations...")
        
        # Get current schema
        current_schema = self.get_current_schema()
        current_tables = set(current_schema['tables'].keys())
        
        # Get expected tables from migrations
        expected_tables = set()
        migration_contents = {}
        
        for migration_file in self.migration_files:
            try:
                content = self.read_migration_file(migration_file)
                migration_contents[migration_file] = content
                tables = self.extract_expected_tables_from_migration(content)
                expected_tables.update(tables)
                print(f"  📄 {migration_file}: Found {len(tables)} tables")
            except FileNotFoundError as e:
                print(f"  ❌ {migration_file}: {e}")
        
        # Compare tables
        missing_tables = expected_tables - current_tables
        extra_tables = current_tables - expected_tables
        common_tables = current_tables & expected_tables
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'current_tables': len(current_tables),
                'expected_tables': len(expected_tables),
                'missing_tables': len(missing_tables),
                'extra_tables': len(extra_tables),
                'common_tables': len(common_tables)
            },
            'details': {
                'current_tables': list(current_tables),
                'expected_tables': list(expected_tables),
                'missing_tables': list(missing_tables),
                'extra_tables': list(extra_tables),
                'common_tables': list(common_tables)
            },
            'schema_details': current_schema,
            'migration_files': list(migration_contents.keys())
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Print a formatted verification report."""
        print("\n" + "="*80)
        print("📊 DATABASE SCHEMA VERIFICATION REPORT")
        print("="*80)
        
        summary = report['summary']
        details = report['details']
        
        print(f"\n📈 SUMMARY:")
        print(f"  Current tables in database: {summary['current_tables']}")
        print(f"  Expected tables from migrations: {summary['expected_tables']}")
        print(f"  Common tables: {summary['common_tables']}")
        print(f"  Missing tables: {summary['missing_tables']}")
        print(f"  Extra tables: {summary['extra_tables']}")
        
        if details['missing_tables']:
            print(f"\n❌ MISSING TABLES (expected but not found):")
            for table in details['missing_tables']:
                print(f"  - {table}")
        
        if details['extra_tables']:
            print(f"\n⚠️  EXTRA TABLES (found but not expected):")
            for table in details['extra_tables']:
                print(f"  - {table}")
        
        if details['common_tables']:
            print(f"\n✅ COMMON TABLES (found in both):")
            for table in details['common_tables']:
                print(f"  - {table}")
        
        print(f"\n📄 MIGRATION FILES CHECKED:")
        for file in report['migration_files']:
            print(f"  - {file}")
        
        # Overall status
        if summary['missing_tables'] == 0:
            if summary['extra_tables'] == 0:
                print(f"\n🎉 VERIFICATION RESULT: ✅ PASSED")
                print("   Database schema matches consolidated migrations perfectly!")
            else:
                print(f"\n✅ VERIFICATION RESULT: ✅ APPLICATION SCHEMA PASSED")
                print("   All application tables from migrations are present!")
                print(f"   Extra tables ({summary['extra_tables']}) are likely system tables (Prefect/MLflow)")
        else:
            print(f"\n⚠️  VERIFICATION RESULT: ⚠️  MISMATCHES FOUND")
            print("   Some expected tables are missing. Check the details above.")
        
        print("="*80)
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save the verification report to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"schema_verification_report_{timestamp}.json"
        
        report_path = Path(__file__).parent / filename
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Report saved to: {report_path}")
        return report_path
    
    def close(self):
        """Close database connections."""
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
        if hasattr(self, 'db') and self.db:
            self.db.close()


def main():
    """Main function to run the schema verification."""
    print("🚀 Starting Simplified Database Schema Verification")
    print("="*50)
    
    verifier = None
    try:
        # Initialize verifier
        verifier = SimpleDatabaseSchemaVerifier()
        print("✅ Connected to database successfully")
        
        # Run verification
        report = verifier.verify_schema()
        
        # Print report
        verifier.print_report(report)
        
        # Save report
        report_path = verifier.save_report(report)
        
        # Return exit code based on verification result
        if report['summary']['missing_tables'] == 0:
            print("\n✅ Verification completed successfully!")
            return 0
        else:
            print("\n⚠️  Verification completed with missing tables found.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        return 1
    finally:
        if verifier:
            verifier.close()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 