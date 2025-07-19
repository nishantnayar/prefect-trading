# UI Documentation

## Overview

The Prefect Trading System includes a modern, responsive Streamlit-based user interface that provides real-time market data visualization, portfolio management, and news integration. The UI is designed to be user-friendly, efficient, and accessible across different devices.

> **📋 Quick Links**: [Architecture Decisions](architecture-decisions.md) | [Setup Guide](setup.md) | [Development Guide](development.md) | [Testing Guide](testing.md) | [API Documentation](api.md)

## UI Architecture

### 1. Main Application (`src/ui/streamlit_app.py`)
- **Entry Point**: Main Streamlit application
- **Navigation**: Sidebar-based navigation with multiple pages
- **Manual Refresh**: Single centralized refresh button in sidebar
- **Custom Styling**: Professional CSS styling
- **PortfolioManager Integration**: Shared singleton instance with intelligent caching

### 2. Home Page (`src/ui/home.py`)
- **Dashboard Overview**: Comprehensive trading dashboard
- **Real-time Data**: Live market data with intelligent caching
- **Portfolio Summary**: Portfolio metrics and performance
- **Market Overview**: Major indices and market breadth
- **Recent Activity**: Latest trading activities
- **Quick Actions**: Common trading operations
- **Market News**: Latest news articles
- **Shared PortfolioManager**: Uses singleton instance for data access

### 3. Portfolio Page (`src/ui/portfolio.py`)
- **Account Overview**: Detailed account information and status
- **Position Table**: Complete list of positions with P&L calculations
- **Portfolio Allocation**: Pie chart showing position distribution
- **Trading History**: Detailed order history and performance metrics
- **Risk Analysis**: Comprehensive risk metrics and warnings
- **Shared PortfolioManager**: Uses singleton instance for data access

### 4. Portfolio Page (`src/ui/portfolio.py`)
- **Account Overview**: Detailed account information and status
- **Position Table**: Complete list of positions with P&L calculations
- **Portfolio Allocation**: Pie chart showing position distribution
- **Trading History**: Detailed order history and performance metrics
- **Risk Analysis**: Comprehensive risk metrics and warnings
- **Shared PortfolioManager**: Uses singleton instance for data access

### 5. Analysis Page (`src/ui/components/symbol_selector.py`)
- **Symbol Selection**: Dropdown with 22+ active symbols from database
- **Comprehensive Analysis**: Multi-tab interface for detailed symbol analysis
- **Market Data Analysis**: Price charts, statistics, and recent data
- **Company Information**: Financial metrics, officers, and business summary
- **Real-time Statistics**: Current price, change, volume, and volatility metrics

### 6. Testing Page (`src/ui/components/testing_results.py`)
- **Coverage Overview**: Overall test coverage metrics with visual indicators
- **File-Level Coverage**: Detailed breakdown by individual files
- **Test Results**: Comprehensive test execution results
- **Execution Logs**: Detailed logs and error information
- **Interactive Tables**: Streamlit dataframes with advanced table functionality
- **Independent Refresh**: Separate refresh functionality for test execution

### 7. Model Performance Dashboard (`src/ui/model_performance/`)
- **Performance Overview**: Top-level metrics and system health indicators
- **Model Rankings**: Interactive rankings table with filtering and sorting
- **Performance Trends**: Time-series charts showing F1 score trends
- **Training History**: Recent training activity with MLflow integration
- **Model Details**: Detailed view of individual model performance
- **Performance Analytics**: Advanced analytics with distribution charts
- **Database Integration**: Automatic data updates after training sessions

### 6. UI Components (`src/ui/components/`)

#### Market Status Component (`market_status.py`)
```python
def display_market_status():
    """
    Display current market status with timezone support.
    
    Features:
    - Real-time market open/closed status
    - Next market events
    - Timezone conversion (EST to CST)
    - Color-coded status indicators
    """
```

#### Symbol Selector Component (`symbol_selector.py`)
```python
def display_symbol_selector():
    """
    Interactive symbol selection component.
    
    Features:
    - Search functionality
    - Dropdown selection
    - Recent symbols
    - Favorite symbols
    """
```

#### Symbol Analysis Component (`symbol_selector.py`)
```python
def display_symbol_selector_with_analysis():
    """
    Comprehensive symbol analysis component with database integration.
    
    Features:
    - Symbol selection from database
    - Multi-tab analysis interface (Overview, Market Data, Company Info)
    - Market data analysis with charts
    - Company information from Yahoo Finance
    - Real-time price statistics
    """
```

#### Enhanced Symbol Analysis Features
```python
def display_symbol_analysis(symbol: str):
    """
    Display comprehensive symbol analysis in tabbed interface.
    
    Tabs:
    - 📊 Overview: Symbol info and market data summary
    - 📈 Market Data: Price charts and statistics
    - 🏢 Company Info: Financial metrics and officers
    """
```

#### Date Display Component (`date_display.py`)
```python
def get_current_cst_formatted():
    """
    Get current time in CST format.
    
    Returns:
        Formatted current time string
    """
```

