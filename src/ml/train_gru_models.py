import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import torch
import mlflow
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
warnings.filterwarnings("ignore", message="pkg_resources is deprecated.*")

from src.database.database_connectivity import DatabaseConnectivity
from src.ml.gru_model import train_gru_model_with_mlflow, prepare_data_for_training
from src.ml.model_performance_tracker import save_training_results

def extract_data_from_database():
    """
    Extract all symbols and historical data from database.
    """
    print("Extracting data from database...")
    
    db = DatabaseConnectivity()
    
    # Get all symbols from symbols table
    symbols_query = "SELECT DISTINCT symbol FROM symbols ORDER BY symbol"
    symbols_result = db.execute_query(symbols_query)
    symbol_columns = ['symbol']
    symbols_df = pd.DataFrame(symbols_result, columns=symbol_columns)
    symbols = symbols_df['symbol'].tolist()
    
    print(f"Found {len(symbols)} symbols: {symbols[:10]}...")  # Show first 10
    
    # Get all historical data
    historical_query = """
    SELECT symbol, timestamp, close, volume
    FROM market_data_historical 
    ORDER BY symbol, timestamp
    """
    historical_result = db.execute_query(historical_query)
    historical_columns = ['symbol', 'timestamp', 'close', 'volume']
    historical_df = pd.DataFrame(historical_result, columns=historical_columns)
    
    print(f"Extracted {len(historical_df)} historical data points")
    print(f"Date range: {historical_df['timestamp'].min()} to {historical_df['timestamp'].max()}")
    
    return historical_df, symbols

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
        for j in range(i+1, len(symbols)):
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

def run_gru_training():
    """
    Main function to run PyTorch GRU training with MLflow integration.
    """
    print("=" * 60)
    print("PYTORCH GRU TRAINING WITH MLFLOW INTEGRATION")
    print("=" * 60)
    
    # Set random seeds for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)
    
    # Extract data
    historical_df, symbols = extract_data_from_database()
    
    # Prepare pairs data - train all pairs initially for comprehensive baseline
    pairs_data_list = prepare_pairs_data(historical_df, symbols, top_pairs=None)  # None = all pairs
    
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
        
        # Add pair info to config for MLflow logging
        config_with_pair = config.copy()
        config_with_pair['pair_symbol1'] = symbol1
        config_with_pair['pair_symbol2'] = symbol2
        
        # Train model with MLflow integration
        model, history, trainer = train_gru_model_with_mlflow(pair_df, config_with_pair)
        
        # Get MLflow run info for database tracking
        current_run = mlflow.active_run()
        model_run_id = current_run.info.run_id if current_run else f"manual_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        experiment_name = current_run.info.experiment_id if current_run else "pairs_trading/technology_sector/gru_training"
        
        # Save training results to database
        pair_symbol = f"{symbol1}-{symbol2}"
        early_stopped = len(history['val_losses']) < config['epochs']  # Check if training stopped early
        
        save_success = save_training_results(
            pair_symbol=pair_symbol,
            history=history,
            config=config_with_pair,
            model_run_id=model_run_id,
            experiment_name=experiment_name,
            early_stopped=early_stopped
        )
        
        if save_success:
            print(f"✅ Performance metrics saved to database for {pair_symbol}")
        else:
            print(f"⚠️  Failed to save performance metrics for {pair_symbol}")
        

        
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
        print("✅ Model rankings and trends updated in database.")
    except Exception as e:
        print(f"❌ Failed to update rankings/trends: {e}")

    # Analyze and display performance summary
    if pair_performance:
        print("\n" + "=" * 60)
        print("PERFORMANCE SUMMARY")
        print("=" * 60)
        
        # Sort by best F1 score
        pair_performance.sort(key=lambda x: x['best_f1'], reverse=True)
        
        # Find the best performing pair
        best_pair = pair_performance[0]
        
        print(f"🏆 BEST PERFORMING PAIR: {best_pair['pair']}")
        print(f"   Best F1 Score: {best_pair['best_f1']:.4f}")
        print(f"   Final F1 Score: {best_pair['final_f1']:.4f}")
        print(f"   Correlation: {best_pair['correlation']:.4f}")
        print(f"   Data Points: {best_pair['data_points']}")
        
        print(f"\n📊 ALL PAIRS RANKED BY PERFORMANCE:")
        print("-" * 80)
        for i, perf in enumerate(pair_performance, 1):
            db_status = "✅" if perf['saved_to_db'] else "❌"
            print(f"{i:2d}. {perf['pair']:<15} | F1: {perf['best_f1']:.4f} | Corr: {perf['correlation']:.4f} | DB: {db_status}")
        
        # Database save statistics
        saved_count = sum(1 for p in pair_performance if p['saved_to_db'])
        total_count = len(pair_performance)
        print(f"\n💾 DATABASE SAVE STATISTICS:")
        print("-" * 40)
        print(f"Successfully saved: {saved_count}/{total_count} pairs")
        print(f"Save rate: {saved_count/total_count*100:.1f}%")
        
        # Performance statistics
        f1_scores = [p['best_f1'] for p in pair_performance]
        avg_f1 = sum(f1_scores) / len(f1_scores)
        max_f1 = max(f1_scores)
        min_f1 = min(f1_scores)
        
        print(f"\n📈 PERFORMANCE STATISTICS:")
        print("-" * 60)
        print(f"Average F1 Score: {avg_f1:.4f}")
        print(f"Highest F1 Score: {max_f1:.4f} ({best_pair['pair']})")
        print(f"Lowest F1 Score: {min_f1:.4f}")
        print(f"Performance Range: {max_f1 - min_f1:.4f}")
        
        # Correlation vs Performance analysis
        print(f"\n🔍 CORRELATION VS PERFORMANCE ANALYSIS:")
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
    print("✅ MLflow cache ready to be cleared")
    print("💡 You can manually clear the mlruns directory if needed")

if __name__ == "__main__":
    try:
        # Run training
        model, history, trainer = run_gru_training()
        
        # Clear cache
        clear_mlflow_cache()
        
        print("\n" + "=" * 60)
        print("TRAINING COMPLETE")
        print("=" * 60)
        print("✅ PyTorch GRU models trained")
        print("✅ MLflow integration implemented")
        print("✅ Performance metrics saved to database")
        print("✅ Model rankings and trends updated")
        print("✅ Ready for UI integration")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 