# Next Steps: GARCH-GRU Pairs Trading Implementation

## Overview
This document tracks the implementation progress for the GARCH-GRU Pairs Trading System with MLflow integration. The system is designed for multi-sector support (technology, healthcare, financial), but currently only the technology sector is active.

## Current Status Summary
- **MLflow Foundation**: ✅ COMPLETED (Week 1)
- **Existing GARCH-GRU Implementation**: ✅ DISCOVERED (Working with F1=0.7445)
- **PyTorch Migration**: 🔄 IN PROGRESS (Week 2-3)
- **MLflow Integration**: ⏳ PENDING (Week 4-5)
- **Production Integration**: ⏳ PENDING (Week 6-7)
- **Database Extensions**: ⏳ PENDING (Week 8)

## Phase 1: MLflow Foundation ✅ COMPLETED

### ✅ Step 1: Dependencies Installation
- **Date**: [Previous]
- **Status**: COMPLETED
- **Details**: 
  - Updated `config/requirements.txt` to replace TensorFlow with PyTorch 2.1.0
  - Added MLflow 2.8.1 and related dependencies
  - All dependencies installed in existing conda environment

### ✅ Step 2: Configuration Setup
- **Date**: [Previous]
- **Status**: COMPLETED
- **Details**:
  - Updated `config/config.yaml` with MLflow configuration
  - Updated `config/env.example` with MLflow environment variables
  - MLflow artifacts directory created at `./mlruns`

### ✅ Step 3: Database Setup
- **Date**: [Previous]
- **Status**: COMPLETED
- **Details**:
  - Created `mlflow_db` database in PostgreSQL
  - Used separate database approach for clean architecture
  - Database connection: `postgresql://postgres:nishant@localhost/mlflow_db`

### ✅ Step 4: MLflow Server Launch
- **Date**: [Previous]
- **Status**: COMPLETED
- **Details**:
  - Started MLflow server with PostgreSQL backend
  - Server running on: http://localhost:5000
  - Web UI accessible and functional

### ✅ Step 5: MLflow Manager Implementation
- **Date**: [Previous]
- **Status**: COMPLETED
- **Details**:
  - Created `src/mlflow_manager.py` with comprehensive functionality
  - Implemented experiment tracking and model registry management
  - Added MLflow configuration manager in `src/ml/config.py`
  - Basic MLflow integration tests implemented

## Phase 2: PyTorch Migration and Refactoring 🔄 IN PROGRESS

### ✅ Step 1: Existing Implementation Analysis
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

### 🔄 Step 2: PyTorch GRU Migration and Refactoring
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

### 🔄 Step 3: GARCH Model Refactoring and Modularization
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

### 🔄 Step 4: Feature Engineering Refactoring and Extraction
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

## Phase 3: MLflow Integration and Strategy Refactoring ⏳ PENDING

### 🔄 Step 1: GARCH-GRU Strategy PyTorch Refactoring
- **Date**: [Week 4]
- **Status**: PLANNED
- **Priority**: HIGH
- **File**: `src/ml/garch_gru_strategy.py`
- **Components**:
  - Refactor existing `GARCHGRUPipeline` class into `GARCHGRUStrategy`
  - Convert to PyTorch-based strategy implementation
  - Extract signal generation logic from existing implementation
  - Signal combination algorithm already implemented
  - Risk management integration
  - Position sizing based on volatility
  - Create clean, modular PyTorch strategy classes
- **Dependencies**: Previous phase components (PyTorch modules)
- **Estimated Time**: 3-4 days (PyTorch refactoring + MLflow integration)
- **Success Criteria**: Same signal generation logic as existing implementation
- **Refactoring Goals**: PyTorch-native strategy, MLflow integration ready

### 🔄 Step 2: PyTorch MLflow Training Pipeline Integration
- **Date**: [Week 4-5]
- **Status**: PLANNED
- **Priority**: HIGH
- **File**: `src/ml/trainer.py`
- **Components**:
  - Create `MLflowGARCHGRUTrainer` class for PyTorch models
  - Convert existing TensorFlow training to PyTorch training loops
  - Automated training workflows (Optuna already implemented)
  - Hyperparameter optimization (already working with F1=0.7445)
  - Model validation and backtesting (already implemented)
  - MLflow integration for PyTorch experiment tracking
  - PyTorch Lightning integration for cleaner training code
