-- =====================================================
-- CONSOLIDATED HISTORICAL DATA MIGRATION
-- Combines migration 010 into a single script
-- =====================================================

-- Migration: Create market_data_historical table for historical market data
-- This table is optimized for storing historical market data at various timeframes

-- Create market_data_historical table
CREATE TABLE IF NOT EXISTS market_data_historical (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open FLOAT NOT NULL,
    high FLOAT NOT NULL,
    low FLOAT NOT NULL,
    close FLOAT NOT NULL,
    volume INTEGER NOT NULL,
    data_source VARCHAR(20) DEFAULT 'alpaca',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance on historical data
CREATE INDEX IF NOT EXISTS idx_market_data_historical_symbol ON market_data_historical(symbol);
CREATE INDEX IF NOT EXISTS idx_market_data_historical_timestamp ON market_data_historical(timestamp);
CREATE INDEX IF NOT EXISTS idx_market_data_historical_symbol_timestamp ON market_data_historical(symbol, timestamp);
CREATE INDEX IF NOT EXISTS idx_market_data_historical_data_source ON market_data_historical(data_source);

-- Create unique constraint to prevent duplicate entries
CREATE UNIQUE INDEX IF NOT EXISTS idx_market_data_historical_unique ON market_data_historical(symbol, timestamp);

-- Add comments to document the table purpose
COMMENT ON TABLE market_data_historical IS 'Historical market data for analysis at various timeframes';
COMMENT ON COLUMN market_data_historical.data_source IS 'Source of the data: alpaca (real data) or recycled (replayed historical data)';
COMMENT ON COLUMN market_data_historical.created_at IS 'Timestamp when this record was inserted into the database'; 