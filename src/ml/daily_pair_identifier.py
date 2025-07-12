"""
Daily Pair Identification Flow for GARCH-GRU Pairs Trading System

This module implements the daily pre-market workflow for identifying valid trading pairs
using GARCH models and statistical analysis. The flow runs at 6:00 AM pre-market to
ensure models are ready before market opens at 9:30 AM.

Flow Design:
1. Data Collection (Historical data)
2. Pair Validation & Screening (Correlation + Cointegration)
3. GARCH Model Fitting
4. Model Selection & Ranking
5. MLflow Storage & Registration
6. Trading Configuration Update
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging
from prefect import flow, task, get_run_logger
import warnings
warnings.filterwarnings('ignore')

# Optional MLflow imports - handle gracefully if not available
try:
    import mlflow
    import mlflow.pytorch
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logging.warning("MLflow not available - model logging will be skipped")

from arch import arch_model
from statsmodels.tsa.stattools import coint, acf
from scipy import stats

from src.database.database_connectivity import DatabaseConnectivity

# Optional MLflow imports - handle gracefully if not available
try:
    from src.mlflow_manager import MLflowManager
    from src.ml.config import MLflowConfig
    MLFLOW_IMPORTS_AVAILABLE = True
except ImportError:
    MLFLOW_IMPORTS_AVAILABLE = False
    logging.warning("MLflow manager imports not available - model logging will be skipped")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@task(name="Gather Historical Data")
def gather_historical_data(lookback_days: int = 60) -> pd.DataFrame:
    """
    Gather historical market data for pair analysis.
    
    Args:
        lookback_days: Number of days of historical data to gather
        
    Returns:
        DataFrame with historical price data for all symbols
    """
    logger = get_run_logger()
    logger.info(f"Gathering {lookback_days} days of historical data...")
    
    try:
        db = DatabaseConnectivity()
        
        # Get all active symbols
        query = """
        SELECT DISTINCT symbol 
        FROM market_data 
        WHERE symbol IS NOT NULL 
        ORDER BY symbol
        """
        symbols_result = db.execute_query(query)
        symbols_df = pd.DataFrame(symbols_result, columns=['symbol'])
        symbols = symbols_df['symbol'].tolist()
        
        logger.info(f"Found {len(symbols)} symbols for analysis")
        
        # Get historical data for each symbol
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        query = """
        SELECT symbol, timestamp, close
        FROM market_data 
        WHERE timestamp >= %s 
        AND timestamp <= %s
        AND symbol = ANY(%s)
        ORDER BY symbol, timestamp
        """
        
        historical_result = db.execute_query(query, (start_date, end_date, symbols))
        data = pd.DataFrame(historical_result, columns=['symbol', 'timestamp', 'close'])
        
        # Pivot to get symbols as columns
        historical_df = data.pivot(index='timestamp', columns='symbol', values='close')
        
        logger.info(f"Gathered {len(historical_df)} data points for {len(symbols)} symbols")
        
        return historical_df
        
    except Exception as e:
        logger.error(f"Error gathering historical data: {e}")
        raise
    finally:
        if 'db' in locals():
            db.close()


@task(name="Calculate Pair Correlations")
def calculate_pair_correlations(historical_df: pd.DataFrame, min_correlation: float = 0.8) -> List[Tuple[str, str, float]]:
    """
    Calculate correlations between all symbol pairs and filter by minimum correlation.
    
    Args:
        historical_df: DataFrame with historical price data
        min_correlation: Minimum correlation threshold
        
    Returns:
        List of tuples (symbol1, symbol2, correlation) for pairs above threshold
    """
    logger = get_run_logger()
    logger.info(f"Calculating pair correlations with minimum threshold {min_correlation}...")
    
    symbols = historical_df.columns.tolist()
    valid_pairs = []
    
    for i, symbol1 in enumerate(symbols):
        for symbol2 in symbols[i+1:]:
            # Calculate correlation
            correlation = historical_df[symbol1].corr(historical_df[symbol2])
            
            if correlation >= min_correlation:
                valid_pairs.append((symbol1, symbol2, correlation))
                logger.info(f"Valid pair found: {symbol1}-{symbol2} (correlation: {correlation:.4f})")
    
    logger.info(f"Found {len(valid_pairs)} pairs above correlation threshold")
    return valid_pairs


@task(name="Test Cointegration")
def test_cointegration(historical_df: pd.DataFrame, pairs: List[Tuple[str, str, float]], 
                      max_pvalue: float = 0.05) -> List[Tuple[str, str, float, float]]:
    """
    Test cointegration for each pair using Engle-Granger test.
    
    Args:
        historical_df: DataFrame with historical price data
        pairs: List of (symbol1, symbol2, correlation) tuples
        max_pvalue: Maximum p-value for cointegration test
        
    Returns:
        List of (symbol1, symbol2, correlation, pvalue) for cointegrated pairs
    """
    logger = get_run_logger()
    logger.info(f"Testing cointegration with maximum p-value {max_pvalue}...")
    
    cointegrated_pairs = []
    
    for symbol1, symbol2, correlation in pairs:
        try:
            # Get price series
            series1 = historical_df[symbol1].dropna()
            series2 = historical_df[symbol2].dropna()
            
            # Align series
            common_index = series1.index.intersection(series2.index)
            if len(common_index) < 30:  # Need minimum data points
                continue
                
            series1_aligned = series1.loc[common_index]
            series2_aligned = series2.loc[common_index]
            
            # Test cointegration
            score, pvalue, _ = coint(series1_aligned, series2_aligned)
            
            if pvalue <= max_pvalue:
                cointegrated_pairs.append((symbol1, symbol2, correlation, pvalue))
                logger.info(f"Cointegrated pair: {symbol1}-{symbol2} (p-value: {pvalue:.4f})")
                
        except Exception as e:
            logger.warning(f"Error testing cointegration for {symbol1}-{symbol2}: {e}")
            continue
    
    logger.info(f"Found {len(cointegrated_pairs)} cointegrated pairs")
    return cointegrated_pairs


@task(name="Fit GARCH Models")
def fit_garch_models(historical_df: pd.DataFrame, 
                    cointegrated_pairs: List[Tuple[str, str, float, float]]) -> List[Dict[str, Any]]:
    """
    Fit GARCH(1,1) models to the spread of each cointegrated pair.
    
    Args:
        historical_df: DataFrame with historical price data
        cointegrated_pairs: List of cointegrated pairs
        
    Returns:
        List of dictionaries with GARCH model results
    """
    logger = get_run_logger()
    logger.info("Fitting GARCH models to pair spreads...")
    
    garch_results = []
    
    for symbol1, symbol2, correlation, pvalue in cointegrated_pairs:
        try:
            # Get price series
            series1 = historical_df[symbol1].dropna()
            series2 = historical_df[symbol2].dropna()
            
            # Align series
            common_index = series1.index.intersection(series2.index)
            series1_aligned = series1.loc[common_index]
            series2_aligned = series2.loc[common_index]
            
            # Calculate spread (log difference)
            spread = np.log(series1_aligned) - np.log(series2_aligned)
            
            # Remove any infinite or NaN values
            spread = spread.replace([np.inf, -np.inf], np.nan).dropna()
            
            if len(spread) < 30:
                continue
            
            # Fit GARCH(1,1) model
            model = arch_model(spread, vol='GARCH', p=1, q=1, dist='normal')
            fitted_model = model.fit(disp='off')
            
            # Calculate model diagnostics
            residuals = fitted_model.resid
            standardized_residuals = fitted_model.resid / fitted_model.conditional_volatility
            
            # Ljung-Box test for autocorrelation
            lb_result = acf(residuals**2, nlags=10, qstat=True)
            lb_stat = lb_result[1][-1]  # Last Q-statistic
            lb_pvalue = lb_result[2][-1]  # Last p-value
            
            # ARCH test
            arch_result = acf(standardized_residuals**2, nlags=10, qstat=True)
            arch_stat = arch_result[1][-1]  # Last Q-statistic
            arch_pvalue = arch_result[2][-1]  # Last p-value
            
            # Volatility forecasting (1-step ahead)
            forecast = fitted_model.forecast(horizon=1)
            forecast_vol = np.sqrt(forecast.variance.values[-1, 0])
            
            # Calculate composite score
            aic_score = 1 / (1 + np.exp(fitted_model.aic / 1000))  # Normalize AIC
            vol_forecast_score = 1 / (1 + np.abs(forecast_vol - spread.std()))  # Volatility forecast accuracy
            lb_score = 1 - float(lb_pvalue)  # Higher is better (less autocorrelation)
            arch_score = 1 - float(arch_pvalue)  # Higher is better (less ARCH effects)
            
            composite_score = float(0.4 * aic_score + 
                                   0.3 * vol_forecast_score + 
                                   0.15 * lb_score + 
                                   0.15 * arch_score)
            
            result = {
                'symbol1': symbol1,
                'symbol2': symbol2,
                'correlation': correlation,
                'cointegration_pvalue': pvalue,
                'garch_model': fitted_model,
                'aic': fitted_model.aic,
                'bic': fitted_model.bic,
                'forecast_volatility': forecast_vol,
                'ljung_box_pvalue': lb_pvalue,
                'arch_test_pvalue': arch_pvalue,
                'composite_score': composite_score,
                'spread_series': spread,
                'residuals': residuals,
                'conditional_volatility': fitted_model.conditional_volatility
            }
            
            garch_results.append(result)
            logger.info(f"GARCH model fitted for {symbol1}-{symbol2} (score: {composite_score:.4f})")
            
        except Exception as e:
            logger.warning(f"Error fitting GARCH model for {symbol1}-{symbol2}: {e}")
            continue
    
    logger.info(f"Successfully fitted GARCH models for {len(garch_results)} pairs")
    return garch_results


@task(name="Select Best Models")
def select_best_models(garch_results: List[Dict[str, Any]], 
                      min_composite_score: float = 0.7,
                      max_pairs: int = 10) -> List[Dict[str, Any]]:
    """
    Select the best GARCH models based on composite score.
    
    Args:
        garch_results: List of GARCH model results
        min_composite_score: Minimum composite score threshold
        max_pairs: Maximum number of pairs to select
        
    Returns:
        List of selected GARCH model results
    """
    logger = get_run_logger()
    logger.info(f"Selecting best models with minimum score {min_composite_score}...")
    
    # Filter by minimum score
    qualified_results = [r for r in garch_results if r['composite_score'] >= min_composite_score]
    
    # Sort by composite score (descending)
    qualified_results.sort(key=lambda x: x['composite_score'], reverse=True)
    
    # Take top pairs
    selected_results = qualified_results[:max_pairs]
    
    logger.info(f"Selected {len(selected_results)} pairs for trading")
    
    for i, result in enumerate(selected_results, 1):
        logger.info(f"{i}. {result['symbol1']}-{result['symbol2']} "
                   f"(score: {result['composite_score']:.4f}, "
                   f"correlation: {result['correlation']:.4f})")
    
    return selected_results


@task(name="Log Models to MLflow")
def log_models_to_mlflow(selected_results: List[Dict[str, Any]]) -> List[str]:
    """
    Log selected GARCH models to MLflow for tracking and serving.
    
    Args:
        selected_results: List of selected GARCH model results
        
    Returns:
        List of MLflow run IDs
    """
    logger = get_run_logger()
    logger.info("Logging models to MLflow...")
    
    if not MLFLOW_AVAILABLE:
        logger.warning("MLflow is not available, skipping model logging.")
        return []
    
    if not MLFLOW_IMPORTS_AVAILABLE:
        logger.warning("MLflow manager imports not available, skipping model logging.")
        return []

    try:
        mlflow_manager = MLflowManager()
    except Exception as e:
        logger.error(f"Error initializing MLflow manager: {e}")
        return []
    
    run_ids = []
    
    for result in selected_results:
        try:
            pair_name = f"{result['symbol1']}-{result['symbol2']}"
            
            with mlflow.start_run(run_name=f"GARCH_Daily_{pair_name}_{datetime.now().strftime('%Y%m%d')}"):
                # Log parameters
                mlflow.log_params({
                    'symbol1': result['symbol1'],
                    'symbol2': result['symbol2'],
                    'correlation': result['correlation'],
                    'cointegration_pvalue': result['cointegration_pvalue'],
                    'aic': result['aic'],
                    'bic': result['bic'],
                    'composite_score': result['composite_score'],
                    'model_type': 'GARCH(1,1)',
                    'training_date': datetime.now().strftime('%Y-%m-%d')
                })
                
                # Log metrics
                mlflow.log_metrics({
                    'composite_score': result['composite_score'],
                    'correlation': result['correlation'],
                    'aic': result['aic'],
                    'bic': result['bic'],
                    'forecast_volatility': result['forecast_volatility'],
                    'ljung_box_pvalue': result['ljung_box_pvalue'],
                    'arch_test_pvalue': result['arch_test_pvalue']
                })
                
                # Log model (save as pickle for now)
                import pickle
                model_path = f"garch_model_{pair_name}.pkl"
                with open(model_path, 'wb') as f:
                    pickle.dump(result['garch_model'], f)
                
                mlflow.log_artifact(model_path, "garch_model")
                
                # Log spread series as artifact
                spread_df = pd.DataFrame({
                    'timestamp': result['spread_series'].index,
                    'spread': result['spread_series'].values
                })
                spread_path = f"spread_{pair_name}.csv"
                spread_df.to_csv(spread_path, index=False)
                mlflow.log_artifact(spread_path, "spread_data")
                
                run_id = mlflow.active_run().info.run_id
                run_ids.append(run_id)
                
                logger.info(f"Logged GARCH model for {pair_name} (run_id: {run_id})")
                
        except Exception as e:
            logger.error(f"Error logging model for {result['symbol1']}-{result['symbol2']}: {e}")
            continue
    
    logger.info(f"Successfully logged {len(run_ids)} models to MLflow")
    return run_ids


@task(name="Update Trading Configuration")
def update_trading_configuration(selected_results: List[Dict[str, Any]], 
                               run_ids: List[str]) -> Dict[str, Any]:
    """
    Update trading configuration with selected pairs and model information.
    
    Args:
        selected_results: List of selected GARCH model results
        run_ids: List of MLflow run IDs
        
    Returns:
        Updated trading configuration
    """
    logger = get_run_logger()
    logger.info("Updating trading configuration...")
    
    try:
        db = DatabaseConnectivity()
        
        # Create trading configuration
        trading_config = {
            'active_pairs': [],
            'last_updated': datetime.now().isoformat(),
            'total_pairs_analyzed': len(selected_results),
            'mlflow_run_ids': run_ids
        }
        
        # Handle case where run_ids might be shorter than selected_results
        for i, result in enumerate(selected_results):
            pair_config = {
                'symbol1': result['symbol1'],
                'symbol2': result['symbol2'],
                'correlation': result['correlation'],
                'composite_score': result['composite_score'],
                'mlflow_run_id': run_ids[i] if i < len(run_ids) else None,
                'forecast_volatility': result['forecast_volatility'],
                'model_parameters': {
                    'aic': result['aic'],
                    'bic': result['bic'],
                    'ljung_box_pvalue': result['ljung_box_pvalue'],
                    'arch_test_pvalue': result['arch_test_pvalue']
                }
            }
            trading_config['active_pairs'].append(pair_config)
        
        # Store configuration in database (you can create a table for this)
        # For now, we'll log it
        logger.info(f"Trading configuration updated with {len(trading_config['active_pairs'])} active pairs")
        
        return trading_config
        
    except Exception as e:
        logger.error(f"Error updating trading configuration: {e}")
        raise
    finally:
        if 'db' in locals():
            db.close()


@flow(name="Daily Pair Identification Flow")
def daily_pair_identification_flow(lookback_days: int = 60, 
                                 min_correlation: float = 0.8,
                                 max_cointegration_pvalue: float = 0.05,
                                 min_composite_score: float = 0.7,
                                 max_pairs: int = 10):
    """
    Daily pre-market flow for identifying valid trading pairs using GARCH models.
    
    This flow runs at 6:00 AM pre-market to ensure models are ready before market opens.
    
    Args:
        lookback_days: Number of days of historical data to analyze
        min_correlation: Minimum correlation threshold for pairs
        max_cointegration_pvalue: Maximum p-value for cointegration test
        min_composite_score: Minimum composite score for model selection
        max_pairs: Maximum number of pairs to select for trading
    """
    logger = get_run_logger()
    logger.info("Starting Daily Pair Identification Flow")
    
    try:
        # Step 1: Gather historical data
        historical_df = gather_historical_data(lookback_days)
        
        # Step 2: Calculate pair correlations
        valid_pairs = calculate_pair_correlations(historical_df, min_correlation)
        
        if not valid_pairs:
            logger.warning("No pairs found above correlation threshold")
            return
        
        # Step 3: Test cointegration
        cointegrated_pairs = test_cointegration(historical_df, valid_pairs, max_cointegration_pvalue)
        
        if not cointegrated_pairs:
            logger.warning("No cointegrated pairs found")
            return
        
        # Step 4: Fit GARCH models
        garch_results = fit_garch_models(historical_df, cointegrated_pairs)
        
        if not garch_results:
            logger.warning("No GARCH models could be fitted")
            return
        
        # Step 5: Select best models
        selected_results = select_best_models(garch_results, min_composite_score, max_pairs)
        
        if not selected_results:
            logger.warning("No models met the minimum composite score threshold")
            return
        
        # Step 6: Log models to MLflow
        run_ids = log_models_to_mlflow(selected_results)
        
        # Step 7: Update trading configuration
        trading_config = update_trading_configuration(selected_results, run_ids)
        
        logger.info("Daily Pair Identification Flow completed successfully")
        logger.info(f"Selected {len(selected_results)} pairs for trading")
        
        return trading_config
        
    except Exception as e:
        logger.error(f"Error in Daily Pair Identification Flow: {e}")
        raise


if __name__ == "__main__":
    # Run the flow
    daily_pair_identification_flow() 