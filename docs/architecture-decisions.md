# Architecture Decisions

## Overview
This document records the key architectural decisions made during the development of the GARCH-GRU Pairs Trading System. It serves as a decision log for future reference and team alignment.

> **📋 Quick Links**: [Setup Guide](setup.md) | [Development Guide](development.md) | [Testing Guide](testing.md) | [UI Documentation](ui.md) | [API Documentation](api.md)

## 1. PyTorch vs TensorFlow Decision

### **Decision: Switch to PyTorch**

### **Context:**
- Original implementation used TensorFlow 2.10.0
- Existing GRU model in `pairs_identification_GRU.ipynb` was built with TensorFlow/Keras

### **Problem:**
- TensorFlow was difficult to run on Windows without WSL
- Local development environment constraints
- Installation and compatibility issues on Windows

### **Options Considered:**

#### **Option A: Keep TensorFlow**
**Pros:**
- Existing code already works
- MLflow has excellent TensorFlow support with `mlflow.keras`
- Production-ready with TensorFlow Serving
- No refactoring needed

**Cons:**
- Windows compatibility issues
- Requires WSL for optimal performance
- Installation complexity on local machine

#### **Option B: Switch to PyTorch**
**Pros:**
- Better native Windows support
- Easier installation (`pip install torch`)
- No WSL required
- More Pythonic and intuitive
- Growing ecosystem and community support

**Cons:**
- Need to refactor existing GRU model
- Update MLflow integration to use `mlflow.pytorch`
- Time investment for migration

### **Decision Rationale:**
- **Primary Factor**: Windows compatibility without WSL
- **Secondary Factor**: Modern PyTorch ecosystem
- **Approach**: Refactor code as we go along, maintaining clean architecture

### **Implementation:**
- Updated `config/requirements.txt`: Removed TensorFlow, added PyTorch 2.1.0
- Future: Convert GRU model from TensorFlow to PyTorch
- Future: Update MLflow integration for PyTorch

---

## 2. Database Architecture Decision

### **Decision: Separate `mlflow_db` Database**

### **Context:**
- Existing trading system uses `trading_system` database
- MLflow needs persistent storage for experiments, runs, and model registry
- Need to decide between single vs separate database approach

### **Options Considered:**

#### **Option A: Use Existing `trading_system` Database**
**Pros:**
- Single database to manage
- Shared connection pool
- Transaction coordination between MLflow and trading operations
- Simpler backup strategy (one database)

**Cons:**
- Schema pollution (MLflow tables mixed with trading tables)
- Potential naming conflicts
- Harder to clean up MLflow data independently
- Different access permissions needed
- Larger backup size

#### **Option B: Separate `mlflow_db` Database**
**Pros:**
- Clean separation of concerns
- Industry standard practice
- Independent backup/restore of MLflow data
- No schema conflicts
- Easy cleanup (can drop entire MLflow database)
- Different access permissions possible
- Future-proof for scaling

**Cons:**
- More databases to manage
- Additional connection overhead
- More complex backup strategy

### **Decision Rationale:**
- **Primary Factor**: Clean architecture and separation of concerns
- **Secondary Factor**: Industry standard practice
- **Tertiary Factor**: Future scalability and maintenance

### **Implementation:**
- Use existing PostgreSQL setup: `postgresql://postgres:nishant@localhost/mlflow_db`
- MLflow server command: `mlflow server --backend-store-uri postgresql://postgres:nishant@localhost/mlflow_db --default-artifact-root file:./mlruns --host 0.0.0.0 --port 5000`

---

## 3. Multi-Sector Architecture Decision

### **Decision: Design for Multi-Sector, Start with Technology Only**

### **Context:**
- System needs to support multiple sectors (technology, healthcare, financial)
- Currently only have technology sector data
- Need to balance current needs with future scalability

### **Options Considered:**

#### **Option A: Technology Sector Only**
**Pros:**
- Simpler implementation
- Focus on current needs
- Faster development

**Cons:**
- Major refactoring needed when adding sectors
- Not scalable
- Code changes required for expansion

#### **Option B: Multi-Sector Ready Architecture**
**Pros:**
- Future-proof design
- No refactoring needed when adding sectors
- Consistent experiment tracking across sectors
- Scalable from day one

**Cons:**
- Slightly more complex initial setup
- More configuration options

### **Decision Rationale:**
- **Primary Factor**: Future scalability without refactoring
- **Secondary Factor**: Consistent architecture across sectors
- **Approach**: Design for multi-sector, implement for technology only

### **Implementation:**
- MLflow experiment naming: `pairs_trading/technology`
- Model naming: `pairs_trading_gru_garch_technology_v1`
- Configuration supports multiple sectors but only technology is active
- Easy to add new sectors by creating new experiments

---

## 4. Custom Database Tables Decision

### **Decision: Use MLflow Built-in Tables Only (For Now)**

### **Context:**
- MLflow automatically creates all necessary tables for tracking
- Custom tables would provide additional analytics and integration features
- Need to balance simplicity with advanced features

### **Options Considered:**

#### **Option A: Custom Database Tables**
**Pros:**
- Advanced analytics and reporting
- Trading signal attribution
- Custom performance tracking
- Enhanced integration with trading system

**Cons:**
- Additional complexity
- More database management
- Not required for basic MLflow operation

#### **Option B: MLflow Built-in Tables Only**
**Pros:**
- Simpler setup
- No additional database migrations
- MLflow handles all tracking automatically
- Faster implementation

**Cons:**
- Limited custom analytics
- No trading signal attribution
- Basic reporting only

### **Decision Rationale:**
- **Primary Factor**: Start simple, add complexity as needed
- **Secondary Factor**: MLflow built-in tables are sufficient for basic operation
- **Future**: Custom tables can be added later for advanced analytics

### **Implementation:**
- Use only MLflow's automatic table creation
- Document custom tables as future enhancements
- Focus on core MLflow functionality first

---

## 5. MLflow Server vs Local Tracking Decision

### **Decision: Use MLflow Server with PostgreSQL Backend**

### **Context:**
- Need to choose between local file tracking and server-based tracking
- User has experience with PostgreSQL backend

### **Options Considered:**

#### **Option A: Local File Tracking**
**Pros:**
- No server setup required
- Works immediately
- Good for development/testing
- Simple file-based storage

**Cons:**
- No web UI
- Limited multi-user support
- Not production-ready
- No persistent database storage

#### **Option B: MLflow Server with PostgreSQL**
**Pros:**
- Web UI at http://localhost:5000
- Persistent database storage
- Production-ready
- Multi-user support
- User already has experience with this setup

**Cons:**
- Requires server setup
- More complex initial configuration

