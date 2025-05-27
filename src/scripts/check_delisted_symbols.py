"""
Script to check for delisted symbols using Alpaca API and update the symbol manager.
"""
import sys
from pathlib import Path
from loguru import logger
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import AssetStatus
from prefect.blocks.system import Secret

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data.symbol_manager import SymbolManager


class DelistedSymbolChecker:
    def __init__(self):
        self.symbol_manager = SymbolManager()

        # Load Alpaca credentials from Prefect secrets
        api_key = Secret.load("alpaca-api-key").get()
        secret_key = Secret.load("alpaca-secret-key").get()

        # Initialize Alpaca trading client
        self.client = TradingClient(api_key, secret_key)

    def check_symbol_status(self, symbol: str) -> bool:
        """
        Check if a symbol is still active and tradable using Alpaca's asset API.
        
        Args:
            symbol: The stock symbol to check
            
        Returns:
            bool: True if symbol is active and tradable, False if delisted
        """
        try:
            asset = self.client.get_asset(symbol)
            is_active = asset.status == AssetStatus.ACTIVE and asset.tradable

            if is_active:
                logger.info(f"{symbol} is active and tradable")
            else:
                logger.info(f"{symbol} is not tradable or inactive. Status: {asset.status}, Tradable: {asset.tradable}")

            return is_active

        except Exception as e:
            logger.warning(f"Error checking symbol {symbol}: {str(e)}")
            return False

    def check_all_symbols(self):
        """Check all active symbols and deactivate delisted ones."""
        try:
            # Get all active symbols
            active_symbols = self.symbol_manager.get_active_symbols()
            logger.info(f"Checking {len(active_symbols)} active symbols...")

            delisted_count = 0
            for symbol in active_symbols:
                if not self.check_symbol_status(symbol):
                    logger.info(f"Symbol {symbol} appears to be delisted. Deactivating...")
                    self.symbol_manager.deactivate_symbol(symbol)
                    delisted_count += 1

            logger.info(f"Maintenance complete. Deactivated {delisted_count} delisted symbols.")

        except Exception as e:
            logger.error(f"Error during maintenance check: {str(e)}")
            raise


def test_single_symbol(symbol: str):
    """Test the checker with a single symbol."""
    try:
        checker = DelistedSymbolChecker()
        logger.info(f"\nTesting symbol: {symbol}")
        is_active = checker.check_symbol_status(symbol)
        logger.info(f"Final result: {symbol} is {'active' if is_active else 'delisted'}")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")


def main():
    """Main entry point for the script."""
    try:
        checker = DelistedSymbolChecker()
        checker.check_all_symbols()
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Test with both a delisted and an active symbol
    # test_single_symbol("ZZZZ")  # Should be delisted
    # test_single_symbol("AAPL")  # Should be active

    main()
