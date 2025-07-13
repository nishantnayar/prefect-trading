# Data Systems Documentation

## Overview

The Prefect Trading System includes multiple data processing systems designed for different use cases and market conditions. This document covers both the Data Recycler System for historical data replay and the GARCH-based Pairs Trading System for real-time trading.

> **📋 Quick Links**: [Architecture Decisions](architecture-decisions.md) | [Setup Guide](setup.md) | [Development Guide](development.md) | [API Documentation](api.md)

## Data Recycler System

### Overview

The Data Recycler System allows you to recycle existing market data from your database to simulate real-time market data feeds during non-market hours. This system creates a local WebSocket server that replays historical data in the same format as Alpaca's WebSocket API, enabling seamless testing and development without requiring live market data.

**Key Features:**
- **Multi-Symbol Support**: Stream data for multiple symbols simultaneously (AAPL, PDFS, ROG)
- **Proxy Data Fallback**: Automatically use AAPL data as proxy for missing symbols
- **Real Market Data**: Uses actual historical market data instead of generated dummy data
- **Real-Time Timestamps**: Sends data with current timestamps for realistic testing
- **1-Minute Intervals**: Simulates real market data timing with 60-second delays
- **Configuration-Driven**: Easy symbol management through `config.yaml`
- **Seamless Transition**: No code changes needed when real data becomes available
- **Zero Risk**: Original files remain unchanged, new system is completely separate

**Note**: Your database contains market data starting from **2025-06-23**. All replay scenarios use dates from this period onwards.

### Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Configuration │    │   Multi-Symbol   │    │   Database      │
│   (config.yaml) │───▶│   Data Recycler  │◄──►│   (market_data) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌──────────────────┐
│   Symbol        │    │   WebSocket      │
│   Mapping       │    │   Client         │
│   (Proxy Logic) │    │   (Your App)     │
└─────────────────┘    └──────────────────┘
```

### Current Configuration

#### Pairs Trading Setup
```yaml
websocket:
  mode: "recycler"
  symbols: ["AAPL", "PDFS", "ROG"]
  recycler:
    symbols: ["AAPL", "PDFS", "ROG"]
    replay_mode: "loop"
    replay_speed: 1.0
    server_url: "ws://localhost:8765"
    loop_count: -1  # -1 = infinite loop
```

#### Symbol Mapping Logic
- **AAPL**: Uses actual AAPL data from database
- **PDFS**: Uses AAPL data as proxy (until real PDFS data is available)
- **ROG**: Uses AAPL data as proxy (until real ROG data is available)

### Components

#### 1. Multi-Symbol Data Recycler Server (`src/data/sources/data_recycler_server.py`)

A local WebSocket server that:
- Loads historical data from the `market_data` table for multiple symbols
- Automatically maps missing symbols to AAPL data as proxy
- Replays data in Alpaca WebSocket format with current timestamps
- Uses 60-second intervals between messages to simulate real market data timing
- Supports multiple replay modes and speed controls
- Streams data for all configured symbols simultaneously

#### 2. Configurable WebSocket Client (`src/data/sources/configurable_websocket.py`)

A WebSocket client that:
- Can connect to either Alpaca or the data recycler server
- Uses the same interface as the original Alpaca WebSocket
- Stores data with source identification (`data_source` column)
- Maintains all existing functionality

#### 3. Configuration System (`src/utils/websocket_config.py`)

Configuration management that:
- Loads WebSocket settings from `config.yaml`
- Supports environment variable overrides
- Provides easy switching between modes
- Manages symbol configuration and proxy fallback

#### 4. Utility Scripts

- `scripts/manage_symbols.py` - Manage symbol configuration and check data status
- `scripts/test_multi_symbol_recycler.py` - Test the multi-symbol system
- `scripts/start_data_recycler.py` - Start the data recycler server
- `scripts/run_configurable_websocket.py` - Run the configurable client

### Usage

#### 1. Check Current Status
```bash
python scripts/manage_symbols.py status
```

**Output:**
```
=== Current Configuration ===
WebSocket Mode: recycler
  Server URL: ws://localhost:8765
  Replay Mode: loop
  Replay Speed: 1.0x
  Symbols: ['AAPL', 'PDFS', 'ROG']

