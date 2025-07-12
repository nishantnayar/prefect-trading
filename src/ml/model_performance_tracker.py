"""
Model Performance Tracker

This module handles saving model performance metrics to the database
after training, including F1 scores, accuracy, precision, recall, and other metrics.
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional
import mlflow

from src.database.database_connectivity import DatabaseConnectivity


class ModelPerformanceTracker:
    """
    Tracks and saves model performance metrics to the database.
    """
    
    def __init__(self):
        self.db = DatabaseConnectivity()
    
    def save_model_performance(
        self,
        pair_symbol: str,
        model_run_id: str,
        experiment_name: str,
        run_name: str,
        training_date: datetime,
        metrics: Dict[str, float],
        hyperparameters: Dict[str, Any],
        model_path: Optional[str] = None,
        feature_importance: Optional[Dict[str, float]] = None
    ) -> bool:
        """
        Save model performance metrics to the database.
        
        Args:
            pair_symbol: The trading pair symbol (e.g., "AAPL-MSFT")
            model_run_id: MLflow run ID
            experiment_name: MLflow experiment name
            run_name: MLflow run name
            training_date: When the model was trained
            metrics: Dictionary of performance metrics
            hyperparameters: Model hyperparameters
            model_path: Path to saved model (optional)
            feature_importance: Feature importance scores (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare the insert query
            query = """
            INSERT INTO model_performance (
                pair_symbol, model_run_id, experiment_name, run_name, training_date,
                f1_score, accuracy, "precision", recall, auc_score,
                loss, val_loss, epochs_trained, early_stopped,
                model_path, hyperparameters, feature_importance
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb
            )
            """
            
            # Extract metrics with defaults
            f1_score = metrics.get('f1_score', None)
            accuracy = metrics.get('accuracy', None)
            precision = metrics.get('precision', None)
            recall = metrics.get('recall', None)
            auc_score = metrics.get('auc_score', None)
            loss = metrics.get('loss', None)
            val_loss = metrics.get('val_loss', None)
            epochs_trained = metrics.get('epochs_trained', None)
            early_stopped = metrics.get('early_stopped', False)
            
            # Convert hyperparameters and feature_importance to JSON
            hyperparams_json = json.dumps(hyperparameters) if hyperparameters else None
            feature_importance_json = json.dumps(feature_importance) if feature_importance else None
            
            # Execute the query
            self.db.execute_query(
                query,
                (
                    pair_symbol, model_run_id, experiment_name, run_name, training_date,
                    f1_score, accuracy, precision, recall, auc_score,
                    loss, val_loss, epochs_trained, early_stopped,
                    model_path, hyperparams_json, feature_importance_json
                )
            )
            
            print(f"Saved performance metrics for {pair_symbol} to database")
            return True
            
        except Exception as e:
            print(f"Error saving performance metrics for {pair_symbol}: {e}")
            return False
    
    def update_model_rankings(self) -> bool:
        """
        Update the model rankings table with current best performers.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.db.execute_query("SELECT update_model_rankings()")
            print("Updated model rankings")
            return True
        except Exception as e:
            print(f"Error updating model rankings: {e}")
            return False
    
    def update_model_trends(self) -> bool:
        """
        Update the model trends table with current averages.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.db.execute_query("SELECT update_model_trends()")
            print("Updated model trends")
            return True
        except Exception as e:
            print(f"Error updating model trends: {e}")
            return False
    
    def get_best_performing_pairs(self, limit: int = 10) -> pd.DataFrame:
        """
        Get the best performing pairs from the database.
        
        Args:
            limit: Number of pairs to return
            
        Returns:
            pd.DataFrame: DataFrame with best performing pairs
        """
        try:
            query = f"SELECT * FROM get_best_performing_pairs({limit})"
            result = self.db.execute_query(query)
            
            if result:
                columns = ['pair_symbol', 'best_f1_score', 'avg_f1_score', 'model_count', 'latest_training_date']
                df = pd.DataFrame(result, columns=columns)
                # Convert model_count to int for consistency
                df['model_count'] = df['model_count'].astype(int)
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error getting best performing pairs: {e}")
            return pd.DataFrame()
    
    def get_pair_performance_trends(self, pair_symbol: str, days_back: int = 30) -> pd.DataFrame:
        """
        Get performance trends for a specific pair.
        
        Args:
            pair_symbol: The trading pair symbol
            days_back: Number of days to look back
            
        Returns:
            pd.DataFrame: DataFrame with performance trends
        """
        try:
            query = f"SELECT * FROM get_pair_performance_trends('{pair_symbol}', {days_back})"
            result = self.db.execute_query(query)
            
            if result:
                columns = ['trend_date', 'avg_f1_7d', 'avg_f1_30d', 'best_f1_7d', 'best_f1_30d', 'model_count_7d', 'model_count_30d']
                return pd.DataFrame(result, columns=columns)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error getting performance trends for {pair_symbol}: {e}")
            return pd.DataFrame()
    
    def get_recent_pair_performance(self, pair_symbol: str, days_back: int = 7) -> pd.DataFrame:
        """
        Get recent model performance for a specific pair.
        
        Args:
            pair_symbol: The trading pair symbol
            days_back: Number of days to look back
            
        Returns:
            pd.DataFrame: DataFrame with recent performance
        """
        try:
            query = f"SELECT * FROM get_recent_pair_performance('{pair_symbol}', {days_back})"
            result = self.db.execute_query(query)
            
            if result:
                columns = ['training_date', 'f1_score', 'accuracy', 'precision', 'recall', 'model_run_id', 'experiment_name']
                return pd.DataFrame(result, columns=columns)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error getting recent performance for {pair_symbol}: {e}")
            return pd.DataFrame()


def extract_mlflow_metrics(run_id: str) -> Dict[str, Any]:
    """
    Extract metrics from MLflow run.
    
    Args:
        run_id: MLflow run ID
        
    Returns:
        Dict containing extracted metrics
    """
    try:
        # Get the MLflow client
        client = mlflow.tracking.MlflowClient()
        
        # Get the run
        run = client.get_run(run_id)
        
        # Extract metrics
        metrics = {}
        for key, value in run.data.metrics.items():
            metrics[key] = value
        
        # Extract parameters
        params = {}
        for key, value in run.data.params.items():
            params[key] = value
        
        return {
            'metrics': metrics,
            'params': params,
            'run_name': run.info.run_name,
            'experiment_name': run.info.experiment_id
        }
        
    except Exception as e:
        print(f"Error extracting MLflow metrics: {e}")
        return {}


def save_training_results(
    pair_symbol: str,
    history: Dict[str, Any],
    config: Dict[str, Any],
    model_run_id: str,
    experiment_name: str,
    run_name: str = None,
    early_stopped: bool = False
) -> bool:
    """
    Save training results to the database.
    
    Args:
        pair_symbol: The trading pair symbol
        history: Training history from the model
        config: Model configuration
        model_run_id: MLflow run ID
        experiment_name: MLflow experiment name
        run_name: MLflow run name (optional)
        early_stopped: Whether training was stopped early
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        tracker = ModelPerformanceTracker()
        
        # Extract final metrics from history
        final_val_loss = history['val_losses'][-1] if history['val_losses'] else None
        final_train_loss = history['train_losses'][-1] if history['train_losses'] else None
        best_val_f1 = history['best_val_f1']
        epochs_trained = len(history['val_losses'])
        
        # Prepare metrics dictionary
        metrics = {
            'f1_score': best_val_f1,
            'loss': final_train_loss,
            'val_loss': final_val_loss,
            'epochs_trained': epochs_trained,
            'early_stopped': early_stopped
        }
        
        # Save to database
        success = tracker.save_model_performance(
            pair_symbol=pair_symbol,
            model_run_id=model_run_id,
            experiment_name=experiment_name,
            run_name=run_name,
            training_date=datetime.now(),
            metrics=metrics,
            hyperparameters=config
        )
        
        if success:
            # Update rankings and trends
            tracker.update_model_rankings()
            tracker.update_model_trends()
        
        return success
        
    except Exception as e:
        print(f"Error saving training results: {e}")
        return False 