#### Testing Results Component (`testing_results.py`)
```python
def render_testing_results():
    """
    Main function to render the testing results page.
    
    Features:
    - Coverage summary with color-coded metrics
    - File-level coverage breakdown in interactive Streamlit dataframes
    - Test execution results and statistics
    - Real-time coverage data from JSON reports
    - Professional styling with progress indicators
    - Manual refresh and test execution capabilities
    """
```

#### Model Performance Components (`src/ui/model_performance/components/`)

##### Metrics Dashboard Component (`metrics_dashboard.py`)
```python
def render_metrics_dashboard(manager):
    """
    Render the metrics dashboard with top-level performance indicators.
    
    Features:
    - Total models count with daily activity
    - Average F1 score with trend indicators
    - Best performing pair identification
    - Training activity monitoring
    - Performance insights and health indicators
    - Safe null value handling for all metrics
    """
```

##### Rankings Table Component (`rankings_table.py`)
```python
def render_rankings_table(manager):
    """
    Render the rankings table with interactive filtering and sorting.
    
    Features:
    - Interactive F1 score filtering with slider
    - Pair-based filtering with multiselect
    - Performance indicators (Excellent/Good/Needs Improvement)
    - CSV export functionality
    - Summary statistics
    - Safe decimal-to-float conversion
    """
```

##### Trends Chart Component (`trends_chart.py`)
```python
def render_trends_chart(manager):
    """
    Render the trends chart with performance metrics over time.
    
    Features:
    - Time period selection (7/30/90 days)
    - Dual-axis charts (F1 scores and model counts)
    - Moving averages (7-day and 30-day)
    - Trend analysis with percentage changes
    - Interactive Plotly charts
    - Safe decimal-to-float conversion
    """
```

##### Training History Component (`training_history.py`)
```python
def render_training_history(manager):
    """
    Render the training history table with recent activity.
    
    Features:
    - Recent training records with performance metrics
    - Training status indicators (Complete/Early Stop)
    - MLflow integration with direct experiment links
    - Summary statistics
    - Performance categorization
    - Safe decimal-to-float conversion
    """
```

##### Performance Analytics Component (`performance_analytics.py`)
```python
def render_performance_analytics(manager):
    """
    Render the performance analytics section with multiple charts.
    
    Features:
    - F1 score distribution histogram
    - Accuracy vs precision scatter plots
    - Training history over time
    - Statistical analysis (mean, median, std dev)
    - Performance trend calculations
    - Safe null value handling
    """
```

##### Model Details Component (`model_details.py`)
```python
def render_model_details(manager):
    """
    Render the model details section with pair selector and detailed view.
    
    Features:
    - Pair selection from available models
    - Detailed performance metrics
    - Training information and hyperparameters
    - MLflow integration
    - Performance comparison with other models
    - Safe null value handling
    """
```

For detailed rationale behind UI architecture decisions, see [Architecture Decisions](architecture-decisions.md).

## Model Performance Dashboard Implementation

### Overview
The Model Performance Dashboard provides comprehensive insights into ML model performance, rankings, trends, and training history. It integrates with the database to automatically display metrics after training sessions.

### Architecture

#### 1. Data Manager (`src/ui/model_performance/utils/data_manager.py`)
```python
class ModelPerformanceManager:
    """
    Manages database operations for model performance data.
    
    Key Features:
    - Decimal-to-float conversion for PostgreSQL compatibility
    - Safe null value handling
    - Comprehensive error handling with fallback values
    - Caching integration for performance optimization
    """
```

**Key Methods:**
- `get_overview_metrics()`: Top-level dashboard metrics
- `get_rankings()`: Model rankings with performance data
- `get_trends()`: Time-series performance trends
- `get_recent_training()`: Recent training activity
- `get_model_details()`: Detailed model information
- `get_f1_distribution()`: F1 score distribution for analytics
- `get_accuracy_precision_data()`: Accuracy vs precision analysis
- `get_training_history()`: Historical training data

#### 2. Component Structure
```
src/ui/model_performance/
├── main.py                    # Main dashboard orchestrator
├── __init__.py               # Package initialization
├── components/               # UI components
│   ├── metrics_dashboard.py  # Overview metrics
│   ├── rankings_table.py     # Rankings and filtering
│   ├── trends_chart.py       # Time-series charts
│   ├── training_history.py   # Recent activity
│   ├── performance_analytics.py # Advanced analytics
│   ├── model_details.py      # Detailed model view
│   └── __init__.py
└── utils/                    # Utility modules
    ├── data_manager.py       # Database operations
    ├── metrics_calculator.py # Metrics calculations
    ├── chart_helpers.py      # Chart utilities
    └── __init__.py
```

### Key Features

#### 1. Database Integration
- **Automatic Updates**: Data automatically refreshes after training
- **PostgreSQL Compatibility**: Handles decimal types and null values
- **Safe Type Conversion**: Converts `decimal.Decimal` to `float` for UI compatibility
- **Error Handling**: Graceful fallbacks for database connection issues

#### 2. Caching System
- **Streamlit Caching**: Intelligent caching with TTL (Time To Live)
- **Cache Invalidation**: Automatic cache clearing for fresh data
- **Performance Optimization**: Reduces database calls while maintaining data freshness

#### 3. Interactive Features
- **Filtering**: F1 score sliders and pair-based filtering
- **Sorting**: Interactive table sorting
- **Export**: CSV download functionality
- **MLflow Integration**: Direct links to MLflow experiments

