#!/usr/bin/env python3
"""
Standalone script to run correlation and cointegration analysis for pairs trading.

This script performs comprehensive pair analysis:
1. Correlation analysis (Pearson's ρ > 0.8)
2. Cointegration testing (Engle-Granger test, p < 0.05)
3. Spread calculation and stationarity testing
4. Pair shortlisting for GRU training

Usage:
    python scripts/run_pair_analysis.py --sectors technology healthcare
    python scripts/run_pair_analysis.py --correlation-threshold 0.85 --cointegration-threshold 0.01
"""

import sys
import os
import argparse
from datetime import datetime, date

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

import pandas as pd
import numpy as np
import warnings
from typing import List, Dict, Optional

warnings.filterwarnings('ignore')

from src.database.database_connectivity import DatabaseConnectivity
from src.data.sources.symbol_manager import SymbolManager
from src.ml.pair_analysis import PairAnalysis, analyze_pairs_for_training


def extract_historical_data(sectors: Optional[List[str]] = None) -> tuple[pd.DataFrame, List[str]]:
    """
    Extract historical data from database for pair analysis.
    
    Args:
        sectors: List of sectors to filter by. If None, uses active sectors from config.
        
    Returns:
        Tuple of (historical_data, symbols)
    """
    print("Extracting historical data from database...")
    
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
    
    print(f"Found {len(symbols)} symbols for sectors {sectors}")
    
    # Get historical data for these symbols
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


def run_pair_analysis(
    historical_df: pd.DataFrame,
    symbols: List[str],
    correlation_threshold: float = 0.8,
    cointegration_threshold: float = 0.05,
    max_pairs: int = 50,
    min_data_points: int = 100,
    verbose: bool = True
) -> tuple[List[Dict], List[pd.DataFrame], pd.DataFrame]:
    """
    Run comprehensive pair analysis.
    
    Args:
        historical_df: Historical price data
        symbols: List of symbols to analyze
        correlation_threshold: Pearson's ρ threshold (default: 0.8)
        cointegration_threshold: Engle-Granger p-value threshold (default: 0.05)
        max_pairs: Maximum number of pairs to return
        min_data_points: Minimum data points required
        verbose: Whether to print detailed output
        
    Returns:
        Tuple of (shortlisted_pairs, training_data_list, correlation_matrix)
    """
    print("=" * 60)
    print("CORRELATION AND COINTEGRATION ANALYSIS")
    print("=" * 60)
    
    # Configure pair analysis
    config = {
        'correlation_threshold': correlation_threshold,
        'cointegration_pvalue_threshold': cointegration_threshold,
        'min_data_points': min_data_points,
        'max_pairs': max_pairs,
        'verbose': verbose
    }
    
    print(f"\nConfiguration:")
    print(f"  Correlation threshold (Pearson's ρ): > {correlation_threshold}")
    print(f"  Cointegration threshold (Engle-Granger p-value): < {cointegration_threshold}")
    print(f"  Minimum data points: {min_data_points}")
    print(f"  Maximum pairs: {max_pairs}")
    
    # Run analysis
    shortlisted_pairs, training_data_list, correlation_matrix = analyze_pairs_for_training(
        historical_df, symbols, config
    )
    
    return shortlisted_pairs, training_data_list, correlation_matrix


def print_analysis_summary(
    shortlisted_pairs: List[Dict],
    training_data_list: List[pd.DataFrame],
    correlation_matrix: pd.DataFrame,
    symbols: List[str]
):
    """
    Print comprehensive analysis summary.
    
    Args:
        shortlisted_pairs: List of shortlisted pairs
        training_data_list: List of training data DataFrames
        correlation_matrix: Correlation matrix
        symbols: List of symbols analyzed
    """
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    
    print(f"\n📊 OVERVIEW:")
    print(f"  Total symbols analyzed: {len(symbols)}")
    print(f"  Correlation matrix shape: {correlation_matrix.shape}")
    print(f"  Shortlisted pairs: {len(shortlisted_pairs)}")
    print(f"  Training data pairs: {len(training_data_list)}")
    
    if shortlisted_pairs:
        print(f"\n🏆 TOP SHORTLISTED PAIRS:")
        print("-" * 50)
        for i, pair in enumerate(shortlisted_pairs[:10], 1):
            print(f"{i:2d}. {pair['symbol1']:<8} - {pair['symbol2']:<8} | "
                  f"Corr: {pair['correlation']:.4f} | "
                  f"Coint_p: {pair['pvalue']:.4f} | "
                  f"Stationary: {pair['spread_stationary']}")
        
        # Calculate statistics
        correlations = [p['correlation'] for p in shortlisted_pairs]
        cointegration_pvalues = [p['pvalue'] for p in shortlisted_pairs]
        data_points = [p['data_points'] for p in shortlisted_pairs]
        
        print(f"\n📈 STATISTICS:")
        print(f"  Average correlation: {np.mean(correlations):.4f}")
        print(f"  Average cointegration p-value: {np.mean(cointegration_pvalues):.4f}")
        print(f"  Average data points per pair: {np.mean(data_points):.1f}")
        print(f"  Highest correlation: {max(correlations):.4f}")
        print(f"  Lowest cointegration p-value: {min(cointegration_pvalues):.4f}")
        
        # Sector analysis if available
        print(f"\n🏭 SECTOR BREAKDOWN:")
        symbol1_sectors = {}
        symbol2_sectors = {}
        
        for pair in shortlisted_pairs:
            # This would need sector information from the database
            # For now, just show symbol distribution
            symbol1_sectors[pair['symbol1']] = symbol1_sectors.get(pair['symbol1'], 0) + 1
            symbol2_sectors[pair['symbol2']] = symbol2_sectors.get(pair['symbol2'], 0) + 1
        
        print(f"  Most frequent symbol1: {max(symbol1_sectors.items(), key=lambda x: x[1])}")
        print(f"  Most frequent symbol2: {max(symbol2_sectors.items(), key=lambda x: x[1])}")
    
    else:
        print("\n❌ No pairs met the criteria!")
        print("Consider:")
        print("  - Lowering correlation threshold")
        print("  - Increasing cointegration threshold")
        print("  - Adding more symbols")
        print("  - Extending data time range")