=== Quick Data Check ===
✅ AAPL: 3171 records available
❌ PDFS: No data (will use AAPL as proxy)
❌ ROG: No data (will use AAPL as proxy)
```

#### 2. Start Data Recycler Server
```bash
python -m src.data.sources.data_recycler_server
```

#### 3. Test the System
```bash
python scripts/test_multi_symbol_recycler.py
```

#### 4. Check Data Status (After Monday's Data Collection)
```bash
python scripts/manage_symbols.py status
```

### Symbol Management

#### Switch to Pairs Trading Mode
```bash
python scripts/manage_symbols.py pairs
```

#### Switch to Testing Mode
```bash
python scripts/manage_symbols.py testing
```

#### Add/Remove Symbols
```bash
# Add a symbol
python scripts/manage_symbols.py add MSFT

# Remove a symbol
python scripts/manage_symbols.py remove PDFS
```

### Data Collection Strategy

#### Phase 1: Proxy Data (Current)
- Use AAPL data as proxy for PDFS and ROG
- Test pairs trading infrastructure immediately
- Develop and validate trading algorithms

#### Phase 2: Real Data Collection & Automatic Transition
- Start collecting real PDFS and ROG data during market hours (Monday)
- On Tuesday, check data availability: `python scripts/manage_symbols.py status`
- If data is available, the system automatically uses real data
- No code changes needed - the system handles the transition seamlessly

### Replay Modes

#### 1. Loop Mode (Default)
```yaml
websocket:
  mode: "recycler"
  recycler:
    replay_mode: "loop"
    replay_speed: 1.0
    symbols: ["AAPL", "PDFS", "ROG"]
    loop_count: -1  # -1 = infinite loop
```

**Features:**
- Continuously loops through all available historical data
- When reaching the end, starts over from the beginning
- Ideal for continuous testing and development

#### 2. Date Range Mode
```yaml
websocket:
  mode: "recycler"
  recycler:
    replay_mode: "date_range"
    date_range:
      start_date: "2025-06-23"  # Your earliest available data
      end_date: "2025-06-30"    # Example: first week of data
    replay_speed: 2.0
    symbols: ["AAPL", "PDFS", "ROG"]
```

**Features:**
- Replays data from specific date ranges within your available data
- Useful for testing specific market conditions or events
- Can replay volatile periods, earnings announcements, etc.

#### 3. Single Pass Mode
```yaml
websocket:
  mode: "recycler"
  recycler:
    replay_mode: "single_pass"
    replay_speed: 1.0
    symbols: ["AAPL", "PDFS", "ROG"]
```

**Features:**
- Replays data once from start to finish
- Stops when reaching the end of available data
- Useful for one-time testing scenarios

## GARCH-Based Pairs Trading System

### Overview

This document outlines the architecture and implementation strategy for an **enterprise-level GARCH-based pairs trading system** with integrated MLflow model management. The system is designed for multi-sector support (e.g., technology, healthcare, financial), but **currently only the technology sector is active**. The architecture, experiment tracking, and model management are all future-proofed for seamless expansion to additional sectors.

### System Architecture

#### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   MLflow Server │    │   Trading       │
│                 │    │                 │    │   Engine        │
│ • WebSocket     │───▶│ • Experiments   │───▶│ • Signal Gen    │
│ • Database      │    │ • Model Registry│    │ • Execution     │
│ • Historical    │    │ • Artifacts     │    │ • Risk Mgmt     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Training        │    │ Model           │    │ Portfolio       │
│ Pipeline        │    │ Validation      │    │ Manager         │
│                 │    │                 │    │                 │
│ • GRU Training  │    │ • A/B Testing   │    │ • Account Info  │
│ • GARCH Fitting │    │ • Backtesting   │    │ • Positions     │
│ • Feature Eng   │    │ • Statistical   │    │ • Performance   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### Core Components

##### 1. Data Layer
- **Real-time Data**: WebSocket feeds for symbol pairs (1-minute bars)
- **Historical Data**: Hourly data for GARCH model training and validation
- **Feature Engineering**: Returns, volatility, spread calculations, technical indicators

##### 2. MLflow Model Management
- **Experiment Tracking**: Comprehensive logging of training runs, parameters, and metrics
- **Model Registry**: Version control, staging, and production deployment
- **Artifact Management**: Model weights, plots, configuration files, and documentation

##### 3. GARCH-GRU Hybrid Strategy Engine
- **Cointegration Testing**: Engle-Granger or Johansen test for pair identification
- **GARCH Model**: GARCH(1,1) for volatility forecasting
- **GRU Neural Network**: Sequence modeling for mean reversion prediction
- **Feature Engineering**: Lagged spreads, GARCH residuals, technical indicators

##### 4. Risk Management
- **Position Sizing**: Based on GARCH volatility forecasts and model confidence
- **Stop Loss**: Dynamic based on GARCH volatility bands
- **Correlation Monitoring**: Real-time correlation tracking and drift detection

##### 5. Execution Engine
- **Order Management**: Alpaca paper trading integration
- **Position Tracking**: Long/short pair positions with model attribution
- **Performance Monitoring**: P&L, Sharpe ratio, drawdown, model performance

### MLflow Integration Strategy

#### Experiment Tracking Structure

##### Experiment Hierarchy
```
pairs_trading/
├── technology_sector/   # Currently active
│   ├── gru_garch_hybrid_v1/
│   ├── gru_garch_hybrid_v2/
│   └── gru_garch_hybrid_v3/
├── healthcare_sector/   # For future expansion
│   ├── gru_garch_hybrid_v1/
│   └── gru_garch_hybrid_v2/
└── financial_sector/    # For future expansion
    └── gru_garch_hybrid_v1/