#### 4. Data Visualization
- **Plotly Charts**: Interactive time-series and distribution charts
- **Performance Indicators**: Color-coded performance categories
- **Trend Analysis**: Percentage change calculations
- **Statistical Analysis**: Mean, median, standard deviation

### Technical Implementation Details

#### 1. Decimal/Float Conversion
```python
def _convert_decimal_to_float(self, value):
    """Convert decimal.Decimal to float if needed."""
    if isinstance(value, Decimal):
        return float(value)
    return value
```

#### 2. Safe Null Value Handling
```python
def _safe_float(value):
    """Safely convert value to float, handling decimal.Decimal."""
    if isinstance(value, Decimal):
        return float(value)
    if pd.isna(value):
        return 0.0
    return float(value)
```

#### 3. Database Query Optimization
```sql
-- Rankings with performance data join
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
```

#### 4. Caching Strategy
- **Overview Metrics**: 5 minutes cache
- **Rankings**: 1 minute cache
- **Trends**: 10 minutes cache
- **Training History**: 30 seconds cache
- **Analytics**: 5 minutes cache
- **Model Details**: 5 minutes cache

### Error Handling

#### 1. Database Connection Issues
- Graceful fallback to empty DataFrames
- User-friendly error messages
- Debug information in expandable sections

#### 2. Null Value Protection
- Safe dictionary access with defaults
- Null checks before formatting operations
- Fallback values for all metrics

#### 3. Type Conversion Safety
- Decimal-to-float conversion for PostgreSQL compatibility
- NaN value handling
- Safe arithmetic operations

### Integration Points

#### 1. Training Script Integration
- Automatic database updates after training
- MLflow run ID tracking
- Performance metrics logging

#### 2. Database Schema
- `model_performance`: Core performance metrics
- `model_rankings`: Daily rankings
- `model_trends`: Time-series trends

#### 3. MLflow Integration
- Direct experiment links
- Run ID tracking
- Hyperparameter display

### Performance Optimizations

#### 1. Caching Strategy
- Intelligent TTL based on data volatility
- Cache invalidation on manual refresh
- Reduced database load

#### 2. Query Optimization
- Efficient JOINs for related data
- Indexed queries for fast retrieval
- Limited result sets with pagination

#### 3. UI Responsiveness
- Asynchronous data loading
- Progressive disclosure of information
- Optimized chart rendering

### Recent Fixes and Improvements

#### 1. Decimal/Float Type Conversion Issues
**Problem**: PostgreSQL returns `decimal.Decimal` objects, but Python arithmetic operations expect `float` values, causing "unsupported operand type(s) for -: 'float' and 'decimal.Decimal'" errors.

**Solution**: 
- Added `_convert_decimal_to_float()` method in data manager
- Added `_safe_float()` helper functions in all components
- Implemented comprehensive type conversion for all numeric operations

#### 2. Null Value Formatting Issues
**Problem**: `None` values being passed to string formatting operations causing "unsupported format string passed to NoneType.format" errors.

**Solution**:
- Added safe dictionary access with `dict.get(key, default) or default` pattern
- Implemented null checks before all formatting operations
- Provided sensible fallback values (0, False, 'N/A') for all potentially null values

#### 3. Database Schema Mismatch
**Problem**: `model_rankings` table missing columns that UI components expected (accuracy, precision, recall, training_date).

**Solution**:
- Updated `get_rankings()` method to use LEFT JOIN with `model_performance` table
- Joined on `pair_symbol` and `model_run_id` to get complete performance data
- Maintained same column structure for UI compatibility

#### 4. Streamlit Caching Issues
**Problem**: Streamlit unable to hash `ModelPerformanceManager` objects in cached functions.

**Solution**:
- Added leading underscores to manager parameters in all cached functions
- Used `_manager` instead of `manager` to exclude from cache key calculation
- Maintained functionality while resolving caching errors

#### 5. Missing Function Definitions
**Problem**: `_safe_float` function used but not defined in some components.

**Solution**:
- Added `_safe_float()` function definition to all components that use it
- Added `decimal.Decimal` import to all components
- Ensured consistent error handling across all components

### Code Quality Improvements

#### 1. Error Handling
- Comprehensive try-catch blocks in all database operations
- Graceful fallbacks for all error conditions
- User-friendly error messages with troubleshooting guidance

#### 2. Type Safety
- Safe type conversion for all numeric operations
- Null value protection throughout the codebase
- Consistent data type handling across components

#### 3. Performance Optimization
- Intelligent caching with appropriate TTL values
- Efficient database queries with proper JOINs
- Reduced redundant database calls

#### 4. Code Documentation
- Comprehensive docstrings for all functions
- Clear parameter and return type annotations
- Inline comments explaining complex operations

### Testing and Validation

#### 1. Database Connectivity
- Automatic connection testing in error scenarios
- Fallback mechanisms for connection failures
- Debug information for troubleshooting

#### 2. Data Integrity
- Validation of data types and ranges
- Safe handling of missing or corrupted data
- Consistent data presentation across components

#### 3. UI Responsiveness
- Efficient rendering of large datasets
- Optimized chart generation
- Smooth user interactions

