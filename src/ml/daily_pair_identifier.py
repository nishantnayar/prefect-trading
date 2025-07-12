"""
Daily Pair Identification Flow for GARCH-GRU Pairs Trading System

This module implements the daily pre-market workflow for identifying valid trading pairs
using GARCH models and statistical analysis, plus GRU model training for all pairs.
The flow runs at 6:00 AM pre-market to ensure models are ready before market opens at 9:30 AM.

Flow Design:
1. Data Collection (Historical data)
2. Pair Validation & Screening (Correlation + Cointegration)
3. GARCH Model Fitting
4. GRU Model Training (for all pairs)
5. Model Selection & Ranking
6. MLflow Storage & Registration
7. Database Performance Tracking
8. Trading Configuration Update
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
import statsmodels.api as sm

from src.database.database_connectivity import DatabaseConnectivity

# Optional MLflow imports - handle gracefully if not available
try:
    from src.mlflow_manager import MLflowManager
    from src.ml.config import MLflowConfig
    MLFLOW_IMPORTS_AVAILABLE = True
except ImportError:
    MLFLOW_IMPORTS_AVAILABLE = False
    logging.warning("MLflow manager imports not available - model logging will be skipped")

# GRU training imports
try:
    import torch
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import GRU, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping
    from sklearn.metrics import accuracy_score, f1_score
    from src.ml.model_performance_tracker import save_training_results
    GRU_AVAILABLE = True
except ImportError:
    GRU_AVAILABLE = False
    logging.warning("GRU training modules not available - GRU training will be skipped")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@task(name="Gather Historical Data")
def gather_historical_data(lookback_days: int = 60, sector: str = "Technology") -> pd.DataFrame:
    """
    Gather historical market data for pair analysis, matching the Jupyter notebook approach.
    
    Args:
        lookback_days: Number of days of historical data to gather
        sector: Sector to filter stocks (default: Technology)
        
    Returns:
        DataFrame with historical price data for all symbols in the specified sector
    """
    logger = get_run_logger()
    logger.info(f"Gathering {lookback_days} days of historical data for {sector} sector...")
    
    try:
        db = DatabaseConnectivity()
        
        # Get symbols from the specified sector (matching notebook approach)
        query = f"""
        SELECT a.symbol, a.timestamp, a.close, y.longname, y.sector, y.industry
        FROM yahoo_finance_info_new y, yahoo_data_hour a
        WHERE y.symbol = a.symbol
        AND y.sector = '{sector}';
        """
        
        data_result = db.execute_query(query)
        original_df = pd.DataFrame(data_result, columns=['symbol', 'timestamp', 'close', 'longname', 'sector', 'industry'])
        
        logger.info(f"Found {len(original_df['symbol'].unique())} symbols in {sector} sector")
        
        # Data quality checks (matching notebook approach)
        symbol_counts = pd.DataFrame(original_df['symbol'].value_counts())
        high = symbol_counts['count'].head(1).values
        low = symbol_counts['count'].tail(1).values
        
        if high[0] != low[0]:
            logger.info("Data quality check: Symbol counts don't match, performing cleaning...")
            
            # Calculate 80% of the highest count
            high_percent = high[0] * 0.80
            
            # Filter symbols with sufficient data
            filtered_symbols = symbol_counts[symbol_counts['count'] > high_percent]
            filtered_symbol_list = filtered_symbols.index
            
            # Filter result_df based on the selected symbols
            original_df = original_df[original_df['symbol'].isin(filtered_symbol_list)]
            logger.info(f"After data quality filtering: {len(original_df['symbol'].unique())} symbols")
        
        # Get the highest count and filter timestamps
        highest_count = original_df['timestamp'].value_counts().max()
        most_common_timestamps = original_df['timestamp'].value_counts()[
            original_df['timestamp'].value_counts() == highest_count
        ].index.tolist()
        
        # Filter the DataFrame
        original_df = original_df[original_df['timestamp'].isin(most_common_timestamps)]
        logger.info(f"After timestamp alignment: {len(original_df['symbol'].unique())} symbols")
        
        # Pivot to get symbols as columns (matching notebook format)
        historical_df = original_df.pivot(index='timestamp', columns='symbol', values='close')
        
        logger.info(f"Final dataset: {len(historical_df)} timestamps for {len(historical_df.columns)} symbols")
        
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


@task(name="Train GRU Models")
def train_gru_models_for_pairs(historical_df: pd.DataFrame, 
                              all_pairs: List[Tuple[str, str, float]], 
                              config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Train GRU models for all pairs, matching the Jupyter notebook approach.
    
    This implementation follows the notebook's methodology:
    1. Calculate spread using OLS regression (beta and mu)
    2. Add GARCH features for volatility modeling
    3. Create comprehensive feature engineering
    4. Define mean reversion target variable
    5. Train GRU models with proper sequence handling
    
    Args:
        historical_df: DataFrame with historical price data
        all_pairs: List of all pairs to train (symbol1, symbol2, correlation)
        config: GRU training configuration
        
    Returns:
        List of training results for each pair
    """
    logger = get_run_logger()
    logger.info("Starting GRU model training for all pairs (notebook approach)...")
    
    if not GRU_AVAILABLE:
        logger.warning("GRU training modules not available, skipping GRU training")
        return []
    
    # Default configuration (matching notebook optimal parameters)
    if config is None:
        config = {
            'sequence_length': 10,
            'gru_units': 64,
            'dropout_rate': 0.255,
            'learning_rate': 0.0003,
            'batch_size': 32,
            'epochs': 100,
            'patience': 10,
            'use_optuna': False,  # Set to True for hyperparameter optimization
            'n_trials': 20  # Number of Optuna trials if enabled
        }
    
    logger.info(f"GRU training configuration: {config}")
    
    # Set random seeds for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)
    
    # Track performance across all pairs
    pair_performance = []
    successful_saves = 0
    total_attempts = 0
    
    # Train a model for each pair
    total_pairs = len(all_pairs)
    for pair_idx, (symbol1, symbol2, correlation) in enumerate(all_pairs, 1):
        total_attempts += 1
        
        logger.info(f"[{pair_idx}/{total_pairs}] Training GRU model for pair: {symbol1}-{symbol2}")
        
        try:
            # Step 1: Get aligned price data
            series1 = historical_df[symbol1].dropna()
            series2 = historical_df[symbol2].dropna()
            
            # Align series
            common_index = series1.index.intersection(series2.index)
            if len(common_index) < 100:  # Minimum data requirement
                logger.info(f"Skipping pair {symbol1}-{symbol2} (not enough data: {len(common_index)})")
                continue
                
            series1_aligned = series1.loc[common_index]
            series2_aligned = series2.loc[common_index]
            
            # Step 2: Calculate spread using OLS regression (matching notebook)
            log_p1 = np.log(series1_aligned)
            log_p2 = np.log(series2_aligned)
            
            # Calculate β (cointegration coefficient) via OLS
            X = sm.add_constant(log_p2)
            model = sm.OLS(log_p1, X).fit()
            beta = model.params[1]  # Slope coefficient
            mu = model.params[0]    # Intercept
            
            # Calculate spread
            spread = log_p1 - beta * log_p2 - mu
            
            # Step 3: Fit GARCH model for volatility features
            spread_returns = spread.diff().dropna()
            scaling_factor = 1 / spread_returns.std()
            scaled_returns = spread_returns * scaling_factor
            
            # Fit GARCH model
            garch_model = arch_model(scaled_returns, vol='Garch', p=1, q=1)
            garch_results = garch_model.fit(update_freq=5, disp='off')
            
            # Get GARCH features
            conditional_vol = garch_results.conditional_volatility / scaling_factor
            standardized_resid = garch_results.resid / garch_results.conditional_volatility
            
            # Step 4: Create comprehensive feature matrix (matching notebook)
            df = spread.to_frame(name='spread')
            
            # Add lagged features
            for lag in range(1, 6):
                df[f'lag_{lag}'] = df['spread'].shift(lag)
            
            # Add GARCH features
            garch_features = pd.DataFrame({
                'garch_vol': conditional_vol,
                'garch_resid': standardized_resid
            }, index=spread_returns.index)
            
            df = df.join(garch_features, how='inner')
            
            # Add technical indicators
            df['MA_5'] = df['spread'].rolling(5).mean()
            df['MA_20'] = df['spread'].rolling(20).mean()
            
            # RSI (14-day)
            delta = df['spread'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()
            rs = avg_gain / avg_loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Drop NaN from rolling calculations
            df = df.dropna()
            
            if len(df) < 50:  # Need sufficient data after feature engineering
                logger.info(f"Skipping pair {symbol1}-{symbol2} (insufficient data after feature engineering: {len(df)})")
                continue
            
            # Step 5: Define target variable (mean reversion prediction)
            future_spread = df['spread'].shift(-1)
            current_spread = df['spread']
            df['target'] = ((future_spread - current_spread) * current_spread < 0).astype(int)
            
            # Select features and target
            features = [
                'lag_1', 'lag_2', 'lag_3', 'lag_4', 'lag_5',
                'garch_vol', 'garch_resid',
                'MA_5', 'MA_20', 'RSI'
            ]
            
            X = df[features]
            y = df['target']
            
            # Drop last row (where target is NaN)
            X = X.iloc[:-1]
            y = y.iloc[:-1]
            
            if len(X) < 50:
                logger.info(f"Skipping pair {symbol1}-{symbol2} (insufficient data after target creation: {len(X)})")
                continue
            
            # Step 6: Train/test split (time-series aware)
            split_idx = int(0.8 * len(X))
            X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
            y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
            
            # Step 7: Create sequences for GRU
            def create_sequences(data, targets, seq_length):
                """Create time-series sequences with aligned features and labels"""
                X, y = [], []
                for i in range(len(data) - seq_length):
                    X.append(data.iloc[i:i+seq_length].values)
                    y.append(targets.iloc[i+seq_length])
                return np.array(X), np.array(y)
            
            X_train_seq, y_train_seq = create_sequences(X_train, y_train, config['sequence_length'])
            X_test_seq, y_test_seq = create_sequences(X_test, y_test, config['sequence_length'])
            
            if len(X_train_seq) < 20 or len(X_test_seq) < 10:
                logger.info(f"Skipping pair {symbol1}-{symbol2} (insufficient sequences: train={len(X_train_seq)}, test={len(X_test_seq)})")
                continue
            
            # Step 8: Hyperparameter optimization (optional, matching notebook)
            if config.get('use_optuna', False):
                logger.info(f"Running Optuna optimization for {symbol1}-{symbol2}...")
                best_params = optimize_hyperparameters_optuna(X_train, y_train, config)
                config.update(best_params)
                # Recreate sequences with optimal sequence length
                X_train_seq, y_train_seq = create_sequences(X_train, y_train, config['sequence_length'])
                X_test_seq, y_test_seq = create_sequences(X_test, y_test, config['sequence_length'])
            
            # Step 9: Build and train GRU model
            model = build_gru_model(X_train_seq.shape[2], config)
            
            # Train with early stopping
            early_stop = EarlyStopping(monitor='val_loss', patience=config['patience'], restore_best_weights=True)
            
            history = model.fit(
                X_train_seq, y_train_seq,
                validation_data=(X_test_seq, y_test_seq),
                epochs=config['epochs'],
                batch_size=config['batch_size'],
                callbacks=[early_stop],
                verbose=0
            )
            
            # Step 10: Evaluate model
            train_probs = model.predict(X_train_seq, verbose=0)
            test_probs = model.predict(X_test_seq, verbose=0)
            
            train_pred = (train_probs > 0.5).astype(int).flatten()
            test_pred = (test_probs > 0.5).astype(int).flatten()
            
            # Calculate metrics
            train_accuracy = accuracy_score(y_train_seq, train_pred)
            test_accuracy = accuracy_score(y_test_seq, test_pred)
            train_f1 = f1_score(y_train_seq, train_pred, zero_division=0)
            test_f1 = f1_score(y_test_seq, test_pred, zero_division=0)
            
            # Find best F1 score from validation history
            best_val_f1 = max(history.history.get('val_f1', [0]))
            
            # Step 11: Save to MLflow and database
            pair_symbol = f"{symbol1}-{symbol2}"
            
            # Add pair info to config for MLflow logging
            config_with_pair = config.copy()
            config_with_pair['pair_symbol1'] = symbol1
            config_with_pair['pair_symbol2'] = symbol2
            config_with_pair['beta'] = beta
            config_with_pair['mu'] = mu
            config_with_pair['correlation'] = correlation
            
            # Save training results to database
            history_data = {
                'train_losses': history.history['loss'],
                'val_losses': history.history['val_loss'],
                'train_accuracies': history.history['accuracy'],
                'val_accuracies': history.history['val_accuracy'],
                'best_val_f1': best_val_f1,
                'final_val_f1': test_f1
            }
            
            save_success = save_training_results(
                pair_symbol=pair_symbol,
                history=history_data,
                config=config_with_pair,
                model_run_id=f"gru_{pair_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                experiment_name="pairs_trading_gru",
                run_name=f"GRU_{pair_symbol}",
                early_stopped=len(history.history['val_loss']) < config['epochs']
            )
            
            if save_success:
                logger.info(f"Performance metrics saved to database for {pair_symbol}")
                successful_saves += 1
                
                # Update rankings incrementally after each successful save
                try:
                    db = DatabaseConnectivity()
                    with db.get_connection() as conn:
                        with conn.cursor() as cursor:
                            cursor.execute("SELECT update_model_rankings();")
                            conn.commit()
                    logger.info(f"Rankings updated after {pair_symbol}")
                except Exception as ranking_error:
                    logger.warning(f"Failed to update rankings after {pair_symbol}: {ranking_error}")
                finally:
                    if 'db' in locals():
                        db.close()
            else:
                logger.warning(f"Failed to save performance metrics for {pair_symbol}")
            
            # Store performance data for summary
            performance_data = {
                'pair': pair_symbol,
                'symbol1': symbol1,
                'symbol2': symbol2,
                'correlation': correlation,
                'beta': beta,
                'mu': mu,
                'data_points': len(df),
                'best_f1': best_val_f1,
                'final_f1': test_f1,
                'train_accuracy': train_accuracy,
                'test_accuracy': test_accuracy,
                'train_f1': train_f1,
                'test_f1': test_f1,
                'epochs_trained': len(history.history['val_loss']),
                'saved_to_db': save_success,
                'early_stopped': len(history.history['val_loss']) < config['epochs']
            }
            pair_performance.append(performance_data)
            
            logger.info(f"Best Validation F1 Score for {symbol1}-{symbol2}: {best_val_f1:.4f}")
            logger.info(f"Final Test F1 Score: {test_f1:.4f}")
            logger.info(f"Epochs trained: {len(history.history['val_loss'])}")
            if len(history.history['val_loss']) < config['epochs']:
                logger.info(f"Training stopped early (patience: {config['patience']})")
                
        except Exception as e:
            logger.error(f"Error training GRU model for {symbol1}-{symbol2}: {e}")
            continue
    
    # Final rankings and trends update
    try:
        db = DatabaseConnectivity()
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT update_model_rankings();")
                cursor.execute("SELECT update_model_trends();")
                conn.commit()
        logger.info("Final model rankings and trends updated in database.")
    except Exception as e:
        logger.error(f"Failed to update final rankings/trends: {e}")
    finally:
        if 'db' in locals():
            db.close()
    
    logger.info(f"GRU training completed for {len(pair_performance)} pairs")
    logger.info(f"Database save success rate: {successful_saves}/{total_attempts} ({successful_saves/total_attempts*100:.1f}%)")
    return pair_performance


def build_gru_model(n_features: int, config: Dict[str, Any]):
    """Build GRU model with specified configuration."""
    model = Sequential([
        GRU(config['gru_units'], input_shape=(config['sequence_length'], n_features)),
        Dropout(config['dropout_rate']),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=config['learning_rate']),
        loss='binary_crossentropy',
        metrics=['accuracy', 'f1']
    )
    return model


def optimize_hyperparameters_optuna(X_train: pd.DataFrame, y_train: pd.Series, config: Dict[str, Any]) -> Dict[str, Any]:
    """Optimize hyperparameters using Optuna (matching notebook approach)."""
    import optuna
    
    def objective(trial):
        # Sample hyperparameters
        sequence_length = trial.suggest_categorical("sequence_length", [10, 20, 30])
        gru_units = trial.suggest_categorical("gru_units", [64, 128])
        dropout_rate = trial.suggest_float("dropout_rate", 0.2, 0.3)
        learning_rate = trial.suggest_float("learning_rate", 1e-4, 1e-2, log=True)
        batch_size = trial.suggest_categorical("batch_size", [32, 64])
        
        # Create sequences
        def create_sequences(data, targets, seq_length):
            X, y = [], []
            for i in range(len(data) - seq_length):
                X.append(data.iloc[i:i+seq_length].values)
                y.append(targets.iloc[i+seq_length])
            return np.array(X), np.array(y)
        
        X_train_seq, y_train_seq = create_sequences(X_train, y_train, sequence_length)
        
        # Validation split
        val_size = int(0.15 * len(X_train_seq))
        X_train_final = X_train_seq[:-val_size]
        y_train_final = y_train_seq[:-val_size]
        X_val = X_train_seq[-val_size:]
        y_val = y_train_seq[-val_size:]
        
        # Build and train model
        model = build_gru_model(X_train_final.shape[2], {
            'sequence_length': sequence_length,
            'gru_units': gru_units,
            'dropout_rate': dropout_rate,
            'learning_rate': learning_rate,
            'batch_size': batch_size,
            'epochs': 50,
            'patience': 5
        })
        
        early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
        
        history = model.fit(
            X_train_final, y_train_final,
            validation_data=(X_val, y_val),
            epochs=50,
            batch_size=batch_size,
            callbacks=[early_stop],
            verbose=0
        )
        
        # Return best validation F1 score
        return max(history.history.get('val_f1', [0]))
    
    # Run optimization
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=config.get('n_trials', 20), show_progress_bar=False)
    
    return study.best_trial.params