### **Decision Rationale:**
- **Primary Factor**: User's existing experience and preference
- **Secondary Factor**: Production-ready setup from the start
- **Tertiary Factor**: Web UI for experiment visualization

### **Implementation:**
- Use existing PostgreSQL setup
- MLflow server with database backend
- Web UI for experiment management

---

## 6. WebSocket Symbol Configuration for Pairs Trading

### **Decision: Add PDFS and ROG to WebSocket Data Collection**

### **Context:**
- Current WebSocket implementation only collects data for AAPL
- Need multiple symbols for pairs trading implementation

---

## 7. PyTorch GRU Training Strategy Decision

### **Decision: Train All Pairs Initially for Comprehensive Baseline**

### **Context:**
- Need to establish baseline performance across all possible pairs
- Want to identify which pairs perform best before optimization
- Current system has 23 symbols generating 253 possible pairs
- Need to balance comprehensive analysis with computational efficiency
- **Note**: This is a new PyTorch implementation, not a migration from TensorFlow

### **Options Considered:**

#### **Option A: Train Top N Pairs Only (Previous Approach)**
**Pros:**
- Faster training time
- Focus on highest correlation pairs
- Lower computational cost
- Quick iteration cycles

**Cons:**
- Miss potential hidden gems (lower correlation but high predictive power)
- No baseline for comparison
- Risk of overfitting to correlation metric
- Limited discovery of unexpected patterns

#### **Option B: Train All Pairs Initially (Current Decision)**
**Pros:**
- Comprehensive baseline across all pairs
- Discover unexpected high-performing pairs
- Better understanding of pair performance distribution
- Data-driven optimization decisions
- Identify pairs that perform well despite lower correlation

**Cons:**
- Longer training time (253 models vs 5-10 models)
- Higher computational cost
- More complex MLflow experiment management
- Potential for information overload

### **Decision Rationale:**
- **Primary Factor**: Establish comprehensive baseline for data-driven optimization
- **Secondary Factor**: Discover unexpected high-performing pairs
- **Tertiary Factor**: Better understanding of performance distribution

### **Implementation:**
- Modified `prepare_pairs_data()` to accept `top_pairs=None` for all pairs
- Updated training loop to handle all pairs that meet correlation threshold (>0.8)
- Enhanced MLflow experiment naming for better organization
- Added performance tracking for all pairs

### **Future Optimization Strategy:**
1. **Phase 1**: Train all pairs (current) - establish baseline
2. **Phase 2**: Analyze performance distribution and identify top performers
3. **Phase 3**: Implement selective training based on performance metrics
4. **Phase 4**: Continuous monitoring and re-evaluation

### **Performance Deprecation Triggers:**
- Training time exceeds acceptable limits (>2 hours for full dataset)
- MLflow experiment management becomes unwieldy
- Computational costs exceed budget
- Performance analysis shows diminishing returns

### **Monitoring Metrics:**
- Total training time per run
- Performance distribution across all pairs
- Top 10% vs bottom 10% performance gap
- Correlation vs performance relationship
- MLflow experiment size and management overhead

---
- System needs to support real-time data collection for multiple symbols

### **Options Considered:**

#### **Option A: Keep Single Symbol (AAPL)**
**Pros:**
- Simple implementation
- No changes needed to existing code
- Lower data volume

**Cons:**
- Cannot implement pairs trading
- Limited to single stock analysis
- Not scalable for multi-symbol strategies

#### **Option B: Add Multiple Symbols for Pairs Trading**
**Pros:**
- Enables pairs trading implementation
- More sophisticated trading strategies
- Scalable for future symbol additions
- Real-world trading scenario

**Cons:**
- More complex data processing
- Higher data volume
- Need to update multiple files

### **Decision Rationale:**
- **Primary Factor**: Enable pairs trading functionality
- **Secondary Factor**: Real-world trading scenario with multiple symbols
- **Tertiary Factor**: Foundation for future strategy expansion

### **Implementation:**
- Updated both `alpaca_websocket.py` and `configurable_websocket.py`
- Configured symbol lists: `['AAPL', 'PDFS', 'ROG']` (AAPL for testing, PDFS-ROG for pairs trading)
- Updated Redis key patterns to handle multiple symbols
- Updated data processing logic to handle all three symbols
- Primary trading pair: (PDFS, ROG)
- Testing symbol: AAPL (highly liquid for testing)

---

## 7. PortfolioManager Singleton Pattern and Caching System

### **Decision: Implement Singleton Pattern with Intelligent Caching**

### **Context:**
- PortfolioManager was being instantiated multiple times across different UI components
- Excessive API calls to Alpaca were causing performance issues and rate limiting
- Multiple refresh buttons were scattered across different pages
- Auto-refresh was causing complete page re-renders every 10 seconds

### **Problem:**
- Multiple "Portfolio Manager initialized successfully" log messages
- Repeated API calls for the same data within seconds
- Redundant refresh buttons creating user confusion
- Poor performance due to unnecessary API calls
- Auto-refresh bypassing caching system

### **Options Considered:**

#### **Option A: Keep Multiple Instances**
**Pros:**
- No code changes required
- Each component manages its own data
- Simple implementation

**Cons:**
- Multiple API connections
- Excessive API calls
- Poor performance
- Rate limiting issues
- Resource waste

#### **Option B: Singleton Pattern with Caching**
**Pros:**
- Single instance across application
- Intelligent caching reduces API calls
- Better performance
- Respects API rate limits
- Clean architecture
- Easy to monitor and debug

**Cons:**
- Requires refactoring existing code
- More complex implementation
- Need to manage cache invalidation

### **Decision Rationale:**
- **Primary Factor**: Performance and API efficiency
- **Secondary Factor**: Clean architecture and maintainability
- **Tertiary Factor**: Better user experience with faster response times

### **Implementation:**

#### **1. Singleton Pattern**
```python
class PortfolioManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PortfolioManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        # Initialize only once
        self._initialized = True
```

#### **2. Caching System**
```python
def _get_cached_data(self, key: str):
    """Get data from cache if it's still valid."""
    if key in self._cache and key in self._cache_timestamps:
        timestamp = self._cache_timestamps[key]
        cache_duration = 10 if key.startswith('orders_') else self._cache_duration
        if datetime.now() - timestamp < timedelta(seconds=cache_duration):
            return self._cache[key]
    return None
```

#### **3. Shared Instance Management**
```python
# In UI modules
_portfolio_manager = None

def get_portfolio_manager():
    """Get or create a shared portfolio manager instance."""
    global _portfolio_manager
    if _portfolio_manager is None:
        _portfolio_manager = PortfolioManager()
    return _portfolio_manager
```