## UI Features

### 1. Intelligent Caching System
- **PortfolioManager Singleton**: Single instance across all UI components
- **Cache Duration Strategy**: 
  - Orders: 10 seconds (frequently changing)
  - Account Info: 30 seconds (relatively stable)
  - Positions: 30 seconds (moderately stable)
  - Portfolio Summary: 30 seconds (computed from other data)
- **Cache Invalidation**: Automatic cache clearing on manual refresh
- **Debug Logging**: Cache hit/miss monitoring for performance optimization

### 2. Centralized Refresh System
- **Single Refresh Button**: Located in main sidebar for all data
- **Clear User Interface**: No confusion about which refresh button to use
- **Consistent Behavior**: All portfolio and market data refreshes together
- **Performance Optimized**: No automatic page refreshes causing excessive API calls
- **User Guidance**: Helpful captions explaining refresh functionality

### 3. Real-time Updates
- **Intelligent Caching**: Reduces API calls while maintaining data freshness
- **Live Data**: Real-time market data updates through caching
- **Status Indicators**: Live market status updates
- **News Feed**: Latest news articles
- **Manual Refresh**: Sidebar button for immediate updates when needed

### 4. Responsive Design
- **Mobile-friendly**: Optimized for mobile devices
- **Tablet Support**: Responsive layouts for tablets
- **Desktop Optimization**: Full-featured desktop experience
- **Flexible Layouts**: Adaptive column arrangements

### 5. Interactive Components
- **Expandable Sections**: Collapsible content areas
- **Interactive Charts**: Clickable data visualizations
- **Search Functionality**: Symbol and news search
- **Filtering Options**: Data filtering capabilities
- **Streamlit Dataframes**: Advanced table functionality with sorting, filtering, and responsive design

### 6. Professional Styling
- **Custom CSS**: Professional appearance
- **Color Coding**: Status-based color indicators
- **Consistent Spacing**: Uniform layout spacing
- **Typography**: Readable font choices

## Testing Results Interface

### 1. Coverage Summary
The Testing Results component provides a comprehensive view of test coverage metrics:

```python
def display_coverage_summary():
    """
    Display overall coverage metrics with visual indicators.
    
    Features:
    - Overall coverage percentage with progress bar
    - Color-coded coverage levels (red/yellow/green)
    - Total files, statements, and coverage statistics
    - Interactive metrics display
    """
```

### 2. File-Level Coverage
Detailed breakdown of coverage by individual files:

```python
def display_file_coverage():
    """
    Display file-level coverage in an interactive Streamlit dataframe.
    
    Features:
    - Sortable columns (file name, statements, missing, coverage)
    - Color-coded coverage percentages
    - Filtering capabilities
    - Responsive table design
    """
```

### 3. Test Execution
Comprehensive test execution results and statistics:

```python
def display_test_results():
    """
    Display test execution results and statistics.
    
    Features:
    - Test outcome summary (passed/failed/skipped)
    - Execution time and performance metrics
    - Individual test details with status indicators
    - Error messages and debugging information
    """
```

### 4. Coverage Data Integration
The component reads coverage data from JSON reports:

```python
def load_coverage_data():
    """
    Load coverage data from JSON report file.
    
    Returns:
        Dictionary containing coverage metrics and file breakdown
    """
```

### 5. Recent Improvements
- **Streamlit Dataframe Integration**: Replaced aggrid with native Streamlit dataframes for better compatibility
- **Path Normalization**: Fixed Windows/Unix path differences for accurate coverage display
- **Deprecation Fixes**: Removed deprecated `fit_columns_on_grid_load` parameter
- **Enhanced Sorting**: Improved table sorting with numeric value preservation
- **Better Error Handling**: Graceful handling of missing coverage data
- **Test Execution**: Added ability to run tests directly from the UI
- **Real-time Updates**: Manual refresh capabilities for immediate data updates

### 6. AgGrid to Streamlit Refactoring (July 2025)
The UI has been refactored to use Streamlit's native dataframes instead of the third-party aggrid component:

#### **Changes Made:**
- **Removed aggrid dependency**: Eliminated `streamlit-aggrid` from requirements
- **Replaced AgGrid components**: Converted all tables to use `st.dataframe()` with styling
- **Simplified code**: Removed complex AgGrid configuration code
- **Better compatibility**: Native Streamlit components provide more reliable performance

#### **Benefits:**
- **Reduced dependencies**: No longer requires external aggrid package
- **Improved stability**: Native Streamlit components have fewer compatibility issues
- **Consistent styling**: All tables now use the same Streamlit styling and behavior
- **Easier maintenance**: Less complex code to maintain and debug
- **Better performance**: Native components are optimized for Streamlit

#### **Files Modified:**
- `src/ui/components/testing_results.py` - Replaced AgGrid with `st.dataframe`
- `config/requirements.txt` - Removed `streamlit-aggrid` dependency

#### **Current Table Implementation:**
```python
# Before (AgGrid)
from st_aggrid import AgGrid, GridOptionsBuilder
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(sortable=True, filterable=True)
grid_options = gb.build()
AgGrid(df, gridOptions=grid_options, theme="streamlit")

# After (Streamlit)
st.dataframe(df, use_container_width=True)
```

