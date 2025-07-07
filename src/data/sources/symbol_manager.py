from datetime import datetime
from typing import List, Optional

from src.database.database_connectivity import DatabaseConnectivity


class SymbolManager:
    """Manages trading symbols in the database."""

    def __init__(self):
        self.db = DatabaseConnectivity()

    def add_symbol(self, symbol: str, name: str = None, is_active: bool = True):
        """Add a new symbol to the database."""
        try:
            with self.db.get_session() as cursor:
                query = """
                    INSERT INTO symbols (symbol, name, is_active)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (symbol) DO UPDATE 
                    SET name = COALESCE(EXCLUDED.name, symbols.name),
                        is_active = EXCLUDED.is_active
                """
                cursor.execute(query, (symbol, name, is_active))
        except Exception as e:
            raise

    def deactivate_symbol(self, symbol: str):
        """Deactivate a symbol in the database and set its end date."""
        try:
            with self.db.get_session() as cursor:
                query = """
                    UPDATE symbols 
                    SET is_active = false,
                        end_date = CURRENT_TIMESTAMP
                    WHERE symbol = %s
                """
                cursor.execute(query, (symbol,))
        except Exception as e:
            raise

    def get_active_symbols(self) -> List[str]:
        """Get list of active stock symbols from the database."""
        try:
            with self.db.get_session() as cursor:
                query = """
                    SELECT symbol 
                    FROM symbols 
                    WHERE is_active = true 
                    ORDER BY symbol
                """
                cursor.execute(query)
                symbols = [row[0] for row in cursor.fetchall()]
                return symbols
        except Exception as e:
            return []

    def get_symbol_info(self, symbol: str) -> Optional[dict]:
        """Get detailed information about a symbol."""
        try:
            with self.db.get_session() as cursor:
                query = """
                    SELECT symbol, name, is_active, start_date, end_date, created_at, updated_at
                    FROM symbols
                    WHERE symbol = %s
                """
                cursor.execute(query, (symbol,))
                result = cursor.fetchone()
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, result))
                return None
        except Exception as e:
            return None

    def update_symbol_name(self, symbol: str, name: str) -> bool:
        """Update the name of a symbol."""
        try:
            with self.db.get_session() as cursor:
                query = """
                    UPDATE symbols 
                    SET name = %s 
                    WHERE symbol = %s
                """
                cursor.execute(query, (name, symbol))
                if cursor.rowcount > 0:
                    return True
                return False
        except Exception as e:
            return False