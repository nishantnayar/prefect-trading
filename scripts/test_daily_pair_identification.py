#!/usr/bin/env python3
"""
Test script for Daily Pair Identification Flow

This script allows manual testing of the daily pair identification flow
without waiting for the scheduled Prefect deployment.
"""

import sys
import os
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ml.daily_pair_identifier import daily_pair_identification_flow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def test_daily_pair_identification():
    """Test the daily pair identification flow."""
    print("=" * 60)
    print("TESTING DAILY PAIR IDENTIFICATION FLOW")
    print("=" * 60)
    print(f"Start time: {datetime.now()}")
    print()

    try:
        # Run the flow with test parameters
        trading_config = daily_pair_identification_flow(
            lookback_days=30,  # Use 30 days for testing (faster)
            min_correlation=0.7,  # Lower threshold for testing
            max_cointegration_pvalue=0.1,  # More lenient for testing
            min_composite_score=0.5,  # Lower threshold for testing
            max_pairs=5  # Limit to 5 pairs for testing
        )

        print("\n" + "=" * 60)
        print("FLOW COMPLETED SUCCESSFULLY")
        print("=" * 60)

        if trading_config:
            print(f"Active pairs: {len(trading_config.get('active_pairs', []))}")
            print(f"Total pairs analyzed: {trading_config.get('total_pairs_analyzed', 0)}")
            print(f"Last updated: {trading_config.get('last_updated', 'N/A')}")

            print("\nActive Pairs:")
            for i, pair in enumerate(trading_config.get('active_pairs', []), 1):
                print(f"{i}. {pair['symbol1']}-{pair['symbol2']}")
                print(f"   Correlation: {pair['correlation']:.4f}")
                print(f"   Composite Score: {pair['composite_score']:.4f}")
                print(f"   MLflow Run ID: {pair['mlflow_run_id']}")
                print()
        else:
            print("No trading configuration returned")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("✅ Test completed successfully!")


if __name__ == "__main__":
    test_daily_pair_identification()