```
> **Note:** Only `technology_sector` is currently in use. The structure is designed for easy addition of new sectors.

##### Tracked Parameters
```python
# Model Hyperparameters
params = {
    'sequence_length': 10,
    'gru_units': 64,
    'dropout_rate': 0.255,
    'learning_rate': 0.0003,
    'batch_size': 32,
    'epochs': 50,
    'validation_split': 0.2,
    'garch_order': (1, 1),
    'garch_model_type': 'GARCH'
}

# Data Parameters
data_params = {
    'sector': 'technology',
    'min_data_points': 1800,
    'train_start_date': '2023-01-01',
    'train_end_date': '2024-12-31',
    'test_start_date': '2025-01-01',
    'test_end_date': '2025-05-14',
    'lookback_days': 30
}

# Feature Engineering Parameters
feature_params = {
    'lag_features': [1, 2, 3, 4, 5],
    'technical_indicators': ['MA_5', 'MA_20', 'RSI'],
    'z_score_window': 7,
    'volatility_window': 20
}
```

##### Tracked Metrics
```python
# Model Performance Metrics
metrics = {
    'train_f1_score': 0.7445,
    'test_f1_score': 0.7321,
    'train_accuracy': 0.7512,
    'test_accuracy': 0.7389,
    'train_precision': 0.7234,
    'test_precision': 0.7156,
    'train_recall': 0.7654,
    'test_recall': 0.7489
}

# Trading Performance Metrics
trading_metrics = {
    'sharpe_ratio': 1.234,
    'max_drawdown': 0.089,
    'total_return': 0.156,
    'win_rate': 0.623,
    'profit_factor': 1.456,
    'calmar_ratio': 1.752,
    'avg_trade_duration': 4.5
}

# Statistical Validation Metrics
statistical_metrics = {
    'cointegration_pvalue': 0.0234,
    'arch_test_pvalue': 0.1131,
    'ljung_box_pvalue': 0.4659,
    'adf_test_pvalue': 0.0012,
    'garch_aic': -1234.56,
    'garch_bic': -1220.34
}
```

##### Model Naming Convention
```
pairs_trading_gru_garch_{sector}_{version}_{date}
Example: pairs_trading_gru_garch_technology_v2_20250514
```
> **Note:** Only `technology` sector models are currently registered. Naming is multi-sector ready.

#### Model Registry Structure

##### Model Stages
1. **Staging**: Newly trained models awaiting validation
2. **Production**: Currently deployed models
3. **Archived**: Previous production models

##### Model Tags
```python
tags = {
    'sector': 'technology',
    'model_type': 'gru_garch_hybrid',
    'feature_set': 'lagged_spread_garch_technical',
    'training_date': '2025-05-14',
    'data_version': 'v1.2',
    'code_version': 'git_commit_hash',
    'garch_order': '1,1',
    'sequence_length': '10'
}
```

### Detailed Component Design

#### A. MLflow-Integrated Training Pipeline

```python
import mlflow
import mlflow.keras
from mlflow.models import infer_signature

