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

## Streamlined Data Loading

### Current Optimization

The system has been optimized for performance by streamlining the start-of-day data loading process:

#### What's Loaded Daily
- **1-minute historical data** (last 7 days) - Core ML pipeline requirement
- **Data preprocessing** with variance stability testing
- **Model training** for all sectors with MLflow integration

#### What's Commented Out (Can Be Run Separately)
- **Hourly historical data loading** - Reduces API usage and execution time
- **Symbol maintenance** - Can be run via separate flow
- **Yahoo Finance data collection** - Can be run via separate flow

#### Benefits
- **Faster execution** - Reduced from ~15 minutes to ~5 minutes
- **Lower API usage** - Reduced Alpaca API calls
- **More reliable** - Fewer potential failure points
- **Focused on ML pipeline** - Prioritizes core trading algorithm needs

#### Running Additional Tasks
```bash
# Run symbol maintenance separately
python -c "from main import symbol_maintenance_flow; symbol_maintenance_flow()"

# Run Yahoo Finance data collection separately
python -c "from main import yahoo_data_loader_flow; yahoo_data_loader_flow()"

# Run hourly data loading separately (if needed)
python -c "from src.data.sources.alpaca_historical_loader import AlpacaDataLoader; AlpacaDataLoader().run_historical_load(timeframe=TimeFrame.Hour)"
```

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
- `scripts/run_tests.py` - Run comprehensive test suites
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
python scripts/run_tests.py
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

### Data Preprocessing and Mathematical Foundations

#### Logarithmic Returns and Z-Score Normalization

This section covers the mathematical foundations for data preprocessing in financial time series analysis, specifically focusing on when to use logarithmic returns vs. log close prices, and how to properly apply z-score normalization.

##### Log Close vs. Log Returns

**Log Close**
- This is simply the natural logarithm of the closing price: `log(P_t)`
- Used primarily in cointegration testing and spread construction.

**Log Returns**
- This is the difference in log closing prices between consecutive time periods: 
  ```
  r_t = log(P_t) - log(P_{t-1}) = log(P_t / P_{t-1})
  ```
- Log returns are used for **modeling price changes**, volatility, and returns distributions.
- **Variance is more stable** for log returns compared to raw prices.

##### Z-Score Normalization - Expanding Window

Z-score normalization is applied using an expanding window approach:
```
Z_t = (X_t - μ_{t-1}) / σ_{t-1}
```

Where:
- `X_t` is the current value (spread or return)
- `μ_{t-1}` is the mean of all previous values
- `σ_{t-1}` is the standard deviation of all previous values

This approach ensures that:
- No look-ahead bias is introduced
- The normalization adapts to changing market conditions
- Historical data is preserved for backtesting

##### When to Use Each Approach

| **Task**              | **Use**                           | **Why**                               |
|-----------------------|-----------------------------------|---------------------------------------|
| Cointegration tests   | log close                         | To assess long-term relationship      |
| Spread construction   | log close                         | To build mean-reverting spread        |
| Volatility modeling   | log returns                       | To stabilize variance                 |
| Z-score normalization | log close (spread) or log returns | Depending on what is being normalized |

##### Implementation Guidelines

**For Cointegration & Spread Construction:**
- Use **log close prices** (not returns)
- Spread is typically based on logs of prices:
  ```
  Spread_t = log(P_{A,t}) - β * log(P_{B,t}) - μ
  ```
- This is because cointegration is about finding stationary combinations of non-stationary price series.

**For Volatility Modeling (GARCH), Time-Series Features:**
- Use **log returns** as input for volatility estimation and normalization
- Log returns provide more stable variance for statistical modeling

**For Normalization / Z-scores:**
- If normalizing the spread, use z-scores **of the spread series** (which itself is constructed from log prices)
- If normalizing returns, use z-scores **of log returns**

##### Code Implementation Example

