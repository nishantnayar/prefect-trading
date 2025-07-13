"""
Data Preprocessing Utilities for Feature Computation and Variance Stability Testing

This module provides utilities for:
1. Stock selection based on data completeness
2. Feature computation (log_close, log_return, z_scores)
3. Variance stability testing (ARCH test, rolling std, Ljung-Box)
4. Database operations for feature storage and retrieval
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
import logging
from datetime import datetime, date
from statsmodels.stats.diagnostic import het_arch, acorr_ljungbox
from statsmodels.tsa.stattools import adfuller
import warnings
import yaml
from pathlib import Path

from src.database.database_connectivity import DatabaseConnectivity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


class DataPreprocessingUtils:
    """
    Utility class for data preprocessing, feature computation, and variance stability testing.
    """
    
    def __init__(self, db_connection: Optional[DatabaseConnectivity] = None):
        """
        Initialize the preprocessing utilities.
        
        Args:
            db_connection: Optional database connection. If None, creates a new one.
        """
        self.db = db_connection or DatabaseConnectivity()
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        """Load configuration from config.yaml"""
        try:
            config_path = Path(__file__).parent.parent.parent.parent / "config" / "config.yaml"
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load config, using defaults: {e}")
            return {
                "variance_stability": {
                    "arch_test_pvalue_threshold": 1e-100,
                    "rolling_std_cv_threshold": 2.0,
                    "ljung_box_pvalue_threshold": 0.001,
                    "test_window": 30,
                    "arch_lags": 5,
                    "ljung_box_lags": 10
                }
            }
        
    def __del__(self):
        """Clean up database connection."""
        if hasattr(self, 'db') and self.db:
            self.db.close()
    
    def select_stocks_by_record_count(
        self, 
        df: pd.DataFrame, 
        threshold_percent: float = 0.8,
        min_records: int = 100
    ) -> List[str]:
        """
        Select stocks with sufficient data records.
        
        Args:
            df: DataFrame with 'symbol' column
            threshold_percent: Percentage of max record count (0.8 = 80%)
            min_records: Minimum number of records required
            
        Returns:
            List of symbol names that meet the criteria
        """
        logger.info("Selecting stocks by record count...")
        
        # Count records per symbol
        symbol_counts = df['symbol'].value_counts()
        max_count = symbol_counts.max()
        threshold_count = max(int(max_count * threshold_percent), min_records)
        
        # Filter symbols
        selected_symbols = symbol_counts[symbol_counts >= threshold_count].index.tolist()
        
        logger.info(f"Selected {len(selected_symbols)} symbols out of {len(symbol_counts)} total")
        logger.info(f"Max records: {max_count}, Threshold: {threshold_count}")
        
        return selected_symbols
    
    def compute_features_for_symbol(
        self, 
        symbol: str, 
        price_data: pd.DataFrame,
        computation_method: str = 'expanding_window',
        min_periods: int = 30
    ) -> pd.DataFrame:
        """
        Compute features for a single symbol.
        
        Args:
            symbol: Stock symbol
            price_data: DataFrame with 'close' column
            computation_method: Method for z-score computation ('expanding_window' or 'rolling_window')
            min_periods: Minimum periods for expanding window
            
        Returns:
            DataFrame with computed features
        """
        logger.info(f"Computing features for {symbol}...")
        
        # Create a copy to avoid modifying original data
        features = price_data.copy()
        
        # Add symbol column if not present
        if 'symbol' not in features.columns:
            features['symbol'] = symbol
        
        # Core features
        features['log_close'] = np.log(features['close'])
        features['log_return'] = features['log_close'].diff()
        
        # Z-score computation
        if computation_method == 'expanding_window':
            features['z_score'] = features.groupby('symbol')['log_return'].transform(
                lambda x: (x - x.expanding(min_periods=min_periods).mean()) / 
                         x.expanding(min_periods=min_periods).std()
            )
        else:  # rolling_window
            features['z_score'] = features.groupby('symbol')['log_return'].transform(
                lambda x: (x - x.rolling(window=min_periods, min_periods=min_periods).mean()) / 
                         x.rolling(window=min_periods, min_periods=min_periods).std()
            )
        
        # Rolling statistics
        features['rolling_std'] = features['log_return'].rolling(30, min_periods=10).std()
        features['rolling_mean'] = features['log_return'].rolling(30, min_periods=10).mean()
        
        # Annualized volatility (assuming daily data)
        features['volatility_annualized'] = features['rolling_std'] * np.sqrt(252)
        
        # Add feature date
        features['feature_date'] = pd.to_datetime(features.index).date if hasattr(features.index, 'date') else date.today()
        
        logger.info(f"Computed features for {symbol}: {len(features)} records")
        
        return features
    
    def compute_features_for_multiple_symbols(
        self, 
        df: pd.DataFrame,
        symbols: Optional[List[str]] = None,
        computation_method: str = 'expanding_window',
        min_periods: int = 30
    ) -> pd.DataFrame:
        """
        Compute features for multiple symbols.
        
        Args:
            df: DataFrame with 'symbol' and 'close' columns
            symbols: List of symbols to process. If None, processes all symbols in df
            computation_method: Method for z-score computation
            min_periods: Minimum periods for expanding window
            
        Returns:
            DataFrame with computed features for all symbols
        """
        logger.info("Computing features for multiple symbols...")
        
        if symbols is None:
            symbols = df['symbol'].unique().tolist()
        
        all_features = []
        
        for symbol in symbols:
            try:
                symbol_data = df[df['symbol'] == symbol].copy()
                if len(symbol_data) < min_periods:
                    logger.warning(f"Skipping {symbol}: insufficient data ({len(symbol_data)} records)")
                    continue
                
                features = self.compute_features_for_symbol(
                    symbol, symbol_data, computation_method, min_periods
                )
                all_features.append(features)
                
            except Exception as e:
                logger.error(f"Error computing features for {symbol}: {e}")
                continue
        
        if not all_features:
            raise ValueError("No features computed for any symbols")
        
        # Combine all features
        combined_features = pd.concat(all_features, ignore_index=True)
        
        # Remove rows with NaN in critical columns
        combined_features = combined_features.dropna(subset=['log_return', 'z_score'])
        
        logger.info(f"Computed features for {len(symbols)} symbols: {len(combined_features)} total records")
        
        return combined_features
    
    def test_variance_stability(
        self, 
        symbol: str, 
        feature_data: pd.DataFrame,
        test_window: int = None,
        arch_lags: int = None,
        ljung_box_lags: int = None
    ) -> Dict:
        """
        Test variance stability for a symbol.
        Returns a dict with all fields present and robust error handling.
        Uses config values for thresholds if not specified.
        """
        logger.info(f"Testing variance stability for {symbol}...")
        
        # Get config values or use defaults
        vs_config = self.config.get("variance_stability", {})
        test_window = test_window or vs_config.get("test_window", 30)
        arch_lags = arch_lags or vs_config.get("arch_lags", 5)
        ljung_box_lags = ljung_box_lags or vs_config.get("ljung_box_lags", 10)
        
        # Get thresholds from config
        arch_threshold = vs_config.get("arch_test_pvalue_threshold", 1e-100)
        cv_threshold = vs_config.get("rolling_std_cv_threshold", 2.0)
        lb_threshold = vs_config.get("ljung_box_pvalue_threshold", 0.001)
        
        symbol_data = feature_data[feature_data['symbol'] == symbol]
        z_scores = symbol_data['z_score'].dropna()
        if len(z_scores) < test_window:
            return {
                'symbol': symbol,
                'is_stable': False,
                'filter_reason': 'insufficient_data',
                'record_count': len(z_scores),
                'test_date': date.today(),
                'arch_test_pvalue': None,
                'rolling_std_cv': None,
                'ljung_box_pvalue': None
            }
        try:
            arch_test = het_arch(z_scores, nlags=arch_lags)
            arch_stat = arch_test[0] if isinstance(arch_test, (tuple, list)) and len(arch_test) > 0 else None
            arch_pvalue = arch_test[1] if isinstance(arch_test, (tuple, list)) and len(arch_test) > 1 else None
            if arch_pvalue is None:
                arch_pvalue = float('nan')
            rolling_std = z_scores.rolling(test_window, min_periods=test_window//2).std()
            rolling_std_cv = rolling_std.std() / rolling_std.mean() if rolling_std.mean() != 0 else float('inf')
            lb_test = acorr_ljungbox(z_scores, lags=ljung_box_lags, return_df=True)
            lb_pvalue_avg = lb_test['lb_pvalue'].mean() if 'lb_pvalue' in lb_test else 0
            # Use config thresholds
            is_stable = (
                arch_pvalue > arch_threshold and 
                rolling_std_cv < cv_threshold and 
                lb_pvalue_avg > lb_threshold
            )
            filter_reason = None
            if not is_stable:
                if arch_pvalue <= arch_threshold:
                    filter_reason = 'arch_test_failed'
                elif rolling_std_cv >= cv_threshold:
                    filter_reason = 'high_volatility'
                else:
                    filter_reason = 'autocorrelation_detected'
            result = {
                'symbol': symbol,
                'is_stable': is_stable,
                'filter_reason': filter_reason,
                'record_count': len(z_scores),
                'test_date': date.today(),
                'arch_test_pvalue': float(arch_pvalue) if arch_pvalue is not None else None,
                'rolling_std_cv': float(rolling_std_cv) if rolling_std_cv is not None else None,
                'ljung_box_pvalue': float(lb_pvalue_avg) if lb_pvalue_avg is not None else None,
                'test_window': test_window,
                'arch_lags': arch_lags
            }
            logger.info(f"Variance stability test for {symbol}: {'STABLE' if is_stable else 'UNSTABLE'} "
                        f"(ARCH p={arch_pvalue if arch_pvalue is not None else 'NA'}, CV={rolling_std_cv if rolling_std_cv is not None else 'NA'})")
            return result
        except Exception as e:
            logger.error(f"Error testing variance stability for {symbol}: {e}")
            return {
                'symbol': symbol,
                'is_stable': False,
                'filter_reason': f'test_error: {e}',
                'record_count': len(z_scores),
                'test_date': date.today(),
                'arch_test_pvalue': None,
                'rolling_std_cv': None,
                'ljung_box_pvalue': None
            }
    
    def test_variance_stability_for_multiple_symbols(
        self, 
        feature_data: pd.DataFrame,
        symbols: Optional[List[str]] = None,
        test_window: int = 30,
        arch_lags: int = 5
    ) -> Tuple[List[str], List[Dict]]:
        """
        Test variance stability for multiple symbols.
        
        Args:
            feature_data: DataFrame with computed features
            symbols: List of symbols to test. If None, tests all symbols in feature_data
            test_window: Window size for rolling statistics
            arch_lags: Number of lags for ARCH test
            
        Returns:
            Tuple of (stable_symbols, test_results)
        """
        logger.info("Testing variance stability for multiple symbols...")
        
        if symbols is None:
            symbols = feature_data['symbol'].unique().tolist()
        
        test_results = []
        stable_symbols = []
        
        for symbol in symbols:
            result = self.test_variance_stability(symbol, feature_data, test_window, arch_lags)
            test_results.append(result)
            
            if result['is_stable']:
                stable_symbols.append(symbol)
        
        logger.info(f"Variance stability test complete: {len(stable_symbols)} stable out of {len(symbols)} total")
        
        return stable_symbols, test_results
    
    def save_features_to_database(
        self, 
        feature_data: pd.DataFrame,
        computation_method: str = 'expanding_window',
        data_source: str = 'market_data_historical'
    ) -> int:
        """
        Save computed features to the database.
        Now inserts one-by-one and logs any row that fails.
        """
        logger.info("Saving features to database (row-by-row for debugging)...")
        try:
            records_to_insert = []
            for _, row in feature_data.iterrows():
                ts = row.get('timestamp', None)
                if ts is None or isinstance(ts, (int, float)):
                    ts = row.name if hasattr(row, 'name') and not isinstance(row.name, (int, float)) else datetime.now()
                if not isinstance(ts, (datetime, pd.Timestamp)):
                    try:
                        ts = pd.to_datetime(ts)
                    except Exception:
                        ts = datetime.now()
                record = {
                    'symbol': row['symbol'],
                    'timestamp': ts,
                    'log_close': float(row['log_close']) if pd.notna(row['log_close']) else None,
                    'log_return': float(row['log_return']) if pd.notna(row['log_return']) else None,
                    'z_score': float(row['z_score']) if pd.notna(row['z_score']) else None,
                    'rolling_std': float(row['rolling_std']) if pd.notna(row['rolling_std']) else None,
                    'rolling_mean': float(row['rolling_mean']) if pd.notna(row['rolling_mean']) else None,
                    'volatility_annualized': float(row['volatility_annualized']) if pd.notna(row['volatility_annualized']) else None,
                    'feature_date': row.get('feature_date', date.today()),
                    'computation_method': computation_method,
                    'data_source': data_source
                }
                records_to_insert.append(record)
            columns = list(records_to_insert[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            column_names = ', '.join([f'"{col}"' if col == 'timestamp' else col for col in columns])
            query = f"""
            INSERT INTO market_data_features ({column_names})
            VALUES ({placeholders})
            ON CONFLICT (symbol, "timestamp") DO UPDATE SET
                log_close = EXCLUDED.log_close,
                log_return = EXCLUDED.log_return,
                z_score = EXCLUDED.z_score,
                rolling_std = EXCLUDED.rolling_std,
                rolling_mean = EXCLUDED.rolling_mean,
                volatility_annualized = EXCLUDED.volatility_annualized,
                updated_at = CURRENT_TIMESTAMP
            """
            total_inserted = 0
            with self.db.get_session() as cursor:
                for record in records_to_insert:
                    try:
                        cursor.execute(query, [record[col] for col in columns])
                        total_inserted += 1
                    except Exception as e:
                        logger.error(f"Failed to insert row: {record}\nError: {e}")
                        print(f"Failed to insert row: {record}\nError: {e}")
            logger.info(f"Saved {total_inserted} feature records to database (row-by-row mode)")
            return total_inserted
        except Exception as e:
            logger.error(f"Error saving features to database: {e}")
            raise
    
    def save_variance_stability_results(
        self, 
        test_results: List[Dict]
    ) -> int:
        """
        Save variance stability test results to the database.
        Now inserts one-by-one and logs any row that fails.
        """
        logger.info("Saving variance stability results to database (row-by-row for debugging)...")
        try:
            records_to_insert = []
            for result in test_results:
                record = {
                    'symbol': str(result['symbol']),
                    'test_date': result['test_date'],
                    'record_count': int(result['record_count']) if result['record_count'] is not None else None,
                    'arch_test_pvalue': float(result['arch_test_pvalue']) if result['arch_test_pvalue'] is not None else None,
                    'rolling_std_cv': float(result['rolling_std_cv']) if result['rolling_std_cv'] is not None else None,
                    'ljung_box_pvalue': float(result['ljung_box_pvalue']) if result['ljung_box_pvalue'] is not None else None,
                    'is_stable': bool(result['is_stable']),
                    'filter_reason': str(result['filter_reason']) if result['filter_reason'] is not None else None,
                    'test_window': int(result.get('test_window', 30)),
                    'arch_lags': int(result.get('arch_lags', 5))
                }
                records_to_insert.append(record)
            columns = list(records_to_insert[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            column_names = ', '.join(columns)
            query = f"""
            INSERT INTO variance_stability_tracking ({column_names})
            VALUES ({placeholders})
            ON CONFLICT (symbol, test_date) DO UPDATE SET
                record_count = EXCLUDED.record_count,
                arch_test_pvalue = EXCLUDED.arch_test_pvalue,
                rolling_std_cv = EXCLUDED.rolling_std_cv,
                ljung_box_pvalue = EXCLUDED.ljung_box_pvalue,
                is_stable = EXCLUDED.is_stable,
                filter_reason = EXCLUDED.filter_reason,
                test_window = EXCLUDED.test_window,
                arch_lags = EXCLUDED.arch_lags
            """
            total_inserted = 0
            with self.db.get_session() as cursor:
                for record in records_to_insert:
                    try:
                        cursor.execute(query, [record[col] for col in columns])
                        total_inserted += 1
                    except Exception as e:
                        logger.error(f"Failed to insert variance result: {record}\nError: {e}")
                        print(f"Failed to insert variance result: {record}\nError: {e}")
            logger.info(f"Saved {total_inserted} variance stability results to database (row-by-row mode)")
            return total_inserted
        except Exception as e:
            logger.error(f"Error saving variance stability results to database: {e}")
            raise
    
    def get_stable_features_from_database(
        self, 
        start_date: Optional[date] = None,
        symbols: Optional[List[str]] = None,
        limit: int = 10000
    ) -> pd.DataFrame:
        """
        Get stable features from the database.
        
        Args:
            start_date: Start date for features (default: 30 days ago)
            symbols: List of symbols to retrieve (default: all stable symbols)
            limit: Maximum number of records to retrieve
            
        Returns:
            DataFrame with stable features
        """
        logger.info("Retrieving stable features from database...")
        
        if start_date is None:
            start_date = date.today() - pd.Timedelta(days=30)
        
        try:
            # Build query
            query = """
            SELECT f.symbol, f."timestamp", f.log_close, f.log_return, f.z_score,
                   f.rolling_std, f.rolling_mean, f.volatility_annualized, f.feature_date
            FROM market_data_features f
            JOIN variance_stability_tracking v ON f.symbol = v.symbol 
                AND f.feature_date = v.test_date
            WHERE v.is_stable = true 
                AND f.feature_date >= %s
            """
            
            params = [start_date]
            
            if symbols:
                symbols_str = "', '".join(symbols)
                query += f" AND f.symbol IN ('{symbols_str}')"
            
            query += " ORDER BY f.symbol, f.\"timestamp\" LIMIT %s"
            params.append(limit)
            
            with self.db.get_session() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                if not results:
                    logger.warning("No stable features found in database")
                    return pd.DataFrame()
                
                # Convert to DataFrame
                columns = ['symbol', 'timestamp', 'log_close', 'log_return', 'z_score',
                          'rolling_std', 'rolling_mean', 'volatility_annualized', 'feature_date']
                df = pd.DataFrame(results, columns=columns)
                
                # Set timestamp as index
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                
                logger.info(f"Retrieved {len(df)} stable feature records from database")
                return df
                
        except Exception as e:
            logger.error(f"Error retrieving stable features from database: {e}")
            raise
    
    def get_variance_stability_status(
        self, 
        target_date: Optional[date] = None
    ) -> pd.DataFrame:
        """
        Get variance stability status for a specific date.
        
        Args:
            target_date: Date to check (default: today)
            
        Returns:
            DataFrame with stability status
        """
        if target_date is None:
            target_date = date.today()
        
        logger.info(f"Retrieving variance stability status for {target_date}...")
        
        try:
            query = """
            SELECT symbol, test_date, is_stable, filter_reason, 
                   arch_test_pvalue, rolling_std_cv, record_count, created_at
            FROM variance_stability_tracking 
            WHERE test_date = %s
            ORDER BY is_stable DESC, symbol
            """
            
            with self.db.get_session() as cursor:
                cursor.execute(query, [target_date])
                results = cursor.fetchall()
                
                if not results:
                    logger.warning(f"No variance stability data found for {target_date}")
                    return pd.DataFrame()
                
                columns = ['symbol', 'test_date', 'is_stable', 'filter_reason',
                          'arch_test_pvalue', 'rolling_std_cv', 'record_count', 'created_at']
                df = pd.DataFrame(results, columns=columns)
                
                logger.info(f"Retrieved variance stability status for {len(df)} symbols")
                return df
                
        except Exception as e:
            logger.error(f"Error retrieving variance stability status: {e}")
            raise


# Convenience functions for easy usage
def select_stocks_by_record_count(df: pd.DataFrame, threshold_percent: float = 0.8) -> List[str]:
    """Convenience function for stock selection."""
    utils = DataPreprocessingUtils()
    return utils.select_stocks_by_record_count(df, threshold_percent)


def compute_features_for_symbol(symbol: str, price_data: pd.DataFrame) -> pd.DataFrame:
    """Convenience function for feature computation."""
    utils = DataPreprocessingUtils()
    return utils.compute_features_for_symbol(symbol, price_data)


def test_variance_stability(symbol: str, feature_data: pd.DataFrame) -> Dict:
    """Convenience function for variance stability testing."""
    utils = DataPreprocessingUtils()
    return utils.test_variance_stability(symbol, feature_data)


def get_stable_features_from_database(start_date: Optional[date] = None) -> pd.DataFrame:
    """Convenience function for retrieving stable features."""
    utils = DataPreprocessingUtils()
    return utils.get_stable_features_from_database(start_date) 