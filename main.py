"""
Main entry point for the trading system.
"""
from datetime import datetime
from prefect import flow, task, get_run_logger
import asyncio

from src.database.database_connectivity import DatabaseConnectivity
from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader
from src.data.sources.alpaca_daily_loader import AlpacaDailyLoader
from src.data.sources.news import NewsLoader
from src.scripts.check_delisted_symbols import DelistedSymbolChecker
from src.data.alpaca_websocket import market_data_websocket_flow as websocket_flow


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


@flow(name="News Data Loader Flow", flow_run_name=lambda: generate_flow_run_name("news-loader"))
def news_data_loader_flow():
    logger = get_run_logger()
    try:
        logger.info("Running news data loader...")
        loader = NewsLoader()
        loader.fetch_and_store_news()
        logger.info("News data collection completed.")
    except Exception as e:
        logger.error(f"News data collection error: {e}")
        raise


@flow(name="Hourly Process Flow", flow_run_name=lambda: generate_flow_run_name("hourly-process"))
def hourly_process_flow():
    logger = get_run_logger()
    logger.info("Starting Hourly Process Flow")
    try:
        db = postgres_connect()
        news_data_loader_flow()
        # alpaca_data_loader_flow()
        logger.info("Hourly flow completed.")
    except Exception as e:
        logger.error(f"Hourly Process error: {e}")
        raise


@flow(name="End-of-Day Process Flow", flow_run_name=lambda: generate_flow_run_name("eod-process"))
def eod_process_flow():
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
def market_data_websocket_flow(end_time: str = "16:00"):
    """
    Prefect flow to manage WebSocket connection during market hours with hourly persistence
    """
    end = datetime.strptime(end_time, "%H:%M").time()
    while datetime.now().time() < end:
        logger = get_run_logger()
        try:
            logger.info("Starting Market Data WebSocket Flow with Hourly Persistence")
            websocket_flow()  # This now includes hourly persistence
            logger.info("Market Data WebSocket Flow completed")
        except Exception as e:
            logger.error(f"Market Data WebSocket Flow error: {e}")
            raise
    pass


if __name__ == '__main__':
    hourly_process_flow()
    eod_process_flow()
    market_data_websocket_flow()