```python
import numpy as np
import pandas as pd

def calculate_log_returns(prices):
    """Calculate log returns from price series."""
    return np.log(prices / prices.shift(1))

def calculate_log_close(prices):
    """Calculate log of closing prices."""
    return np.log(prices)

def calculate_spread(log_prices_a, log_prices_b, beta):
    """Calculate spread from log prices using beta."""
    return log_prices_a - beta * log_prices_b

def expanding_zscore(series, min_periods=30):
    """Calculate z-score using expanding window."""
    expanding_mean = series.expanding(min_periods=min_periods).mean()
    expanding_std = series.expanding(min_periods=min_periods).std()
    return (series - expanding_mean) / expanding_std

# Example usage for pairs trading
def prepare_pairs_data(price_a, price_b, beta):
    """Prepare data for pairs trading analysis."""
    # Step 1: Calculate log prices
    log_price_a = calculate_log_close(price_a)
    log_price_b = calculate_log_close(price_b)
    
    # Step 2: Calculate spread
    spread = calculate_spread(log_price_a, log_price_b, beta)
    
    # Step 3: Calculate z-score of spread
    spread_zscore = expanding_zscore(spread)
    
    # Step 4: Calculate log returns for volatility modeling
    returns_a = calculate_log_returns(price_a)
    returns_b = calculate_log_returns(price_b)
    
    return {
        'spread': spread,
        'spread_zscore': spread_zscore,
        'returns_a': returns_a,
        'returns_b': returns_b
    }
```

##### Statistical Tests for Variance Stability

After applying logarithmic transformations, it's important to validate that variance has been successfully stabilized. The following tests help confirm that the data preprocessing is working correctly:

| **Method** | **Successful Stabilization Sign** |
|------------|-----------------------------------|
| **Visual Plot** | No obvious "funnel" shape (e.g., widening/narrowing volatility) |
| **Rolling Std** | Flat or stable trend (no large spikes/dips) |
| **ARCH Test** | p-value > 0.05 → Residual heteroscedasticity is not significant |

**Implementation Example:**
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.stats.diagnostic import het_arch

def test_variance_stability(returns, window=30):
    """
    Test variance stability of return series.
    
    Args:
        returns: Log return series
        window: Rolling window size for standard deviation
    
    Returns:
        dict: Test results and plots
    """
    # 1. Visual Plot - Check for funnel shape
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.plot(returns)
    plt.title('Log Returns Over Time')
    plt.ylabel('Log Returns')
    
    # 2. Rolling Standard Deviation
    rolling_std = returns.rolling(window=window).std()
    
    plt.subplot(2, 2, 2)
    plt.plot(rolling_std)
    plt.title(f'Rolling Standard Deviation (Window={window})')
    plt.ylabel('Standard Deviation')
    
    # 3. ARCH Test for heteroscedasticity
    # Remove NaN values for testing
    clean_returns = returns.dropna()
    arch_stat, arch_pvalue = het_arch(clean_returns, nlags=4)
    
    plt.subplot(2, 2, 3)
    plt.hist(returns, bins=50, alpha=0.7)
    plt.title('Distribution of Log Returns')
    plt.xlabel('Log Returns')
    
    plt.subplot(2, 2, 4)
    plt.scatter(returns[:-1], returns[1:], alpha=0.5)
    plt.xlabel('Log Returns (t-1)')
    plt.ylabel('Log Returns (t)')
    plt.title('Autocorrelation Plot')
    
    plt.tight_layout()
    plt.show()
    
    # 4. Summary statistics
    results = {
        'rolling_std_mean': rolling_std.mean(),
        'rolling_std_std': rolling_std.std(),
        'rolling_std_cv': rolling_std.std() / rolling_std.mean(),  # Coefficient of variation
        'arch_statistic': arch_stat,
        'arch_pvalue': arch_pvalue,
        'is_stable': arch_pvalue > 0.05 and rolling_std.std() / rolling_std.mean() < 0.5
    }
    
    print(f"Variance Stability Test Results:")
    print(f"  - Rolling Std Mean: {results['rolling_std_mean']:.6f}")
    print(f"  - Rolling Std Std: {results['rolling_std_std']:.6f}")
    print(f"  - Coefficient of Variation: {results['rolling_std_cv']:.4f}")
    print(f"  - ARCH Test p-value: {results['arch_pvalue']:.4f}")
    print(f"  - Variance Stable: {'✅ YES' if results['is_stable'] else '❌ NO'}")
    
    return results

# Example usage
def validate_log_transformation(raw_prices):
    """
    Validate that log transformation stabilizes variance.
    """
    # Calculate log returns
    log_returns = np.log(raw_prices / raw_prices.shift(1))
    
    # Test variance stability
    stability_results = test_variance_stability(log_returns)
    
    if stability_results['is_stable']:
        print("✅ Log transformation successfully stabilized variance")
        return log_returns
    else:
        print("⚠️  Variance may not be fully stabilized. Consider additional transformations.")
        return log_returns