class MLflowGARCHGRUTrainer:
    def __init__(self, experiment_name="pairs_trading"):
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)
        
    def train_and_log_model(self, data_params, model_params, feature_params):
        with mlflow.start_run():
            # Log parameters
            mlflow.log_params(data_params)
            mlflow.log_params(model_params)
            mlflow.log_params(feature_params)
            
            # Train model
            model, metrics = self.train_gru_garch_model(data_params, model_params, feature_params)
            
            # Log metrics
            mlflow.log_metrics(metrics)
            
            # Log model
            mlflow.keras.log_model(model, "model")
            
            # Log artifacts
            mlflow.log_artifact("garch_diagnostics.png")
            mlflow.log_artifact("training_history.png")
            
            return model, metrics
```

#### B. Two-Model Architecture

##### Model 1: Daily Pair Identification
- **Purpose**: Identify valid pairs for trading
- **Frequency**: Daily pre-market (6:00 AM)
- **Input**: Historical data (30-60 days)
- **Output**: Valid pairs with GARCH models
- **Criteria**: Cointegration, correlation, GARCH fit quality

##### Model 2: Real-time Signal Generation
- **Purpose**: Generate trading signals for valid pairs
- **Frequency**: Every 5 minutes during trading hours
- **Input**: Real-time websocket data + pre-selected GARCH models
- **Output**: Entry/exit signals with confidence scores
- **Criteria**: GARCH volatility + GRU predictions

#### C. Quality Gates

##### Pair Selection Criteria
- **Correlation threshold**: 0.8 minimum
- **Cointegration test**: p-value < 0.05
- **Model quality**: Composite score > 0.7
- **Statistical diagnostics**: Ljung-Box and ARCH tests

##### Performance Metrics
- **40% AIC/BIC**: Model fit quality
- **30% Volatility forecasting accuracy**: 1-step ahead
- **20% Trading performance**: Recent backtest
- **10% Statistical diagnostics**: Residual quality

### Implementation Status

#### Current Status Summary
- **MLflow Foundation**: ✅ COMPLETED (Week 1)
- **Existing GARCH-GRU Implementation**: ✅ DISCOVERED (Working with F1=0.7445)
- **Daily Pair Identification Architecture**: ✅ DESIGNED (Current)
- **Two-Model Architecture**: ✅ DESIGNED (Current)
- **PyTorch Migration**: 🔄 IN PROGRESS (Week 2-3)
- **MLflow Integration**: ⏳ PENDING (Week 4-5)
- **Production Integration**: ⏳ PENDING (Week 6-7)
- **Database Extensions**: ⏳ PENDING (Week 8)

#### Phase 1: MLflow Foundation ✅ COMPLETED

##### ✅ Step 1: Dependencies Installation
- **Date**: [Previous]
- **Status**: COMPLETED
- **Details**: 
  - Updated `config/requirements.txt` to replace TensorFlow with PyTorch 2.1.0
  - Added MLflow 2.8.1 and related dependencies
  - All dependencies installed in existing conda environment

##### ✅ Step 2: Configuration Setup
- **Date**: [Previous]
- **Status**: COMPLETED
- **Details**:
  - Updated `config/config.yaml` with MLflow configuration
  - Updated `config/env.example` with MLflow environment variables
  - MLflow artifacts directory created at `./mlruns`

##### ✅ Step 3: Database Setup
- **Date**: [Previous]
- **Status**: COMPLETED
- **Details**:
  - Created `mlflow_db` database in PostgreSQL
  - Used separate database approach for clean architecture
  - Database connection: `postgresql://postgres:nishant@localhost/mlflow_db`

##### ✅ Step 4: MLflow Server Launch
- **Date**: [Previous]
- **Status**: COMPLETED
- **Details**:
  - Started MLflow server with PostgreSQL backend
  - Server running on: http://localhost:5000
  - Web UI accessible and functional