#### **4. Cache Duration Strategy**
- **Orders**: 10 seconds (frequently changing)
- **Account Info**: 30 seconds (relatively stable)
- **Positions**: 30 seconds (moderately stable)
- **Portfolio Summary**: 30 seconds (computed from other data)

### **Results:**
- **Single initialization**: Only one "Portfolio Manager initialized successfully" message
- **Reduced API calls**: Caching eliminates redundant calls
- **Better performance**: Faster response times for UI components
- **Cleaner UI**: Single refresh button in sidebar
- **Improved UX**: No more multiple refresh buttons

---

## 8. UI Refresh Button Consolidation

### **Decision: Centralize Refresh Functionality**

### **Context:**
- Multiple refresh buttons were scattered across different pages
- Users were confused about which refresh button to use
- Redundant functionality was creating maintenance overhead
- Auto-refresh was causing performance issues

### **Problem:**
- Home page had refresh button for portfolio section
- Portfolio page had its own refresh button
- Main sidebar had global refresh button
- Auto-refresh was causing complete page re-renders every 10 seconds

### **Options Considered:**

#### **Option A: Keep Multiple Refresh Buttons**
**Pros:**
- Page-specific refresh control
- No code changes required
- Users can refresh specific sections

**Cons:**
- User confusion about which button to use
- Redundant functionality
- Inconsistent behavior
- Maintenance overhead

#### **Option B: Centralize Refresh in Sidebar**
**Pros:**
- Single point of control
- Clear user interface
- Consistent behavior
- Easier maintenance
- Better performance

**Cons:**
- Less granular control
- All data refreshes together

### **Decision Rationale:**
- **Primary Factor**: User experience and interface clarity
- **Secondary Factor**: Performance and maintenance
- **Tertiary Factor**: Consistency across the application

### **Implementation:**

#### **1. Removed Redundant Buttons**
- Removed refresh button from Home page portfolio section
- Removed refresh button from Portfolio page
- Kept testing results refresh button (different functionality)

#### **2. Enhanced Main Sidebar Button**
```python
# Single refresh button in sidebar
if st.button("🔄 Refresh All Data", help="Force refresh all portfolio and market data"):
    clear_portfolio_manager()
    st.rerun()
```

#### **3. Disabled Auto-refresh**
```python
# Auto-refresh disabled - using intelligent caching instead
# st_autorefresh(interval=10000)  # Disabled to prevent excessive API calls
```

#### **4. Added User Guidance**
```python
st.caption("💡 Use the refresh button above to update all data across the app")
```

### **Results:**
- **Cleaner interface**: Single refresh button
- **Better UX**: Users know exactly where to refresh
- **Improved performance**: No automatic page refreshes
- **Consistent behavior**: All data refreshes together
- **Easier maintenance**: One place to manage refresh logic

---

## 9. Dual WebSocket Implementation Strategy

### **Decision: Maintain Both alpaca_websocket.py and configurable_websocket.py Until Code Stabilizes**

### **Context:**
- Successfully implemented configuration-based symbol management for both websocket implementations
- `configurable_websocket.py` provides advanced features (Alpaca + Recycler modes)
- `alpaca_websocket.py` is used by `main.py` and provides standalone Alpaca functionality
- Code is still in development and stabilization phase

### **Problem:**
- `configurable_websocket.py` is more feature-rich but newer
- `alpaca_websocket.py` is simpler but actively used by main.py
- Need to ensure system stability while developing advanced features
- Risk of breaking existing functionality during development

### **Options Considered:**

#### **Option A: Remove alpaca_websocket.py Immediately**
**Pros:**
- Single websocket implementation
- Less code duplication
- Cleaner architecture
- All features in one place

**Cons:**
- Risk of breaking main.py functionality
- No fallback if configurable_websocket has issues
- Harder to debug and isolate issues
- Development instability

#### **Option B: Keep Both Implementations**
**Pros:**
- Stable main.py functionality
- Fallback option if issues arise
- Easier debugging and testing
- Gradual migration path
- Both use same configuration system

**Cons:**
- Code duplication
- Maintenance overhead
- Slightly larger codebase

#### **Option C: Migrate main.py to configurable_websocket**
**Pros:**
- Single implementation
- Advanced features available
- Cleaner architecture

**Cons:**
- Risk of breaking existing functionality
- More complex implementation
- Potential stability issues during development

### **Decision Rationale:**
- **Primary Factor**: System stability during development phase
- **Secondary Factor**: Risk mitigation with fallback option
- **Tertiary Factor**: Gradual migration path to advanced features

### **Implementation:**

#### **1. Current State**
- `alpaca_websocket.py`: Used by `main.py`, standalone Alpaca functionality
- `configurable_websocket.py`: Advanced implementation with Alpaca + Recycler modes
- Both use `get_websocket_symbols()` for configuration-based symbol management

#### **2. Configuration Consistency**
```python
# Both files use the same configuration approach
from src.utils.websocket_config import get_websocket_symbols
symbols = get_websocket_symbols()  # Gets symbols from config.yaml
```

#### **3. Migration Strategy**
- **Phase 1**: Maintain both implementations (current)
- **Phase 2**: Test configurable_websocket thoroughly
- **Phase 3**: Migrate main.py to use configurable_websocket
- **Phase 4**: Remove alpaca_websocket.py once stable

#### **4. Testing Approach**
- Test both implementations independently
- Compare functionality and performance
- Ensure configurable_websocket handles all alpaca_websocket use cases
- Validate main.py integration with configurable_websocket

### **Success Criteria for Migration:**
- Configurable_websocket passes all alpaca_websocket tests
- Main.py works seamlessly with configurable_websocket
- No performance degradation
- All existing functionality preserved
- Advanced features (Recycler mode) working correctly

### **Timeline:**
- **Immediate**: Keep both implementations
- **Short-term**: Complete testing and validation
- **Medium-term**: Migrate main.py to configurable_websocket
- **Long-term**: Remove alpaca_websocket.py

### **Results:**
- **Stable development**: No risk to existing functionality
- **Feature development**: Can enhance configurable_websocket safely
- **Testing flexibility**: Can compare implementations
- **Gradual migration**: Low-risk path to advanced features
- **Configuration consistency**: Both use same symbol configuration

---

## 10. Multi-Symbol Data Recycler with Proxy Support

### **Decision: Implement Configuration-Driven Multi-Symbol Support with AAPL Proxy Fallback**

### **Context:**
- Data recycler was hardcoded for AAPL only
- User wants to trade PDFS and ROG pairs but doesn't have data for these symbols yet
- Need to support multiple symbols while maintaining system functionality
- Market is closed, so no immediate access to PDFS/ROG data

### **Problem:**
- Data recycler only supported single symbol (AAPL)
- PDFS and ROG data not available in database yet
- Need to test pairs trading infrastructure immediately
- Want to transition to real data when available without code changes