```

##### Practical Data Preparation and Variance Stabilization Workflow

This section describes the practical workflow for preparing and normalizing financial time series data, as implemented in the research Jupyter notebook.

##### Step 1: Data Preparation – Stock Selection

- **Goal:** Focus on stocks with the most complete data.
- **Method:**
  1. Count the number of records for each stock symbol:
     ```python
     symbol_counts = pd.DataFrame(original_df['symbol'].value_counts())
     ```
  2. Select stocks with at least 80% of the maximum record count:
     ```python
     high = symbol_counts['count'].head(1).values
     high_percent = high[0] * 0.80
     # Filter symbols as needed
     ```

##### Step 2: Normalization

- **Goal:** Stabilize variance and prepare features for modeling.
- **Method:**
  1. For each symbol, compute:
     - `log_close`: Natural log of the close price.
     - `log_return`: Difference of log_close (i.e., log returns).
     - `z_scores`: Expanding window z-score of log returns.
     ```python
     gru_result_df['log_close'] = gru_result_df.groupby('symbol')['close'].transform(lambda x: np.log(x))
     gru_result_df['log_return'] = gru_result_df.groupby('symbol')['log_close'].diff()
     gru_result_df['z_scores'] = gru_result_df.groupby('symbol')['log_return'].transform(
         lambda x: (x - x.expanding().mean()) / x.expanding().std()
     )
     ```
  2. Remove rows with NaN in `log_return` or `z_scores`:
     ```python
     gru_result_df = gru_result_df.dropna(subset=['log_return'])
     gru_result_df = gru_result_df.dropna(subset=['z_scores'])
     ```

##### Step 3: Variance Stability Testing and Filtering

- **Goal:** Ensure that variance stabilization is effective for each stock.
- **Method:**
  1. For each symbol, apply:
     - **Rolling Standard Deviation:** Should be flat/stable after transformation.
     - **ARCH Test:** Use `het_arch` from `statsmodels`; require p-value > 0.05 for stability.
     ```python
     from statsmodels.stats.diagnostic import het_arch
     for symbol in symbols:
         symbol_data = gru_result_df[gru_result_df['symbol'] == symbol]
         _, pvalue, *_ = het_arch(symbol_data['z_scores'].dropna(), nlags=5)
         if pvalue > 0.05:
             # Stock passes variance stability test
         else:
             # Stock fails, consider removing
     ```
  2. Remove stocks that do not meet the variance stability criteria.

---

**Note:**  
This workflow ensures that only stocks with sufficient, stable, and well-normalized data are used for downstream modeling (e.g., GRU, GARCH). The approach is fully aligned with best practices for financial time series preprocessing.

---

#### Feature Storage and Database Design

To maintain data integrity and performance, computed features are stored in a separate table rather than modifying the original historical data.

##### Database Schema

```sql
-- Table for storing computed features
CREATE TABLE market_data_features (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- Core features
    log_close DECIMAL(15,6),
    log_return DECIMAL(15,6),
    z_score DECIMAL(15,6),
    
    -- Additional computed features
    rolling_std DECIMAL(15,6),
    rolling_mean DECIMAL(15,6),
    volatility_annualized DECIMAL(15,6),
    
    -- Metadata
    feature_date DATE NOT NULL,
    computation_method VARCHAR(50) DEFAULT 'expanding_window',
    data_source VARCHAR(20) DEFAULT 'market_data_historical',
    
    -- Tracking
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints and indexes
    UNIQUE(symbol, timestamp),
    CONSTRAINT fk_symbol FOREIGN KEY (symbol) REFERENCES symbols(symbol)
);

-- Indexes for performance
CREATE INDEX idx_features_symbol_timestamp ON market_data_features(symbol, timestamp);
CREATE INDEX idx_features_date ON market_data_features(feature_date);
CREATE INDEX idx_features_symbol_date ON market_data_features(symbol, feature_date);

