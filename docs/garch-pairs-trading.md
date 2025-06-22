# GARCH-Based Pairs Trading Strategy Documentation

## Overview

This document outlines the architecture and implementation strategy for a **GARCH-based pairs trading system** designed for paper trading with two symbols on an hourly basis. The system leverages Generalized Autoregressive Conditional Heteroskedasticity (GARCH) models for volatility forecasting and mean reversion strategies.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WebSocket     │    │   GARCH Pairs   │    │   Execution     │
│   Data (1min)   │───▶│   Strategy      │───▶│   Engine        │
│                 │    │                 │    │                 │
│ • AAPL, MSFT    │    │ • Cointegration │    │ • Order Mgmt    │
│ • OHLCV         │    │ • GARCH Model   │    │ • Position Mgmt │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Hourly        │    │   Portfolio     │
                       │   Decision      │    │   Manager       │
                       │   Engine        │    │                 │
                       │                 │    │ • Account Info  │
                       │ • Signal Gen    │    │ • Positions     │
                       │ • Risk Mgmt     │    │ • Performance   │
                       └─────────────────┘    └─────────────────┘
```

### Core Components

#### 1. Data Layer
- **Real-time Data**: WebSocket feeds for AAPL and MSFT (1-minute bars)
- **Historical Data**: Hourly data for GARCH model training
- **Feature Engineering**: Returns, volatility, spread calculations

#### 2. GARCH Pairs Strategy Engine
- **Cointegration Testing**: Engle-Granger or Johansen test
- **GARCH Model**: GARCH(1,1) for volatility forecasting
- **Spread Analysis**: Mean reversion signals based on GARCH volatility

#### 3. Risk Management
- **Position Sizing**: Based on GARCH volatility forecasts
- **Stop Loss**: Dynamic based on GARCH volatility bands
- **Correlation Monitoring**: Real-time correlation tracking

#### 4. Execution Engine
- **Order Management**: Alpaca paper trading integration
- **Position Tracking**: Long/short pair positions
- **Performance Monitoring**: P&L, Sharpe ratio, drawdown

## Detailed Component Design

### A. Data Processing Pipeline

```pseudo
CLASS DataProcessor:
    METHOD process_realtime_data(symbol1, symbol2):
        // Get 1-minute WebSocket data
        data1 = get_websocket_data(symbol1)
        data2 = get_websocket_data(symbol2)
        
        // Calculate returns
        returns1 = calculate_returns(data1.close)
        returns2 = calculate_returns(data2.close)
        
        // Calculate spread
        spread = calculate_spread(returns1, returns2)
        
        // Store in Redis for hourly aggregation
        store_in_redis(spread, timestamp)
        
    METHOD aggregate_hourly_data():
        // Aggregate 1-minute data to hourly
        hourly_data = aggregate_from_redis()
        
        // Calculate hourly features
        hourly_returns1 = calculate_hourly_returns(symbol1)
        hourly_returns2 = calculate_hourly_returns(symbol2)
        hourly_spread = calculate_hourly_spread()
        
        // Store in PostgreSQL
        store_in_database(hourly_data)
```

### B. GARCH Pairs Strategy Engine

```pseudo
CLASS GARCHPairsStrategy:
    PROPERTIES:
        symbol1, symbol2
        garch_model
        cointegration_params
        volatility_threshold
        mean_reversion_threshold
        
    METHOD initialize_strategy():
        // Load historical data (last 30 days)
        historical_data = load_historical_data(30_days)
        
        // Test for cointegration
        cointegration_result = test_cointegration(
            historical_data.symbol1, 
            historical_data.symbol2
        )
        
        IF cointegration_result.is_cointegrated:
            // Fit GARCH model on spread
            spread = calculate_spread(historical_data)
            garch_model = fit_garch_model(spread)
            
            // Calculate mean and volatility thresholds
            mean_threshold = calculate_mean_threshold(spread)
            volatility_threshold = calculate_volatility_threshold(garch_model)
            
            RETURN True
        ELSE:
            RETURN False
            
    METHOD generate_signals(hourly_data):
        // Get latest spread
        current_spread = calculate_spread(hourly_data)
        
        // Forecast volatility using GARCH
        volatility_forecast = garch_model.forecast_volatility()
        
        // Calculate z-score of spread
        z_score = calculate_z_score(current_spread, historical_spread)
        
        // Generate trading signals
        IF z_score > mean_reversion_threshold AND volatility_forecast < volatility_threshold:
            // Short spread (long symbol1, short symbol2)
            RETURN Signal(type="SHORT_SPREAD", confidence=calculate_confidence())
            
        ELSE IF z_score < -mean_reversion_threshold AND volatility_forecast < volatility_threshold:
            // Long spread (short symbol1, long symbol2)
            RETURN Signal(type="LONG_SPREAD", confidence=calculate_confidence())
            
        ELSE:
            // Close positions if volatility is high
            IF volatility_forecast > volatility_threshold:
                RETURN Signal(type="CLOSE_POSITIONS", confidence=1.0)
                
        RETURN Signal(type="HOLD", confidence=0.0)
        
    METHOD calculate_position_size(signal, portfolio_value):
        // Get current volatility forecast
        volatility = garch_model.forecast_volatility()
        
        // Calculate Kelly criterion position size
        kelly_fraction = calculate_kelly_criterion(signal)
        
        // Apply volatility scaling
        position_size = kelly_fraction * (1 / volatility) * portfolio_value
        
        // Apply risk limits
        max_position = portfolio_value * 0.1  // 10% max position
        
        RETURN min(position_size, max_position)
