from prefect.blocks.system import Secret
import psycopg2
from psycopg2 import pool
from typing import Optional
import os
from contextlib import contextmanager


class DatabaseConnectivity:
    def __init__(self):
        self.connection_pool = None
        self._initialize_connection_pool()

    def _initialize_connection_pool(self):
        """Initialize the connection pool using Prefect secrets."""
        try:
            # Get database credentials from Prefect secrets
            db_host = Secret.load("db-host").get()
            db_port = "5432"  # Default PostgreSQL port
            db_name = Secret.load("db-name").get()
            db_user = Secret.load("db-user").get()
            db_password = Secret.load("db-password").get()

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
