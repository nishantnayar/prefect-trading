from prefect.blocks.system import Secret
import psycopg2
from psycopg2 import pool
from typing import Optional
import os
from contextlib import contextmanager
from pathlib import Path

# Load environment variables from .env file if it exists
def load_env_file():
    """Load environment variables from .env file"""
    # Look for .env file in config directory
    env_file = Path(__file__).parent.parent.parent / "config" / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load .env file on module import
load_env_file()


class DatabaseConnectivity:
    def __init__(self):
        self.connection_pool = None
        self._initialize_connection_pool()

    def _initialize_connection_pool(self):
        """Initialize the connection pool using environment variables or Prefect secrets."""
        try:
            # Try to get database credentials from environment variables first
            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = os.getenv('DB_PORT', '5432')
            db_name = os.getenv('DB_NAME', 'trading_system')
            db_user = os.getenv('DB_USER')
            db_password = os.getenv('DB_PASSWORD')
            
            # If environment variables are not set, try Prefect secrets
            if not db_user:
                try:
                    db_user = Secret.load("db-user").get()
                except:
                    pass
            
            if not db_password:
                try:
                    db_password = Secret.load("db-password").get()
                except:
                    pass
            
            if not db_user or not db_password:
                raise ValueError("Database credentials not found. Please set DB_USER and DB_PASSWORD environment variables or configure Prefect secrets.")

            # Create connection pool
            self.connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )
        except Exception as e:
            raise

    def get_connection(self):
        """Get a connection from the pool."""
        try:
            return self.connection_pool.getconn()
        except Exception as e:
            raise

    def release_connection(self, connection):
        """Release a connection back to the pool."""
        try:
            self.connection_pool.putconn(connection)
        except Exception as e:
            raise

    @contextmanager
    def get_session(self):
        """Context manager that yields a cursor and handles commit/rollback/release."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                yield cursor
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            self.release_connection(conn)

    def execute_query(self, query: str, params: Optional[tuple] = None):
        """Execute a query and return the results."""
        connection = None
        try:
            connection = self.get_connection()
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:  # If the query returns data
                    return cursor.fetchall()
                connection.commit()
                return None
        except Exception as e:
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                self.release_connection(connection)

    def close(self):
        """Close all connections in the pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
