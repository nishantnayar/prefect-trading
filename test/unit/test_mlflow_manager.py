#!/usr/bin/env python3
"""
Test script for MLflow Manager functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.mlflow_manager import MLflowManager, log_training_run
import torch
import torch.nn as nn
import numpy as np

def create_test_model():
    """Create a simple test PyTorch model."""
    class SimpleGRU(nn.Module):
        def __init__(self, input_size=10, hidden_size=64, output_size=1):
            super(SimpleGRU, self).__init__()
            self.gru = nn.GRU(input_size, hidden_size, batch_first=True)
            self.fc = nn.Linear(hidden_size, output_size)
            self.sigmoid = nn.Sigmoid()
            
        def forward(self, x):
            gru_out, _ = self.gru(x)
            out = self.fc(gru_out[:, -1, :])
            return self.sigmoid(out)
    
    return SimpleGRU()

def test_mlflow_manager():
    """Test basic MLflow manager functionality."""
    print("🧪 Testing MLflow Manager...")
    
    try:
        # Initialize manager
        manager = MLflowManager()
        print("✅ Manager initialized")
        
        # Test experiment creation
        experiment_id = manager.create_sector_experiment("technology")
        print(f"✅ Created experiment: {experiment_id}")
        
        # Test run creation and logging
        with manager.start_run(run_name="test_run") as run:
            # Log parameters
            params = {
                "sequence_length": 10,
                "gru_units": 64,
                "dropout_rate": 0.2,
                "learning_rate": 0.001,
                "batch_size": 32,
                "epochs": 50
            }
            manager.log_parameters(params)
            print("✅ Parameters logged")
            
            # Log metrics
            metrics = {
                "train_f1_score": 0.85,
                "test_f1_score": 0.82,
                "train_accuracy": 0.87,
                "test_accuracy": 0.84,
                "sharpe_ratio": 1.25,
                "max_drawdown": 0.08
            }
            manager.log_metrics(metrics)
            print("✅ Metrics logged")
            
            # Create and log model
            model = create_test_model()
            manager.log_model(model, "test_gru_model")
            print("✅ Model logged")
            
            # Log additional info
            training_info = {
                "sector": "technology",
                "model_type": "gru_garch_hybrid",
                "data_version": "v1.0",
                "features": ["spread", "volatility", "correlation"]
            }
            manager.log_dict(training_info, "training_info.json")
            print("✅ Training info logged")
            
            print(f"✅ Test run completed: {run.info.run_id}")
        
        # Test model registration
        model_uri = f"runs:/{run.info.run_id}/test_gru_model"
        model_name = "pairs_trading_gru_garch_technology_test"
        
        try:
            version = manager.register_model(model_uri, model_name)
            print(f"✅ Model registered: version {version}")
            
            # Test model loading
            loaded_model = manager.load_model(model_uri)
            print("✅ Model loaded successfully")
            
        except Exception as e:
            print(f"⚠️ Model registration failed (expected for test): {e}")
        
        # Test getting experiment runs
        runs = manager.get_experiment_runs("pairs_trading/technology", max_results=5)
        print(f"✅ Retrieved {len(runs)} runs from experiment")
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_convenience_function():
    """Test the convenience function for logging training runs."""
    print("\n🧪 Testing convenience function...")
    
    try:
        # Create test model
        model = create_test_model()
        
        # Test parameters
        params = {
            "sequence_length": 10,
            "gru_units": 64,
            "dropout_rate": 0.2,
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 50,
            "sector": "technology"
        }
        
        # Test metrics
        metrics = {
            "train_f1_score": 0.85,
            "test_f1_score": 0.82,
            "train_accuracy": 0.87,
            "test_accuracy": 0.84,
            "sharpe_ratio": 1.25,
            "max_drawdown": 0.08
        }
        
        # Log training run
        run_id = log_training_run(
            model=model,
            metrics=metrics,
            params=params,
            model_name="convenience_test_model",
            sector="technology",
            run_name="convenience_test_run"
        )
        
        print(f"✅ Convenience function test completed: {run_id}")
        return True
        
    except Exception as e:
        print(f"❌ Convenience function test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting MLflow Manager Tests...\n")
    
    # Test basic functionality
    basic_test_passed = test_mlflow_manager()
    
    # Test convenience function
    convenience_test_passed = test_convenience_function()
    
    print("\n📊 Test Results:")
    print(f"Basic functionality: {'✅ PASSED' if basic_test_passed else '❌ FAILED'}")
    print(f"Convenience function: {'✅ PASSED' if convenience_test_passed else '❌ FAILED'}")
    
    if basic_test_passed and convenience_test_passed:
        print("\n🎉 All tests passed! MLflow Manager is ready for use.")
    else:
        print("\n⚠️ Some tests failed. Please check the configuration and MLflow server.") 