##### ✅ Step 5: MLflow Manager Implementation
- **Date**: [Previous]
- **Status**: COMPLETED
- **Details**:
  - Created `src/mlflow_manager.py` with comprehensive functionality
  - Implemented experiment tracking and model registry management
  - Added MLflow configuration manager in `src/ml/config.py`
  - Basic MLflow integration tests implemented

#### Phase 2: PyTorch Migration and Refactoring 🔄 IN PROGRESS

##### ✅ Step 1: Existing Implementation Analysis
- **Date**: [Current]
- **Status**: COMPLETED
- **Priority**: HIGH
- **File**: `src/scripts/pairs_identification_GRU.ipynb`
- **Components**: 
  - Complete GARCH-GRU pipeline already implemented
  - GARCH(1,1) model with volatility forecasting
  - GRU neural network for mean reversion prediction
  - Feature engineering with technical indicators
  - Hyperparameter optimization using Optuna
  - Cointegration testing and spread calculation
- **Key Findings**:
  - Best F1 Score: 0.7445 (exceeds target of 0.70)
  - Optimal hyperparameters identified
  - Full pipeline tested on technology sector data
  - TensorFlow/Keras implementation (needs PyTorch migration)
- **Estimated Time**: 0 days (already implemented)

##### ✅ Step 2: Two-Model Architecture Design
- **Date**: [Current]
- **Status**: COMPLETED
- **Priority**: HIGH
- **Design**: Two distinct models for different purposes
- **Model 1: Daily Pair Identification**:
  - Purpose: Identify valid pairs for trading
  - Frequency: Daily pre-market (6:00 AM)
  - Input: Historical data (30-60 days)
  - Output: Valid pairs with GARCH models
  - Criteria: Cointegration, correlation, GARCH fit quality
- **Model 2: Real-time Signal Generation**:
  - Purpose: Generate trading signals for valid pairs
  - Frequency: Every 5 minutes during trading hours
  - Input: Real-time websocket data + pre-selected GARCH models
  - Output: Entry/exit signals with confidence scores
  - Criteria: GARCH volatility + GRU predictions
- **Benefits**:
  - Separation of concerns
  - Performance optimization (daily heavy computation vs real-time light)
  - Reliability and scalability
  - Clear debugging and monitoring
- **Estimated Time**: 0 days (design completed)

##### ✅ Step 3: Daily Pair Identification Architecture Design
- **Date**: [Current]
- **Status**: COMPLETED
- **Priority**: HIGH
- **Orchestration**: Prefect workflows for 6:00 AM pre-market execution
- **Flow Design**:
  1. Data Collection (Historical data)
  2. Pair Validation & Screening (Correlation + Cointegration)
  3. GARCH Model Fitting
  4. Model Selection & Ranking
  5. MLflow Storage & Registration
  6. Trading Configuration Update
- **Quality Gates**:
  - Correlation threshold: 0.8 minimum
  - Cointegration test: p-value < 0.05
  - Model quality: Composite score > 0.7
  - Statistical diagnostics: Ljung-Box and ARCH tests
- **MLflow Integration**:
  - Model versioning for each day
  - Artifact storage for models and metadata
  - Experiment tracking with full lineage
  - Consistent naming with existing MLflow structure
- **Performance Metrics**:
  - 40% AIC/BIC (model fit quality)
  - 30% Volatility forecasting accuracy (1-step ahead)
  - 20% Trading performance (recent backtest)
  - 10% Statistical diagnostics (residual quality)
- **Estimated Time**: 0 days (design completed)

##### 🔄 Step 4: PyTorch GRU Migration and Refactoring
- **Date**: [Current]
- **Status**: IN PROGRESS
- **Priority**: HIGH
- **File**: `src/ml/gru_model.py`
- **Components**:
  - Convert existing TensorFlow GRU to PyTorch
  - Refactor monolithic pipeline into modular components
  - Maintain exact same architecture and hyperparameters
  - Preserve F1=0.7445 performance
  - Add MLflow model logging capabilities
  - Create clean, reusable PyTorch classes
- **Dependencies**: `torch`, `numpy`, `pandas` (existing)
- **Estimated Time**: 3-4 days
- **Success Criteria**: F1 score ≥ 0.7445 after PyTorch migration
- **Refactoring Goals**: Modular, maintainable, MLflow-ready code