### **Options Considered:**

#### **Option A: Keep Single Symbol (AAPL)**
**Pros:**
- No code changes required
- Simple implementation
- No risk of breaking existing functionality

**Cons:**
- Cannot test pairs trading with multiple symbols
- Need to refactor later when PDFS/ROG data is available
- Limited testing capabilities

#### **Option B: Multi-Symbol with Proxy Support**
**Pros:**
- Immediate support for PDFS and ROG symbols
- Uses AAPL data as proxy for missing symbols
- Configuration-driven symbol management
- Easy transition to real data when available
- No code changes needed when real data becomes available

**Cons:**
- More complex implementation
- Proxy data may not perfectly represent real symbol behavior
- Need to manage symbol mapping logic

#### **Option C: Wait for Real Data**
**Pros:**
- No proxy data complications
- Real symbol behavior from the start

**Cons:**
- Cannot test pairs trading infrastructure immediately
- Delays development and testing
- No immediate solution for current needs

### **Decision Rationale:**
- **Primary Factor**: Immediate testing capability for pairs trading infrastructure
- **Secondary Factor**: Easy transition path to real data when available
- **Tertiary Factor**: Configuration-driven approach for future flexibility

### **Implementation:**

#### **1. Multi-Symbol Data Recycler**
```python
class MultiSymbolDataRecycler:
    def __init__(self):
        self.config = get_websocket_config()
        self.symbols = self.config.get_recycler_symbols()
        self.symbol_mapping = self._create_symbol_mapping()
    
    def _create_symbol_mapping(self) -> Dict[str, str]:
        """Map requested symbols to available symbols with fallback"""
        mapping = {}
        available_symbols = self._get_available_symbols()
        
        for symbol in self.symbols:
            if symbol in available_symbols:
                mapping[symbol] = symbol  # Use actual data
            else:
                mapping[symbol] = FALLBACK_SYMBOL  # Use AAPL as proxy
        return mapping
```

#### **2. Configuration Management**
```yaml
websocket:
  mode: "recycler"
  symbols: ["AAPL", "PDFS", "ROG"]
  recycler:
    symbols: ["AAPL", "PDFS", "ROG"]  # PDFS/ROG will use AAPL as proxy
```

#### **3. Symbol Management Utilities**
- `scripts/manage_symbols.py`: Manage symbol configuration and simple data verification
- Easy switching between testing and pairs trading modes
- One command to check data availability after Monday's collection

#### **4. Data Flow**
```
Requested: [AAPL, PDFS, ROG]
Available: [AAPL]
Mapping:   AAPL→AAPL, PDFS→AAPL, ROG→AAPL
Result:    All symbols use AAPL data with correct symbol names
```

### **Results:**
- **Immediate testing**: Can test pairs trading with PDFS/ROG symbols immediately
- **Proxy data**: Uses AAPL data as realistic proxy for missing symbols
- **Easy transition**: When real data becomes available, no code changes needed
- **Configuration flexibility**: Easy to add/remove symbols via configuration
- **Development continuity**: No delays in pairs trading development

### **Transition Strategy:**
1. **Phase 1**: Use AAPL proxy data for PDFS/ROG (current)
2. **Phase 2**: Collect real PDFS/ROG data on Monday, check availability on Tuesday with `python scripts/manage_symbols.py status`
3. **Automatic Transition**: System automatically uses real data when available (no code changes needed)

---

## Summary of Key Decisions

1. **PyTorch over TensorFlow**: Better Windows compatibility
2. **Separate `mlflow_db`**: Clean architecture and industry standard
3. **Multi-sector ready**: Future-proof design starting with technology only
4. **MLflow built-in tables only**: Start simple, add custom tables later
5. **MLflow server with PostgreSQL**: Production-ready with web UI
6. **WebSocket symbols with testing**: AAPL for testing, PDFS-ROG for pairs trading
7. **PortfolioManager singleton with caching**: Performance optimization and API efficiency
8. **Centralized refresh functionality**: Better user experience and interface clarity
9. **Dual WebSocket Implementation**: Maintain both implementations until code stabilizes
10. **Multi-Symbol Data Recycler with Proxy Support**: Configuration-driven symbol management with fallback to AAPL data
11. **Two-Model Architecture**: Separate pair identification (daily) and signal generation (real-time)
12. **Daily Pair Identification**: Prefect orchestration at 6:00 AM pre-market
13. **MLflow Model Retention**: Indefinite storage for historical analysis and rollback capability
14. **Model Comparison Metrics**: Composite score with weighted performance evaluation
15. **Scaling Strategy**: Single industry (technology) first, then parallel expansion

## Future Enhancements

> **📋 Centralized Registry**: All future enhancements are now tracked in this section for better project management and planning.

### High Priority Enhancements

#### 1. MLflow Model Management
- **Convert GRU model from TensorFlow to PyTorch**: Complete the migration started in Decision #1
- **Update MLflow integration for PyTorch**: Implement `mlflow.pytorch` integration
- **Automated rebaselining workflows**: Implement periodic model retraining via Prefect
- **Model serving infrastructure**: Add model deployment and serving capabilities
- **Custom database tables for advanced analytics**: Implement trading signal attribution and performance tracking
- **Daily pair identification implementation**: Prefect workflow for automated pair validation and GARCH model selection
- **Real-time signal generation**: 5-minute interval signal generation using pre-selected models
- **Model comparison and selection**: Automated model ranking with composite scoring system

#### 2. Data Source Expansion
- **Add more symbol pairs for diversified trading**: Expand beyond PDFS-ROG pair
- **Transition from proxy data to real PDFS/ROG data**: Complete the transition when real data becomes available
- **Additional data sources**: Integrate more market data providers
- **Real-time data quality monitoring**: Implement data validation and quality checks

#### 3. System Architecture
- **Expand to additional sectors**: Healthcare, financial sectors beyond technology
- **Microservices architecture**: Consider breaking down monolithic components
- **Containerization**: Docker support for easier deployment
- **CI/CD pipeline**: Automated testing and deployment

### Medium Priority Enhancements

#### 1. Performance Optimization
- **Database query optimization**: Implement advanced indexing and query optimization
- **Caching improvements**: Redis integration for better performance
- **API rate limiting**: Implement intelligent rate limiting strategies
- **Memory optimization**: Reduce memory usage in data processing

#### 2. Security Enhancements
- **API key rotation**: Automated key management
- **Data encryption**: Encrypt sensitive data at rest and in transit
- **Access control**: Role-based access control system
- **Audit logging**: Comprehensive audit trail