All tables maintain their functionality while using Streamlit's native components for better reliability and consistency.

## Page Structure

### 1. Home Page
```
┌─────────────────────────────────────────────────────────┐
│ Header: Dashboard Title, Time, Market Status           │
├─────────────────────────────────────────────────────────┤
│ Portfolio Overview (4 metrics + expandable details)    │
├─────────────────────────────────────────────────────────┤
│ Market Overview (3 columns: Indices, Tech, Breadth)    │
├─────────────────────────────────────────────────────────┤
│ Recent Activity (structured activity list)             │
├─────────────────────────────────────────────────────────┤
│ Quick Actions (2x2 grid of action buttons)            │
├─────────────────────────────────────────────────────────┤
│ Market News (expandable news articles)                │
└─────────────────────────────────────────────────────────┘
```

### 2. Portfolio Page
```
┌─────────────────────────────────────────────────────────┐
│ Account Overview (balance, buying power, status)      │
├─────────────────────────────────────────────────────────┤
│ Positions Table (symbol, shares, P&L, allocation)     │
├─────────────────────────────────────────────────────────┤
│ Portfolio Allocation (pie chart visualization)        │
├─────────────────────────────────────────────────────────┤
│ Trading History (recent trades and performance)       │
├─────────────────────────────────────────────────────────┤
│ Risk Analysis (margin, concentration, warnings)       │
└─────────────────────────────────────────────────────────┘
```

### 3. Testing Page
```
┌─────────────────────────────────────────────────────────┐
│ Test Summary (overall results and execution time)     │
├─────────────────────────────────────────────────────────┤
│ Coverage Overview (overall metrics and insights)      │
├─────────────────────────────────────────────────────────┤
│ Coverage Details (file-level breakdown in Streamlit)  │
├─────────────────────────────────────────────────────────┤
│ Test Results (individual test outcomes)               │
├─────────────────────────────────────────────────────────┤
│ Execution Logs (stdout, stderr, errors)               │
└─────────────────────────────────────────────────────────┘
```

### 4. Analysis Page
- **Data Analysis**: Historical data analysis
- **Trading Signals**: Technical analysis indicators
- **Performance Metrics**: Portfolio performance analysis
- **Risk Assessment**: Risk analysis tools

### 5. Settings Page
- **User Preferences**: User-specific settings
- **System Configuration**: System-level settings
- **API Configuration**: API key management
- **Display Options**: UI customization

## Component Details

### 1. Portfolio Overview
```python
def display_portfolio_summary():
    """
    Display portfolio metrics in a compact format.
    
    Primary Metrics:
    - Total Value
    - Daily P&L
    - Open Positions
    - Win Rate
    
    Secondary Metrics (in expander):
    - Average Trade
    - Risk/Reward Ratio
    - Maximum Drawdown
    - Pending Orders
    """
```

### 2. Market Overview
```python
def display_market_overview():
    """
    Display market information in three columns.
    
    Column 1 - Major Indices:
    - S&P 500
    - NASDAQ
    - DOW
    
    Column 2 - Tech Leaders:
    - AAPL
    - MSFT
    - GOOGL
    
    Column 3 - Market Breadth:
    - Advancers
    - Decliners
    - New Highs
    """
```

### 3. Recent Activity
```python
def display_recent_activity():
    """
    Display recent trading activity.
    
    Format:
    - Action type (Buy/Sell/Limit)
    - Symbol and shares
    - Price
    - Time
    """
```

### 4. Market News
```python
def display_market_news():
    """
    Display market news from database.
    
    Features:
    - Latest 3 articles
    - Expandable article details
    - Source and publication time
    - Article links
    - Error handling for missing data
    """
```

## Styling and CSS

### 1. Custom CSS (`config/streamlit_style.css`)
```css
/* Professional styling for the trading dashboard */
.main-header {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
    color: white;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
}

.metric-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 0.5rem;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.status-indicator {
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-weight: bold;
    font-size: 0.875rem;
}

.status-open {
    background-color: #d4edda;
    color: #155724;
}

.status-closed {
    background-color: #f8d7da;
    color: #721c24;
}
```

### 2. Responsive Design
```css
/* Mobile-first responsive design */
@media (max-width: 768px) {
    .metric-grid {
        grid-template-columns: 1fr;
    }
    
    .market-overview {
        flex-direction: column;
    }
}

@media (min-width: 769px) {
    .metric-grid {
        grid-template-columns: repeat(4, 1fr);
    }
    
    .market-overview {
        flex-direction: row;
    }
}
```

## Refresh System

### 1. Simple Refresh Controls

The application uses a simple and effective refresh system based on Streamlit's built-in session state and rerun functionality.

#### **Main Refresh Button**
```python
# Sidebar refresh control
if st.button("🔄 Refresh All Data", help="Force refresh all data"):
    # Clear session state
    for key in list(st.session_state.keys()):
        if key != 'cache_manager':
            del st.session_state[key]
    st.rerun()
```

#### **Page-Specific Refresh**
```python
# Symbol analysis refresh
if st.button("🔄 Refresh", help="Refresh symbol data"):
    st.session_state.selected_symbol = None
    st.rerun()

# Model performance refresh
if st.button("🔄 Refresh Data", help="Manually refresh all data"):
    st.rerun()
```

