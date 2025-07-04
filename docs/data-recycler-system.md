# Data Recycler System

## Overview

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

## Architecture

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

## Current Configuration

### Pairs Trading Setup
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

### Symbol Mapping Logic
- **AAPL**: Uses actual AAPL data from database
- **PDFS**: Uses AAPL data as proxy (until real PDFS data is available)
- **ROG**: Uses AAPL data as proxy (until real ROG data is available)

## Components

### 1. Multi-Symbol Data Recycler Server (`src/data/sources/data_recycler_server.py`)

A local WebSocket server that:
- Loads historical data from the `market_data` table for multiple symbols
- Automatically maps missing symbols to AAPL data as proxy
- Replays data in Alpaca WebSocket format with current timestamps
- Uses 60-second intervals between messages to simulate real market data timing
- Supports multiple replay modes and speed controls
- Streams data for all configured symbols simultaneously

### 2. Configurable WebSocket Client (`src/data/sources/configurable_websocket.py`)

A WebSocket client that:
- Can connect to either Alpaca or the data recycler server
- Uses the same interface as the original Alpaca WebSocket
- Stores data with source identification (`data_source` column)
- Maintains all existing functionality

### 3. Configuration System (`src/utils/websocket_config.py`)

Configuration management that:
- Loads WebSocket settings from `config.yaml`
- Supports environment variable overrides
- Provides easy switching between modes
- Manages symbol configuration and proxy fallback

### 4. Utility Scripts

- `scripts/manage_symbols.py` - Manage symbol configuration and check data status
- `scripts/test_multi_symbol_recycler.py` - Test the multi-symbol system
- `scripts/start_data_recycler.py` - Start the data recycler server
- `scripts/run_configurable_websocket.py` - Run the configurable client

## Usage

### 1. Check Current Status
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

### 2. Start Data Recycler Server
```bash
python -m src.data.sources.data_recycler_server
```

### 3. Test the System
```bash
python scripts/test_multi_symbol_recycler.py
```

### 4. Check Data Status (After Monday's Data Collection)
```bash
python scripts/manage_symbols.py status
```

## Symbol Management

### Switch to Pairs Trading Mode
```bash
python scripts/manage_symbols.py pairs
```

### Switch to Testing Mode
```bash
python scripts/manage_symbols.py testing
```

### Add/Remove Symbols
```bash
# Add a symbol
python scripts/manage_symbols.py add MSFT

# Remove a symbol
python scripts/manage_symbols.py remove PDFS
```

## Data Collection Strategy

### Phase 1: Proxy Data (Current)
- Use AAPL data as proxy for PDFS and ROG
- Test pairs trading infrastructure immediately
- Develop and validate trading algorithms

### Phase 2: Real Data Collection & Automatic Transition
- Start collecting real PDFS and ROG data during market hours (Monday)
- On Tuesday, check data availability: `python scripts/manage_symbols.py status`
- If data is available, the system automatically uses real data
- No code changes needed - the system handles the transition seamlessly

## Replay Modes

### 1. Loop Mode (Default)
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
    symbols: ["AAPL", "PDFS", "ROG"]
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
    symbols: ["AAPL", "PDFS", "ROG"]
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

## Database Schema

### Data Source Column
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

## Message Format

The data recycler sends messages in Alpaca WebSocket format:

```json
[
  {
    "S": "AAPL",
    "t": "2025-07-04T16:34:37.123456",
    "o": 150.25,
    "h": 151.50,
    "l": 149.75,
    "c": 150.75,
    "v": 1000000
  },
  {
    "S": "PDFS",
    "t": "2025-07-04T16:34:37.123456",
    "o": 150.25,
    "h": 151.50,
    "l": 149.75,
    "c": 150.75,
    "v": 1000000
  },
  {
    "S": "ROG",
    "t": "2025-07-04T16:34:37.123456",
    "o": 150.25,
    "h": 151.50,
    "l": 149.75,
    "c": 150.75,
    "v": 1000000
  }
]
```

**Note**: PDFS and ROG currently use AAPL data with their own symbol names.

