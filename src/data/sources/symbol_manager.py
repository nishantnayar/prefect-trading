from datetime import datetime
from typing import List, Optional
import yaml
from pathlib import Path

from src.database.database_connectivity import DatabaseConnectivity
from src.utils.config_loader import get_sectors_config


class SymbolManager:
    """Manages trading symbols in the database."""

    def __init__(self):
        self.db = DatabaseConnectivity()
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from config.yaml"""
        try:
            # Use the new config loader
            config = get_sectors_config()
            print("Loaded sectors configuration")
            return {"sectors": config}
        except Exception as e:
            print(f"Warning: Could not load config, using defaults: {e}")
            return {"sectors": {"active": ["technology"]}}

    def get_active_sectors(self) -> List[str]:
        """Get list of active sectors from configuration."""
        return self.config.get("sectors", {}).get("active", ["technology"])

    def get_available_sectors(self) -> List[str]:
        """Get list of all available sectors from configuration."""
        return self.config.get("sectors", {}).get("available", ["technology", "healthcare", "financial"])

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

    def get_active_symbols(self, sectors: Optional[List[str]] = None) -> List[str]:
        """Get list of active stock symbols from the database, optionally filtered by sector.
        
        Args:
            sectors: List of sectors to filter by. If None, uses active sectors from config.
        """
        try:
            if sectors is None:
                sectors = self.get_active_sectors()
            
            with self.db.get_session() as cursor:
                if sectors:
                    # Filter by sector using yahoo_company_info table
                    query = """
                        SELECT DISTINCT s.symbol 
                        FROM symbols s
                        JOIN yahoo_company_info y ON s.symbol = y.symbol
                        WHERE s.is_active = true 
                        AND y.sector = ANY(%s)
                        ORDER BY s.symbol
                    """
                    cursor.execute(query, (sectors,))
                else:
                    # Get all active symbols without sector filtering
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
            print(f"Error getting active symbols: {e}")
            return []

    def get_symbols_by_sector(self, sector: str) -> List[str]:
        """Get all symbols for a specific sector."""
        try:
            with self.db.get_session() as cursor:
                query = """
                    SELECT DISTINCT s.symbol 
                    FROM symbols s
                    JOIN yahoo_company_info y ON s.symbol = y.symbol
                    WHERE s.is_active = true 
                    AND y.sector = %s
                    ORDER BY s.symbol
                """
                cursor.execute(query, (sector,))
                symbols = [row[0] for row in cursor.fetchall()]
                return symbols
        except Exception as e:
            print(f"Error getting symbols for sector {sector}: {e}")
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

    def get_symbol_with_sector_info(self, symbol: str) -> Optional[dict]:
        """Get symbol information including sector details."""
        try:
            with self.db.get_session() as cursor:
                query = """
                    SELECT s.symbol, s.name, s.is_active, s.start_date, s.end_date, 
                           s.created_at, s.updated_at, y.sector, y.industry
                    FROM symbols s
                    LEFT JOIN yahoo_company_info y ON s.symbol = y.symbol
                    WHERE s.symbol = %s
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

    def get_sector_summary(self) -> dict:
        """Get summary of symbols by sector."""
        try:
            with self.db.get_session() as cursor:
                query = """
                    SELECT y.sector, COUNT(DISTINCT s.symbol) as symbol_count
                    FROM symbols s
                    JOIN yahoo_company_info y ON s.symbol = y.symbol
                    WHERE s.is_active = true AND y.sector IS NOT NULL
                    GROUP BY y.sector
                    ORDER BY symbol_count DESC
                """
                cursor.execute(query)
                results = cursor.fetchall()
                return {row[0]: row[1] for row in results}
        except Exception as e:
            print(f"Error getting sector summary: {e}")
            return {}