@task(name="Update Model Rankings and Trends")
def update_model_rankings_and_trends() -> bool:
    """
    Update model rankings and trends in the database.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger = get_run_logger()
    logger.info("Updating model rankings and trends...")
    
    try:
        db = DatabaseConnectivity()
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT update_model_rankings();")
                cursor.execute("SELECT update_model_trends();")
                conn.commit()
        logger.info("Model rankings and trends updated in database.")
        return True
    except Exception as e:
        logger.error(f"Failed to update rankings/trends: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()


@task(name="Analyze Training Performance")
def analyze_training_performance(pair_performance: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze and summarize training performance across all pairs.
    
    Args:
        pair_performance: List of training results for each pair
        
    Returns:
        Dictionary with performance analysis
    """
    logger = get_run_logger()
    logger.info("Analyzing training performance...")
    
    if not pair_performance:
        logger.warning("No performance data to analyze")
        return {}
    
    # Sort by best F1 score
    pair_performance.sort(key=lambda x: x['best_f1'], reverse=True)
    
    # Find the best performing pair
    best_pair = pair_performance[0]
    
    # Database save statistics
    saved_count = sum(1 for p in pair_performance if p['saved_to_db'])
    total_count = len(pair_performance)
    
    # Performance statistics
    f1_scores = [p['best_f1'] for p in pair_performance]
    avg_f1 = sum(f1_scores) / len(f1_scores)
    max_f1 = max(f1_scores)
    min_f1 = min(f1_scores)
    
    # Correlation vs Performance analysis
    high_corr_pairs = [p for p in pair_performance if p['correlation'] > 0.85]
    low_corr_pairs = [p for p in pair_performance if p['correlation'] <= 0.85]
    
    high_corr_avg = sum(p['best_f1'] for p in high_corr_pairs) / len(high_corr_pairs) if high_corr_pairs else 0
    low_corr_avg = sum(p['best_f1'] for p in low_corr_pairs) / len(low_corr_pairs) if low_corr_pairs else 0
    
    analysis = {
        'total_pairs_trained': total_count,
        'successfully_saved': saved_count,
        'save_rate': saved_count/total_count*100 if total_count > 0 else 0,
        'best_pair': {
            'pair': best_pair['pair'],
            'best_f1': best_pair['best_f1'],
            'final_f1': best_pair['final_f1'],
            'correlation': best_pair['correlation'],
            'data_points': best_pair['data_points']
        },
        'performance_stats': {
            'average_f1': avg_f1,
            'highest_f1': max_f1,
            'lowest_f1': min_f1,
            'performance_range': max_f1 - min_f1
        },
        'correlation_analysis': {
            'high_correlation_pairs': len(high_corr_pairs),
            'high_correlation_avg_f1': high_corr_avg,
            'low_correlation_pairs': len(low_corr_pairs),
            'low_correlation_avg_f1': low_corr_avg
        },
        'all_pairs_ranked': [
            {
                'rank': i+1,
                'pair': p['pair'],
                'best_f1': p['best_f1'],
                'correlation': p['correlation'],
                'saved_to_db': p['saved_to_db']
            }
            for i, p in enumerate(pair_performance)
        ]
    }
    
    # Log summary
    logger.info(f"BEST PERFORMING PAIR: {best_pair['pair']}")
    logger.info(f"   Best F1 Score: {best_pair['best_f1']:.4f}")
    logger.info(f"   Final F1 Score: {best_pair['final_f1']:.4f}")
    logger.info(f"   Correlation: {best_pair['correlation']:.4f}")
    logger.info(f"   Data Points: {best_pair['data_points']}")
    
    logger.info(f"DATABASE SAVE STATISTICS:")
    logger.info(f"   Successfully saved: {saved_count}/{total_count} pairs")
    logger.info(f"   Save rate: {saved_count/total_count*100:.1f}%")
    
    logger.info(f"PERFORMANCE STATISTICS:")
    logger.info(f"   Average F1 Score: {avg_f1:.4f}")
    logger.info(f"   Highest F1 Score: {max_f1:.4f} ({best_pair['pair']})")
    logger.info(f"   Lowest F1 Score: {min_f1:.4f}")
    logger.info(f"   Performance Range: {max_f1 - min_f1:.4f}")
    
    if high_corr_pairs:
        logger.info(f"CORRELATION VS PERFORMANCE ANALYSIS:")
        logger.info(f"   High correlation pairs (>0.85): {len(high_corr_pairs)} pairs, Avg F1: {high_corr_avg:.4f}")
    
    if low_corr_pairs:
        logger.info(f"   Lower correlation pairs (≤0.85): {len(low_corr_pairs)} pairs, Avg F1: {low_corr_avg:.4f}")
    
    return analysis