#### 3. User Experience
- **Advanced UI components**: More interactive charts and visualizations
- **Mobile app**: Native mobile application
- **Real-time notifications**: Push notifications for important events
- **Customizable dashboards**: User-configurable dashboard layouts

### Low Priority Enhancements

#### 1. Analytics and Reporting
- **Advanced analytics**: Machine learning-based insights
- **Custom reports**: User-defined report generation
- **Data export**: Multiple format support (CSV, Excel, PDF)
- **Historical analysis**: Long-term trend analysis

#### 2. Integration
- **Third-party integrations**: Slack, email, SMS notifications
- **API marketplace**: Public API for external integrations
- **Webhook support**: Real-time event notifications
- **Data warehouse integration**: BigQuery, Snowflake support

### Testing Enhancements

#### Critical Testing Gaps to Address

##### High Priority (Critical Gaps)
- **Data Source Unit Tests**: Complete unit tests for `alpaca_websocket.py`, `alpaca_historical_loader.py`, `alpaca_daily_loader.py`, `yahoo_finance_loader.py`, `news.py`, `data_recycler_server.py`, `configurable_websocket.py`, `hourly_persistence.py`
- **Utility Module Tests**: Unit tests for `websocket_config.py`, `data_recycler_utils.py`, `market_hours.py`
- **Database Integration Tests**: Real database operation tests, migration script tests, schema validation tests
- **Error Handling Tests**: Network failures, API failures, database failures, data corruption scenarios

##### Medium Priority (Important Gaps)
- **Script Unit Tests**: Unit tests for `manage_symbols.py`, `setup_test_env.py`, `manual_save.py`
- **Performance Tests**: Load testing, memory usage, API rate limiting, database performance
- **Security Tests**: API key validation, input validation, data sanitization, authentication flows
- **Data Quality Tests**: Data validation, data completeness, data consistency, data transformation accuracy

##### Low Priority (Nice to Have)
- **Documentation Tests**: API documentation accuracy, code examples validation, README validation
- **UI Edge Case Tests**: Complex user interactions, large datasets, market holidays, responsive design
- **Cross-Platform Tests**: Different operating systems compatibility

### Configuration Files Updated

- `config/requirements.txt`: PyTorch instead of TensorFlow
- `config/config.yaml`: Simplified MLflow configuration
- `config/env.example`: MLflow environment variables
- `docs/garch-pairs-trading.md`: Updated architecture documentation
- `src/data/sources/alpaca_websocket.py`: Added PDFS and ROG symbols
- `src/data/sources/configurable_websocket.py`: Added PDFS and ROG symbols
- `src/data/sources/data_recycler_server.py`: Refactored for multi-symbol support with proxy fallback
- `scripts/manage_symbols.py`: New utility for symbol configuration management
- `scripts/test_multi_symbol_recycler.py`: Test script for verification

### Related Documentation

- **[Setup Guide](setup.md)**: Installation and configuration instructions
- **[Development Guide](development.md)**: Development practices and workflows
- **[Testing Guide](testing.md)**: Testing strategies and implementation
- **[UI Documentation](ui.md)**: User interface components and features
- **[API Documentation](api.md)**: External and internal API usage

---

## 11. Two-Model Architecture for Pairs Trading

### **Decision: Separate Pair Identification (Daily) and Signal Generation (Real-time)**

### **Context:**
- Existing GARCH-GRU implementation in `pairs_identification_GRU.ipynb` combines pair identification and signal generation
- Need to optimize for production deployment with different performance requirements
- Daily pair identification is computationally intensive (cointegration tests, GARCH fitting)
- Real-time signal generation needs to be fast and efficient

### **Problem:**
- Single model approach mixes heavy computation (daily) with light computation (real-time)
- No clear separation between pair validation and trading signals
- Difficult to optimize for different performance requirements
- Hard to debug and monitor different aspects of the system

### **Options Considered:**

#### **Option A: Single Model Approach**
**Pros:**
- Simpler implementation
- No coordination between models
- Single point of failure

**Cons:**
- Mixed performance requirements
- Harder to optimize
- Difficult debugging and monitoring
- Not scalable for production

#### **Option B: Two-Model Architecture**
**Pros:**
- Clear separation of concerns
- Optimized for different performance requirements
- Better debugging and monitoring
- Scalable and maintainable
- Daily heavy computation vs real-time light computation

**Cons:**
- More complex coordination
- Two systems to maintain
- Need to manage model selection and handoff

### **Decision Rationale:**
- **Primary Factor**: Performance optimization for different use cases
- **Secondary Factor**: Scalability and maintainability
- **Tertiary Factor**: Clear separation of concerns for debugging and monitoring

### **Implementation:**

#### **Model 1: Daily Pair Identification**
- **Purpose**: Identify valid pairs for trading
- **Frequency**: Daily pre-market (6:00 AM)
- **Input**: Historical data (30-60 days)
- **Output**: Valid pairs with GARCH models
- **Criteria**: Cointegration, correlation, GARCH fit quality
- **Orchestration**: Prefect workflows

#### **Model 2: Real-time Signal Generation**
- **Purpose**: Generate trading signals for valid pairs
- **Frequency**: Every 5 minutes during trading hours
- **Input**: Real-time websocket data + pre-selected GARCH models
- **Output**: Entry/exit signals with confidence scores
- **Criteria**: GARCH volatility + GRU predictions

---

## 12. Daily Pair Identification Timing and Orchestration

### **Decision: Prefect Orchestration at 6:00 AM Pre-market**

### **Context:**
- Need to identify valid pairs before market opens
- Computational requirements are heavy (cointegration tests, GARCH fitting)
- Need reliable orchestration and error handling
- Market opens at 9:30 AM ET

### **Problem:**
- When should pair identification run?
- How to handle failures and retries?
- What orchestration system to use?
- How to ensure models are ready for trading?

### **Options Considered:**

#### **Option A: Market Open (9:30 AM)**
**Pros:**
- Latest data available
- No pre-market data needed

**Cons:**
- No time for model validation
- Trading starts without validated pairs
- Rush to complete before trading begins
- Risk of trading with invalid models

#### **Option B: Pre-market (6:00 AM)**
**Pros:**
- Ample time for computation
- Models ready before market opens
- Time for validation and testing
- Reliable orchestration with Prefect

**Cons:**
- Uses slightly older data
- Need to handle pre-market data availability

#### **Option C: End of Previous Day**
**Pros:**
- Maximum time for computation
- Models ready overnight

**Cons:**
- Data may be stale
- No overnight monitoring
- Harder to handle failures

### **Decision Rationale:**
- **Primary Factor**: Ensure models are ready before market opens
- **Secondary Factor**: Reliable orchestration with Prefect
- **Tertiary Factor**: Time for validation and error handling

