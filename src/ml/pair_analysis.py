"""
Pair Analysis Module for Correlation and Cointegration Testing

This module provides comprehensive analysis for pairs trading:
1. Correlation analysis (Pearson's ρ)
2. Cointegration testing (Engle-Granger test)
3. Pair shortlisting based on statistical criteria
4. Spread calculation and validation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
import logging
from datetime import datetime, date
import warnings
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.stattools import adfuller
from scipy import stats
import yaml
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


class PairAnalysis:
    """
    Comprehensive pair analysis for correlation and cointegration testing.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the pair analysis module.
        
        Args:
            config: Optional configuration dictionary. If None, uses defaults.
        """
        self.config = config or self._get_default_config()
        logger.info("PairAnalysis initialized with configuration")
        
    def _get_default_config(self) -> Dict:
        """Get default configuration for pair analysis."""
        return {
            'correlation_threshold': 0.8,  # Pearson's ρ > 0.8
            'cointegration_pvalue_threshold': 0.05,  # Engle-Granger p-value < 0.05
            'min_data_points': 100,  # Minimum data points for analysis
            'min_correlation': 0.5,  # Minimum correlation to consider for cointegration
            'spread_method': 'log_difference',  # 'log_difference' or 'ratio'
            'max_pairs': 50,  # Maximum number of pairs to return
            'save_results': True,  # Whether to save results to database
            'verbose': True  # Whether to print detailed output
        }
    
    def calculate_correlation_matrix(
        self, 
        price_data: pd.DataFrame,
        symbols: Optional[List[str]] = None,
        method: str = 'pearson'
    ) -> pd.DataFrame:
        """
        Calculate correlation matrix for all symbol pairs.
        
        Args:
            price_data: DataFrame with 'symbol', 'timestamp', 'close' columns
            symbols: List of symbols to analyze. If None, uses all symbols in data
            method: Correlation method ('pearson', 'spearman', 'kendall')
            
        Returns:
            Correlation matrix DataFrame
        """
        logger.info(f"Calculating {method} correlation matrix...")
        
        if symbols is None:
            symbols = price_data['symbol'].unique().tolist()
        
        # Pivot data for correlation analysis
        pivoted_data = price_data.pivot(index='timestamp', columns='symbol', values='close')
        
        # Calculate log prices for better correlation analysis
        log_prices = np.log(pivoted_data)
        
        # Calculate correlation matrix
        correlation_matrix = log_prices.corr(method=method)
        
        logger.info(f"Correlation matrix calculated for {len(symbols)} symbols")
        
        return correlation_matrix
    
    def find_highly_correlated_pairs(
        self, 
        correlation_matrix: pd.DataFrame,
        threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Find pairs with high correlation above threshold.
        
        Args:
            correlation_matrix: Correlation matrix from calculate_correlation_matrix
            threshold: Correlation threshold. If None, uses config default
            
        Returns:
            List of dictionaries with pair information and correlation
        """
        threshold = threshold or self.config['correlation_threshold']
        logger.info(f"Finding pairs with correlation > {threshold}")
        
        highly_correlated_pairs = []
        
        # Get upper triangle of correlation matrix (avoid duplicates)
        upper_triangle = correlation_matrix.where(
            np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
        )
        
        # Find pairs above threshold
        for symbol1 in correlation_matrix.columns:
            for symbol2 in correlation_matrix.columns:
                if symbol1 < symbol2:  # Avoid duplicates
                    corr_value = correlation_matrix.loc[symbol1, symbol2]
                    
                    if not pd.isna(corr_value) and corr_value > threshold:
                        highly_correlated_pairs.append({
                            'symbol1': symbol1,
                            'symbol2': symbol2,
                            'correlation': corr_value,
                            'correlation_rank': len(highly_correlated_pairs) + 1
                        })
        
        # Sort by correlation (highest first)
        highly_correlated_pairs.sort(key=lambda x: x['correlation'], reverse=True)
        
        logger.info(f"Found {len(highly_correlated_pairs)} pairs with correlation > {threshold}")
        
        return highly_correlated_pairs
    
    def test_cointegration(
        self, 
        price_data: pd.DataFrame,
        symbol1: str,
        symbol2: str,
        significance_level: Optional[float] = None
    ) -> Dict:
        """
        Test cointegration between two symbols using Engle-Granger test.
        
        Args:
            price_data: DataFrame with 'symbol', 'timestamp', 'close' columns
            symbol1: First symbol
            symbol2: Second symbol
            significance_level: Significance level for test. If None, uses config default
            
        Returns:
            Dictionary with cointegration test results
        """
        significance_level = significance_level or self.config['cointegration_pvalue_threshold']
        
        try:
            # Get price data for both symbols
            symbol1_data = price_data[price_data['symbol'] == symbol1].set_index('timestamp')['close']
            symbol2_data = price_data[price_data['symbol'] == symbol2].set_index('timestamp')['close']
            
            # Align data
            aligned_data = pd.concat([symbol1_data, symbol2_data], axis=1).dropna()
            aligned_data.columns = [symbol1, symbol2]
            
            if len(aligned_data) < self.config['min_data_points']:
                return {
                    'symbol1': symbol1,
                    'symbol2': symbol2,
                    'cointegrated': False,
                    'pvalue': None,
                    'test_statistic': None,
                    'critical_values': None,
                    'error': 'Insufficient data points',
                    'data_points': len(aligned_data)
                }
            
            # Perform Engle-Granger cointegration test
            score, pvalue, critical_values = coint(aligned_data[symbol1], aligned_data[symbol2])
            
            # Determine if cointegrated
            is_cointegrated = pvalue < significance_level
            
            result = {
                'symbol1': symbol1,
                'symbol2': symbol2,
                'cointegrated': is_cointegrated,
                'pvalue': pvalue,
                'test_statistic': score,
                'critical_values': critical_values,
                'significance_level': significance_level,
                'data_points': len(aligned_data),
                'error': None
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error testing cointegration for {symbol1}-{symbol2}: {e}")
            return {
                'symbol1': symbol1,
                'symbol2': symbol2,
                'cointegrated': False,
                'pvalue': None,
                'test_statistic': None,
                'critical_values': None,
                'error': str(e),
                'data_points': 0
            }
    
    def test_cointegration_for_pairs(
        self, 
        price_data: pd.DataFrame,
        correlated_pairs: List[Dict],
        significance_level: Optional[float] = None
    ) -> List[Dict]:
        """
        Test cointegration for a list of correlated pairs.
        
        Args:
            price_data: DataFrame with 'symbol', 'timestamp', 'close' columns
            correlated_pairs: List of correlated pairs from find_highly_correlated_pairs
            significance_level: Significance level for test. If None, uses config default
            
        Returns:
            List of dictionaries with both correlation and cointegration results
        """
        significance_level = significance_level or self.config['cointegration_pvalue_threshold']
        logger.info(f"Testing cointegration for {len(correlated_pairs)} pairs...")
        
        results = []
        
        for i, pair in enumerate(correlated_pairs):
            if self.config['verbose']:
                print(f"Testing cointegration {i+1}/{len(correlated_pairs)}: {pair['symbol1']}-{pair['symbol2']}")
            
            coint_result = self.test_cointegration(
                price_data, pair['symbol1'], pair['symbol2'], significance_level
            )
            
            # Combine correlation and cointegration results
            combined_result = {**pair, **coint_result}
            results.append(combined_result)
        
        logger.info(f"Cointegration testing completed for {len(results)} pairs")
        
        return results
    
    def calculate_spread(
        self, 
        price_data: pd.DataFrame,
        symbol1: str,
        symbol2: str,
        method: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Calculate spread between two symbols.
        
        Args:
            price_data: DataFrame with 'symbol', 'timestamp', 'close' columns
            symbol1: First symbol
            symbol2: Second symbol
            method: Spread calculation method ('log_difference' or 'ratio')
            
        Returns:
            DataFrame with timestamp and spread
        """
        method = method or self.config['spread_method']
        
        try:
            # Get price data for both symbols
            symbol1_data = price_data[price_data['symbol'] == symbol1].set_index('timestamp')['close']
            symbol2_data = price_data[price_data['symbol'] == symbol2].set_index('timestamp')['close']
            
            # Align data
            aligned_data = pd.concat([symbol1_data, symbol2_data], axis=1).dropna()
            aligned_data.columns = [symbol1, symbol2]
            
            # Calculate spread based on method
            if method == 'log_difference':
                spread = np.log(aligned_data[symbol1]) - np.log(aligned_data[symbol2])
            elif method == 'ratio':
                spread = np.log(aligned_data[symbol1] / aligned_data[symbol2])
            else:
                raise ValueError(f"Unknown spread method: {method}")
            
            # Create result DataFrame
            result = pd.DataFrame({
                'timestamp': aligned_data.index,
                'symbol1': symbol1,
                'symbol2': symbol2,
                'spread': spread,
                'spread_method': method
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating spread for {symbol1}-{symbol2}: {e}")
            return pd.DataFrame()
    
    def test_spread_stationarity(
        self, 
        spread_data: pd.DataFrame,
        significance_level: float = 0.05
    ) -> Dict:
        """
        Test if the spread is stationary using Augmented Dickey-Fuller test.
        
        Args:
            spread_data: DataFrame with 'spread' column
            significance_level: Significance level for ADF test
            
        Returns:
            Dictionary with stationarity test results
        """
        try:
            spread_series = spread_data['spread'].dropna()
            
            if len(spread_series) < 10:
                return {
                    'stationary': False,
                    'pvalue': None,
                    'test_statistic': None,
                    'critical_values': None,
                    'error': 'Insufficient data for ADF test'
                }
            
            # Perform Augmented Dickey-Fuller test
            adf_result = adfuller(spread_series)
            adf_stat = adf_result[0]
            pvalue = adf_result[1]
            critical_values = adf_result[4]
            
            # Determine if stationary
            is_stationary = pvalue < significance_level
            
            result = {
                'stationary': is_stationary,
                'pvalue': pvalue,
                'test_statistic': adf_stat,
                'critical_values': critical_values,
                'significance_level': significance_level,
                'error': None
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error testing spread stationarity: {e}")
            return {
                'stationary': False,
                'pvalue': None,
                'test_statistic': None,
                'critical_values': None,
                'error': str(e)
            }
    
    def shortlist_pairs(
        self, 
        price_data: pd.DataFrame,
        symbols: Optional[List[str]] = None,
        max_pairs: Optional[int] = None
    ) -> Tuple[List[Dict], pd.DataFrame]:
        """
        Comprehensive pair shortlisting with correlation and cointegration analysis.
        
        Args:
            price_data: DataFrame with 'symbol', 'timestamp', 'close' columns
            symbols: List of symbols to analyze. If None, uses all symbols in data
            max_pairs: Maximum number of pairs to return. If None, uses config default
            
        Returns:
            Tuple of (shortlisted_pairs, correlation_matrix)
        """
        max_pairs = max_pairs or self.config['max_pairs']
        
        logger.info("=" * 60)
        logger.info("PAIR SHORTLISTING WITH CORRELATION AND COINTEGRATION")
        logger.info("=" * 60)
        
        # Step 1: Calculate correlation matrix
        logger.info("\nStep 1: Calculating correlation matrix...")
        correlation_matrix = self.calculate_correlation_matrix(price_data, symbols)
        
        # Step 2: Find highly correlated pairs
        logger.info("\nStep 2: Finding highly correlated pairs...")
        correlated_pairs = self.find_highly_correlated_pairs(correlation_matrix)
        
        if not correlated_pairs:
            logger.warning("No highly correlated pairs found!")
            return [], correlation_matrix
        
        # Step 3: Test cointegration for correlated pairs
        logger.info("\nStep 3: Testing cointegration...")
        cointegration_results = self.test_cointegration_for_pairs(price_data, correlated_pairs)
        
        # Step 4: Filter and rank pairs
        logger.info("\nStep 4: Filtering and ranking pairs...")
        shortlisted_pairs = []
        
        for result in cointegration_results:
            # Check if pair meets all criteria
            meets_correlation = result['correlation'] > self.config['correlation_threshold']
            meets_cointegration = result['cointegrated']
            sufficient_data = result['data_points'] >= self.config['min_data_points']
            no_error = result['error'] is None
            
            if meets_correlation and meets_cointegration and sufficient_data and no_error:
                # Calculate spread and test stationarity
                spread_data = self.calculate_spread(
                    price_data, result['symbol1'], result['symbol2']
                )
                
                if not spread_data.empty:
                    stationarity_result = self.test_spread_stationarity(spread_data)
                    
                    # Add spread and stationarity info to result
                    result['spread_stationary'] = stationarity_result['stationary']
                    result['spread_pvalue'] = stationarity_result['pvalue']
                    result['spread_data_points'] = len(spread_data)
                    
                    shortlisted_pairs.append(result)
        
        # Sort by correlation (highest first) and limit to max_pairs
        shortlisted_pairs.sort(key=lambda x: x['correlation'], reverse=True)
        shortlisted_pairs = shortlisted_pairs[:max_pairs]
        
        # Print summary
        logger.info(f"\n[SUMMARY] PAIR SHORTLISTING RESULTS:")
        logger.info("-" * 50)
        logger.info(f"Total symbols analyzed: {len(correlation_matrix.columns)}")
        logger.info(f"Highly correlated pairs (>0.8): {len(correlated_pairs)}")
        logger.info(f"Cointegrated pairs: {len([p for p in cointegration_results if p['cointegrated']])}")
        logger.info(f"Final shortlisted pairs: {len(shortlisted_pairs)}")
        
        if shortlisted_pairs:
            logger.info("\nTop shortlisted pairs:")
            for i, pair in enumerate(shortlisted_pairs[:10], 1):
                logger.info(f"{i:2d}. {pair['symbol1']}-{pair['symbol2']}: "
                          f"Corr={pair['correlation']:.4f}, "
                          f"Coint_p={pair['pvalue']:.4f}, "
                          f"Spread_stationary={pair['spread_stationary']}")
        
        return shortlisted_pairs, correlation_matrix
    
    def create_pairs_data_for_training(
        self, 
        price_data: pd.DataFrame,
        shortlisted_pairs: List[Dict]
    ) -> List[pd.DataFrame]:
        """
        Create training data for shortlisted pairs.
        
        Args:
            price_data: DataFrame with 'symbol', 'timestamp', 'close' columns
            shortlisted_pairs: List of shortlisted pairs from shortlist_pairs
            
        Returns:
            List of DataFrames, one for each pair with spread and features
        """
        logger.info(f"Creating training data for {len(shortlisted_pairs)} pairs...")
        
        pairs_data_list = []
        
        for pair in shortlisted_pairs:
            symbol1, symbol2 = pair['symbol1'], pair['symbol2']
            
            try:
                # Calculate spread
                spread_data = self.calculate_spread(price_data, symbol1, symbol2)
                
                if spread_data.empty:
                    continue
                
                # Add pair metadata
                pair_data = spread_data.copy()
                pair_data['correlation'] = pair['correlation']
                pair_data['cointegration_pvalue'] = pair['pvalue']
                pair_data['spread_stationary'] = pair['spread_stationary']
                
                # Add basic features
                pair_data['spread_lag1'] = pair_data['spread'].shift(1)
                pair_data['spread_lag2'] = pair_data['spread'].shift(2)
                pair_data['spread_lag3'] = pair_data['spread'].shift(3)
                pair_data['spread_lag4'] = pair_data['spread'].shift(4)
                pair_data['spread_lag5'] = pair_data['spread'].shift(5)
                
                # Rolling statistics
                pair_data['spread_ma5'] = pair_data['spread'].rolling(5).mean()
                pair_data['spread_ma20'] = pair_data['spread'].rolling(20).mean()
                pair_data['spread_std5'] = pair_data['spread'].rolling(5).std()
                pair_data['spread_std20'] = pair_data['spread'].rolling(20).std()
                
                # Z-score of spread
                pair_data['spread_zscore'] = (pair_data['spread'] - pair_data['spread_ma20']) / pair_data['spread_std20']
                
                # Drop NaN values
                pair_data = pair_data.dropna()
                
                if len(pair_data) >= self.config['min_data_points']:
                    pairs_data_list.append(pair_data)
                    logger.info(f"Created training data for {symbol1}-{symbol2}: {len(pair_data)} records")
                
            except Exception as e:
                logger.error(f"Error creating training data for {symbol1}-{symbol2}: {e}")
                continue
        
        logger.info(f"Created training data for {len(pairs_data_list)} pairs")
        
        return pairs_data_list
    
    def save_analysis_results(
        self, 
        shortlisted_pairs: List[Dict],
        correlation_matrix: pd.DataFrame,
        analysis_date: Optional[date] = None
    ) -> bool:
        """
        Save analysis results to database (placeholder for future implementation).
        
        Args:
            shortlisted_pairs: List of shortlisted pairs
            correlation_matrix: Correlation matrix
            analysis_date: Date of analysis. If None, uses today
            
        Returns:
            True if successful, False otherwise
        """
        if not self.config['save_results']:
            return True
        
        analysis_date = analysis_date or date.today()
        
        try:
            # TODO: Implement database saving
            logger.info(f"Analysis results would be saved for {analysis_date}")
            return True
        except Exception as e:
            logger.error(f"Error saving analysis results: {e}")
            return False


def analyze_pairs_for_training(
    price_data: pd.DataFrame,
    symbols: Optional[List[str]] = None,
    config: Optional[Dict] = None
) -> Tuple[List[Dict], List[pd.DataFrame], pd.DataFrame]:
    """
    Convenience function for complete pair analysis and training data preparation.
    
    Args:
        price_data: DataFrame with 'symbol', 'timestamp', 'close' columns
        symbols: List of symbols to analyze. If None, uses all symbols in data
        config: Optional configuration dictionary
        
    Returns:
        Tuple of (shortlisted_pairs, training_data_list, correlation_matrix)
    """
    # Initialize analyzer
    analyzer = PairAnalysis(config)
    
    # Perform comprehensive analysis
    shortlisted_pairs, correlation_matrix = analyzer.shortlist_pairs(price_data, symbols)
    
    # Create training data
    training_data_list = analyzer.create_pairs_data_for_training(price_data, shortlisted_pairs)
    
    # Save results if configured
    analyzer.save_analysis_results(shortlisted_pairs, correlation_matrix)
    
    return shortlisted_pairs, training_data_list, correlation_matrix 