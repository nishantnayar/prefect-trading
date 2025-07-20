"""
Prefect flows for data preprocessing with variance stability testing.

This module provides Prefect flows and tasks for:
1. Feature computation and preprocessing
2. Variance stability testing
3. Database operations for feature storage
4. Integration with the training pipeline
"""

from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import pandas as pd
from prefect import flow, task, get_run_logger
from prefect.artifacts import create_markdown_artifact

from src.database.database_connectivity import DatabaseConnectivity
from src.data.sources.symbol_manager import SymbolManager
from src.utils.data_preprocessing_utils import DataPreprocessingUtils
from src.ml.train_gru_models import extract_data_from_database


@task(name="Extract Historical Data")
def extract_historical_data_task(sectors: Optional[List[str]] = None) -> Tuple[pd.DataFrame, List[str]]:
    """
    Extract historical data from database for specified sectors.
    
    Args:
        sectors: List of sectors to extract data for. If None, uses active sectors from config.
        
    Returns:
        Tuple of (historical_dataframe, symbols_list)
    """
    logger = get_run_logger()
    logger.info(f"Extracting historical data for sectors: {sectors}")
    
    try:
        historical_df, symbols = extract_data_from_database(sectors=sectors)
        logger.info(f"Extracted {len(historical_df)} records for {len(symbols)} symbols")
        return historical_df, symbols
    except Exception as e:
        logger.error(f"Error extracting historical data: {e}")
        raise


@task(name="Select Stocks by Record Count")
def select_stocks_task(
    historical_df: pd.DataFrame,
    threshold_percent: float = 0.8,
    min_records: int = 100
) -> List[str]:
    """
    Select stocks with sufficient data records.
    
    Args:
        historical_df: DataFrame with historical data
        threshold_percent: Percentage of max record count
        min_records: Minimum number of records required
        
    Returns:
        List of selected symbol names
    """
    logger = get_run_logger()
    logger.info(f"Selecting stocks with threshold_percent={threshold_percent}, min_records={min_records}")
    
    try:
        utils = DataPreprocessingUtils()
        selected_symbols = utils.select_stocks_by_record_count(
            historical_df, threshold_percent, min_records
        )
        logger.info(f"Selected {len(selected_symbols)} symbols for feature computation")
        return selected_symbols
    except Exception as e:
        logger.error(f"Error selecting stocks: {e}")
        raise


@task(name="Compute Features")
def compute_features_task(
    historical_df: pd.DataFrame,
    symbols: List[str],
    computation_method: str = 'expanding_window',
    min_periods: int = 30
) -> pd.DataFrame:
    """
    Compute features for selected symbols.
    
    Args:
        historical_df: DataFrame with historical data
        symbols: List of symbols to compute features for
        computation_method: Method for z-score computation
        min_periods: Minimum periods for expanding window
        
    Returns:
        DataFrame with computed features
    """
    logger = get_run_logger()
    logger.info(f"Computing features for {len(symbols)} symbols using {computation_method}")
    
    try:
        utils = DataPreprocessingUtils()
        features = utils.compute_features_for_multiple_symbols(
            historical_df, symbols, computation_method, min_periods
        )
        logger.info(f"Computed features for {len(symbols)} symbols: {len(features)} total records")
        return features
    except Exception as e:
        logger.error(f"Error computing features: {e}")
        raise


@task(name="Test Variance Stability")
def test_variance_stability_task(
    features_df: pd.DataFrame,
    symbols: List[str],
    test_window: int = 30,
    arch_lags: int = 5
) -> Tuple[List[str], List[Dict]]:
    """
    Test variance stability for multiple symbols.
    
    Args:
        features_df: DataFrame with computed features
        symbols: List of symbols to test
        test_window: Window size for rolling statistics
        arch_lags: Number of lags for ARCH test
        
    Returns:
        Tuple of (stable_symbols, test_results)
    """
    logger = get_run_logger()
    logger.info(f"Testing variance stability for {len(symbols)} symbols")
    
    try:
        utils = DataPreprocessingUtils()
        stable_symbols, test_results = utils.test_variance_stability_for_multiple_symbols(
            features_df, symbols, test_window, arch_lags
        )
        logger.info(f"Variance stability test complete: {len(stable_symbols)} stable out of {len(symbols)} total")
        return stable_symbols, test_results
    except Exception as e:
        logger.error(f"Error testing variance stability: {e}")
        raise