```

### C. Risk Management Engine

```pseudo
CLASS RiskManager:
    PROPERTIES:
        max_position_size
        max_correlation
        stop_loss_pct
        volatility_multiplier
        
    METHOD validate_trade(signal, current_positions):
        // Check position limits
        IF total_positions > max_positions:
            RETURN False
            
        // Check correlation
        correlation = calculate_correlation(symbol1, symbol2)
        IF correlation > max_correlation:
            RETURN False
            
        // Check volatility limits
        volatility = get_current_volatility()
        IF volatility > volatility_threshold:
            RETURN False
            
        RETURN True
        
    METHOD calculate_stop_loss(signal, entry_price):
        // Dynamic stop loss based on GARCH volatility
        volatility = garch_model.forecast_volatility()
        
        // Stop loss = volatility * multiplier
        stop_loss_distance = volatility * volatility_multiplier
        
        IF signal.type == "LONG_SPREAD":
            RETURN entry_price - stop_loss_distance
        ELSE:
            RETURN entry_price + stop_loss_distance
            
    METHOD monitor_positions(current_positions):
        FOR position IN current_positions:
            // Check stop loss
            IF position.pnl < -stop_loss_pct:
                close_position(position)
                
            // Check correlation drift
            correlation = calculate_correlation(symbol1, symbol2)
            IF correlation < min_correlation:
                close_position(position)
```

### D. Execution Engine

```pseudo
CLASS ExecutionEngine:
    PROPERTIES:
        trading_client
        portfolio_manager
        risk_manager
        
    METHOD execute_pairs_trade(signal):
        // Validate trade with risk manager
        IF NOT risk_manager.validate_trade(signal):
            RETURN None
            
        // Calculate position sizes
        position_size = strategy.calculate_position_size(signal)
        
        // Execute pair orders
        IF signal.type == "LONG_SPREAD":
            // Short symbol1, Long symbol2
            order1 = place_order(symbol1, "SELL", position_size)
            order2 = place_order(symbol2, "BUY", position_size)
            
        ELSE IF signal.type == "SHORT_SPREAD":
            // Long symbol1, Short symbol2
            order1 = place_order(symbol1, "BUY", position_size)
            order2 = place_order(symbol2, "SELL", position_size)
            
        // Log trade
        log_trade(signal, order1, order2)
        
        RETURN [order1, order2]
        
    METHOD close_pairs_position(position):
        // Close both legs of the pair
        close_order1 = place_order(position.symbol1, "CLOSE", position.size)
        close_order2 = place_order(position.symbol2, "CLOSE", position.size)
        
        // Calculate P&L
        pnl = calculate_pnl(position)
        
        // Log trade
        log_closed_trade(position, pnl)
        
        RETURN pnl