### **Implementation:**
- **Schedule**: 6:00 AM daily using Prefect workflows
- **Orchestration**: Prefect for reliability and monitoring
- **Error Handling**: Automatic retries and alerts
- **Validation**: Model quality checks before trading begins

---

## 13. MLflow Model Retention Policy

### **Decision: Indefinite Model Retention**

### **Context:**
- MLflow stores model versions and artifacts
- Need to decide how long to keep old model versions
- Historical analysis and rollback capabilities needed
- Storage costs vs analytical value

### **Problem:**
- How long should we keep old model versions?
- Balance between storage costs and analytical value
- Need for historical analysis and rollback
- Performance impact of large model registry

### **Options Considered:**

#### **Option A: Limited Retention (30-90 days)**
**Pros:**
- Lower storage costs
- Faster model registry queries
- Simpler cleanup

**Cons:**
- No historical analysis
- Cannot rollback to old models
- Loss of model evolution insights
- No long-term performance tracking

#### **Option B: Indefinite Retention**
**Pros:**
- Complete historical analysis
- Rollback capability to any previous model
- Model evolution tracking
- Long-term performance analysis
- Research and development value

**Cons:**
- Higher storage costs
- Slower queries with large registry
- More complex management

### **Decision Rationale:**
- **Primary Factor**: Historical analysis and rollback capability
- **Secondary Factor**: Research and development value
- **Tertiary Factor**: MLflow handles storage efficiently

### **Implementation:**
- **Retention Policy**: Keep all model versions indefinitely
- **Storage Optimization**: MLflow's built-in compression and optimization
- **Cleanup Strategy**: Manual cleanup only when necessary
- **Monitoring**: Track storage usage and performance

---

## 14. Model Comparison and Selection Metrics

### **Decision: Composite Score with Weighted Performance Evaluation**

### **Context:**
- Need to compare GARCH models across different days
- Multiple performance metrics available (AIC, BIC, volatility forecasting, trading performance)
- Need objective criteria for model selection
- Balance between model fit and trading performance

### **Problem:**
- How to compare models from different days?
- What metrics to prioritize?
- How to weight different performance aspects?
- What threshold for model selection?

### **Options Considered:**

#### **Option A: Single Metric (AIC/BIC)**
**Pros:**
- Simple and objective
- Standard statistical measure
- Easy to implement

**Cons:**
- Doesn't consider trading performance
- May not reflect real-world effectiveness
- Ignores volatility forecasting accuracy

#### **Option B: Multiple Metrics (Unweighted)**
**Pros:**
- Considers multiple aspects
- More comprehensive evaluation

**Cons:**
- No prioritization
- Hard to rank models
- May not reflect business priorities

#### **Option C: Composite Score with Weights**
**Pros:**
- Balanced evaluation
- Configurable weights
- Reflects business priorities
- Objective ranking

**Cons:**
- More complex implementation
- Need to tune weights

### **Decision Rationale:**
- **Primary Factor**: Balanced evaluation of model quality and trading performance
- **Secondary Factor**: Configurable and objective ranking
- **Tertiary Factor**: Reflects business priorities

### **Implementation:**
- **Composite Score Formula**:
  - 40% AIC/BIC (model fit quality)
  - 30% Volatility forecasting accuracy (1-step ahead)
  - 20% Trading performance (recent backtest)
  - 10% Statistical diagnostics (residual quality)
- **Selection Criteria**: Composite score > 0.7
- **Lookback Period**: 10 days with 3-day rolling average
- **Quality Gates**: Correlation 0.8, cointegration p<0.05

---

## 15. Scaling Strategy for Multi-Sector Expansion

### **Decision: Single Industry (Technology) First, Then Parallel Expansion**

### **Context:**
- System designed for multi-sector support (technology, healthcare, financial)
- Currently only technology sector is active
- Need to balance current needs with future scalability
- Performance and complexity considerations

### **Problem:**
- How to scale from single sector to multiple sectors?
- When to add parallel processing?
- How to manage complexity and performance?
- What's the optimal expansion strategy?

### **Options Considered:**

#### **Option A: Parallel Processing from Start**
**Pros:**
- Ready for multi-sector immediately
- Maximum performance
- Future-proof architecture

**Cons:**
- Unnecessary complexity
- Higher resource usage
- Harder to debug and maintain
- Premature optimization

#### **Option B: Sequential Processing**
**Pros:**
- Simple implementation
- Lower resource usage
- Easier to debug

**Cons:**
- Poor performance with multiple sectors
- Not scalable
- Will need major refactoring later

#### **Option C: Single Industry First, Then Parallel**
**Pros:**
- Start simple and proven
- Learn from real usage
- Gradual complexity increase
- Optimize based on actual needs

**Cons:**
- Need refactoring when scaling
- Not immediately scalable

### **Decision Rationale:**
- **Primary Factor**: Start with proven, simple implementation
- **Secondary Factor**: Learn from real usage before optimizing
- **Tertiary Factor**: Gradual complexity increase

### **Implementation:**
- **Phase 1**: Technology sector only (current)
- **Phase 2**: Evaluate performance and bottlenecks
- **Phase 3**: Add parallel processing for multiple sectors
- **Phase 4**: Optimize based on actual usage patterns

---

## Decision Template for Future Use

### Decision: [Brief description]

### **Context:**
- [Background information]
- [Current situation]
- [Problem statement]

### **Options Considered:**

#### **Option A: [Description]**
**Pros:**
- [List of advantages]

**Cons:**
- [List of disadvantages]

#### **Option B: [Description]**
**Pros:**
- [List of advantages]

**Cons:**
- [List of disadvantages]

### **Decision Rationale:**
- **Primary Factor**: [Main reason]
- **Secondary Factor**: [Supporting reason]
- **Tertiary Factor**: [Additional consideration]

### **Implementation:**
- [Specific implementation details]
- [Configuration changes]
- [Code changes]

---

## Implementation Planning

### Overview
This section tracks the implementation progress for the GARCH-GRU Pairs Trading System with MLflow integration. The system is designed for multi-sector support (technology, healthcare, financial), but currently only the technology sector is active.

### Current Status Summary
- **MLflow Foundation**: ✅ COMPLETED (Week 1)
- **Existing GARCH-GRU Implementation**: ✅ DISCOVERED (Working with F1=0.7445)
- **Daily Pair Identification Architecture**: ✅ DESIGNED (Current)
- **Two-Model Architecture**: ✅ DESIGNED (Current)
- **PyTorch Migration**: 🔄 IN PROGRESS (Week 2-3)
- **MLflow Integration**: ⏳ PENDING (Week 4-5)
- **Production Integration**: ⏳ PENDING (Week 6-7)
- **Database Extensions**: ⏳ PENDING (Week 8)

