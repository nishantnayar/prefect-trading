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

## Summary of Key Decisions

1. **PyTorch over TensorFlow**: Better Windows compatibility
2. **Separate `mlflow_db`**: Clean architecture and industry standard
3. **Multi-sector ready**: Future-proof design starting with technology only
4. **MLflow built-in tables only**: Start simple, add custom tables later
5. **MLflow server with PostgreSQL**: Production-ready with web UI
6. **WebSocket symbols with testing**: AAPL for testing, PDFS-ROG for pairs trading

## Future Enhancements

- Convert GRU model from TensorFlow to PyTorch
- Add custom database tables for advanced analytics
- Expand to additional sectors (healthcare, financial)
- Implement automated rebaselining workflows
- Add model serving infrastructure
- Add more symbol pairs for diversified trading

## Configuration Files Updated

- `config/requirements.txt`: PyTorch instead of TensorFlow
- `config/config.yaml`: Simplified MLflow configuration
- `config/env.example`: MLflow environment variables
- `docs/garch-pairs-trading.md`: Updated architecture documentation
- `src/data/sources/alpaca_websocket.py`: Added PDFS and ROG symbols
- `src/data/sources/configurable_websocket.py`: Added PDFS and ROG symbols

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