-- Table for variance stability tracking
CREATE TABLE variance_stability_tracking (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    test_date DATE NOT NULL,
    
    -- Test metrics
    record_count INTEGER,
    arch_test_pvalue DECIMAL(10,6),
    rolling_std_cv DECIMAL(10,6),  -- Coefficient of variation
    ljung_box_pvalue DECIMAL(10,6),
    
    -- Results
    is_stable BOOLEAN NOT NULL,
    filter_reason TEXT,  -- 'arch_test_failed', 'insufficient_data', 'high_volatility'
    
    -- Test parameters
    test_window INTEGER DEFAULT 30,
    arch_lags INTEGER DEFAULT 5,
    
    -- Tracking
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(symbol, test_date),
    CONSTRAINT fk_stability_symbol FOREIGN KEY (symbol) REFERENCES symbols(symbol)
);

-- Indexes for variance stability
CREATE INDEX idx_stability_symbol_date ON variance_stability_tracking(symbol, test_date);
CREATE INDEX idx_stability_date_stable ON variance_stability_tracking(test_date, is_stable);
```

##### Feature Computation Strategy

**Daily Workflow:**
1. **Check Existing Features:** Query `market_data_features` for today's symbols
2. **Compute Missing Features:** Generate features for symbols without data
3. **Variance Stability Test:** Check stability and update `variance_stability_tracking`
4. **Use Stable Features:** Filter to only stable symbols for modeling

**Performance Optimizations:**
- **Caching:** Cache frequently used features in memory during trading day
- **Batch Processing:** Compute features in batches for multiple symbols
- **Incremental Updates:** Only compute features for new data points
- **Partitioning:** Consider partitioning by date for large datasets

**Feature Computation Methods:**

```python
def compute_features_for_symbol(symbol: str, price_data: pd.DataFrame) -> pd.DataFrame:
    """
    Compute all features for a single symbol.
    
    Args:
        symbol: Stock symbol
        price_data: DataFrame with 'close' column
        
    Returns:
        DataFrame with computed features
    """
    features = price_data.copy()
    
    # Core features
    features['log_close'] = np.log(features['close'])
    features['log_return'] = features['log_close'].diff()
    
    # Z-score with expanding window
    features['z_score'] = features.groupby('symbol')['log_return'].transform(
        lambda x: (x - x.expanding().mean()) / x.expanding().std()
    )
    
    # Rolling statistics
    features['rolling_std'] = features['log_return'].rolling(30).std()
    features['rolling_mean'] = features['log_return'].rolling(30).mean()
    
    # Annualized volatility
    features['volatility_annualized'] = features['rolling_std'] * np.sqrt(252)
    
    return features
```

##### Variance Stability Testing Strategy

**Testing Criteria:**
1. **ARCH Test:** p-value > 0.05 (no significant heteroscedasticity)
2. **Rolling Std CV:** Coefficient of variation < 0.5 (stable variance)
3. **Ljung-Box Test:** p-value > 0.05 (no significant autocorrelation)

**Filtering Logic:**
```python
def test_variance_stability(symbol: str, feature_data: pd.DataFrame) -> dict:
    """
    Test variance stability for a symbol.
    
    Returns:
        Dict with test results and stability status
    """
    # Get z_scores for testing
    z_scores = feature_data['z_score'].dropna()
    
    if len(z_scores) < 30:
        return {
            'is_stable': False,
            'filter_reason': 'insufficient_data',
            'record_count': len(z_scores)
        }
    
    # ARCH test
    arch_stat, arch_pvalue = het_arch(z_scores, nlags=5)
    
    # Rolling std coefficient of variation
    rolling_std = z_scores.rolling(30).std()
    rolling_std_cv = rolling_std.std() / rolling_std.mean()
    
    # Ljung-Box test
    lb_stat, lb_pvalue = acorr_ljungbox(z_scores, lags=10, return_df=True)
    
    # Determine stability
    is_stable = (
        arch_pvalue > 0.05 and 
        rolling_std_cv < 0.5 and 
        all(p > 0.05 for p in lb_pvalue)
    )
    
    filter_reason = None
    if not is_stable:
        if arch_pvalue <= 0.05:
            filter_reason = 'arch_test_failed'
        elif rolling_std_cv >= 0.5:
            filter_reason = 'high_volatility'
        else:
            filter_reason = 'autocorrelation_detected'
    
    return {
        'is_stable': is_stable,
        'filter_reason': filter_reason,
        'arch_test_pvalue': arch_pvalue,
        'rolling_std_cv': rolling_std_cv,
        'ljung_box_pvalue': lb_pvalue.tolist(),
        'record_count': len(z_scores)
    }