##### 🔄 Step 5: GARCH Model Refactoring and Modularization
- **Date**: [Current]
- **Status**: PLANNED
- **Priority**: MEDIUM
- **File**: `src/ml/garch_model.py`
- **Components**:
  - Extract GARCH functionality from existing pipeline
  - Create modular `GARCHModel` and `PairsGARCHModel` classes
  - Refactor into clean, reusable PyTorch-compatible components
  - Maintain existing performance and diagnostics
  - Add MLflow experiment tracking
  - Ensure compatibility with PyTorch workflow
- **Dependencies**: `arch`, `statsmodels`, `scipy` (existing)
- **Estimated Time**: 2-3 days
- **Success Criteria**: Same GARCH diagnostics as existing implementation
- **Refactoring Goals**: Clean separation of concerns, PyTorch integration ready

##### 🔄 Step 6: Feature Engineering Refactoring and Extraction
- **Date**: [Current]
- **Status**: PLANNED
- **Priority**: MEDIUM
- **File**: `src/ml/feature_engineering.py`
- **Components**:
  - Extract feature engineering from existing pipeline
  - Refactor into PyTorch-compatible feature pipeline
  - Technical indicators (MA, RSI) already implemented
  - Lagged features (1-5 lags) already implemented
  - GARCH residuals integration already implemented
  - Feature scaling and normalization
  - Create clean, modular feature engineering classes
- **Dependencies**: `scikit-learn`, `torch` (existing)
- **Estimated Time**: 2 days (refactoring + PyTorch integration)
- **Success Criteria**: Same feature set as existing implementation
- **Refactoring Goals**: PyTorch tensor compatibility, modular design

#### Phase 3: MLflow Integration and Strategy Refactoring 🔄 IN PROGRESS

##### ✅ Step 1: PyTorch GRU Implementation
- **Date**: [Completed]
- **Status**: COMPLETED
- **Priority**: HIGH
- **File**: `src/ml/gru_model.py`
- **Components**:
  - ✅ PyTorch GRU model implementation
  - ✅ Complete training pipeline with MLflow integration
  - ✅ All pairs training for comprehensive baseline
  - ✅ Performance analysis and ranking
  - ✅ Database integration for performance tracking
  - ✅ Automated rankings and trends updates
  - ✅ Comprehensive error handling and logging
- **Dependencies**: PyTorch, MLflow, PostgreSQL
- **Actual Time**: 3 days
- **Success Criteria**: ✅ Complete PyTorch GRU training system with MLflow tracking
- **Implementation**: 
  - Complete training pipeline: Data preparation → Model training → Performance analysis → Database storage
  - All pairs training: Train models for all pairs that meet correlation threshold (>0.8)
  - Performance analysis: Comprehensive ranking and statistics for model comparison
  - MLflow integration: Experiment tracking with descriptive run names and metadata
  - Database storage: Performance metrics, rankings, and trends stored in PostgreSQL
  - Production ready: Error handling, resource management, and comprehensive logging

##### 🔄 Step 2: Real-time Signal Generation Implementation
- **Date**: [Week 5]
- **Status**: PLANNED
- **Priority**: HIGH
- **File**: `src/ml/signal_generator.py`
- **Components**:
  - Real-time data processing from WebSocket
  - GARCH volatility forecasting
  - GRU signal generation
  - Signal confidence scoring
  - MLflow model loading and inference
  - Performance monitoring and logging
- **Dependencies**: Previous phase components
- **Estimated Time**: 3-4 days
- **Success Criteria**: Real-time signal generation with MLflow model serving

##### 🔄 Step 3: MLflow Model Serving Integration
- **Date**: [Week 5]
- **Status**: PLANNED
- **Priority**: MEDIUM
- **Components**:
  - MLflow model serving setup
  - Model versioning and staging
  - A/B testing framework
  - Model performance monitoring
  - Automated model promotion/demotion
- **Dependencies**: MLflow server, model registry
- **Estimated Time**: 2-3 days
- **Success Criteria**: Automated model serving with version control

#### Phase 4: Production Integration ⏳ PENDING

