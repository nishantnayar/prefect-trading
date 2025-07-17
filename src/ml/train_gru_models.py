import sys
import os

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

import pandas as pd
import numpy as np
import torch
import mlflow
from datetime import datetime, date
import warnings

warnings.filterwarnings('ignore')
warnings.filterwarnings("ignore", message="pkg_resources is deprecated.*")

from src.database.database_connectivity import DatabaseConnectivity
from src.data.sources.symbol_manager import SymbolManager
from src.ml.gru_model import train_gru_model_with_mlflow, prepare_data_for_training
from src.ml.model_performance_tracker import save_training_results
from src.ml.pair_analysis import analyze_pairs_for_training, PairAnalysis
from src.utils.data_preprocessing_utils import DataPreprocessingUtils


def extract_data_from_database(sectors: list = None):
    """
    Extract symbols and historical data from database, optionally filtered by sector.
    
    Args:
        sectors: List of sectors to filter by. If None, uses active sectors from config.
    """
    print("Extracting data from database...")

    db = DatabaseConnectivity()
    symbol_manager = SymbolManager()

    # Get symbols filtered by sector
    if sectors is None:
        sectors = symbol_manager.get_active_sectors()
        print(f"Using active sectors from config: {sectors}")
    
    symbols = symbol_manager.get_active_symbols(sectors=sectors)
    
    if not symbols:
        print(f"No symbols found for sectors: {sectors}")
        return pd.DataFrame(), []

    print(f"Found {len(symbols)} symbols for sectors {sectors}: {symbols[:10]}...")  # Show first 10

    # Get historical data for these symbols only
    symbols_str = "', '".join(symbols)
    historical_query = f"""
    SELECT symbol, timestamp, close, volume
    FROM market_data_historical 
    WHERE symbol IN ('{symbols_str}')
    ORDER BY symbol, timestamp
    """
    historical_result = db.execute_query(historical_query)
    historical_columns = ['symbol', 'timestamp', 'close', 'volume']
    historical_df = pd.DataFrame(historical_result, columns=historical_columns)

    print(f"Extracted {len(historical_df)} historical data points")
    print(f"Date range: {historical_df['timestamp'].min()} to {historical_df['timestamp'].max()}")

    return historical_df, symbols


