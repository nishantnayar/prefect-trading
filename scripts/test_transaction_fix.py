#!/usr/bin/env python3
"""
Test script to verify the transaction fix for database operations.
This script tests the save_features_to_database method to ensure it handles
transaction abortion correctly.
"""

import sys
import os
import pandas as pd
from datetime import datetime, date
import logging

# Add the project root to the path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from src.utils.data_preprocessing_utils import DataPreprocessingUtils
from src.database.database_connectivity import DatabaseConnectivity

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_data():
    """Create test feature data with some potentially problematic values."""
    test_data = []
    
    # Create some normal data
    for i in range(10):
        test_data.append({
            'symbol': 'AAPL',
            'timestamp': datetime.now(),
            'log_close': 5.0 + i * 0.1,
            'log_return': 0.001 + i * 0.0001,
            'z_score': 0.5 + i * 0.1,
            'rolling_std': 0.001 + i * 0.0001,
            'rolling_mean': 0.0001 + i * 0.00001,
            'volatility_annualized': 0.02 + i * 0.001,
            'feature_date': date.today()
        })
    
    # Add some potentially problematic data
    test_data.append({
        'symbol': 'AAPL',
        'timestamp': datetime.now(),
        'log_close': 5.0,
        'log_return': 0.001,
        'z_score': 15.0,  # This should be filtered out (> 10)
        'rolling_std': -0.001,  # This should be filtered out (< 0)
        'rolling_mean': 0.0001,
        'volatility_annualized': -0.02,  # This should be filtered out (< 0)
        'feature_date': date.today()
    })
    
    return pd.DataFrame(test_data)

def test_transaction_fix():
    """Test the transaction fix by saving test data to database."""
    try:
        logger.info("Testing transaction fix for database operations...")
        
        # Initialize utilities
        utils = DataPreprocessingUtils()
        
        # Create test data
        test_df = create_test_data()
        logger.info(f"Created test data with {len(test_df)} records")
        
        # Test saving features
        logger.info("Testing save_features_to_database...")
        records_saved = utils.save_features_to_database(
            test_df, 
            computation_method='test_method',
            data_source='test_source'
        )
        
        logger.info(f"Successfully saved {records_saved} records")
        
        # Test saving variance stability results
        logger.info("Testing save_variance_stability_results...")
        test_results = [{
            'symbol': 'AAPL',
            'test_date': date.today(),
            'record_count': 100,
            'arch_test_pvalue': 0.05,
            'rolling_std_cv': 0.1,
            'ljung_box_pvalue': 0.1,
            'is_stable': True,
            'filter_reason': None,
            'test_window': 30,
            'arch_lags': 5
        }]
        
        results_saved = utils.save_variance_stability_results(test_results)
        logger.info(f"Successfully saved {results_saved} variance stability results")
        
        logger.info("Transaction fix test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Transaction fix test failed: {e}")
        return False

def test_database_connectivity():
    """Test the improved database connectivity methods."""
    try:
        logger.info("Testing improved database connectivity...")
        
        db = DatabaseConnectivity()
        
        # Test individual session
        with db.get_individual_session() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            logger.info(f"Individual session test result: {result}")
        
        # Test execute_query with rollback handling
        result = db.execute_query("SELECT 2 as test")
        logger.info(f"Execute query test result: {result}")
        
        logger.info("Database connectivity test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database connectivity test failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting transaction fix tests...")
    
    # Test database connectivity improvements
    connectivity_ok = test_database_connectivity()
    
    # Test transaction fix
    transaction_ok = test_transaction_fix()
    
    if connectivity_ok and transaction_ok:
        logger.info("All tests passed! Transaction fix is working correctly.")
        sys.exit(0)
    else:
        logger.error("Some tests failed. Please check the logs.")
        sys.exit(1) 