##### 🔄 Step 1: Prefect Workflow Integration
- **Date**: [Week 6]
- **Status**: PLANNED
- **Priority**: HIGH
- **Components**:
  - Daily pair identification workflow
  - Real-time signal generation workflow
  - Model training and validation workflow
  - Performance monitoring workflow
  - Error handling and alerting
- **Dependencies**: All previous phases
- **Estimated Time**: 3-4 days
- **Success Criteria**: Production-ready workflows with monitoring

##### 🔄 Step 2: Risk Management Integration
- **Date**: [Week 7]
- **Status**: PLANNED
- **Priority**: HIGH
- **Components**:
  - Position sizing based on GARCH volatility
  - Dynamic stop-loss implementation
  - Correlation drift detection
  - Risk limit enforcement
  - Performance attribution
- **Dependencies**: Signal generation, portfolio management
- **Estimated Time**: 2-3 days
- **Success Criteria**: Comprehensive risk management system

##### 🔄 Step 3: Performance Monitoring and Alerting
- **Date**: [Week 7]
- **Status**: PLANNED
- **Priority**: MEDIUM
- **Components**:
  - Real-time performance dashboards
  - Model performance tracking
  - Trading performance metrics
  - Automated alerting system
  - Performance reporting
- **Dependencies**: All trading components
- **Estimated Time**: 2-3 days
- **Success Criteria**: Comprehensive monitoring and alerting

#### Phase 5: Database Extensions ⏳ PENDING

##### 🔄 Step 1: Model Metadata Storage
- **Date**: [Week 8]
- **Status**: PLANNED
- **Priority**: MEDIUM
- **Components**:
  - Model performance history
  - Trading signal history
  - Pair performance tracking
  - Model version tracking
  - Performance attribution data
- **Dependencies**: Database schema design
- **Estimated Time**: 2-3 days
- **Success Criteria**: Complete model and trading history storage

##### 🔄 Step 2: Historical Performance Analysis
- **Date**: [Week 8]
- **Status**: PLANNED
- **Priority**: LOW
- **Components**:
  - Historical backtesting framework
  - Performance comparison tools
  - Model evolution tracking
  - Strategy optimization tools
- **Dependencies**: Historical data, model metadata
- **Estimated Time**: 2-3 days
- **Success Criteria**: Comprehensive historical analysis capabilities

### Best Practices

#### For Data Recycler System
1. **Use Real Market Data**: Always use actual historical data instead of generated data
2. **Test Multiple Scenarios**: Use different replay modes for comprehensive testing
3. **Monitor Performance**: Track system performance during replay sessions
4. **Validate Data Quality**: Ensure data integrity and consistency

#### For GARCH Pairs Trading
1. **Regular Model Retraining**: Retrain models periodically with new data
2. **Monitor Model Performance**: Track model performance metrics continuously
3. **Risk Management**: Implement comprehensive risk management strategies
4. **Backtesting**: Always backtest strategies before live deployment

### Troubleshooting

#### Data Recycler Issues
1. **No Data Available**: Check database for historical data
2. **WebSocket Connection Issues**: Verify server is running and accessible
3. **Symbol Mapping Problems**: Check configuration for symbol mappings

#### GARCH Pairs Trading Issues
1. **Model Performance Degradation**: Retrain models with recent data
2. **Signal Quality Issues**: Check feature engineering and model parameters
3. **Risk Management Alerts**: Review position sizing and stop-loss settings

### Future Enhancements

#### Data Recycler Enhancements
- **Multi-timeframe Support**: Support for different time intervals
- **Custom Data Sources**: Integration with additional data providers
- **Advanced Replay Modes**: More sophisticated replay scenarios

#### GARCH Pairs Trading Enhancements
- **Multi-sector Expansion**: Add healthcare and financial sectors
- **Advanced Models**: Implement more sophisticated ML models
- **Real-time Optimization**: Dynamic parameter optimization
- **Alternative Strategies**: Implement additional trading strategies

### Related Documentation

- **[Architecture Decisions](architecture-decisions.md)**: Design rationale and system architecture decisions
- **[API Documentation](api.md)**: External API integrations and data sources
- **[Setup Guide](setup.md)**: System setup and configuration
- **[Development Guide](development.md)**: Development practices and workflows 