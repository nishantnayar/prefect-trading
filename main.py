"""
Main entry point for the trading system.
"""
from datetime import datetime
from prefect import flow, task, get_run_logger

from src.database.database_connectivity import DatabaseConnectivity
from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader
from src.data.sources.alpaca_daily_loader import AlpacaDailyLoader
from src.data.sources.news import NewsLoader
from src.scripts.check_delisted_symbols import DelistedSymbolChecker
from src.data.sources.alpaca_websocket import market_data_websocket_flow as websocket_flow
from src.ml.daily_pair_identifier import daily_pair_identification_flow


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


@flow(name="Start of Day Flow", flow_run_name=lambda: generate_flow_run_name("start-of-day"))
def start_of_day_flow(sector: str = "Technology"):
    """
    Prefect flow for start of day operations including historical data gathering, 
    GARCH analysis, and GRU model training.
    This flow runs at 6:00 AM pre-market to prepare models for trading.
    Matches the Jupyter notebook approach for data processing and model training.
    
    Args:
        sector: Sector to analyze (default: Technology, matching notebook)
    """
    logger = get_run_logger()
    logger.info(f"Starting Start of Day Flow for {sector} sector")

    try:
        # Step 1: Gather historical data, run GARCH analysis, and train GRU models
        logger.info(f"Running daily pair identification with GARCH analysis and GRU training for {sector} sector...")
        results = daily_pair_identification_flow(sector=sector)

        if results is None:
            logger.warning(f"Daily pair identification flow returned no results for {sector} sector")
            return None

        # Extract results
        garch_results = results.get('garch_results', [])
        gru_results = results.get('gru_results', [])
        trading_config = results.get('trading_config', {})
        performance_analysis = results.get('performance_analysis', {})
        rankings_updated = results.get('rankings_updated', False)
        sector_analyzed = results.get('sector_analyzed', sector)

        # Log summary
        logger.info(f"Sector Analyzed: {sector_analyzed}")
        logger.info(f"GARCH Analysis: {len(garch_results)} pairs selected")
        logger.info(f"GRU Training: {len(gru_results)} models trained")
        logger.info(f"Database Rankings: {'Updated' if rankings_updated else 'Failed'}")
        
        if performance_analysis:
            best_pair = performance_analysis.get('best_pair', {})
            if best_pair:
                logger.info(f"Best GRU Model: {best_pair.get('pair', 'N/A')} "
                           f"(F1: {best_pair.get('best_f1', 0):.4f})")

        # Step 2: Additional start of day tasks can be added here
        # For example: data validation, system health checks, etc.

        logger.info(f"Start of Day Flow completed successfully for {sector_analyzed} sector")
        return {
            'garch_results': garch_results,
            'gru_results': gru_results,
            'trading_config': trading_config,
            'performance_analysis': performance_analysis,
            'rankings_updated': rankings_updated,
            'sector_analyzed': sector_analyzed
        }

    except Exception as e:
        logger.error(f"Start of Day Flow error: {e}")
        raise


if __name__ == '__main__':
    hourly_process_flow()
    eod_process_flow()
    market_data_websocket_flow()
