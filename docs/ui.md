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

### 4. Analysis Page (`src/ui/components/symbol_selector.py`)
- **Symbol Selection**: Dropdown with 22+ active symbols from database
- **Comprehensive Analysis**: Multi-tab interface for detailed symbol analysis
- **Market Data Analysis**: Price charts, statistics, and recent data
- **Company Information**: Financial metrics, officers, and business summary
- **Real-time Statistics**: Current price, change, volume, and volatility metrics

### 5. Testing Page (`src/ui/components/testing_results.py`)
- **Coverage Overview**: Overall test coverage metrics with visual indicators
- **File-Level Coverage**: Detailed breakdown by individual files
- **Test Results**: Comprehensive test execution results
- **Execution Logs**: Detailed logs and error information
- **Interactive Tables**: AgGrid integration for advanced table functionality
- **Independent Refresh**: Separate refresh functionality for test execution

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
    - File-level coverage breakdown in interactive AgGrid tables
    - Test execution results and statistics
    - Real-time coverage data from JSON reports
    - Professional styling with progress indicators
    - Manual refresh and test execution capabilities
    """
```

For detailed rationale behind UI architecture decisions, see [Architecture Decisions](architecture-decisions.md).

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
- **AgGrid Tables**: Advanced table functionality with sorting, filtering, and pagination

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
    Display file-level coverage in an interactive AgGrid table.
    
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
- **AgGrid Integration**: Replaced basic tables with advanced AgGrid functionality
- **Path Normalization**: Fixed Windows/Unix path differences for accurate coverage display
- **Deprecation Fixes**: Removed deprecated `fit_columns_on_grid_load` parameter
- **Enhanced Sorting**: Improved table sorting with numeric value preservation
- **Better Error Handling**: Graceful handling of missing coverage data
- **Test Execution**: Added ability to run tests directly from the UI
- **Real-time Updates**: Manual refresh capabilities for immediate data updates

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
│ Coverage Details (file-level breakdown in AgGrid)     │
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
- **Interactive Tables**: AgGrid integration for advanced table functionality
- **Test Execution**: Direct test execution from UI
- **Independent Refresh**: Separate refresh functionality for testing operations

The UI architecture prioritizes performance, user experience, and maintainability while providing comprehensive trading functionality in a modern, responsive interface.

### Related Documentation

- **[Architecture Decisions](architecture-decisions.md)**: UI/UX design rationale and decisions
- **[Development Guide](development.md)**: UI development practices and workflows
- **[Testing Guide](testing.md)**: UI testing strategies and implementation
- **[Setup Guide](setup.md)**: UI setup and configuration
- **[API Documentation](api.md)**: Backend API integration 