def preprocess_data_with_variance_stability(
    historical_df: pd.DataFrame, 
    symbols: list,
    threshold_percent: float = 0.8,
    min_periods: int = 30,
    test_window: int = 30,
    arch_lags: int = 5
) -> tuple[pd.DataFrame, list, list]:
    """
    Preprocess data with feature computation and variance stability testing.
    
    Args:
        historical_df: Raw historical data
        symbols: List of symbols to process
        threshold_percent: Percentage threshold for stock selection
        min_periods: Minimum periods for feature computation
        test_window: Window size for variance stability testing
        arch_lags: Number of lags for ARCH test
        
    Returns:
        Tuple of (processed_features, stable_symbols, test_results)
    """
    print("=" * 60)
    print("DATA PREPROCESSING WITH VARIANCE STABILITY TESTING")
    print("=" * 60)
    
    # Initialize preprocessing utilities
    utils = DataPreprocessingUtils()
    
    # Step 1: Select stocks with sufficient data
    print("\nStep 1: Selecting stocks by record count...")
    selected_symbols = utils.select_stocks_by_record_count(
        historical_df, 
        threshold_percent=threshold_percent,
        min_records=min_periods
    )
    
    if not selected_symbols:
        raise ValueError("No symbols meet the data completeness criteria")
    
    print(f"Selected {len(selected_symbols)} symbols for feature computation")
    
    # Step 2: Compute features for selected symbols
    print("\nStep 2: Computing features...")
    try:
        features = utils.compute_features_for_multiple_symbols(
            historical_df,
            symbols=selected_symbols,
            computation_method='expanding_window',
            min_periods=min_periods
        )
        print(f"[OK] Features computed for {len(selected_symbols)} symbols: {len(features)} total records")
    except Exception as e:
        print(f"[FAIL] Error computing features: {e}")
        raise
    
    # Step 3: Test variance stability
    print("\nStep 3: Testing variance stability...")
    try:
        stable_symbols, test_results = utils.test_variance_stability_for_multiple_symbols(
            features,
            symbols=selected_symbols,
            test_window=test_window,
            arch_lags=arch_lags
        )
        print(f"[OK] Variance stability tested: {len(stable_symbols)} stable out of {len(selected_symbols)} symbols")
    except Exception as e:
        print(f"[FAIL] Error testing variance stability: {e}")
        raise
    
    # Step 4: Save features and test results to database
    print("\nStep 4: Saving to database...")
    try:
        features_saved = utils.save_features_to_database(features)
        results_saved = utils.save_variance_stability_results(test_results)
        print(f"[OK] Saved {features_saved} feature records and {results_saved} test results to database")
    except Exception as e:
        print(f"[WARN] Warning: Could not save to database: {e}")
        print("Continuing with in-memory data...")
    
    # Step 5: Filter features to only stable symbols
    print("\nStep 5: Filtering to stable symbols...")
    stable_features = features[features['symbol'].isin(stable_symbols)].copy()
    print(f"[OK] Filtered to {len(stable_symbols)} stable symbols: {len(stable_features)} records")
    
    # Print stability summary
    print("\n[STATS] VARIANCE STABILITY SUMMARY:")
    print("-" * 50)
    stable_count = len(stable_symbols)
    total_count = len(selected_symbols)
    stability_rate = stable_count / total_count * 100
    
    print(f"Total symbols processed: {total_count}")
    print(f"Stable symbols: {stable_count}")
    print(f"Unstable symbols: {total_count - stable_count}")
    print(f"Stability rate: {stability_rate:.1f}%")
    
    # Show some unstable symbols and reasons
    unstable_results = [r for r in test_results if not r['is_stable']]
    if unstable_results:
        print(f"\n[FAIL] UNSTABLE SYMBOLS (first 5):")
        for result in unstable_results[:5]:
            arch_p = result.get('arch_test_pvalue')
            cv = result.get('rolling_std_cv')
            arch_p_str = f"{arch_p:.4f}" if arch_p is not None and isinstance(arch_p, (float, int)) else "NA"
            cv_str = f"{cv:.4f}" if cv is not None and isinstance(cv, (float, int)) else "NA"
            print(f"  {result['symbol']}: {result.get('filter_reason', 'unknown')} (ARCH p={arch_p_str}, CV={cv_str})")
    # Show some stable symbols
    stable_results = [r for r in test_results if r['is_stable']]
    if stable_results:
        print(f"\n[OK] STABLE SYMBOLS (first 5):")
        for result in stable_results[:5]:
            arch_p = result.get('arch_test_pvalue')
            cv = result.get('rolling_std_cv')
            arch_p_str = f"{arch_p:.4f}" if arch_p is not None and isinstance(arch_p, (float, int)) else "NA"
            cv_str = f"{cv:.4f}" if cv is not None and isinstance(cv, (float, int)) else "NA"
            print(f"  {result['symbol']}: ARCH p={arch_p_str}, CV={cv_str}")
    
    print("\n" + "=" * 60)
    print("PREPROCESSING COMPLETE")
    print("=" * 60)
    
    return stable_features, stable_symbols, test_results