```

### E. Main Trading Flow

```pseudo
CLASS GARCHPairsTradingSystem:
    PROPERTIES:
        data_processor
        strategy_engine
        risk_manager
        execution_engine
        portfolio_manager
        
    METHOD initialize_system():
        // Initialize all components
        data_processor = DataProcessor()
        strategy_engine = GARCHPairsStrategy()
        risk_manager = RiskManager()
        execution_engine = ExecutionEngine()
        
        // Initialize strategy
        IF NOT strategy_engine.initialize_strategy():
            RAISE Exception("Strategy initialization failed")
            
    METHOD hourly_trading_cycle():
        // 1. Get latest hourly data
        hourly_data = data_processor.aggregate_hourly_data()
        
        // 2. Generate trading signals
        signals = strategy_engine.generate_signals(hourly_data)
        
        // 3. Execute trades
        FOR signal IN signals:
            IF signal.type != "HOLD":
                execution_engine.execute_pairs_trade(signal)
                
        // 4. Monitor existing positions
        current_positions = portfolio_manager.get_positions()
        risk_manager.monitor_positions(current_positions)
        
        // 5. Update performance metrics
        update_performance_metrics()
        
    METHOD run_continuous():
        WHILE market_is_open():
            // Process real-time data
            data_processor.process_realtime_data()
            
            // Check if it's time for hourly decision
            IF is_hourly_decision_time():
                hourly_trading_cycle()
                
            // Sleep for 1 minute
            sleep(60_seconds)
```

## Database Schema

### Pairs Trading Tables

```sql
-- Pairs data storage
CREATE TABLE pairs_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    symbol1 VARCHAR(10) NOT NULL,
    symbol2 VARCHAR(10) NOT NULL,
    price1 DECIMAL(10,4),
    price2 DECIMAL(10,4),
    return1 DECIMAL(10,6),
    return2 DECIMAL(10,6),
    spread DECIMAL(10,6),
    correlation DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GARCH model parameters and forecasts