- **Dependencies**: Previous phase components, `optuna`, `torch` (existing)
- **Estimated Time**: 3-4 days (PyTorch conversion + MLflow integration)
- **Success Criteria**: MLflow experiments track all PyTorch training runs
- **Refactoring Goals**: PyTorch-native training, MLflow integration, clean code

## Phase 4: Production Integration ⏳ PENDING

### 🔄 Step 1: Periodic Rebaselining Workflows
- **Date**: [Week 6]
- **Status**: PLANNED
- **Priority**: MEDIUM
- **File**: `src/ml/rebaselining.py`
- **Components**:
  - Prefect workflows for automated retraining
  - Model performance monitoring (F1=0.7445 baseline)
  - Automated model promotion/demotion
  - A/B testing framework
  - Performance degradation alerts
- **Dependencies**: Previous phase components, `prefect`
- **Estimated Time**: 3-4 days
- **Success Criteria**: Automated retraining maintains F1 ≥ 0.70

### 🔄 Step 2: Model Serving and Integration
- **Date**: [Week 6-7]
- **Status**: PLANNED
- **Priority**: MEDIUM
- **File**: `src/ml/model_serving.py`
- **Components**:
  - `MLflowModelServing` class (as outlined in document)
  - Production model loading
  - Real-time prediction serving
  - Model version management
  - Performance monitoring
- **Dependencies**: Previous phase components
- **Estimated Time**: 2-3 days
- **Success Criteria**: Real-time predictions with < 100ms latency

## Phase 5: Database Extensions ⏳ PENDING

### 🔄 Step 1: MLflow Integration Tables
- **Date**: [Week 8]
- **Status**: PLANNED
- **Priority**: LOW
- **File**: `src/database/migrations/010_mlflow_integration/`
- **Components**:
  - `model_registry` table
  - `model_performance_history` table
  - `trading_signals` table with model attribution
  - `pairs_data` table for enhanced analytics
- **Dependencies**: Previous phase components
- **Estimated Time**: 1-2 days
- **Success Criteria**: Database schema supports MLflow model tracking

### 🔄 Step 2: Data Pipeline Enhancements
- **Date**: [Week 8]
- **Status**: PLANNED
- **Priority**: LOW
- **File**: `src/data/pairs_data_manager.py`
- **Components**:
  - Pairs data collection and storage
  - Real-time data processing
  - Historical data management
  - Data quality monitoring
- **Dependencies**: Previous phase components
- **Estimated Time**: 2-3 days
- **Success Criteria**: Data pipeline supports existing pairs trading data

## Phase 6: Testing and Validation ⏳ PENDING

### 🔄 Step 1: Unit Tests
- **Date**: [Week 3-4]
- **Status**: PLANNED
- **Priority**: MEDIUM
- **Directory**: `test/unit/ml/`
- **Components**:
  - GARCH model tests (validate existing performance)
  - GRU model tests (validate PyTorch migration)
  - Strategy tests (validate refactored components)
  - Feature engineering tests (validate extracted pipeline)
- **Dependencies**: All previous phases
- **Estimated Time**: 2-3 days
- **Success Criteria**: All tests pass with F1 ≥ 0.7445

### 🔄 Step 2: Integration Tests
- **Date**: [Week 5-6]
- **Status**: PLANNED
- **Priority**: MEDIUM
- **Directory**: `test/integration/ml/`
- **Components**:
  - End-to-end training pipeline tests
  - Model serving tests
  - Rebaselining workflow tests
- **Dependencies**: All previous phases
- **Estimated Time**: 2-3 days
- **Success Criteria**: Full pipeline maintains performance

### 🔄 Step 3: Backtesting Framework
- **Date**: [Week 6-7]
- **Status**: PLANNED
- **Priority**: MEDIUM
- **File**: `src/ml/backtesting.py`
- **Components**:
  - Historical performance simulation
  - Risk metrics calculation
  - Performance comparison tools
  - Strategy validation