@task(name="Track Flow Progress")
def track_flow_progress(step_name: str, step_number: int, total_steps: int, details: str = ""):
    """
    Track progress of the daily pair identification flow.
    
    Args:
        step_name: Name of the current step
        step_number: Current step number
        total_steps: Total number of steps
        details: Additional details about the step
    """
    logger = get_run_logger()
    progress_percent = (step_number / total_steps) * 100
    logger.info(f"PROGRESS: Step {step_number}/{total_steps} ({progress_percent:.1f}%) - {step_name}")
    if details:
        logger.info(f"  Details: {details}")


@flow(name="Daily Pair Identification Flow")
def daily_pair_identification_flow(lookback_days: int = 60, 
                                 min_correlation: float = 0.8,
                                 max_cointegration_pvalue: float = 0.05,
                                 min_composite_score: float = 0.7,
                                 max_pairs: int = 10,
                                 train_all_pairs: bool = True,
                                 sector: str = "Technology"):
    """
    Daily pre-market flow for identifying valid trading pairs using GARCH models and GRU training.
    
    This flow runs at 6:00 AM pre-market to ensure models are ready before market opens.
    Matches the Jupyter notebook approach for data processing and model training.
    
    Args:
        lookback_days: Number of days of historical data to analyze
        min_correlation: Minimum correlation threshold for pairs
        max_cointegration_pvalue: Maximum p-value for cointegration test
        min_composite_score: Minimum composite score for model selection
        max_pairs: Maximum number of pairs to select for trading
        train_all_pairs: Whether to train GRU models for all pairs (not just selected ones)
        sector: Sector to analyze (default: Technology, matching notebook)
    """
    logger = get_run_logger()
    logger.info("Starting Daily Pair Identification Flow (notebook approach)")
    
    try:
        # Step 1: Gather historical data (matching notebook approach)
        track_flow_progress("Gather Historical Data", 1, 9, f"Lookback: {lookback_days} days, Sector: {sector}")
        historical_df = gather_historical_data(lookback_days, sector)
        
        if historical_df.empty or len(historical_df.columns) < 2:
            logger.warning(f"No sufficient data found for {sector} sector")
            return None
        
        # Step 2: Calculate pair correlations
        track_flow_progress("Calculate Pair Correlations", 2, 9, f"Min correlation: {min_correlation}")
        valid_pairs = calculate_pair_correlations(historical_df, min_correlation)
        
        if not valid_pairs:
            logger.warning("No pairs found above correlation threshold")
            return None
        
        # Step 3: Test cointegration
        track_flow_progress("Test Cointegration", 3, 9, f"Max p-value: {max_cointegration_pvalue}")
        cointegrated_pairs = test_cointegration(historical_df, valid_pairs, max_cointegration_pvalue)
        
        if not cointegrated_pairs:
            logger.warning("No cointegrated pairs found")
            return None
        
        # Step 4: Fit GARCH models
        track_flow_progress("Fit GARCH Models", 4, 9, f"Pairs to fit: {len(cointegrated_pairs)}")
        garch_results = fit_garch_models(historical_df, cointegrated_pairs)
        
        if not garch_results:
            logger.warning("No GARCH models could be fitted")
            return None
        
        # Step 5: Select best models
        track_flow_progress("Select Best Models", 5, 9, f"Min score: {min_composite_score}, Max pairs: {max_pairs}")
        selected_results = select_best_models(garch_results, min_composite_score, max_pairs)
        
        if not selected_results:
            logger.warning("No models met the minimum composite score threshold")
            return None
        
        # Step 6: Log GARCH models to MLflow
        track_flow_progress("Log GARCH Models to MLflow", 6, 9, f"Models to log: {len(selected_results)}")
        garch_run_ids = log_models_to_mlflow(selected_results)
        
        # Step 7: Update trading configuration
        track_flow_progress("Update Trading Configuration", 7, 9, f"Selected pairs: {len(selected_results)}")
        trading_config = update_trading_configuration(selected_results, garch_run_ids)
        
        # Step 8: Train GRU models (matching notebook approach)
        if train_all_pairs:
            # Train GRU models for ALL pairs (not just selected ones)
            all_pairs_for_gru = [(symbol1, symbol2, correlation) for symbol1, symbol2, correlation, _ in cointegrated_pairs]
            track_flow_progress("Train GRU Models", 8, 9, f"Training all {len(all_pairs_for_gru)} cointegrated pairs")
        else:
            # Train GRU models only for selected pairs
            all_pairs_for_gru = [(r['symbol1'], r['symbol2'], r['correlation']) for r in selected_results]
            track_flow_progress("Train GRU Models", 8, 9, f"Training {len(all_pairs_for_gru)} selected pairs")
        
        gru_training_results = train_gru_models_for_pairs(historical_df, all_pairs_for_gru)
        
        # Step 9: Analyze training performance
        track_flow_progress("Analyze Training Performance", 9, 9, f"Models trained: {len(gru_training_results)}")
        performance_analysis = analyze_training_performance(gru_training_results)
        
        logger.info("Daily Pair Identification Flow completed successfully")
        logger.info(f"Selected {len(selected_results)} pairs for GARCH analysis")
        logger.info(f"Trained GRU models for {len(gru_training_results)} pairs")
        logger.info(f"Analysis completed for {sector} sector")
        
        # Return both GARCH and GRU results
        return {
            'garch_results': selected_results,
            'garch_run_ids': garch_run_ids,
            'trading_config': trading_config,
            'gru_results': gru_training_results,
            'performance_analysis': performance_analysis,
            'rankings_updated': True,  # Rankings are updated incrementally during training
            'sector_analyzed': sector
        }
        
    except Exception as e:
        logger.error(f"Error in Daily Pair Identification Flow: {e}")
        raise


if __name__ == "__main__":
    # Run the flow
    daily_pair_identification_flow() 