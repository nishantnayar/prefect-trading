-- =====================================================
-- CONSOLIDATED DATA SOURCE ENHANCEMENT MIGRATION
-- Combines migration 008 into a single script
-- =====================================================

-- Migration: Add data_source column to market_data table
-- This allows tracking whether data came from Alpaca or was recycled

-- Add data_source column with default value 'alpaca' for existing data
ALTER TABLE market_data ADD COLUMN data_source VARCHAR(20) DEFAULT 'alpaca';

-- Create index for efficient filtering by data source
CREATE INDEX idx_market_data_source ON market_data(data_source);

-- Add comment to document the column purpose
COMMENT ON COLUMN market_data.data_source IS 'Source of the data: alpaca (real data) or recycled (replayed historical data)'; 