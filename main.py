from datetime import datetime
from prefect import flow, task, get_run_logger

from src.database.database_connectivity import DatabaseConnectivity
from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader
from src.data.sources.alpaca_daily_loader import AlpacaDailyLoader


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
        loader.run()
        logger.info("Alpaca hourly data collection completed.")
    except Exception as e:
        logger.error(f"Alpaca data collection error: {e}")
        raise


@flow(name="Hourly Process Flow", flow_run_name=lambda: generate_flow_run_name("hourly-process"))
def hourly_proces_flow():
    logger = get_run_logger()
    logger.info("Starting Hourly Process Flow")
    try:
        db = postgres_connect()
        alpaca_data_loader_flow
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
        yahoo_data_loader_flow()
        logger.info("End-of-Day flow completed.")
    except Exception as e:
        logger.error(f"EOD Process error: {e}")
        raise


if __name__ == '__main__':
    hourly_proces_flow()
    eod_proces_flow()