- **Dependencies**: All previous phases
- **Estimated Time**: 3-4 days
- **Success Criteria**: Backtesting validates F1=0.7445 performance

## Dependencies and Requirements

### Existing Dependencies (Already Available):
```yaml
# Already in environment from existing implementation
arch: "^6.2.0"           # GARCH modeling (already used)
statsmodels: "^0.14.0"   # Statistical tests (already used)
scikit-learn: "^1.3.0"   # Machine learning utilities (already used)
tensorflow: "^2.10.0"    # GRU neural networks (needs PyTorch migration)
optuna: "^3.2.0"         # Hyperparameter optimization (already used)
matplotlib: "^3.5.0"     # Visualization (already used)
pandas: "^1.5.0"         # Data manipulation (already used)
numpy: "^1.21.0"         # Numerical computing (already used)
```

### New Dependencies Needed:
```yaml
# Add to config/requirements.txt for PyTorch migration
torch: "^2.1.0"          # Replace TensorFlow with PyTorch
pytorch-lightning: "^2.0.0"  # For cleaner training code
mlflow-pytorch: "^2.8.1"     # For PyTorch model logging
```

### Configuration Updates Needed:
- Add GARCH-GRU specific configuration to `config/config.yaml`
- Update MLflow configuration for model registry
- Add performance thresholds and trading parameters

## Success Metrics

### Model Performance Targets:
- F1 Score ≥ 0.7445 (already achieved, maintain this level)
- Sharpe Ratio > 1.0 (to be validated)
- Maximum Drawdown < 10% (to be validated)
- Model update success rate > 95%

### Operational Metrics:
- System uptime > 99.5%
- Model inference latency < 100ms
- Training pipeline reliability > 99.9%
- PyTorch migration success: F1 score maintained
- MLflow integration: All experiments tracked

## Risk Assessment and Mitigation

### Technical Risks:
1. **PyTorch Migration Performance Loss**: Mitigation: Maintain exact same hyperparameters and architecture
2. **GARCH Model Convergence**: Already working, implement robust error handling
3. **GRU Training Stability**: Already working with early stopping, maintain same approach
4. **Data Quality Issues**: Implement comprehensive data validation
5. **Model Performance Degradation**: Set up automated monitoring with F1=0.7445 baseline

### Operational Risks:
1. **Model Deployment Failures**: Implement rollback mechanisms
2. **Performance Bottlenecks**: Monitor and optimize inference latency
3. **Data Pipeline Failures**: Implement redundancy and error recovery
4. **MLflow Integration Issues**: Test thoroughly before production deployment

## Implementation Timeline

### Week 2-3: PyTorch Migration and Refactoring
- **Week 2**: PyTorch GRU migration and refactoring (maintain F1=0.7445)
- **Week 3**: GARCH model PyTorch refactoring and modularization
- **Week 3**: Feature engineering PyTorch extraction and refactoring
- **Week 3**: Basic unit tests for PyTorch refactored components
- **Success Criteria**: All PyTorch components maintain existing performance

### Week 4-5: PyTorch MLflow Integration
- **Week 4**: GARCH-GRU strategy PyTorch refactoring with MLflow
- **Week 4-5**: PyTorch model training pipeline with MLflow integration
- **Week 5**: PyTorch hyperparameter optimization with MLflow tracking
- **Week 5**: PyTorch strategy tests with MLflow experiments
- **Success Criteria**: PyTorch + MLflow tracks all experiments and maintains performance

### Week 6-7: Production Integration
- **Week 6**: PyTorch periodic rebaselining workflows
- **Week 6-7**: PyTorch model serving implementation
- **Week 7**: PyTorch performance monitoring and integration tests
- **Success Criteria**: Production-ready PyTorch system with automated retraining

### Week 8: Database and Final Integration
- **Week 8**: Database schema extensions for PyTorch models
- **Week 8**: PyTorch data pipeline enhancements
- **Week 8**: End-to-end PyTorch testing and documentation updates
- **Success Criteria**: Complete enterprise-ready PyTorch system