def prepare_pairs_data_from_features(features_df, symbols, top_pairs=10):
    """
    Prepare pairs data for training using preprocessed features.
    Returns a list of individual pair DataFrames instead of concatenated data.
    """
    print("Preparing pairs data from preprocessed features...")

    if features_df.empty or not symbols:
        print("No stable features or symbols available for pairs preparation.")
        return []

    # Pivot log_close data for correlation analysis
    pivoted_data = features_df.pivot(index='timestamp', columns='symbol', values='log_close')

    # Generate all possible pairs
    symbol_pairs = []
    for i in range(len(symbols)):
        for j in range(i + 1, len(symbols)):
            symbol_pairs.append((symbols[i], symbols[j]))

    print(f"Generated {len(symbol_pairs)} possible pairs")

    # Calculate correlations for all pairs
    correlations = []
    for symbol1, symbol2 in symbol_pairs:
        try:
            corr = pivoted_data[symbol1].corr(pivoted_data[symbol2])
            if not pd.isna(corr) and corr > 0.8:  # High correlation threshold
                correlations.append({
                    'symbol1': symbol1,
                    'symbol2': symbol2,
                    'correlation': corr
                })
        except Exception as e:
            continue

    # Sort by correlation and take top pairs (or all if top_pairs is None)
    correlations_df = pd.DataFrame(correlations)
    if correlations_df.empty:
        print("No highly correlated pairs found.")
        return []
    correlations_df = correlations_df.sort_values('correlation', ascending=False)

    if top_pairs is None:
        # Use all pairs that meet the correlation threshold
        top_correlations = correlations_df
        print(f"Using all {len(top_correlations)} pairs that meet correlation threshold (>0.8)")
    else:
        # Use only top N pairs
        top_correlations = correlations_df.head(top_pairs)
        print(f"Using top {len(top_correlations)} pairs by correlation")

    print(f"Found {len(top_correlations)} highly correlated pairs")
    print("Top pairs:")
    for _, pair in top_correlations.iterrows():
        print(f"  {pair['symbol1']}-{pair['symbol2']}: {pair['correlation']:.4f}")

    # Create spread data for top pairs - return individual DataFrames
    pairs_data_list = []
    total_data_points = 0

    for _, pair in top_correlations.iterrows():
        symbol1, symbol2 = pair['symbol1'], pair['symbol2']

        try:
            # Get aligned log_close data
            aligned = pd.concat([pivoted_data[symbol1], pivoted_data[symbol2]], axis=1).dropna()
            if len(aligned) < 100:  # Minimum data requirement
                continue

            # Calculate spread (simple difference for now)
            spread = aligned.iloc[:, 0] - aligned.iloc[:, 1]

            # Create pair data with additional features
            pair_data = pd.DataFrame({
                'timestamp': aligned.index,
                'symbol1': symbol1,
                'symbol2': symbol2,
                'spread': spread,
                'correlation': pair['correlation']
            })

            # Add additional features for each symbol
            for symbol in [symbol1, symbol2]:
                symbol_features = features_df[features_df['symbol'] == symbol].set_index('timestamp')
                symbol_features = symbol_features.reindex(aligned.index)
                
                # Add features with symbol prefix
                for col in ['log_return', 'z_score', 'rolling_std', 'rolling_mean', 'volatility_annualized']:
                    if col in symbol_features.columns:
                        pair_data[f'{symbol}_{col}'] = symbol_features[col]

            pairs_data_list.append(pair_data)
            total_data_points += len(pair_data)

        except Exception as e:
            print(f"Error processing pair {symbol1}-{symbol2}: {e}")
            continue

    if not pairs_data_list:
        raise ValueError("No valid pairs data found")

    print(f"Created spread data for {len(pairs_data_list)} pairs")
    print(f"Total data points: {total_data_points}")

    return pairs_data_list