@task(name="Save Features to Database")
def save_features_task(
    features_df: pd.DataFrame,
    computation_method: str = 'expanding_window',
    data_source: str = 'market_data_historical'
) -> int:
    """
    Save computed features to database.
    
    Args:
        features_df: DataFrame with computed features
        computation_method: Method used for computation
        data_source: Source of the original data
        
    Returns:
        Number of records saved
    """
    logger = get_run_logger()
    logger.info(f"Saving {len(features_df)} feature records to database")
    
    try:
        utils = DataPreprocessingUtils()
        records_saved = utils.save_features_to_database(
            features_df, computation_method, data_source
        )
        logger.info(f"Successfully saved {records_saved} feature records to database")
        return records_saved
    except Exception as e:
        logger.error(f"Error saving features to database: {e}")
        # Don't raise - continue with in-memory data
        return 0


@task(name="Save Variance Stability Results")
def save_variance_results_task(test_results: List[Dict]) -> int:
    """
    Save variance stability test results to database.
    
    Args:
        test_results: List of test result dictionaries
        
    Returns:
        Number of records saved
    """
    logger = get_run_logger()
    logger.info(f"Saving {len(test_results)} variance stability results to database")
    
    try:
        utils = DataPreprocessingUtils()
        records_saved = utils.save_variance_stability_results(test_results)
        logger.info(f"Successfully saved {records_saved} variance stability results to database")
        return records_saved
    except Exception as e:
        logger.error(f"Error saving variance stability results to database: {e}")
        # Don't raise - continue with in-memory data
        return 0


@task(name="Create Preprocessing Report")
def create_preprocessing_report_task(
    total_symbols: int,
    selected_symbols: int,
    stable_symbols: int,
    features_saved: int,
    results_saved: int,
    test_results: List[Dict]
) -> str:
    """
    Create a markdown report of the preprocessing results.
    
    Args:
        total_symbols: Total number of symbols processed
        selected_symbols: Number of symbols selected for feature computation
        stable_symbols: Number of stable symbols
        features_saved: Number of feature records saved to database
        results_saved: Number of variance stability results saved to database
        test_results: List of test result dictionaries
        
    Returns:
        Markdown report string
    """
    logger = get_run_logger()
    
    # Calculate statistics
    stability_rate = (stable_symbols / selected_symbols * 100) if selected_symbols > 0 else 0
    
    # Group results by filter reason
    filter_reasons = {}
    for result in test_results:
        reason = result.get('filter_reason', 'unknown')
        filter_reasons[reason] = filter_reasons.get(reason, 0) + 1
    
    # Create markdown report
    report = f"""
# Data Preprocessing Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics

- **Total Symbols Processed:** {total_symbols}
- **Symbols Selected for Features:** {selected_symbols}
- **Stable Symbols:** {stable_symbols}
- **Stability Rate:** {stability_rate:.1f}%
- **Feature Records Saved:** {features_saved}
- **Variance Results Saved:** {results_saved}

## Filter Reasons

"""
    
    for reason, count in filter_reasons.items():
        report += f"- **{reason}:** {count} symbols\n"
    
    report += f"""
## Stable Symbols

"""
    
    stable_results = [r for r in test_results if r.get('is_stable', False)]
    for result in stable_results[:10]:  # Show first 10
        symbol = result['symbol']
        arch_p = result.get('arch_test_pvalue', 'N/A')
        cv = result.get('rolling_std_cv', 'N/A')
        report += f"- **{symbol}:** ARCH p={arch_p:.2e}, CV={cv:.4f}\n"
    
    if len(stable_results) > 10:
        report += f"- ... and {len(stable_results) - 10} more\n"
    
    report += f"""
## Unstable Symbols

"""
    
    unstable_results = [r for r in test_results if not r.get('is_stable', False)]
    for result in unstable_results[:10]:  # Show first 10
        symbol = result['symbol']
        reason = result.get('filter_reason', 'unknown')
        arch_p = result.get('arch_test_pvalue')
        cv = result.get('rolling_std_cv')
        
        # Handle None values safely
        arch_p_str = f"{arch_p:.2e}" if arch_p is not None else "N/A"
        cv_str = f"{cv:.4f}" if cv is not None else "N/A"
        
        report += f"- **{symbol}:** {reason} (ARCH p={arch_p_str}, CV={cv_str})\n"
    
    if len(unstable_results) > 10:
        report += f"- ... and {len(unstable_results) - 10} more\n"
    
    # Create Prefect artifact
    create_markdown_artifact(
        key="preprocessing-report",
        markdown=report,
        description="Data preprocessing with variance stability testing report"
    )
    
    logger.info("Created preprocessing report")
    return report