### 2. Refresh Strategy

#### **Session State Clearing**
- Clears all session state variables
- Forces fresh data loading on next render
- Simple and reliable approach

#### **Rerun Mechanism**
- Uses `st.rerun()` to restart the app
- Ensures all data is reloaded from source
- No complex caching logic required

### 3. Refresh Controls

#### **Sidebar Controls**
- **🔄 Refresh All Data**: Main refresh button for entire app
- **💡 Help Text**: Clear instructions for users

#### **Page-Specific Controls**
- **Symbol Analysis**: Inline refresh button
- **Model Performance**: Data refresh button
- **Testing Results**: JSON refresh button

### 4. Benefits of Simple Approach

#### **Reliability**
- No complex cache management
- Uses Streamlit's built-in mechanisms
- Fewer points of failure

#### **Maintainability**
- Simple code structure
- Easy to understand and debug
- No external dependencies

#### **Performance**
- Direct data reloading
- No cache invalidation complexity
- Predictable behavior

## Data Integration

### 1. PortfolioManager Architecture

#### **Singleton Pattern Implementation**
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

#### **Shared Instance Management**
```python
# In UI modules (home.py, portfolio.py)
_portfolio_manager = None

def get_portfolio_manager():
    """Get or create a shared portfolio manager instance."""
    global _portfolio_manager
    if _portfolio_manager is None:
        _portfolio_manager = PortfolioManager()
    return _portfolio_manager

def clear_portfolio_manager():
    """Clear the shared portfolio manager instance."""
    global _portfolio_manager
    _portfolio_manager = None
```

#### **Caching System**
```python
def _get_cached_data(self, key: str):
    """Get data from cache if it's still valid."""
    if key in self._cache and key in self._cache_timestamps:
        timestamp = self._cache_timestamps[key]
        cache_duration = 10 if key.startswith('orders_') else self._cache_duration
        if datetime.now() - timestamp < timedelta(seconds=cache_duration):
            return self._cache[key]
    return None

def _set_cached_data(self, key: str, data):
    """Store data in cache with timestamp."""
    self._cache[key] = data
    self._cache_timestamps[key] = datetime.now()
```

#### **Cache Duration Strategy**
- **Orders**: 10 seconds (frequently changing data)
- **Account Info**: 30 seconds (relatively stable)
- **Positions**: 30 seconds (moderately stable)
- **Portfolio Summary**: 30 seconds (computed from other cached data)

### 2. Database Connectivity
```python
from src.database.database_connectivity import DatabaseConnectivity

def get_market_data():
    """Fetch market data from database."""
    db = DatabaseConnectivity()
    with db.get_session() as cursor:
        cursor.execute("SELECT * FROM market_data ORDER BY timestamp DESC LIMIT 100")
        return cursor.fetchall()
```

### 3. News Integration
```python
def get_news_articles():
    """Fetch news articles from database."""
    db = DatabaseConnectivity()
    with db.get_session() as cursor:
        cursor.execute("""
            SELECT title, source_name, url, published_at, description
            FROM news_articles
            ORDER BY published_at DESC
            LIMIT 3
        """)
        return cursor.fetchall()
```

### 4. Real-time Data
```python
def get_live_market_data():
    """Get real-time market data."""
    # Integration with WebSocket or API calls
    pass
```

## Error Handling

### 1. Data Loading Errors
```python
def safe_data_loading(func):
    """Decorator for safe data loading with error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return None
    return wrapper
```

### 2. UI Error States
```python
def display_with_fallback(data, fallback_message="No data available"):
    """Display data with fallback for empty states."""
    if data is None or len(data) == 0:
        st.info(fallback_message)
    else:
        # Display actual data
        pass
```

## Performance Optimization

### 1. PortfolioManager Singleton Pattern
```python
# Single instance across all UI components
def get_portfolio_manager():
    """Get or create a shared portfolio manager instance."""
    global _portfolio_manager
    if _portfolio_manager is None:
        _portfolio_manager = PortfolioManager()
    return _portfolio_manager
```

### 2. Intelligent Caching System
```python
# Cache with different durations for different data types
def get_account_info(self):
    """Get account information with caching."""
    cached_data = self._get_cached_data('account_info')
    if cached_data:
        return cached_data
    
    # Fetch from API if not cached
    data = self._fetch_account_info()
    self._set_cached_data('account_info', data)
    return data
```

### 3. Cache Invalidation Strategy
```python
# Clear cache on manual refresh
if st.button("🔄 Refresh All Data"):
    clear_portfolio_manager()  # Clears singleton instance
    st.rerun()  # Forces complete refresh
```

### 4. Lazy Loading
```python
def lazy_load_component(component_func, *args, **kwargs):
    """Lazy load UI components for better performance."""
    with st.spinner("Loading..."):
        return component_func(*args, **kwargs)
```

### 5. Efficient Rendering
```python
def optimize_rendering():
    """Optimize UI rendering performance."""
    # Use st.container() for complex layouts
    # Minimize re-renders through caching
    # Use efficient data structures
    pass
```