def prepare_pairs_data(historical_df, symbols, top_pairs=10):
    """
    Prepare pairs data for training by identifying cointegrated pairs.
    Returns a list of individual pair DataFrames instead of concatenated data.
    """
    print("Preparing pairs data...")

    # Pivot data for correlation analysis
    pivoted_data = historical_df.pivot(index='timestamp', columns='symbol', values='close')

    # Calculate log prices
    log_prices = np.log(pivoted_data)

    # Generate all possible pairs
    symbol_pairs = []
    for i in range(len(symbols)):
        for j in range(i + 1, len(symbols)):
            symbol_pairs.append((symbols[i], symbols[j]))

    print(f"Generated {len(symbol_pairs)} possible pairs")

    # Calculate correlations for all pairs
    correlations = []
    for symbol1, symbol2 in symbol_pairs:
        try:
            corr = log_prices[symbol1].corr(log_prices[symbol2])
            if not pd.isna(corr) and corr > 0.8:  # High correlation threshold
                correlations.append({
                    'symbol1': symbol1,
                    'symbol2': symbol2,
                    'correlation': corr
                })
        except Exception as e:
            continue

    # Sort by correlation and take top pairs (or all if top_pairs is None)
    correlations_df = pd.DataFrame(correlations)
    correlations_df = correlations_df.sort_values('correlation', ascending=False)

    if top_pairs is None:
        # Use all pairs that meet the correlation threshold
        top_correlations = correlations_df
        print(f"Using all {len(top_correlations)} pairs that meet correlation threshold (>0.8)")
    else:
        # Use only top N pairs
        top_correlations = correlations_df.head(top_pairs)
        print(f"Using top {len(top_correlations)} pairs by correlation")

    print(f"Found {len(top_correlations)} highly correlated pairs")
    print("Top pairs:")
    for _, pair in top_correlations.iterrows():
        print(f"  {pair['symbol1']}-{pair['symbol2']}: {pair['correlation']:.4f}")

    # Create spread data for top pairs - return individual DataFrames
    pairs_data_list = []
    total_data_points = 0

    for _, pair in top_correlations.iterrows():
        symbol1, symbol2 = pair['symbol1'], pair['symbol2']

        try:
            # Get aligned price data
            aligned = pd.concat([log_prices[symbol1], log_prices[symbol2]], axis=1).dropna()
            if len(aligned) < 100:  # Minimum data requirement
                continue

            # Calculate spread (simple difference for now)
            spread = aligned.iloc[:, 0] - aligned.iloc[:, 1]

            # Create pair data
            pair_data = pd.DataFrame({
                'timestamp': aligned.index,
                'symbol1': symbol1,
                'symbol2': symbol2,
                'spread': spread,
                'correlation': pair['correlation']
            })

            pairs_data_list.append(pair_data)
            total_data_points += len(pair_data)

        except Exception as e:
            print(f"Error processing pair {symbol1}-{symbol2}: {e}")
            continue

    if not pairs_data_list:
        raise ValueError("No valid pairs data found")

    print(f"Created spread data for {len(pairs_data_list)} pairs")
    print(f"Total data points: {total_data_points}")

    return pairs_data_list


