# UI Documentation

## Overview

The Prefect Trading System includes a modern, responsive Streamlit-based user interface that provides real-time market data visualization, portfolio management, and news integration. The UI is designed to be user-friendly, efficient, and accessible across different devices.

## UI Architecture

### 1. Main Application (`src/ui/streamlit_app.py`)
- **Entry Point**: Main Streamlit application
- **Navigation**: Sidebar-based navigation with multiple pages
- **Auto-refresh**: 10-second automatic page refresh
- **Custom Styling**: Professional CSS styling

### 2. Home Page (`src/ui/home.py`)
- **Dashboard Overview**: Comprehensive trading dashboard
- **Real-time Data**: Live market data with auto-refresh
- **Portfolio Summary**: Portfolio metrics and performance
- **Market Overview**: Major indices and market breadth
- **Recent Activity**: Latest trading activities
- **Quick Actions**: Common trading operations
- **Market News**: Latest news articles

### 3. UI Components (`src/ui/components/`)

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

#### Date Display Component (`date_display.py`)
```python
def get_current_cst_formatted():
    """
    Get current time in CST format.
    
    Returns:
        Formatted current time string
    """
```

## UI Features

### 1. Real-time Updates
- **Auto-refresh**: Page refreshes every 10 seconds
- **Live Data**: Real-time market data updates
- **Status Indicators**: Live market status updates
- **News Feed**: Latest news articles

### 2. Responsive Design
- **Mobile-friendly**: Optimized for mobile devices
- **Tablet Support**: Responsive layouts for tablets
- **Desktop Optimization**: Full-featured desktop experience
- **Flexible Layouts**: Adaptive column arrangements

### 3. Interactive Components
- **Expandable Sections**: Collapsible content areas
- **Interactive Charts**: Clickable data visualizations
- **Search Functionality**: Symbol and news search
- **Filtering Options**: Data filtering capabilities

### 4. Professional Styling
- **Custom CSS**: Professional appearance
- **Color Coding**: Status-based color indicators
- **Consistent Spacing**: Uniform layout spacing
- **Typography**: Readable font choices

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

### 2. Analysis Page
- **Data Analysis**: Historical data analysis
- **Trading Signals**: Technical analysis indicators
- **Performance Metrics**: Portfolio performance analysis
- **Risk Assessment**: Risk analysis tools

### 3. Settings Page
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

### 1. Database Connectivity
```python
from src.database.database_connectivity import DatabaseConnectivity

def get_market_data():
    """Fetch market data from database."""
    db = DatabaseConnectivity()
    with db.get_session() as cursor:
        cursor.execute("SELECT * FROM market_data ORDER BY timestamp DESC LIMIT 100")
        return cursor.fetchall()
```

### 2. News Integration
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

### 3. Real-time Data
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

### 1. Lazy Loading
```python
def lazy_load_component(component_func, *args, **kwargs):
    """Lazy load UI components for better performance."""
    with st.spinner("Loading..."):
        return component_func(*args, **kwargs)
```

### 2. Caching
```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_market_data():
    """Cache market data to reduce database calls."""
    return get_market_data()
```

### 3. Efficient Rendering
```python
def optimize_rendering():
    """Optimize UI rendering performance."""
    # Use st.container() for complex layouts
    # Minimize re-renders
    # Use efficient data structures
    pass
```

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