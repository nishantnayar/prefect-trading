# Data Recycler WebSocket System

## Overview

The Data Recycler WebSocket System allows you to recycle existing market data from your database to simulate real-time market data feeds during non-market hours. This system creates a local WebSocket server that replays historical data in the same format as Alpaca's WebSocket API, enabling seamless testing and development without requiring live market data.

**Note**: Your database contains market data starting from **2025-06-23**. All replay scenarios will use dates from this period onwards.

## Key Features

- **Real Market Data**: Uses actual historical market data instead of generated dummy data
- **Multiple Replay Modes**: Loop, date range, and single pass replay options
- **Speed Control**: Adjustable replay speed (0.5x to 10x real-time)
- **Seamless Switching**: Easy configuration to switch between real Alpaca and recycled data
- **Data Source Tracking**: Clear identification of recycled vs real data in database
- **Zero Risk**: Original files remain unchanged, new system is completely separate

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Configurable  │    │   Data Recycler  │    │   Database      │
│   WebSocket     │◄──►│   Server         │◄──►│   (market_data) │
│   Client        │    │   (Local)        │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌──────────────────┐
│   Redis Cache   │    │   Configuration  │
│   (Real-time)   │    │   (config.yaml)  │
└─────────────────┘    └──────────────────┘
```

## Components

### 1. Data Recycler Server (`src/data/sources/data_recycler_server.py`)

A local WebSocket server that:
- Loads historical data from the `market_data` table (starting from 2025-06-23)
- Replays data in Alpaca WebSocket format
- Supports multiple replay modes and speed controls
- Simulates authentication and subscription responses

### 2. Configurable WebSocket Client (`src/data/sources/configurable_websocket.py`)

A new WebSocket client that:
- Can connect to either Alpaca or the data recycler server
- Uses the same interface as the original Alpaca WebSocket
- Stores data with source identification (`data_source` column)
- Maintains all existing functionality

### 3. Configuration System (`src/utils/websocket_config.py`)

Configuration management that:
- Loads WebSocket settings from `config.yaml`
- Supports environment variable overrides
- Provides easy switching between modes

### 4. Utility Scripts

- `scripts/start_data_recycler.py` - Start the data recycler server
- `scripts/run_configurable_websocket.py` - Run the configurable client
- `scripts/switch_to_recycler.py` - Switch configuration to recycler mode
- `scripts/switch_to_alpaca.py` - Switch configuration to Alpaca mode

## Replay Modes

### 1. Loop Mode (Default)
```yaml
websocket:
  mode: "recycler"
  recycler:
    replay_mode: "loop"
    replay_speed: 1.0
    symbols: ["AAPL"]
    loop_count: -1  # -1 = infinite loop
```

**Features:**
- Continuously loops through all available historical data (from 2025-06-23 onwards)
- When reaching the end, starts over from the beginning
- Ideal for continuous testing and development

### 2. Date Range Mode
```yaml
websocket:
  mode: "recycler"
  recycler:
    replay_mode: "date_range"
    date_range:
      start_date: "2025-06-23"  # Your earliest available data
      end_date: "2025-06-30"    # Example: first week of data
    replay_speed: 2.0
    symbols: ["AAPL", "MSFT"]
```

**Features:**
- Replays data from specific date ranges within your available data
- Useful for testing specific market conditions or events
- Can replay volatile periods, earnings announcements, etc.

### 3. Single Pass Mode
```yaml
websocket:
  mode: "recycler"
  recycler:
    replay_mode: "single_pass"
    replay_speed: 5.0
    symbols: ["AAPL"]
    loop_count: 1
```

**Features:**
- Replays data once and stops
- Good for one-time testing scenarios
- Can be used for automated testing

## Speed Control

The replay speed can be adjusted to accelerate testing:

- `0.5x`: Half speed (slower than real-time)
- `1.0x`: Real-time speed (same as original data)
- `2.0x`: Twice as fast
- `5.0x`: Five times faster
- `10.0x`: Ten times faster

## Database Schema Changes

### New Column: `data_source`

```sql
ALTER TABLE market_data ADD COLUMN data_source VARCHAR(20) DEFAULT 'alpaca';
CREATE INDEX idx_market_data_source ON market_data(data_source);
```

**Values:**
- `'alpaca'` - Original Alpaca data
- `'recycled'` - Replayed historical data

### Data Source Utilities

```python
# Get only real Alpaca data
real_data = get_market_data_by_source('alpaca', 'AAPL')

# Get only recycled data
recycled_data = get_market_data_by_source('recycled', 'AAPL')

# Get all data with source information
all_data = db.query("""
    SELECT *, data_source 
    FROM market_data 
    WHERE symbol = 'AAPL' 
    ORDER BY timestamp DESC
""")
```

## Configuration

### Main Configuration (`config/config.yaml`)

```yaml
websocket:
  mode: "recycler"  # "alpaca" or "recycler"
  recycler:
    server_url: "ws://localhost:8765"
    replay_mode: "loop"  # "loop", "date_range", "single_pass"
    replay_speed: 1.0
    date_range:
      start_date: "2025-06-23"  # Your earliest available data
      end_date: "2025-06-30"    # Example date range
    symbols: ["AAPL", "MSFT", "GOOGL"]
    loop_count: -1  # -1 = infinite, 1 = single pass
    data_retention:
      recycled_data_days: 1  # Keep recycled data for 1 day
      auto_cleanup: true     # Automatically clean up old recycled data
```

### Environment Variables

```bash
# Override configuration via environment variables
export WEBSOCKET_MODE=recycler
export RECYCLER_REPLAY_SPEED=2.0
export RECYCLER_SYMBOLS=AAPL,MSFT
```

## Usage

### 1. Start Data Recycler Server

```bash
# Start the data recycler server
python scripts/start_data_recycler.py

