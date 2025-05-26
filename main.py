import dask
import argparse
from datetime import datetime, timedelta
import platform
import sys
import traceback
from typing import List
from prefect import flow, task, get_run_logger
from prefect.blocks.system import Secret
from prefect_dask import DaskTaskRunner
from prefect_email import EmailServerCredentials, email_send_message

from src.database.database_connectivity import DatabaseConnectivity
from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader


def generate_flow_run_name(flow_prefix: str) -> str:
    # Generate a custom flow run name with timestamp.
    return f"{flow_prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


@task
def postgres_connect():
    # Connect to PostgreSQL.
    logger = get_run_logger()
    try:
        logger.info("Attempting to connect to PostgreSQL...")
        return DatabaseConnectivity()
    except Exception as e:
        logger.error("Database connection error: %s", e)
        raise

@task
def end_of_day_yahoo():
    logger = get_run_logger()
    try:
        logger.info("Attempting to run yahoo data collection at the end of day...")
        return YahooFinanceDataLoader()
    except Exception as e:
        logger.error("end of day yahoo data collection error: %s", e)
        raise


@flow(flow_run_name=lambda: generate_flow_run_name("hourly-process"))
def hourly_proces_flow():
    try:
        print('Testing Hourly Process')
        # Run batch processing flows
        postgres_db = postgres_connect()
    except Exception as e:
        print("Hourly Process error: %s", e)
        raise


@flow(flow_run_name=lambda: generate_flow_run_name("eod-process"))
def eod_proces_flow():
    try:
        print('Testing end of day Process')
        # Run batch processing flows
        postgres_db = postgres_connect()
        loader = YahooFinanceDataLoader()
        loader.run()
    except Exception as e:
        print("Hourly Process error: %s", e)
        raise


if __name__ == '__main__':
    hourly_proces_flow()
    eod_proces_flow()
