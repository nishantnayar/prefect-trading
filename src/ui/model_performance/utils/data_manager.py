"""
Model Performance Data Manager

This module provides the ModelPerformanceManager class for handling database
operations related to model performance, rankings, and trends.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import streamlit as st
from decimal import Decimal

from src.database.database_connectivity import DatabaseConnectivity


class ModelPerformanceManager:
    """
    Manages database operations for model performance data.
    
    This class provides methods to retrieve and format model performance metrics,
    rankings, trends, and training history for display in the UI.
    """
    
    def __init__(self):
        """Initialize the ModelPerformanceManager with database connectivity."""
        self.db = DatabaseConnectivity()
    
    def _convert_decimal_to_float(self, value):
        """
        Convert decimal.Decimal to float if needed.
        
        Args:
            value: Value that might be decimal.Decimal
            
        Returns:
            float value or original value if not decimal
        """
        if isinstance(value, Decimal):
            return float(value)
        return value
    
    def get_overview_metrics(self) -> Dict:
        """
        Get top-level performance metrics for the dashboard overview.
        
        Returns:
            Dict containing overview metrics:
            - total_models: Total number of models trained
            - avg_f1_score: Average F1 score across all models
            - best_pair: Best performing pair symbol
            - best_f1_score: F1 score of best performing pair
            - models_today: Number of models trained today
            - f1_change: Percentage change in average F1 score
        """
        try:
            # Get total models count
            total_query = "SELECT COUNT(*) FROM model_performance"
            total_result = self.db.execute_query(total_query)
            total_models = total_result[0][0] if total_result else 0
            
            # Get average F1 score
            avg_query = "SELECT AVG(f1_score) FROM model_performance WHERE f1_score IS NOT NULL"
            avg_result = self.db.execute_query(avg_query)
            avg_f1_score = self._convert_decimal_to_float(avg_result[0][0]) if avg_result and avg_result[0][0] else 0.0
            
            # Get best performing pair
            best_query = """
                SELECT pair_symbol, f1_score 
                FROM model_performance 
                WHERE f1_score IS NOT NULL 
                ORDER BY f1_score DESC 
                LIMIT 1
            """
            best_result = self.db.execute_query(best_query)
            best_pair = best_result[0][0] if best_result else "N/A"
            best_f1_score = self._convert_decimal_to_float(best_result[0][1]) if best_result else 0.0
            
            # Get models trained today
            today_query = """
                SELECT COUNT(*) 
                FROM model_performance 
                WHERE DATE(training_date) = CURRENT_DATE
            """
            today_result = self.db.execute_query(today_query)
            models_today = today_result[0][0] if today_result else 0
            
            # Calculate F1 score change (compare today's avg vs yesterday's avg)
            change_query = """
                SELECT 
                    AVG(CASE WHEN DATE(training_date) = CURRENT_DATE THEN f1_score END) as today_avg,
                    AVG(CASE WHEN DATE(training_date) = CURRENT_DATE - INTERVAL '1 day' THEN f1_score END) as yesterday_avg
                FROM model_performance 
                WHERE f1_score IS NOT NULL
            """
            change_result = self.db.execute_query(change_query)
            today_avg = self._convert_decimal_to_float(change_result[0][0]) if change_result and change_result[0][0] else 0.0
            yesterday_avg = self._convert_decimal_to_float(change_result[0][1]) if change_result and change_result[0][1] else 0.0
            
            f1_change = 0.0
            if yesterday_avg > 0:
                f1_change = ((today_avg - yesterday_avg) / yesterday_avg) * 100
            
            return {
                'total_models': total_models,
                'avg_f1_score': avg_f1_score,
                'best_pair': best_pair,
                'best_f1_score': best_f1_score,
                'models_today': models_today,
                'f1_change': f1_change
            }
            
        except Exception as e:
            st.error(f"Error getting overview metrics: {e}")
            return {
                'total_models': 0,
                'avg_f1_score': 0.0,
                'best_pair': "N/A",
                'best_f1_score': 0.0,
                'models_today': 0,
                'f1_change': 0.0
            }
    
    def get_rankings(self, limit: int = 20) -> pd.DataFrame:
        """
        Get current model rankings ordered by F1 score.
        
        Args:
            limit: Maximum number of rankings to return
            
        Returns:
            DataFrame with columns: rank_position, pair_symbol, f1_score, 
            accuracy, precision, recall, training_date, model_run_id
        """
        try:
            query = """
                SELECT 
                    mr.rank_position,
                    mr.pair_symbol,
                    mr.f1_score,
                    mp.accuracy,
                    mp."precision",
                    mp.recall,
                    mp.training_date,
                    mr.model_run_id,
                    mr.experiment_name
                FROM model_rankings mr
                LEFT JOIN model_performance mp ON mr.pair_symbol = mp.pair_symbol 
                    AND mr.model_run_id = mp.model_run_id
                WHERE mr.ranking_date = CURRENT_DATE
                ORDER BY mr.rank_position
                LIMIT %s
            """
            result = self.db.execute_query(query, (limit,))
            
            if not result:
                return pd.DataFrame()
            
            columns = [
                'rank_position', 'pair_symbol', 'f1_score', 'accuracy',
                'precision', 'recall', 'training_date', 'model_run_id', 'experiment_name'
            ]
            
            df = pd.DataFrame(result, columns=columns)
            df['training_date'] = pd.to_datetime(df['training_date'])
            
            # Convert decimal columns to float
            numeric_columns = ['f1_score', 'accuracy', 'precision', 'recall']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = df[col].apply(self._convert_decimal_to_float)
            
            return df
            
        except Exception as e:
            st.error(f"Error getting rankings: {e}")
            return pd.DataFrame()
    
    def get_trends(self, days: int = 30) -> pd.DataFrame:
        """
        Get performance trends over the specified number of days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            DataFrame with columns: trend_date, avg_f1_7d, avg_f1_30d, 
            best_f1_7d, best_f1_30d, model_count_7d, model_count_30d
        """
        try:
            query = """
                SELECT 
                    trend_date,
                    avg_f1_7d,
                    avg_f1_30d,
                    best_f1_7d,
                    best_f1_30d,
                    model_count_7d,
                    model_count_30d
                FROM model_trends 
                WHERE trend_date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY trend_date DESC
            """
            result = self.db.execute_query(query, (days,))
            
            if not result:
                return pd.DataFrame()
            
            columns = [
                'trend_date', 'avg_f1_7d', 'avg_f1_30d', 'best_f1_7d',
                'best_f1_30d', 'model_count_7d', 'model_count_30d'
            ]
            
            df = pd.DataFrame(result, columns=columns)
            df['trend_date'] = pd.to_datetime(df['trend_date'])
            
            # Convert decimal columns to float
            numeric_columns = ['avg_f1_7d', 'avg_f1_30d', 'best_f1_7d', 'best_f1_30d']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = df[col].apply(self._convert_decimal_to_float)
            
            return df
            
        except Exception as e:
            st.error(f"Error getting trends: {e}")
            return pd.DataFrame()
    
    def get_recent_training(self, limit: int = 20) -> pd.DataFrame:
        """
        Get recent training activity.
        
        Args:
            limit: Maximum number of recent training records to return
            
        Returns:
            DataFrame with columns: pair_symbol, f1_score, accuracy, 
            training_date, model_run_id, experiment_name, epochs_trained, early_stopped
        """
        try:
            query = """
                SELECT 
                    pair_symbol,
                    f1_score,
                    accuracy,
                    training_date,
                    model_run_id,
                    experiment_name,
                    epochs_trained,
                    early_stopped
                FROM model_performance 
                WHERE f1_score IS NOT NULL
                ORDER BY training_date DESC
                LIMIT %s
            """
            result = self.db.execute_query(query, (limit,))
            
            if not result:
                return pd.DataFrame()
            
            columns = [
                'pair_symbol', 'f1_score', 'accuracy', 'training_date',
                'model_run_id', 'experiment_name', 'epochs_trained', 'early_stopped'
            ]
            
            df = pd.DataFrame(result, columns=columns)
            df['training_date'] = pd.to_datetime(df['training_date'])
            
            # Convert decimal columns to float
            numeric_columns = ['f1_score', 'accuracy']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = df[col].apply(self._convert_decimal_to_float)
            
            # Add status column
            df['status'] = '✅'  # All completed models are successful
            
            # Add duration column (placeholder - could be calculated from actual data)
            df['duration'] = '2m 30s'  # Placeholder
            
            return df
            
        except Exception as e:
            st.error(f"Error getting recent training: {e}")
            return pd.DataFrame()
    
    def get_model_details(self, pair_symbol: str) -> Dict:
        """
        Get detailed metrics for a specific model pair.
        
        Args:
            pair_symbol: The pair symbol to get details for
            
        Returns:
            Dict containing detailed model information
        """
        try:
            query = """
                SELECT 
                    pair_symbol,
                    f1_score,
                    accuracy,
                    "precision",
                    recall,
                    auc_score,
                    loss,
                    val_loss,
                    epochs_trained,
                    early_stopped,
                    training_date,
                    model_run_id,
                    experiment_name,
                    hyperparameters
                FROM model_performance 
                WHERE pair_symbol = %s
                ORDER BY training_date DESC
                LIMIT 1
            """
            result = self.db.execute_query(query, (pair_symbol,))
            
            if not result:
                return {}
            
            row = result[0]
            columns = [
                'pair_symbol', 'f1_score', 'accuracy', 'precision', 'recall',
                'auc_score', 'loss', 'val_loss', 'epochs_trained', 'early_stopped',
                'training_date', 'model_run_id', 'experiment_name', 'hyperparameters'
            ]
            
            details = dict(zip(columns, row))
            details['training_date'] = pd.to_datetime(details['training_date'])
            
            # Convert decimal values to float
            numeric_keys = ['f1_score', 'accuracy', 'precision', 'recall', 'auc_score', 'loss', 'val_loss']
            for key in numeric_keys:
                if key in details and details[key] is not None:
                    details[key] = self._convert_decimal_to_float(details[key])
            
            # Calculate duration (placeholder)
            details['duration'] = '2m 30s'
            
            return details
            
        except Exception as e:
            st.error(f"Error getting model details: {e}")
            return {}
    
    def get_f1_distribution(self) -> pd.DataFrame:
        """
        Get F1 score distribution for analytics.
        
        Returns:
            DataFrame with F1 scores for histogram analysis
        """
        try:
            query = """
                SELECT f1_score
                FROM model_performance 
                WHERE f1_score IS NOT NULL
                ORDER BY f1_score
            """
            result = self.db.execute_query(query)
            
            if not result:
                return pd.DataFrame()
            
            df = pd.DataFrame(result, columns=['f1_score'])
            
            # Convert decimal values to float
            df['f1_score'] = df['f1_score'].apply(self._convert_decimal_to_float)
            
            return df
            
        except Exception as e:
            st.error(f"Error getting F1 distribution: {e}")
            return pd.DataFrame()
    
    def get_accuracy_precision_data(self) -> pd.DataFrame:
        """
        Get accuracy vs precision data for scatter plot.
        
        Returns:
            DataFrame with accuracy, precision, and F1 score for scatter plot
        """
        try:
            query = """
                SELECT 
                    pair_symbol,
                    accuracy,
                    "precision",
                    f1_score
                FROM model_performance 
                WHERE f1_score IS NOT NULL 
                AND accuracy IS NOT NULL 
                AND "precision" IS NOT NULL
                ORDER BY f1_score DESC
            """
            result = self.db.execute_query(query)
            
            if not result:
                return pd.DataFrame()
            
            columns = ['pair_symbol', 'accuracy', 'precision', 'f1_score']
            df = pd.DataFrame(result, columns=columns)
            
            # Convert decimal values to float
            numeric_columns = ['accuracy', 'precision', 'f1_score']
            for col in numeric_columns:
                df[col] = df[col].apply(self._convert_decimal_to_float)
            
            return df
            
        except Exception as e:
            st.error(f"Error getting accuracy-precision data: {e}")
            return pd.DataFrame()
    
    def get_training_history(self) -> pd.DataFrame:
        """
        Get training history over time for line chart.
        
        Returns:
            DataFrame with training dates and F1 scores
        """
        try:
            query = """
                SELECT 
                    pair_symbol,
                    training_date,
                    f1_score
                FROM model_performance 
                WHERE f1_score IS NOT NULL
                ORDER BY training_date
            """
            result = self.db.execute_query(query)
            
            if not result:
                return pd.DataFrame()
            
            columns = ['pair_symbol', 'training_date', 'f1_score']
            df = pd.DataFrame(result, columns=columns)
            df['training_date'] = pd.to_datetime(df['training_date'])
            
            # Convert decimal values to float
            df['f1_score'] = df['f1_score'].apply(self._convert_decimal_to_float)
            
            return df
            
        except Exception as e:
            st.error(f"Error getting training history: {e}")
            return pd.DataFrame() 