# Or run directly
python -m src.data.sources.data_recycler_server
```

### 2. Run Configurable WebSocket Client

```bash
# Run the configurable websocket client
python scripts/run_configurable_websocket.py

# Or run the new main file
python main_configurable.py
```

### 3. Switch Between Modes

```bash
# Switch to recycler mode
python scripts/switch_to_recycler.py

# Switch back to Alpaca mode
python scripts/switch_to_alpaca.py
```

### 4. Clean Up Recycled Data

```bash
# Clean up old recycled data
python scripts/cleanup_recycled_data.py
```

## Integration with Existing System

### File Structure

```
src/data/sources/
├── alpaca_websocket.py (UNCHANGED - original)
├── data_recycler_server.py (NEW)
├── configurable_websocket.py (NEW)
├── websocket_runner.py (NEW)
└── hourly_persistence.py (unchanged)

src/utils/
└── websocket_config.py (NEW)

scripts/
├── start_data_recycler.py (NEW)
├── run_configurable_websocket.py (NEW)
├── switch_to_recycler.py (NEW)
├── switch_to_alpaca.py (NEW)
└── cleanup_recycled_data.py (NEW)

main_configurable.py (NEW - optional)
```

### Migration Strategy

1. **Phase 1**: Implement data recycler server and configurable client
2. **Phase 2**: Test thoroughly with recycled data
3. **Phase 3**: Gradually migrate to using the configurable system
4. **Phase 4**: Update Prefect deployments to use new system (optional)
5. **Phase 5**: Keep original files as backup for emergency rollback

### Rollback Plan

If issues arise, rollback is simple:

```bash
# Stop using configurable system
python main.py  # Use original system

# Or switch back to Alpaca mode
python scripts/switch_to_alpaca.py
```

## Testing Scenarios

### 1. Continuous Development Testing
```yaml
websocket:
  mode: "recycler"
  recycler:
    replay_mode: "loop"
    replay_speed: 2.0
    symbols: ["AAPL"]
```

### 2. Specific Market Event Testing
```yaml
websocket:
  mode: "recycler"
  recycler:
    replay_mode: "date_range"
    date_range:
      start_date: "2025-06-23"  # Your earliest available data
      end_date: "2025-06-25"    # Example: first few days
    replay_speed: 1.0
    symbols: ["AAPL", "MSFT"]
```

### 3. Fast Testing
```yaml
websocket:
  mode: "recycler"
  recycler:
    replay_mode: "single_pass"
    replay_speed: 10.0
    symbols: ["AAPL"]
    loop_count: 1
```

### 4. Available Data Range Testing
```yaml
websocket:
  mode: "recycler"
  recycler:
    replay_mode: "date_range"
    date_range:
      start_date: "2025-06-23"  # Your data start date
      end_date: "2025-07-23"    # Example: first month of data
    replay_speed: 1.0
    symbols: ["AAPL"]
```

## Benefits

1. **Realistic Testing**: Uses actual market data patterns and movements from your database
2. **24/7 Development**: Can test during non-market hours using your existing data
3. **Flexible Scenarios**: Replay specific market conditions or time periods from 2025-06-23 onwards
4. **Speed Control**: Accelerate testing with faster replay speeds
5. **Zero Risk**: Original system remains unchanged
6. **Easy Rollback**: Simple configuration change to switch back
7. **Data Lineage**: Clear tracking of data sources
8. **Cost Effective**: No additional API costs for testing

## Troubleshooting

### Common Issues

1. **No Historical Data Available**
   - Ensure `market_data` table has data for the requested symbols starting from 2025-06-23
   - Check date ranges are within your available data period
   - Use the data availability checker utility

2. **WebSocket Connection Failed**
   - Verify data recycler server is running on correct port
   - Check firewall settings

3. **Replay Speed Issues**
   - Adjust `replay_speed` configuration
   - Monitor system resources during high-speed replay

4. **Database Performance**
   - Consider indexing on `data_source` column
   - Implement data cleanup for old recycled data

### Data Availability Checker

```python
# Check available data ranges
from src.utils.data_recycler_utils import get_available_date_ranges

# Get available date ranges for AAPL
ranges = get_available_date_ranges('AAPL')
print(f"Available data for AAPL: {ranges}")

# Get data statistics
stats = get_data_statistics('AAPL')
print(f"Data statistics: {stats}")
```

### Debug Mode

Enable debug logging:

```yaml
logging:
  level: DEBUG
  websocket_debug: true
```

## Future Enhancements

1. **Multiple Data Sources**: Support for multiple historical data sources
2. **Advanced Filtering**: Filter data by volume, price ranges, etc.
3. **Scenario Builder**: Create custom market scenarios
4. **Performance Metrics**: Track replay performance and data quality
5. **API Endpoints**: REST API for managing recycler configuration
6. **Web UI**: Web interface for managing recycler settings

## Security Considerations

1. **Local Only**: Data recycler server runs locally only
2. **No External Connections**: Recycler doesn't connect to external services
3. **Data Isolation**: Recycled data is clearly marked and can be cleaned up
4. **Configuration Validation**: All configuration is validated before use

## Performance Considerations

1. **Memory Usage**: Large datasets may require significant memory
2. **Database Load**: Consider read-only replicas for large datasets
3. **Network**: Local WebSocket connections minimize network overhead
4. **Cleanup**: Regular cleanup of old recycled data to prevent bloat

## Data Availability Note

**Important**: Your database contains market data starting from **2025-06-23**. When configuring date ranges for replay, ensure all dates fall within this period. The system will automatically validate date ranges and warn if requested dates are outside the available data range. 