### Phase 1: MLflow Foundation ✅ COMPLETED

#### ✅ Step 1: Dependencies Installation
- **Date**: [Previous]
- **Status**: COMPLETED
- **Details**: 
  - Updated `config/requirements.txt` to replace TensorFlow with PyTorch 2.1.0
  - Added MLflow 2.8.1 and related dependencies
  - All dependencies installed in existing conda environment

#### ✅ Step 2: Configuration Setup
- **Date**: [Previous]
- **Status**: COMPLETED
- **Details**:
  - Updated `config/config.yaml` with MLflow configuration
  - Updated `config/env.example` with MLflow environment variables
  - MLflow artifacts directory created at `./mlruns`

#### ✅ Step 3: Database Setup
- **Date**: [Previous]
- **Status**: COMPLETED
- **Details**:
  - Created `mlflow_db` database in PostgreSQL
  - Used separate database approach for clean architecture
  - Database connection: `postgresql://postgres:nishant@localhost/mlflow_db`

#### ✅ Step 4: MLflow Server Launch
- **Date**: [Previous]
- **Status**: COMPLETED
- **Details**:
  - Started MLflow server with PostgreSQL backend
  - Server running on: http://localhost:5000
  - Web UI accessible and functional

#### ✅ Step 5: MLflow Manager Implementation
- **Date**: [Previous]
- **Status**: COMPLETED
- **Details**:
  - Created `src/mlflow_manager.py` with comprehensive functionality
  - Implemented experiment tracking and model registry management
  - Added MLflow configuration manager in `src/ml/config.py`
  - Basic MLflow integration tests implemented

### Phase 2: PyTorch Migration and Refactoring 🔄 IN PROGRESS

#### ✅ Step 1: Existing Implementation Analysis
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

#### ✅ Step 2: Two-Model Architecture Design
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

#### ✅ Step 3: Daily Pair Identification Architecture Design
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

#### ✅ Step 4: PyTorch GRU Implementation
- **Date**: [Completed]
- **Status**: COMPLETED
- **Priority**: HIGH
- **File**: `src/ml/gru_model.py`
- **Components**:
  - ✅ New PyTorch GRU implementation (not a migration)
  - ✅ Modular pipeline design with clean components
  - ✅ Optimized architecture and hyperparameters
  - ✅ MLflow model logging capabilities
  - ✅ Clean, reusable PyTorch classes
  - ✅ **Training Strategy**: Train all pairs initially for comprehensive baseline
  - ✅ **Performance Analysis**: Comprehensive ranking and statistics
  - ✅ **Clean Output**: Focus on performance ranking without target comparisons
- **Dependencies**: `torch`, `numpy`, `pandas` (existing)
- **Actual Time**: 3 days
- **Success Criteria**: ✅ New PyTorch implementation completed with MLflow integration
- **Implementation Goals**: ✅ Modular, maintainable, MLflow-ready code

#### 🔄 Step 5: GARCH Model Refactoring and Modularization
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

#### 🔄 Step 6: Feature Engineering Refactoring and Extraction
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

### Phase 3: MLflow Integration and Strategy Refactoring ⏳ PENDING

#### 🔄 Step 1: Daily Pair Identification Implementation
- **Date**: [Week 4]
- **Status**: PLANNED
- **Priority**: HIGH
- **File**: `src/ml/daily_pair_identifier.py`
- **Components**:
  - Implement Prefect workflow for daily pair identification
  - Data collection and preprocessing tasks
  - Pair validation with correlation and cointegration tests
  - GARCH model fitting and evaluation
  - Model selection and ranking logic
  - MLflow integration for model storage
  - Trading configuration updates
- **Dependencies**: Previous phase components (PyTorch modules)
- **Estimated Time**: 3-4 days
- **Success Criteria**: Automated daily pair identification with MLflow tracking

#### 🔄 Step 2: Real-time Signal Generation Implementation
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

#### 🔄 Step 3: MLflow Model Serving Integration
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

### Phase 4: Production Integration ⏳ PENDING

#### 🔄 Step 1: Prefect Workflow Integration
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

#### 🔄 Step 2: Risk Management Integration
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

#### 🔄 Step 3: Performance Monitoring and Alerting
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

### Phase 5: Database Extensions ✅ COMPLETED

#### ✅ Step 1: Model Metadata Storage
- **Date**: [Completed]
- **Status**: COMPLETED
- **Priority**: MEDIUM
- **File**: `src/database/migrations/011_model_performance_tracking_complete.sql`
- **Components**:
  - ✅ Model performance history (`model_performance` table)
  - ✅ Model rankings tracking (`model_rankings` table)
  - ✅ Performance trends analysis (`model_trends` table)
  - ✅ Pair performance tracking with MLflow integration
  - ✅ Automated rankings and trends updates
- **Dependencies**: Database schema design
- **Actual Time**: 2 days
- **Success Criteria**: ✅ Complete model and trading history storage
- **Implementation**: 
  - Three main tables: `model_performance`, `model_rankings`, `model_trends`
  - Automated functions: `update_model_rankings()`, `update_model_trends()`
  - Integration with training pipeline for automatic updates

#### ✅ Step 2: Historical Performance Analysis
- **Date**: [Completed]
- **Status**: COMPLETED
- **Priority**: MEDIUM
- **Components**:
  - ✅ Performance metrics storage and retrieval
  - ✅ Model ranking system with F1 score ordering
  - ✅ Performance trends over 7-day and 30-day periods
  - ✅ Database functions for analytics queries
  - ✅ Integration with training pipeline
- **Dependencies**: Historical data, model metadata
- **Actual Time**: 1 day
- **Success Criteria**: ✅ Comprehensive historical analysis capabilities
- **Implementation**:
  - Functions: `get_best_performing_pairs()`, `get_pair_performance_trends()`, `get_recent_pair_performance()`
  - Views: `current_best_models` for easy access to top performers
  - Automatic updates after each training session

---

## 5. Model Performance Tracking Architecture

### **Decision: Automated Database Integration with MLflow**

### **Context:**
- MLflow tracks experiments, runs, and models
- Need persistent storage for performance metrics and rankings
- Training pipeline generates performance data that needs to be stored and analyzed

### **Options Considered:**

#### **Option A: MLflow Only**
**Pros:**
- Single source of truth
- Built-in experiment tracking
- No additional database complexity

**Cons:**
- Limited analytics capabilities
- No custom ranking system
- Difficult to query for UI integration
- No historical trends analysis

#### **Option B: Custom Database Tables + MLflow Integration**
**Pros:**
- Advanced analytics and ranking
- Custom performance tracking
- Easy UI integration
- Historical trends analysis
- Automated updates