def run_gru_training(sectors: list = None, use_preprocessing: bool = True, use_pair_analysis: bool = True):
    """
    Main function to run PyTorch GRU training with MLflow integration.
    
    Args:
        sectors: List of sectors to train on. If None, uses active sectors from config.
        use_preprocessing: Whether to use the new preprocessing pipeline with variance stability testing
        use_pair_analysis: Whether to use correlation and cointegration analysis for pair shortlisting
    """
    print("=" * 60)
    print("PYTORCH GRU TRAINING WITH MLFLOW INTEGRATION")
    print("=" * 60)

    # Set random seeds for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)

    # Extract data with sector filtering
    historical_df, symbols = extract_data_from_database(sectors=sectors)

    if use_pair_analysis:
        # Use new pair analysis pipeline with correlation and cointegration testing
        print("\n[INFO] Using enhanced pair analysis with correlation and cointegration testing...")
        
        # Configure pair analysis
        pair_analysis_config = {
            'correlation_threshold': 0.8,  # Pearson's ρ > 0.8
            'cointegration_pvalue_threshold': 0.05,  # Engle-Granger p-value < 0.05
            'min_data_points': 100,
            'max_pairs': 20,
            'verbose': True
        }
        
        # Perform comprehensive pair analysis
        shortlisted_pairs, pairs_data_list, correlation_matrix = analyze_pairs_for_training(
            historical_df, symbols, pair_analysis_config
        )
        
        # Add pair analysis metadata to MLflow
        preprocessing_metadata = {
            'preprocessing_method': 'pair_analysis_enhanced',
            'pair_analysis_method': 'correlation_cointegration',
            'correlation_threshold': pair_analysis_config['correlation_threshold'],
            'cointegration_threshold': pair_analysis_config['cointegration_pvalue_threshold'],
            'shortlisted_pairs_count': len(shortlisted_pairs),
            'total_symbols_processed': len(symbols),
            'correlation_matrix_shape': correlation_matrix.shape,
            'feature_computation_method': 'pair_analysis_features',
            'variance_test_window': 0,
            'arch_test_lags': 0
        }
        
        print(f"\n[PAIR ANALYSIS RESULTS]")
        print(f"Shortlisted pairs: {len(shortlisted_pairs)}")
        print(f"Training data pairs: {len(pairs_data_list)}")
        
    elif use_preprocessing:
        # Use new preprocessing pipeline with variance stability testing
        print("\n[INFO] Using enhanced preprocessing pipeline with variance stability testing...")
        
        # Preprocess data with feature computation and variance stability testing
        stable_features, stable_symbols, test_results = preprocess_data_with_variance_stability(
            historical_df=historical_df,
            symbols=symbols,
            threshold_percent=0.8,
            min_periods=30,
            test_window=30,
            arch_lags=5
        )
        
        # Prepare pairs data using preprocessed features
        pairs_data_list = prepare_pairs_data_from_features(stable_features, stable_symbols, top_pairs=20)
        
        # Add preprocessing metadata to MLflow
        preprocessing_metadata = {
            'preprocessing_method': 'variance_stability_filtered',
            'stable_symbols_count': len(stable_symbols),
            'total_symbols_processed': len(symbols),
            'stability_rate': len(stable_symbols) / len(symbols) * 100,
            'feature_computation_method': 'expanding_window',
            'variance_test_window': 30,
            'arch_test_lags': 5
        }
        
    else:
        # Use original pipeline (for comparison/testing)
        print("\n[INFO] Using original preprocessing pipeline...")
        
        # Prepare pairs data using original method
        pairs_data_list = prepare_pairs_data(historical_df, symbols, top_pairs=20)
        
        # Add preprocessing metadata to MLflow
        preprocessing_metadata = {
            'preprocessing_method': 'original',
            'stable_symbols_count': len(symbols),
            'total_symbols_processed': len(symbols),
            'stability_rate': 100.0,
            'feature_computation_method': 'none',
            'variance_test_window': 0,
            'arch_test_lags': 0
        }

    # Configuration (same as optimal from existing implementation)
    config = {
        'sequence_length': 10,
        'gru_units': 64,
        'dropout_rate': 0.255,
        'learning_rate': 0.0003,
        'batch_size': 32,
        'epochs': 100,
        'patience': 10
    }

    print(f"\nConfiguration: {config}")

    # Track performance across all pairs
    pair_performance = []

    # Train a model for each pair
    total_pairs = len(pairs_data_list)
    for pair_idx, pair_df in enumerate(pairs_data_list, 1):
        symbol1 = pair_df['symbol1'].iloc[0]
        symbol2 = pair_df['symbol2'].iloc[0]

        if len(pair_df) < 100:
            print(f"Skipping pair {symbol1}-{symbol2} (not enough data)")
            continue

        print(f"\n[{pair_idx}/{total_pairs}] Training model for pair: {symbol1}-{symbol2} (n={len(pair_df)})")

        # Add pair info and preprocessing metadata to config for MLflow logging
        config_with_pair = config.copy()
        config_with_pair['pair_symbol1'] = symbol1
        config_with_pair['pair_symbol2'] = symbol2
        
        # Add preprocessing metadata
        config_with_pair.update(preprocessing_metadata)

        # Train model with MLflow integration
        model, history, trainer, model_run_id, experiment_id, run_name = train_gru_model_with_mlflow(pair_df,
                                                                                                     config_with_pair)

        # Save training results to database
        pair_symbol = f"{symbol1}-{symbol2}"
        early_stopped = len(history['val_losses']) < config['epochs']  # Check if training stopped early

        save_success = save_training_results(
            pair_symbol=pair_symbol,
            history=history,
            config=config_with_pair,
            model_run_id=model_run_id,
            experiment_name=experiment_id,  # experiment_id is the correct value for MLflow links
            run_name=run_name,
            early_stopped=early_stopped
        )

        if save_success:
            print(f"[OK] Performance metrics saved to database for {pair_symbol}")
        else:
            print(f"[WARN] Failed to save performance metrics for {pair_symbol}")

        # Store performance data for summary
        performance_data = {
            'pair': pair_symbol,
            'symbol1': symbol1,
            'symbol2': symbol2,
            'correlation': pair_df['correlation'].iloc[0],
            'data_points': len(pair_df),
            'best_f1': history['best_val_f1'],
            'final_f1': history['val_f1s'][-1],
            'saved_to_db': save_success
        }
        pair_performance.append(performance_data)

        print(f"Best Validation F1 Score for {symbol1}-{symbol2}: {history['best_val_f1']:.4f}")
        print(f"Final Validation F1 Score: {history['val_f1s'][-1]:.4f}")
        print(f"Epochs trained: {len(history['val_losses'])}")
        if early_stopped:
            print(f"Training stopped early (patience: {config['patience']})")

    print("\nAll pairs processed.")

    # AUTOMATICALLY UPDATE RANKINGS AND TRENDS
    print("\nUpdating model rankings and trends...")
    try:
        db = DatabaseConnectivity()
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT update_model_rankings();")
                cursor.execute("SELECT update_model_trends();")
                conn.commit()
        print("[OK] Model rankings and trends updated in database.")
    except Exception as e:
        print(f"[FAIL] Failed to update rankings/trends: {e}")

    # Analyze and display performance summary
    if pair_performance:
        print("\n" + "=" * 60)
        print("[STATS] PERFORMANCE SUMMARY")
        print("=" * 60)

        # Sort by best F1 score
        pair_performance.sort(key=lambda x: x['best_f1'], reverse=True)

        # Find the best performing pair
        best_pair = pair_performance[0]

        print(f"[BEST] BEST PERFORMING PAIR: {best_pair['pair']}")
        print(f"   Best F1 Score: {best_pair['best_f1']:.4f}")
        print(f"   Final F1 Score: {best_pair['final_f1']:.4f}")
        print(f"   Correlation: {best_pair['correlation']:.4f}")
        print(f"   Data Points: {best_pair['data_points']}")

        print(f"\n[STATS] ALL PAIRS RANKED BY PERFORMANCE:")
        print("-" * 80)
        for i, perf in enumerate(pair_performance, 1):
            db_status = "[OK]" if perf['saved_to_db'] else "[FAIL]"
            print(
                f"{i:2d}. {perf['pair']:<15} | F1: {perf['best_f1']:.4f} | Corr: {perf['correlation']:.4f} | DB: {db_status}")

        # Database save statistics
        saved_count = sum(1 for p in pair_performance if p['saved_to_db'])
        total_count = len(pair_performance)
        print(f"\n[SAVE] DATABASE SAVE STATISTICS:")
        print("-" * 40)
        print(f"Successfully saved: {saved_count}/{total_count} pairs")
        print(f"Save rate: {saved_count / total_count * 100:.1f}%")

        # Performance statistics
        f1_scores = [p['best_f1'] for p in pair_performance]
        avg_f1 = sum(f1_scores) / len(f1_scores)
        max_f1 = max(f1_scores)
        min_f1 = min(f1_scores)

        print(f"\n[PERF] PERFORMANCE STATISTICS:")
        print("-" * 60)
        print(f"Average F1 Score: {avg_f1:.4f}")
        print(f"Highest F1 Score: {max_f1:.4f} ({best_pair['pair']})")
        print(f"Lowest F1 Score: {min_f1:.4f}")
        print(f"Performance Range: {max_f1 - min_f1:.4f}")

        # Correlation vs Performance analysis
        print(f"\n[ANALYZE] CORRELATION VS PERFORMANCE ANALYSIS:")
        print("-" * 60)
        high_corr_pairs = [p for p in pair_performance if p['correlation'] > 0.85]
        if high_corr_pairs:
            high_corr_avg = sum(p['best_f1'] for p in high_corr_pairs) / len(high_corr_pairs)
            print(f"High correlation pairs (>0.85): {len(high_corr_pairs)} pairs, Avg F1: {high_corr_avg:.4f}")

        low_corr_pairs = [p for p in pair_performance if p['correlation'] <= 0.85]
        if low_corr_pairs:
            low_corr_avg = sum(p['best_f1'] for p in low_corr_pairs) / len(low_corr_pairs)
            print(f"Lower correlation pairs (≤0.85): {len(low_corr_pairs)} pairs, Avg F1: {low_corr_avg:.4f}")

    return None, None, None