## Architecture Decisions Made
- **PyTorch over TensorFlow**: Better Windows compatibility (migration needed)
- **PyTorch Lightning**: For cleaner training code and MLflow integration
- **Separate `mlflow_db`**: Clean architecture and industry standard
- **Multi-sector ready**: Future-proof design starting with technology only
- **MLflow built-in tables only**: Start simple, add custom tables later
- **MLflow server with PostgreSQL**: Production-ready with web UI
- **GARCH(1,1) model**: Standard choice for volatility forecasting (already implemented)
- **GRU for sequence modeling**: Better for mean reversion prediction than LSTM (already implemented)
- **Optuna for hyperparameter optimization**: Already achieving F1=0.7445
- **Refactoring over rebuilding**: Leverage existing working implementation
- **Modular PyTorch design**: Clean separation of concerns for maintainability

## Configuration Summary
```yaml
# MLflow Configuration
mlflow:
  tracking_uri: "http://localhost:5000"
  registry_uri: "http://localhost:5000"
  experiment_name: "pairs_trading"
  backend_store_uri: "postgresql://postgres:nishant@localhost/mlflow_db"
  artifact_root: "file:./mlruns"

# GARCH-GRU Configuration (from existing implementation)
garch_gru_pairs:
  symbols:
    technology:
      - ["AAPL", "MSFT"]
      - ["GOOGL", "META"]
      - ["NVDA", "AMD"]
  garch_model:
    p: 1
    q: 1
    model_type: "GARCH"
  gru_model:
    sequence_length: 10          # Optimal from Optuna
    gru_units: 64               # Optimal from Optuna
    dropout_rate: 0.255         # Optimal from Optuna
    learning_rate: 0.0003       # Optimal from Optuna
    batch_size: 32              # Optimal from Optuna
  performance:
    best_f1_score: 0.7445       # Already achieved
    target_f1_score: 0.70       # Target exceeded
```

## Files Created/Modified
- `config/requirements.txt`: Updated with PyTorch and MLflow dependencies
- `config/config.yaml`: Added MLflow configuration
- `config/env.example`: Added MLflow environment variables
- `scripts/create_mlflow_db.sql`: Database creation script
- `src/mlflow_manager.py`: MLflow management utilities
- `src/ml/config.py`: MLflow configuration manager
- `docs/architecture-decisions.md`: Decision log
- `docs/next-steps-implementation.md`: This progress document

## Verification Checklist
- [x] MLflow server starts without errors
- [x] Web UI accessible at http://localhost:5000
- [x] Database connection working
- [x] Artifacts directory created
- [x] Dependencies installed correctly
- [x] Configuration files updated
- [x] MLflow manager implemented and tested
- [x] Existing GARCH-GRU implementation discovered (F1=0.7445)
- [x] Optimal hyperparameters identified via Optuna
- [ ] PyTorch GRU migration (maintain F1=0.7445)
- [ ] GARCH model modularization
- [ ] Feature engineering extraction
- [ ] Strategy refactoring with MLflow
- [ ] Training pipeline MLflow integration
- [ ] Production integration
- [ ] Database extensions
- [ ] Comprehensive testing

## Notes
- Server running in background mode
- Using simplified MLflow server command (no explicit host/port)
- Database `mlflow_db` successfully created and connected
- **EXISTING IMPLEMENTATION FOUND**: Complete GARCH-GRU pipeline already working
- **PERFORMANCE EXCEEDS TARGETS**: F1=0.7445 > 0.70 target
- **OPTIMAL HYPERPARAMETERS IDENTIFIED**: Via Optuna optimization
- **PYTORCH MIGRATION STRATEGY**: Refactor existing TensorFlow implementation to PyTorch
- **REFACTORING APPROACH**: Modular, clean PyTorch code with MLflow integration
- **PYTORCH LIGHTNING**: Use for cleaner training code and better MLflow integration
- Focus on technology sector first, expand to other sectors later
- Maintain backward compatibility with existing trading system
- **REDUCED IMPLEMENTATION TIME**: From 8 weeks to 4-5 weeks due to existing code
- **PYTORCH NATIVE**: All components will be PyTorch-native for better integration 