def save_analysis_results(
    shortlisted_pairs: List[Dict],
    training_data_list: List[pd.DataFrame],
    correlation_matrix: pd.DataFrame,
    output_dir: str = "analysis_results"
):
    """
    Save analysis results to files.
    
    Args:
        shortlisted_pairs: List of shortlisted pairs
        training_data_list: List of training data DataFrames
        correlation_matrix: Correlation matrix
        output_dir: Output directory
    """
    import os
    from datetime import datetime
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save shortlisted pairs
    if shortlisted_pairs:
        pairs_df = pd.DataFrame(shortlisted_pairs)
        pairs_file = os.path.join(output_dir, f"shortlisted_pairs_{timestamp}.csv")
        pairs_df.to_csv(pairs_file, index=False)
        print(f"✅ Shortlisted pairs saved to: {pairs_file}")
    
    # Save correlation matrix
    corr_file = os.path.join(output_dir, f"correlation_matrix_{timestamp}.csv")
    correlation_matrix.to_csv(corr_file)
    print(f"✅ Correlation matrix saved to: {corr_file}")
    
    # Save training data summary
    if training_data_list:
        training_summary = []
        for i, pair_data in enumerate(training_data_list):
            symbol1 = pair_data['symbol1'].iloc[0]
            symbol2 = pair_data['symbol2'].iloc[0]
            training_summary.append({
                'pair_index': i,
                'symbol1': symbol1,
                'symbol2': symbol2,
                'data_points': len(pair_data),
                'date_range_start': pair_data['timestamp'].min(),
                'date_range_end': pair_data['timestamp'].max()
            })
        
        summary_df = pd.DataFrame(training_summary)
        summary_file = os.path.join(output_dir, f"training_data_summary_{timestamp}.csv")
        summary_df.to_csv(summary_file, index=False)
        print(f"✅ Training data summary saved to: {summary_file}")
    
    print(f"✅ All results saved to directory: {output_dir}")


def main():
    """Main function to run pair analysis."""
    parser = argparse.ArgumentParser(
        description='Run correlation and cointegration analysis for pairs trading',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_pair_analysis.py --sectors technology healthcare
  python scripts/run_pair_analysis.py --correlation-threshold 0.85 --cointegration-threshold 0.01
  python scripts/run_pair_analysis.py --max-pairs 100 --min-data-points 200
        """
    )
    
    parser.add_argument('--sectors', nargs='+', default=None,
                       help='Sectors to analyze (default: all active sectors)')
    parser.add_argument('--correlation-threshold', type=float, default=0.8,
                       help='Correlation threshold (Pearson\'s ρ, default: 0.8)')
    parser.add_argument('--cointegration-threshold', type=float, default=0.05,
                       help='Cointegration p-value threshold (default: 0.05)')
    parser.add_argument('--max-pairs', type=int, default=50,
                       help='Maximum number of pairs to return (default: 50)')
    parser.add_argument('--min-data-points', type=int, default=100,
                       help='Minimum data points required (default: 100)')
    parser.add_argument('--output-dir', default='analysis_results',
                       help='Output directory for results (default: analysis_results)')
    parser.add_argument('--no-save', action='store_true',
                       help='Do not save results to files')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress detailed output')
    
    args = parser.parse_args()
    
    try:
        # Extract data
        historical_df, symbols = extract_historical_data(args.sectors)
        
        if historical_df.empty or not symbols:
            print("❌ No data available for analysis")
            return 1
        
        # Run analysis
        shortlisted_pairs, training_data_list, correlation_matrix = run_pair_analysis(
            historical_df=historical_df,
            symbols=symbols,
            correlation_threshold=args.correlation_threshold,
            cointegration_threshold=args.cointegration_threshold,
            max_pairs=args.max_pairs,
            min_data_points=args.min_data_points,
            verbose=not args.quiet
        )
        
        # Print summary
        print_analysis_summary(shortlisted_pairs, training_data_list, correlation_matrix, symbols)
        
        # Save results
        if not args.no_save:
            save_analysis_results(
                shortlisted_pairs, training_data_list, correlation_matrix, args.output_dir
            )
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print("✅ Correlation analysis completed")
        print("✅ Cointegration testing completed")
        print("✅ Pair shortlisting completed")
        print("✅ Training data prepared")
        
        if shortlisted_pairs:
            print(f"✅ {len(shortlisted_pairs)} pairs ready for GRU training")
        else:
            print("⚠️  No pairs met criteria - consider adjusting thresholds")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 