```

##### Data Access Patterns

**For Modeling:**
```sql
-- Get stable features for modeling
SELECT f.* 
FROM market_data_features f
JOIN variance_stability_tracking v ON f.symbol = v.symbol 
    AND f.feature_date = v.test_date
WHERE v.is_stable = true 
    AND f.feature_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY f.symbol, f.timestamp;
```

**For Monitoring:**
```sql
-- Check variance stability status
SELECT symbol, test_date, is_stable, filter_reason, arch_test_pvalue
FROM variance_stability_tracking 
WHERE test_date = CURRENT_DATE
ORDER BY is_stable DESC, symbol;
```

---

##### Key Considerations

1. **No Look-Ahead Bias**: Always use expanding windows for z-score calculation to avoid using future information
2. **Minimum Periods**: Use at least 30 periods for stable statistics
3. **Data Quality**: Handle missing values and outliers appropriately
4. **Stationarity**: Ensure spread series is stationary before applying z-score normalization
5. **Beta Estimation**: Use proper methods (OLS, Kalman filter) for beta estimation in spread construction
6. **Variance Validation**: Always test for variance stability after transformations

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

## Variance Stability Testing

Variance stability testing is a critical step in financial time series analysis to ensure that the statistical properties of the data are consistent over time. This is especially important for pairs trading strategies where we rely on stable relationships between assets.

### Theory and Background

**Why Variance Stability Matters:**
- **Pairs Trading Assumption**: Pairs trading assumes that the spread between two correlated assets will revert to its mean. This assumption breaks down if the variance of the spread is not stable.
- **Model Performance**: Machine learning models trained on data with unstable variance may perform poorly in production.
- **Risk Management**: Unstable variance can lead to unexpected losses and poor risk estimates.

**Statistical Tests Used:**
1. **ARCH Test (Autoregressive Conditional Heteroskedasticity)**: Tests for heteroskedasticity in the residuals
2. **Rolling Standard Deviation Coefficient of Variation**: Measures the stability of volatility over time
3. **Ljung-Box Test**: Tests for autocorrelation in the residuals

### Configuration

Variance stability criteria are configurable via `config/config.yaml`:

```yaml
variance_stability:
  # Original strict criteria (commented out)
  # arch_test_pvalue_threshold: 0.05
  # rolling_std_cv_threshold: 0.5
  # ljung_box_pvalue_threshold: 0.05
  
  # Current relaxed criteria (for testing/development)
  arch_test_pvalue_threshold: 1e-100  # Essentially ignore ARCH test
  rolling_std_cv_threshold: 2.0       # Allow higher volatility
  ljung_box_pvalue_threshold: 0.001   # More lenient autocorrelation test
  
  # Test parameters
  test_window: 30
  arch_lags: 5
  ljung_box_lags: 10
```

**Thresholds Explained:**
- **ARCH p-value**: Must be > threshold (higher = more lenient)
- **Rolling std CV**: Must be < threshold (lower = more strict)
- **Ljung-Box p-value**: Must be > threshold (higher = more lenient)

### Practical Workflow

**When to Use Log Close vs Log Returns:**
- **Log Close**: Use when you want to model the price level directly
- **Log Returns**: Use for variance stability testing and most ML applications (recommended)

**Z-Score Normalization:**
- Computed using expanding or rolling windows
- Helps stabilize variance and make data more suitable for ML models

**Variance Stability Testing Process:**
1. Compute log returns from price data
2. Calculate z-scores using expanding/rolling windows
3. Apply statistical tests (ARCH, rolling std CV, Ljung-Box)
4. Filter symbols based on stability criteria
5. Use only stable symbols for pairs trading

### Implementation Details

The variance stability testing is implemented in `src/utils/data_preprocessing_utils.py` and integrates with the training pipeline in `src/ml/train_gru_models.py`.

**Key Features:**
- Configurable thresholds via config file
- Robust error handling for edge cases
- Database storage of test results
- Integration with MLflow for experiment tracking
- Support for both expanding and rolling window computations

**Usage Example:**
```python
from src.utils.data_preprocessing_utils import DataPreprocessingUtils

utils = DataPreprocessingUtils()
stable_features, stable_symbols, test_results = utils.test_variance_stability_for_multiple_symbols(
    feature_data, symbols, test_window=30, arch_lags=5
)
``` 