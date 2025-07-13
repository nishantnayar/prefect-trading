"""
Main entry point for the trading system.
"""
from datetime import datetime
from prefect import flow, task, get_run_logger

from src.database.database_connectivity import DatabaseConnectivity
from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader
from src.data.sources.alpaca_daily_loader import AlpacaDailyLoader
from src.data.sources.alpaca_historical_loader import AlpacaDataLoader
from src.data.sources.news import NewsLoader
from src.scripts.check_delisted_symbols import DelistedSymbolChecker
from src.data.sources.alpaca_websocket import market_data_websocket_flow as websocket_flow
from alpaca.data.timeframe import TimeFrame

# Import new preprocessing and training flows
from src.flows.preprocessing_flows import (
    data_preprocessing_flow,
    daily_preprocessing_flow
)
from src.flows.training_flows import (
    complete_training_flow,
    daily_training_flow,
    sector_training_flow
)


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


@task(name="Load Historical Data Task")
def load_historical_data_task():
    """
    Prefect task to load historical market data.
    This task loads both hourly and 1-minute historical data for all active symbols.
    """
    logger = get_run_logger()
    try:
        logger.info("Initializing historical data loader...")
        historical_loader = AlpacaDataLoader()

        # Load hourly historical data (last 30 days) - COMMENTED OUT
        # logger.info("Loading hourly historical data...")
        # historical_loader.run_historical_load(timeframe=TimeFrame.Hour)

        # Load 1-minute historical data (last 7 days)
        logger.info("Loading 1-minute historical data...")
        historical_loader.load_1min_historical_data()

        logger.info("Historical data loading completed successfully")
        return True
    except Exception as e:
        logger.error(f"Historical data loading error: {e}")
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


@flow(name="Start of Day Flow", flow_run_name=lambda: generate_flow_run_name("start-of-day"))
def start_of_day_flow():
    """
    Prefect flow to run start-of-day processes for the trading system.
    This includes historical data loading, data preprocessing, model training, and other initialization tasks.
    """
    logger = get_run_logger()
    logger.info("Starting Start of Day Flow")
    try:
        # Connect to database
        db = postgres_connect()

        # Task 1: Load historical data (first task)
        logger.info("Executing Task 1: Historical Data Loading")
        load_historical_data_task()

        # Task 2: Data preprocessing with variance stability testing
        logger.info("Executing Task 2: Data Preprocessing")
        daily_preprocessing_flow()

        # Task 3: Model training for all sectors
        logger.info("Executing Task 3: Model Training")
        complete_training_flow()

        # Task 4: Symbol maintenance check
        # logger.info("Executing Task 4: Symbol Maintenance")
        # symbol_maintenance_flow()

        # Task 5: Load additional market data (Yahoo Finance)
        # logger.info("Executing Task 5: Yahoo Finance Data Loading")
        # yahoo_data_loader_flow()

        logger.info("Start of Day Flow completed successfully")
    except Exception as e:
        logger.error(f"Start of Day Flow error: {e}")
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
    # Uncomment the flow you want to run:
    # start_of_day_flow()             # Start of day processes
    # hourly_process_flow()           # Hourly data collection
    # eod_process_flow()              # End-of-day processing
    # market_data_websocket_flow()    # Real-time WebSocket data

    # For testing, run start of day flow
    start_of_day_flow()