### 6. API Call Optimization
- **Reduced API Calls**: Caching eliminates redundant calls
- **Rate Limit Respect**: Intelligent caching prevents hitting API limits
- **Batch Operations**: Group related API calls when possible
- **Error Handling**: Graceful degradation when API calls fail

## Accessibility

### 1. WCAG 2.1 Compliance
- **Color Contrast**: Sufficient color contrast ratios
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: Proper ARIA labels
- **Focus Indicators**: Clear focus indicators

### 2. User Experience
- **Loading States**: Clear loading indicators
- **Error Messages**: Helpful error messages
- **Success Feedback**: Confirmation messages
- **Progressive Disclosure**: Information revealed progressively

## Portfolio Management

### Overview

The Portfolio Management system provides comprehensive portfolio tracking and analysis using real-time data from your Alpaca trading account. It replaces dummy data with actual account information, positions, and performance metrics.

### Features

#### 1. Real-Time Portfolio Data
- **Account Overview**: Portfolio value, cash, buying power, equity
- **Current Positions**: All open positions with real-time pricing and P&L
- **Trading History**: Recent orders and performance metrics
- **Risk Analysis**: Margin utilization, position concentration, and risk warnings
- **Intelligent Caching**: Multi-tier caching system for optimal performance

#### 2. Portfolio Dashboard (Home Page)
The home page displays:
- Real portfolio value and daily P&L
- Actual number of open positions
- Calculated win rate from trading history
- Recent trading activity from your account
- Additional metrics like margin usage and buying power
- Shared PortfolioManager instance for efficient data access

#### 3. Comprehensive Portfolio Page
A dedicated portfolio page provides:
- **Account Overview**: Detailed account information and status
- **Position Table**: Complete list of positions with P&L calculations
- **Portfolio Allocation**: Pie chart showing position distribution
- **Trading History**: Detailed order history and performance metrics
- **Risk Analysis**: Comprehensive risk metrics and warnings
- **Shared PortfolioManager**: Uses singleton instance for data access

### Setup

#### 1. Alpaca API Configuration
Ensure your Alpaca API credentials are properly configured in `config/.env`:

```bash
ALPACA_API_KEY=your_alpaca_api_key
ALPACA_SECRET_KEY=your_alpaca_secret_key
```

#### 2. Testing the Connection
Run the test script to verify your setup:

```bash
python scripts/run_tests.py database
```

This will test:
- API connection to Alpaca
- Account information retrieval
- Position data fetching
- Portfolio metrics calculation

### Usage

#### Home Page
The home page automatically displays your real portfolio data:
- Portfolio overview with key metrics
- Recent trading activity
- Quick access to portfolio details

#### Portfolio Page
Navigate to the "Portfolio" page in the sidebar for detailed analysis:

1. **Account Overview**: View account balance, buying power, and status
2. **Positions**: See all current positions with P&L
3. **Allocation**: Visual representation of portfolio distribution
4. **Trading History**: Review recent trades and performance
5. **Risk Analysis**: Monitor risk metrics and warnings

### Portfolio Metrics

#### Key Metrics Displayed
- **Total Value**: Portfolio value including cash and positions
- **Daily P&L**: Unrealized profit/loss for current positions
- **Open Positions**: Number of active positions
- **Win Rate**: Percentage of profitable trades
- **Buying Power**: Available funds for new trades
- **Margin Used**: Percentage of portfolio using margin

#### Risk Metrics
- **Margin Utilization**: Percentage of portfolio using margin
- **Position Concentration**: Largest position as percentage of portfolio
- **Pattern Day Trader Status**: PDT restrictions and warnings
- **Trading Status**: Account trading permissions

### Data Sources

#### Alpaca API Integration
The portfolio system integrates with Alpaca's API to fetch:
- Account information and balance
- Current positions and pricing
- Order history and fills
- Real-time market data for calculations

#### Data Refresh
- **Intelligent Caching**: Multi-tier caching system with different durations
  - Orders: 10 seconds (frequently changing data)
  - Account Info: 30 seconds (relatively stable)
  - Positions: 30 seconds (moderately stable)
  - Portfolio Summary: 30 seconds (computed from other data)
- **Centralized Refresh**: Single refresh button in sidebar for all data
- **Cache Invalidation**: Automatic cache clearing on manual refresh
- **Performance Optimized**: No automatic page refreshes causing excessive API calls

### Error Handling

#### Fallback Behavior
If the Alpaca API is unavailable or credentials are invalid:
- Home page shows error message with fallback to dummy data
- Portfolio page displays error with troubleshooting tips
- Test script provides detailed error information

#### Common Issues
1. **Invalid API Credentials**: Check your Alpaca API key and secret
2. **Network Issues**: Verify internet connection and API accessibility
3. **Account Status**: Ensure your Alpaca account is active
4. **Rate Limits**: Alpaca API has rate limits for data requests

### Technical Implementation

#### PortfolioManager Class
Located in `src/data/sources/portfolio_manager.py`:
- **Singleton Pattern**: Single instance across all UI components
- **Intelligent Caching**: Multi-tier caching system with different durations
- **API Management**: Manages Alpaca API connections efficiently
- **Data Fetching**: Fetches account and position data with caching
- **Metrics Calculation**: Calculates portfolio metrics from cached data
- **Cache Management**: Provides cache invalidation and refresh capabilities