@flow(name="Data Preprocessing with Variance Stability Flow")
def data_preprocessing_flow(
    sectors: Optional[List[str]] = None,
    threshold_percent: float = 0.8,
    min_records: int = 100,
    computation_method: str = 'expanding_window',
    min_periods: int = 30,
    test_window: int = 30,
    arch_lags: int = 5
) -> Tuple[pd.DataFrame, List[str], List[Dict]]:
    """
    Complete data preprocessing flow with variance stability testing.
    
    Args:
        sectors: List of sectors to process. If None, uses active sectors from config.
        threshold_percent: Percentage threshold for stock selection
        min_records: Minimum records required for stock selection
        computation_method: Method for z-score computation
        min_periods: Minimum periods for expanding window
        test_window: Window size for variance stability testing
        arch_lags: Number of lags for ARCH test
        
    Returns:
        Tuple of (stable_features, stable_symbols, test_results)
    """
    logger = get_run_logger()
    logger.info("Starting Data Preprocessing with Variance Stability Flow")
    
    try:
        # Step 1: Extract historical data
        logger.info("Step 1: Extracting historical data...")
        historical_df, all_symbols = extract_historical_data_task(sectors)
        
        # Step 2: Select stocks with sufficient data
        logger.info("Step 2: Selecting stocks by record count...")
        selected_symbols = select_stocks_task(historical_df, threshold_percent, min_records)
        
        if not selected_symbols:
            raise ValueError("No symbols meet the data completeness criteria")
        
        # Step 3: Compute features
        logger.info("Step 3: Computing features...")
        features = compute_features_task(historical_df, selected_symbols, computation_method, min_periods)
        
        # Step 4: Test variance stability
        logger.info("Step 4: Testing variance stability...")
        stable_symbols, test_results = test_variance_stability_task(features, selected_symbols, test_window, arch_lags)
        
        # Step 5: Save to database
        logger.info("Step 5: Saving to database...")
        features_saved = save_features_task(features, computation_method)
        results_saved = save_variance_results_task(test_results)
        
        # Step 6: Filter features to stable symbols
        logger.info("Step 6: Filtering to stable symbols...")
        stable_features = features[features['symbol'].isin(stable_symbols)].copy()
        
        # Step 7: Create report
        logger.info("Step 7: Creating preprocessing report...")
        report = create_preprocessing_report_task(
            len(all_symbols), len(selected_symbols), len(stable_symbols),
            features_saved, results_saved, test_results
        )
        
        logger.info(f"Data preprocessing completed successfully!")
        logger.info(f"Stable features: {len(stable_features)} records")
        logger.info(f"Stable symbols: {len(stable_symbols)}")
        
        return stable_features, stable_symbols, test_results
        
    except Exception as e:
        logger.error(f"Data preprocessing flow failed: {e}")
        raise


@flow(name="Daily Preprocessing Flow")
def daily_preprocessing_flow():
    """
    Daily preprocessing flow that runs automatically.
    Uses default configuration and processes all active sectors.
    """
    logger = get_run_logger()
    logger.info("Starting Daily Preprocessing Flow")
    
    try:
        # Get active sectors from config
        symbol_manager = SymbolManager()
        active_sectors = symbol_manager.get_active_sectors()
        
        logger.info(f"Processing active sectors: {active_sectors}")
        
        # Run preprocessing for active sectors
        stable_features, stable_symbols, test_results = data_preprocessing_flow(
            sectors=active_sectors,
            threshold_percent=0.8,
            min_records=100,
            computation_method='expanding_window',
            min_periods=30,
            test_window=30,
            arch_lags=5
        )
        
        logger.info("Daily preprocessing completed successfully")
        return stable_features, stable_symbols, test_results
        
    except Exception as e:
        logger.error(f"Daily preprocessing flow failed: {e}")
        raise


if __name__ == "__main__":
    # For testing
    daily_preprocessing_flow() 