**Cons:**
- Additional database complexity
- Need to maintain data consistency

### **Decision Rationale:**
- **Primary Factor**: Advanced analytics and UI integration requirements
- **Secondary Factor**: Automated performance tracking
- **Approach**: Use MLflow for experiment tracking, custom database for analytics

### **Implementation:**
- **Database Tables**:
  - `model_performance`: Stores training results with MLflow run IDs
  - `model_rankings`: Tracks best performing pairs by F1 score
  - `model_trends`: Analyzes performance trends over time
- **Automation**: Functions called automatically after training
- **Integration**: MLflow run IDs link database records to MLflow experiments

---

## 6. MLflow Run Naming and Database Integration

### **Decision: Separate Identifiers for Different Purposes**

### **Context:**
- MLflow uses run names for UI display
- Database needs unique identifiers for relationships
- Need to balance human readability with system integrity

### **Implementation:**
- **MLflow Run Names**: Descriptive, human-readable names
  - Format: `"GRU_Training_{pair_name}_{timestamp}_v1"`
  - Example: `"GRU_Training_NVDA-AMD_20250712_131425_v1"`
- **Database model_run_id**: MLflow's internal UUID
  - Format: MLflow's guaranteed-unique run ID
  - Example: `"abc123def456"`
- **Benefits**:
  - Data integrity through unique IDs
  - User-friendly MLflow interface
  - Proper referential integrity
  - Traceability between systems

---

## 7. Training Pipeline Automation

### **Decision: Automated Performance Tracking**

### **Context:**
- Training generates performance metrics
- Rankings and trends need to be updated
- Manual updates are error-prone and time-consuming

### **Implementation:**
- **Automatic Updates**: After all pairs are processed
- **Functions Called**:
  - `update_model_rankings()`: Updates pair rankings by F1 score
  - `update_model_trends()`: Updates performance trends over time
- **Integration Point**: End of training loop in `train_gru_models.py`
- **Error Handling**: Graceful failure with logging
- **Benefits**:
  - No manual intervention required
  - Consistent data updates
  - Real-time rankings and trends
  - Clean training output

---

### Phase 6: UI Integration ⏳ PENDING

#### 🔄 Step 1: Performance Dashboard
- **Date**: [Week 9]
- **Status**: PLANNED
- **Priority**: HIGH
- **Components**:
  - Model rankings display
  - Performance trends visualization
  - Pair performance comparison
  - Training history tracking
- **Dependencies**: Database performance tables
- **Estimated Time**: 2-3 days
- **Success Criteria**: Interactive performance dashboard

#### 🔄 Step 2: Training Monitoring
- **Date**: [Week 9]
- **Status**: PLANNED
- **Priority**: MEDIUM
- **Components**:
  - Real-time training progress
  - Model performance alerts
  - Training history logs
  - Performance degradation detection
- **Dependencies**: Performance tracking system
- **Estimated Time**: 2 days
- **Success Criteria**: Comprehensive training monitoring 

---

## 8. Daily Pair Identification Flow Architecture

### **Decision: Automated Pre-market Pair Identification with GARCH Analysis**

### **Context:**
- Need to identify valid trading pairs before market opens
- GARCH models require significant computation time
- Statistical analysis (correlation, cointegration) is computationally intensive
- Models need to be ready for real-time signal generation during market hours

### **Problem:**
- When should pair identification run?
- How to handle the computational requirements?
- What statistical criteria to use for pair selection?
- How to integrate with existing MLflow and Prefect infrastructure?

### **Options Considered:**

#### **Option A: Market Open (9:30 AM)**
**Pros:**
- Latest data available
- No pre-market data needed

**Cons:**
- No time for model validation
- Trading starts without validated pairs
- Rush to complete before trading begins
- Risk of trading with invalid models

#### **Option B: Pre-market (6:00 AM)**
**Pros:**
- Ample time for computation
- Models ready before market opens
- Time for validation and testing
- Reliable orchestration with Prefect

**Cons:**
- Uses slightly older data
- Need to handle pre-market data availability

#### **Option C: End of Previous Day**
**Pros:**
- Maximum time for computation
- Models ready overnight

**Cons:**
- Data may be stale
- No overnight monitoring
- Harder to handle failures

### **Decision Rationale:**
- **Primary Factor**: Ensure models are ready before market opens
- **Secondary Factor**: Reliable orchestration with Prefect
- **Tertiary Factor**: Time for validation and error handling

### **Implementation:**

#### **Flow Design: 7-Step Process**
1. **Data Collection** - Gather historical market data (60 days by default)
2. **Correlation Analysis** - Calculate correlations between all symbol pairs
3. **Cointegration Testing** - Test for cointegration using Engle-Granger test
4. **GARCH Model Fitting** - Fit GARCH(1,1) models to pair spreads
5. **Model Selection** - Select best models based on composite score
6. **MLflow Logging** - Log models and metadata to MLflow
7. **Configuration Update** - Update trading configuration with selected pairs

#### **Quality Gates**
- **Correlation Threshold**: 0.8 minimum correlation
- **Cointegration Test**: p-value < 0.05
- **Model Quality**: Composite score > 0.7
- **Statistical Diagnostics**: Ljung-Box and ARCH tests

#### **Composite Score Formula**
- **40% AIC/BIC** - Model fit quality
- **30% Volatility forecasting accuracy** - 1-step ahead forecast
- **20% Trading performance** - Recent backtest (placeholder)
- **10% Statistical diagnostics** - Residual quality

#### **Prefect Integration**
- **Schedule**: 6:00 AM EST Mon-Fri using cron: `"0 6 * * 1-5"`
- **Work Pool**: Dedicated "daily" work pool for pre-market tasks
- **Error Handling**: Comprehensive logging and graceful failure handling
- **Monitoring**: Full integration with Prefect UI for flow monitoring

#### **MLflow Integration**
- **Model Versioning**: Each day gets a new model version
- **Artifact Storage**: GARCH models and spread data
- **Experiment Tracking**: Full lineage and metadata
- **Performance Metrics**: Comprehensive model evaluation

### **Benefits:**
- **Automated Execution**: No manual intervention required
- **Statistical Rigor**: Comprehensive statistical validation
- **Production Ready**: Error handling and resource management
- **Scalable**: Easy to add new sectors and symbols
- **Traceable**: Full MLflow integration for model lineage
- **Testable**: Manual testing commands for development

### **Success Metrics:**
- **Execution Time**: Complete within 2 hours (6:00 AM - 8:00 AM)
- **Model Quality**: Composite scores > 0.7 for selected pairs
- **Reliability**: 99%+ successful execution rate
- **Integration**: Seamless handoff to real-time signal generation

---

### Phase 6: UI Integration ⏳ PENDING 