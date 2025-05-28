"""
Main entry point for the trading system.
"""
from datetime import datetime
from prefect import flow, task, get_run_logger
import asyncio

from src.database.database_connectivity import DatabaseConnectivity
from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader
from src.data.sources.alpaca_daily_loader import AlpacaDailyLoader
from src.scripts.check_delisted_symbols import DelistedSymbolChecker
from src.data.alpaca_websocket import websocket_connection


def generate_flow_run_name(flow_prefix: str) -> str:
    return f"{flow_prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


@task(name="PostgreSQL Connect Task")
def postgres_connect():
    logger = get_run_logger()
    try:
        logger.info("Attempting to connect to PostgreSQL...")
        db = DatabaseConnectivity()
        logger.info("PostgreSQL connection successful.")
        return db
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise


@flow(name="Yahoo Data Loader Flow", flow_run_name=lambda: generate_flow_run_name("yahoo-loader"))
def yahoo_data_loader_flow():
    logger = get_run_logger()
    try:
        logger.info("Running Yahoo Finance data loader...")
        loader = YahooFinanceDataLoader()
        loader.run()
        logger.info("Yahoo Finance data collection completed.")
    except Exception as e:
        logger.error(f"Yahoo data collection error: {e}")
        raise


@flow(name="Alpaca hourly Loader Flow", flow_run_name=lambda: generate_flow_run_name("alpaca-hourly-loader"))
def alpaca_data_loader_flow():
    logger = get_run_logger()
    try:
        logger.info("Running alpaca hourly loader...")
        loader = AlpacaDailyLoader()
        loader.run_daily_load()
        logger.info("Alpaca hourly data collection completed.")
    except Exception as e:
        logger.error(f"Alpaca data collection error: {e}")
        raise


@flow(name="Symbol Maintenance Flow", flow_run_name=lambda: generate_flow_run_name("symbol-maintenance"))
def symbol_maintenance_flow():
    logger = get_run_logger()
    try:
        logger.info("Running symbol maintenance check...")
        checker = DelistedSymbolChecker()
        checker.check_all_symbols()  # Actually run the check
        logger.info("Symbol maintenance check completed.")
    except Exception as e:
        logger.error(f"Symbol maintenance check error: {e}")
        raise


@flow(name="Hourly Process Flow", flow_run_name=lambda: generate_flow_run_name("hourly-process"))
def hourly_proces_flow():
    logger = get_run_logger()
    logger.info("Starting Hourly Process Flow")
    try:
        db = postgres_connect()
        # alpaca_data_loader_flow()
        logger.info("Hourly flow completed.")
    except Exception as e:
        logger.error(f"Hourly Process error: {e}")
        raise


@flow(name="End-of-Day Process Flow", flow_run_name=lambda: generate_flow_run_name("eod-process"))
def eod_proces_flow():
    logger = get_run_logger()
    logger.info("Starting End-of-Day Process Flow")
    try:
        db = postgres_connect()
        symbol_maintenance_flow()
        yahoo_data_loader_flow()
        logger.info("End-of-Day flow completed.")
    except Exception as e:
        logger.error(f"EOD Process error: {e}")
        raise


@flow(name="Market Data WebSocket Flow", flow_run_name=lambda: generate_flow_run_name("websocket-data"))
def market_data_websocket_flow():
    """
    Prefect flow to manage WebSocket connection during market hours
    """
    logger = get_run_logger()
    try:
        logger.info("Starting Market Data WebSocket Flow")
        asyncio.run(websocket_connection())
        logger.info("Market Data WebSocket Flow completed")
    except Exception as e:
        logger.error(f"Market Data WebSocket Flow error: {e}")
        raise


if __name__ == '__main__':
    hourly_proces_flow()
    eod_proces_flow()
    market_data_websocket_flow()