## Configuration Options

### Main Configuration (`config/config.yaml`)
```yaml
websocket:
  mode: "recycler"  # "alpaca" or "recycler"
  symbols: ["AAPL", "PDFS", "ROG"]
  recycler:
    server_url: "ws://localhost:8765"
    replay_mode: "loop"  # "loop", "date_range", "single_pass"
    replay_speed: 1.0
    date_range:
      start_date: "2025-06-23"  # Your earliest available data
      end_date: "2025-06-30"    # Example date range
    symbols: ["AAPL", "PDFS", "ROG"]
    loop_count: -1  # -1 = infinite, 1 = single pass
    data_retention:
      recycled_data_days: 1  # Keep recycled data for 1 day
      auto_cleanup: true     # Automatically clean up old data
```

### Environment Variables
```bash
# Override configuration via environment variables
export WEBSOCKET_MODE=recycler
export RECYCLER_REPLAY_SPEED=2.0
export RECYCLER_SYMBOLS=AAPL,PDFS,ROG
```

## Benefits

### Immediate Testing
- Test pairs trading infrastructure without waiting for real data
- Validate trading algorithms with realistic market data patterns
- Develop and debug during non-market hours

### Easy Transition
- No code changes when real data becomes available
- Automatic fallback to proxy data when needed
- Seamless switching between testing and production modes

### Configuration Flexibility
- Easy to add/remove symbols via configuration
- Support for different replay modes and speeds
- Environment-specific configurations

### Risk Mitigation
- Zero risk to existing functionality
- Proxy data provides realistic testing environment
- Easy rollback if issues arise

## Troubleshooting

### Connection Issues
```bash
# Check if server is running
python scripts/test_multi_symbol_recycler.py

# Start server if needed
python -m src.data.sources.data_recycler_server
```

### Configuration Issues
```bash
# Validate configuration
python scripts/manage_symbols.py status

# Reset to default
python scripts/manage_symbols.py testing
```

### Data Issues
```bash
# Check data availability
python scripts/manage_symbols.py status

# Verify after Monday's data collection
python scripts/manage_symbols.py status
```

### Common Issues

1. **Connection Closes Immediately**
   - **Expected Behavior**: The current implementation streams all data once then closes
   - **Solution**: This is normal for single pass mode. Restart the server to replay data again
   - **Alternative**: Modify server code to implement loop mode for continuous streaming

2. **No Historical Data Available**
   - Ensure `market_data` table has data for the requested symbols starting from 2025-06-23
   - Check date ranges are within your available data period
   - Use the data availability checker utility

3. **WebSocket Connection Failed**
   - Verify data recycler server is running on correct port (8765)
   - Check firewall settings
   - Ensure no other service is using port 8765

4. **Timing Issues**
   - **Current Setting**: 60-second intervals between messages
   - **Adjustment**: Modify `REPLAY_DELAY_SECONDS` in `data_recycler_server.py`
   - **Real-time Simulation**: Messages use current timestamps, not historical ones

## Integration with Existing System

The data recycler system integrates seamlessly with your existing system:

- **WebSocket Clients**: Use existing `configurable_websocket.py`
- **Database**: Uses existing `market_data` table
- **Configuration**: Extends existing `config.yaml` structure
- **Utilities**: Works with existing data management scripts

## Success Metrics

- **Immediate Testing**: Can test pairs trading with PDFS/ROG symbols
- **Simple Transition**: One command to check data availability
- **Automatic Switch**: System uses real data when available
- **System Stability**: No impact on existing functionality

## Future Enhancements

1. **Advanced Proxy Logic**: Use multiple symbols as proxy data
2. **Data Quality Metrics**: Monitor proxy data quality vs real data
3. **Automated Data Collection**: Schedule data collection for missing symbols
4. **Performance Optimization**: Optimize for large datasets
5. **Web UI**: Web interface for managing symbol configuration
6. **Multiple Data Sources**: Support for multiple historical data sources
7. **Advanced Filtering**: Filter data by volume, price ranges, etc.
8. **Scenario Builder**: Create custom market scenarios

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