#### UI Components
- **Home Page**: `src/ui/home.py` - Updated to use shared PortfolioManager instance
- **Portfolio Page**: `src/ui/portfolio.py` - Uses singleton instance for data access
- **Main App**: `src/ui/streamlit_app.py` - Centralized refresh functionality
- **Shared Instance Management**: Global instance management with get_portfolio_manager() and clear_portfolio_manager()

#### Dependencies
- `alpaca-py`: Alpaca API client
- `plotly`: Chart generation for portfolio allocation
- `pandas`: Data processing and analysis
- `streamlit`: UI framework

### Troubleshooting

#### Common Problems

1. **"0 orders found" when you have open orders**
   This is the most common issue and is almost always caused by an **API key mismatch**. You might be viewing one paper account in your web browser, but your `config/.env` file is using keys for a *different* paper account.

   **Solution:**
   - **Log in to your Alpaca paper trading dashboard.**
   - **Navigate to the API Keys section.**
   - **Regenerate your API keys.** You will only see the secret key once, so copy it immediately.
   - **Paste the new API Key and Secret Key** into your `config/.env` file.
   - This guarantees you are using the correct keys for the account you are viewing.

2. **"Unable to fetch portfolio data"**
   - Check that your Alpaca API credentials in `config/.env` are correct.
   - Verify your internet connection.
   - Ensure your Alpaca account is active and that you have agreed to the latest terms of service.

3. **"Error loading portfolio data"**
   - Run the test script for detailed error information: `python scripts/run_tests.py database`
   - Check the logs in the `logs/` directory for detailed error messages and tracebacks.
   - Make sure the Alpaca API service is operational by checking their status page.

#### Getting Help
1. **Run the test script:** `python scripts/run_tests.py database`
2. Check the logs for detailed error messages.

## Testing

### 1. UI Testing
```python
def test_ui_components():
    """Test UI components functionality."""
    # Test market status display
    # Test symbol selector
    # Test data loading
    # Test error handling
    pass
```

### 2. Responsive Testing
```python
def test_responsive_design():
    """Test responsive design across devices."""
    # Test mobile layout
    # Test tablet layout
    # Test desktop layout
    pass
```

## Deployment

### 1. Local Development
```bash
# Run Streamlit app locally
streamlit run src/ui/streamlit_app.py

# Run with debug mode
streamlit run src/ui/streamlit_app.py --debug

# Run with custom port
streamlit run src/ui/streamlit_app.py --server.port 8502
```

### 2. Production Deployment
```bash
# Build and deploy
# (Add your deployment steps here)

# Environment variables
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

## Best Practices

### 1. UI Development
- Use consistent component patterns
- Implement proper error handling
- Optimize for performance
- Follow accessibility guidelines

### 2. Data Display
- Use appropriate data visualizations
- Implement proper data formatting
- Handle empty states gracefully
- Provide data context

### 3. User Experience
- Keep interfaces simple and intuitive
- Provide clear navigation
- Use consistent terminology
- Implement proper feedback mechanisms

## Summary

The Prefect Trading System UI provides a comprehensive, user-friendly interface for trading operations with the following key features:

### **Core Architecture**
- **Singleton PortfolioManager**: Single instance across all UI components for efficient resource usage
- **Intelligent Caching**: Multi-tier caching system with different durations for different data types
- **Centralized Refresh**: Single refresh button in sidebar for consistent user experience
- **Performance Optimized**: Eliminated auto-refresh to prevent excessive API calls

### **User Experience**
- **Clean Interface**: Professional styling with consistent design patterns
- **Responsive Design**: Optimized for mobile, tablet, and desktop devices
- **Interactive Components**: Advanced tables, charts, and search functionality
- **Real-time Data**: Live market data through intelligent caching system

### **Performance Features**
- **API Efficiency**: Reduced API calls through intelligent caching
- **Rate Limit Management**: Respects API rate limits through cache duration strategy
- **Fast Response Times**: Cached data provides instant UI updates
- **Resource Optimization**: Single PortfolioManager instance reduces memory usage

### **Data Management**
- **Cache Duration Strategy**: 
  - Orders: 10 seconds (frequently changing)
  - Account Info: 30 seconds (relatively stable)
  - Positions: 30 seconds (moderately stable)
  - Portfolio Summary: 30 seconds (computed data)
- **Cache Invalidation**: Automatic clearing on manual refresh
- **Error Handling**: Graceful degradation when data is unavailable

### **Testing Integration**
- **Coverage Display**: Real-time test coverage metrics with visual indicators
- **Interactive Tables**: Streamlit dataframes with advanced table functionality
- **Test Execution**: Direct test execution from UI
- **Independent Refresh**: Separate refresh functionality for testing operations

The UI architecture prioritizes performance, user experience, and maintainability while providing comprehensive trading functionality in a modern, responsive interface.

### Related Documentation

- **[Architecture Decisions](architecture-decisions.md)**: UI/UX design rationale and decisions
- **[Development Guide](development.md)**: UI development practices and workflows
- **[Testing Guide](testing.md)**: UI testing strategies and implementation
- **[Setup Guide](setup.md)**: UI setup and configuration
- **[API Documentation](api.md)**: Backend API integration 