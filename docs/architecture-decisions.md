# Architecture Decisions

## Overview
This document records the key architectural decisions made during the development of the GARCH-GRU Pairs Trading System. It serves as a decision log for future reference and team alignment.

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

## Future Enhancements

- Convert GRU model from TensorFlow to PyTorch
- Add custom database tables for advanced analytics
- Expand to additional sectors (healthcare, financial)
- Implement automated rebaselining workflows
- Add model serving infrastructure
- Add more symbol pairs for diversified trading
- Transition from proxy data to real PDFS/ROG data when available

## Configuration Files Updated

- `config/requirements.txt`: PyTorch instead of TensorFlow
- `config/config.yaml`: Simplified MLflow configuration
- `config/env.example`: MLflow environment variables
- `docs/garch-pairs-trading.md`: Updated architecture documentation
- `src/data/sources/alpaca_websocket.py`: Added PDFS and ROG symbols
- `src/data/sources/configurable_websocket.py`: Added PDFS and ROG symbols
- `src/data/sources/data_recycler_server.py`: Refactored for multi-symbol support with proxy fallback
- `scripts/manage_symbols.py`: New utility for symbol configuration management
- `scripts/test_multi_symbol_recycler.py`: Test script for verification

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