CREATE TABLE garch_models (
    id SERIAL PRIMARY KEY,
    symbol_pair VARCHAR(20) NOT NULL,
    model_params JSONB,
    volatility_forecast DECIMAL(10,6),
    mean_threshold DECIMAL(10,6),
    volatility_threshold DECIMAL(10,6),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trading signals
CREATE TABLE pairs_signals (
    id SERIAL PRIMARY KEY,
    signal_type VARCHAR(20) NOT NULL, -- 'LONG_SPREAD', 'SHORT_SPREAD', 'CLOSE'
    symbol1 VARCHAR(10) NOT NULL,
    symbol2 VARCHAR(10) NOT NULL,
    spread_value DECIMAL(10,6),
    z_score DECIMAL(10,6),
    volatility_forecast DECIMAL(10,6),
    confidence DECIMAL(5,4),
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pairs positions tracking
CREATE TABLE pairs_positions (
    id SERIAL PRIMARY KEY,
    signal_id INTEGER REFERENCES pairs_signals(id),
    symbol1_order_id VARCHAR(50),
    symbol2_order_id VARCHAR(50),
    position_size DECIMAL(10,2),
    entry_spread DECIMAL(10,6),
    current_pnl DECIMAL(10,2),
    status VARCHAR(20), -- 'OPEN', 'CLOSED'
    opened_at TIMESTAMP,
    closed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Configuration Parameters

### GARCH Pairs Trading Configuration

```yaml
# GARCH Pairs Trading Configuration
garch_pairs:
  symbols:
    - AAPL
    - MSFT
  
  # GARCH Model Parameters
  garch_model:
    p: 1  # AR order
    q: 1  # MA order
    model_type: "GARCH"  # GARCH, EGARCH, GJR-GARCH
    
  # Trading Parameters
  trading:
    mean_reversion_threshold: 2.0  # Z-score threshold
    volatility_threshold: 0.02     # Max volatility for trading
    position_size_pct: 0.1         # Max 10% of portfolio
    stop_loss_pct: 0.02            # 2% stop loss
    
  # Risk Management
  risk:
    max_correlation: 0.8           # Max correlation between symbols
    min_correlation: 0.3           # Min correlation for pairs trading
    max_positions: 3               # Max concurrent positions
    volatility_multiplier: 2.0     # Stop loss volatility multiplier
    
  # Data Parameters
  data:
    lookback_days: 30              # Historical data for model fitting
    cointegration_test: "engle_granger"  # or "johansen"
    confidence_level: 0.95         # Statistical confidence level
```

## Implementation Strategy

### Phase 1: Foundation (Week 1)
1. **Create trading modules** (strategy, risk, execution)
2. **Add database tables** for signals and orders
3. **Enhance data collection** with technical indicators

### Phase 2: Strategy Development (Week 2)
1. **Implement GARCH model** in the strategy engine
2. **Add cointegration testing** and spread calculation
3. **Create signal generation** logic

### Phase 3: Execution & Testing (Week 3)
1. **Build execution engine** with Alpaca integration
2. **Add position management** and stop-loss handling
3. **Create testing framework** for strategy backtesting

### Phase 4: Integration & Monitoring (Week 4)
1. **Integrate with existing Prefect flows**
2. **Add monitoring and alerting**
3. **Create dashboard views** for algo trading

## Key Features

### 1. GARCH Volatility Modeling
- **Volatility Forecasting**: Predicts future volatility using GARCH(1,1) model
- **Volatility Clustering**: Captures periods of high/low volatility
- **Dynamic Thresholds**: Adjusts trading thresholds based on volatility forecasts

### 2. Cointegration Testing
- **Engle-Granger Test**: Tests for cointegration between symbol pairs
- **Johansen Test**: Alternative cointegration test for multiple variables
- **Spread Calculation**: Computes mean-reverting spread between symbols

### 3. Mean Reversion Strategy
- **Z-Score Signals**: Generates signals based on spread deviation from mean
- **Volatility Filtering**: Only trades when volatility is below threshold
- **Dynamic Position Sizing**: Scales positions based on volatility forecasts

### 4. Risk Management
- **Correlation Monitoring**: Tracks correlation between symbol pairs
- **Dynamic Stop Loss**: Stop losses based on GARCH volatility bands
- **Position Limits**: Maximum position size and concurrent positions

### 5. Paper Trading Integration
- **Alpaca Paper Trading**: Safe testing environment
- **Real-time Execution**: Live order placement and monitoring
- **Performance Tracking**: Comprehensive P&L and risk metrics

## Mathematical Foundation

### GARCH Model
The GARCH(1,1) model is defined as:

```
σ²_t = ω + α₁ε²_{t-1} + β₁σ²_{t-1}
```

Where:
- `σ²_t` is the conditional variance at time t
- `ω` is the constant term
- `α₁` is the ARCH parameter (lagged squared error)
- `β₁` is the GARCH parameter (lagged variance)
- `ε_t` is the error term

### Cointegration
Two time series are cointegrated if there exists a linear combination that is stationary:

```
Y_t = βX_t + ε_t
```

Where `ε_t` is stationary (I(0)).

### Spread Calculation
The spread between two cointegrated series:

```
Spread_t = Y_t - βX_t
```

### Z-Score
The z-score of the spread:

```
Z_t = (Spread_t - μ) / σ
```

Where `μ` and `σ` are the mean and standard deviation of the spread.

## Performance Metrics

### Trading Performance
- **Total Return**: Overall strategy performance
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades

### Risk Metrics
- **Volatility**: Standard deviation of returns
- **VaR**: Value at Risk (95% confidence)
- **Correlation Stability**: Consistency of pair correlation
- **Position Duration**: Average holding period

### Model Performance
- **GARCH Fit**: Model goodness-of-fit statistics
- **Volatility Forecast Accuracy**: Out-of-sample volatility predictions
- **Cointegration Stability**: Persistence of cointegration relationship

## Monitoring and Alerts

### Real-time Monitoring
- **Position Status**: Open/closed positions and P&L
- **Signal Generation**: New trading signals and confidence levels
- **Risk Metrics**: Current risk exposure and limits
- **Model Performance**: GARCH model fit and forecast accuracy

### Alert System
- **High Volatility**: Alerts when volatility exceeds thresholds
- **Correlation Drift**: Warnings when correlation breaks down
- **Position Limits**: Notifications when approaching position limits
- **Model Degradation**: Alerts when GARCH model performance deteriorates

## Future Enhancements

### Advanced GARCH Models
- **EGARCH**: Exponential GARCH for asymmetric volatility
- **GJR-GARCH**: Glosten-Jagannathan-Runkle GARCH for leverage effects
- **Multivariate GARCH**: For multiple asset pairs

### Machine Learning Integration
- **Feature Engineering**: Additional technical indicators
- **Ensemble Methods**: Combining multiple GARCH models
- **Deep Learning**: Neural networks for volatility forecasting

### Portfolio Optimization
- **Multi-Pair Trading**: Managing multiple symbol pairs
- **Risk Parity**: Equal risk contribution across pairs
- **Dynamic Rebalancing**: Automatic portfolio rebalancing

## Conclusion

This GARCH-based pairs trading system provides a robust foundation for algorithmic trading with:

1. **Sophisticated Volatility Modeling**: Using GARCH for volatility forecasting
2. **Statistical Rigor**: Cointegration testing for pair selection
3. **Risk Management**: Multiple layers of risk controls
4. **Paper Trading**: Safe testing environment
5. **Scalable Architecture**: Modular design for future enhancements

The system integrates seamlessly with the existing Prefect trading infrastructure and provides a solid foundation for quantitative trading strategies. 