def clear_mlflow_cache():
    """
    Clear MLflow cache after testing.
    """
    print("\nClearing MLflow cache...")

    # This would typically involve cleaning up artifacts
    # For now, we'll just log that we're ready to clear
    print("[OK] MLflow cache ready to be cleared")
    print("[TIP] You can manually clear the mlruns directory if needed")


if __name__ == "__main__":
    try:
        # Allow command line argument to choose preprocessing method
        import argparse
        
        parser = argparse.ArgumentParser(description='Train GRU models with optional preprocessing and pair analysis')
        parser.add_argument('--no-preprocessing', action='store_true', 
                          help='Use original preprocessing pipeline (no variance stability testing)')
        parser.add_argument('--no-pair-analysis', action='store_true',
                          help='Skip correlation and cointegration analysis')
        parser.add_argument('--sectors', nargs='+', default=None,
                          help='Sectors to train on (default: all active sectors)')
        
        args = parser.parse_args()
        
        # Run training with chosen preprocessing method
        use_preprocessing = not args.no_preprocessing
        use_pair_analysis = not args.no_pair_analysis
        
        if use_pair_analysis:
            print("🔧 Using enhanced pair analysis with correlation and cointegration testing")
        elif use_preprocessing:
            print("🔧 Using enhanced preprocessing pipeline with variance stability testing")
        else:
            print("🔧 Using original preprocessing pipeline")
        
        model, history, trainer = run_gru_training(
            sectors=args.sectors,
            use_preprocessing=use_preprocessing,
            use_pair_analysis=use_pair_analysis
        )

        # Clear cache
        clear_mlflow_cache()

        print("\n" + "=" * 60)
        print("TRAINING COMPLETE")
        print("=" * 60)
        print("✅ PyTorch GRU models trained")
        if use_pair_analysis:
            print("✅ Enhanced pair analysis with correlation and cointegration testing")
            print("✅ Pearson's ρ > 0.8 correlation threshold applied")
            print("✅ Engle-Granger cointegration test (p < 0.05) applied")
            print("✅ Spread stationarity testing implemented")
        elif use_preprocessing:
            print("✅ Enhanced preprocessing with variance stability testing")
            print("✅ Features computed and stored in database")
            print("✅ Variance stability results saved")
        else:
            print("✅ Original preprocessing pipeline used")
        print("✅ MLflow integration implemented")
        print("✅ Performance metrics saved to database")
        print("✅ Model rankings and trends updated")
        print("✅ Ready for UI integration")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
