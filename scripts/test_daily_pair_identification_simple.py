#!/usr/bin/env python3
"""
Simple test script for Daily Pair Identification Flow

This script tests the basic functionality without MLflow dependencies
to ensure the flow can run even when MLflow is not properly configured.
"""

import sys
import os
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_basic_imports():
    """Test that basic imports work without MLflow issues."""
    print("=" * 60)
    print("TESTING BASIC IMPORTS")
    print("=" * 60)
    
    try:
        # Test basic imports
        print("✅ Testing basic imports...")
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        print("✅ Basic Python imports successful")
        
        # Test MLflow imports (should be optional)
        print("✅ Testing MLflow imports...")
        try:
            import mlflow
            print("✅ MLflow import successful")
        except ImportError:
            print("⚠️  MLflow not available (this is okay)")
        
        # Test MLflow manager imports (should be optional)
        try:
            from src.mlflow_manager import MLflowManager
            print("✅ MLflow manager import successful")
        except ImportError:
            print("⚠️  MLflow manager not available (this is okay)")
        
        # Test MLflow config imports (should be optional)
        try:
            from src.ml.config import MLflowConfig
            print("✅ MLflow config import successful")
        except ImportError:
            print("⚠️  MLflow config not available (this is okay)")
        
        # Test database connectivity
        print("✅ Testing database connectivity...")
        from src.database.database_connectivity import DatabaseConnectivity
        print("✅ Database connectivity import successful")
        
        # Test daily pair identifier import
        print("✅ Testing daily pair identifier import...")
        from src.ml.daily_pair_identifier import daily_pair_identification_flow
        print("✅ Daily pair identifier import successful")
        
        print("\n✅ All basic imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_loading():
    """Test that configuration loading works properly."""
    print("\n" + "=" * 60)
    print("TESTING CONFIGURATION LOADING")
    print("=" * 60)
    
    try:
        from src.ml.config import MLflowConfig
        
        # Test config loading
        print("✅ Testing MLflowConfig initialization...")
        config = MLflowConfig()
        print("✅ MLflowConfig initialized successfully")
        
        # Test config methods
        print("✅ Testing config methods...")
        model_registry_config = config.get_model_registry_config()
        print(f"✅ Model registry config: {model_registry_config}")
        
        performance_thresholds = config.get_performance_thresholds()
        print(f"✅ Performance thresholds: {performance_thresholds}")
        
        print("\n✅ Configuration loading successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test that database connection works."""
    print("\n" + "=" * 60)
    print("TESTING DATABASE CONNECTION")
    print("=" * 60)
    
    try:
        from src.database.database_connectivity import DatabaseConnectivity
        
        print("✅ Testing database connection...")
        db = DatabaseConnectivity()
        print("✅ Database connection successful")
        
        # Test a simple query
        print("✅ Testing simple database query...")
        query = "SELECT COUNT(*) as count FROM market_data LIMIT 1"
        result = db.execute_query(query)
        print(f"✅ Query result: {result}")
        
        db.close()
        print("\n✅ Database connection test successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("DAILY PAIR IDENTIFICATION - BASIC FUNCTIONALITY TEST")
    print("=" * 60)
    print(f"Start time: {datetime.now()}")
    print()
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Configuration Loading", test_config_loading),
        ("Database Connection", test_database_connection),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! The daily pair identification flow should work.")
        print("\nNext steps:")
        print("1. Run: make test-pairs")
        print("2. Run: make run-pairs")
        print("3. Deploy: prefect deploy")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 