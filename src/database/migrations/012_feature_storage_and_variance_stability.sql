-- Migration 012: Feature Storage and Variance Stability Tracking System
-- This migration creates tables for storing computed features and tracking variance stability
-- Run this manually: psql -d your_database -f src/database/migrations/012_feature_storage_and_variance_stability.sql

-- ============================================================================
-- CREATE TABLES
-- ============================================================================

-- Create table for storing computed features
CREATE TABLE IF NOT EXISTS market_data_features (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    "timestamp" TIMESTAMP NOT NULL,
    
    -- Core features
    log_close DECIMAL(15,6),
    log_return DECIMAL(15,6),
    z_score DECIMAL(15,6),
    
    -- Additional computed features
    rolling_std DECIMAL(15,6),
    rolling_mean DECIMAL(15,6),
    volatility_annualized DECIMAL(15,6),
    
    -- Metadata
    feature_date DATE NOT NULL,
    computation_method VARCHAR(50) DEFAULT 'expanding_window',
    data_source VARCHAR(50) DEFAULT 'market_data_historical',
    
    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(symbol, "timestamp")
);

-- Create table for variance stability tracking
CREATE TABLE IF NOT EXISTS variance_stability_tracking (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    test_date DATE NOT NULL,
    
    -- Test metrics
    record_count INTEGER,
    arch_test_pvalue DECIMAL(10,6),
    rolling_std_cv DECIMAL(10,6),  -- Coefficient of variation
    ljung_box_pvalue DECIMAL(10,6),
    
    -- Results
    is_stable BOOLEAN NOT NULL,
    filter_reason TEXT,  -- 'arch_test_failed', 'insufficient_data', 'high_volatility', 'autocorrelation_detected'
    
    -- Test parameters
    test_window INTEGER DEFAULT 30,
    arch_lags INTEGER DEFAULT 5,
    
    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(symbol, test_date)
);

-- ============================================================================
-- CREATE INDEXES
-- ============================================================================

-- Market data features indexes
CREATE INDEX IF NOT EXISTS idx_features_symbol_timestamp ON market_data_features(symbol, "timestamp");
CREATE INDEX IF NOT EXISTS idx_features_date ON market_data_features(feature_date);
CREATE INDEX IF NOT EXISTS idx_features_symbol_date ON market_data_features(symbol, feature_date);
CREATE INDEX IF NOT EXISTS idx_features_computation_method ON market_data_features(computation_method);

-- Variance stability tracking indexes
CREATE INDEX IF NOT EXISTS idx_stability_symbol_date ON variance_stability_tracking(symbol, test_date);
CREATE INDEX IF NOT EXISTS idx_stability_date_stable ON variance_stability_tracking(test_date, is_stable);
CREATE INDEX IF NOT EXISTS idx_stability_filter_reason ON variance_stability_tracking(filter_reason);
CREATE INDEX IF NOT EXISTS idx_stability_arch_pvalue ON variance_stability_tracking(arch_test_pvalue);

-- ============================================================================
-- DROP EXISTING CONSTRAINTS (to avoid conflicts)
-- ============================================================================

DO $$ 
BEGIN
    -- Drop market_data_features constraints
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_log_close' AND table_name = 'market_data_features') THEN
        ALTER TABLE market_data_features DROP CONSTRAINT chk_log_close;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_log_return' AND table_name = 'market_data_features') THEN
        ALTER TABLE market_data_features DROP CONSTRAINT chk_log_return;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_z_score' AND table_name = 'market_data_features') THEN
        ALTER TABLE market_data_features DROP CONSTRAINT chk_z_score;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_rolling_std' AND table_name = 'market_data_features') THEN
        ALTER TABLE market_data_features DROP CONSTRAINT chk_rolling_std;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_volatility_annualized' AND table_name = 'market_data_features') THEN
        ALTER TABLE market_data_features DROP CONSTRAINT chk_volatility_annualized;
    END IF;
    
    -- Drop variance_stability_tracking constraints
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_arch_test_pvalue' AND table_name = 'variance_stability_tracking') THEN
        ALTER TABLE variance_stability_tracking DROP CONSTRAINT chk_arch_test_pvalue;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_rolling_std_cv' AND table_name = 'variance_stability_tracking') THEN
        ALTER TABLE variance_stability_tracking DROP CONSTRAINT chk_rolling_std_cv;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_ljung_box_pvalue' AND table_name = 'variance_stability_tracking') THEN
        ALTER TABLE variance_stability_tracking DROP CONSTRAINT chk_ljung_box_pvalue;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_record_count' AND table_name = 'variance_stability_tracking') THEN
        ALTER TABLE variance_stability_tracking DROP CONSTRAINT chk_record_count;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_test_window' AND table_name = 'variance_stability_tracking') THEN
        ALTER TABLE variance_stability_tracking DROP CONSTRAINT chk_test_window;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_arch_lags' AND table_name = 'variance_stability_tracking') THEN
        ALTER TABLE variance_stability_tracking DROP CONSTRAINT chk_arch_lags;
    END IF;
END $$;

-- ============================================================================
-- ADD CONSTRAINTS
-- ============================================================================

-- Market data features constraints
ALTER TABLE market_data_features 
ADD CONSTRAINT chk_log_close CHECK (log_close IS NULL OR log_close > -1000),
ADD CONSTRAINT chk_log_return CHECK (log_return IS NULL OR log_return > -100),
ADD CONSTRAINT chk_z_score CHECK (z_score IS NULL OR z_score BETWEEN -10 AND 10),
ADD CONSTRAINT chk_rolling_std CHECK (rolling_std IS NULL OR rolling_std >= 0),
ADD CONSTRAINT chk_volatility_annualized CHECK (volatility_annualized IS NULL OR volatility_annualized >= 0);

-- Variance stability tracking constraints
ALTER TABLE variance_stability_tracking
ADD CONSTRAINT chk_arch_test_pvalue CHECK (arch_test_pvalue IS NULL OR (arch_test_pvalue >= 0 AND arch_test_pvalue <= 1)),
ADD CONSTRAINT chk_rolling_std_cv CHECK (rolling_std_cv IS NULL OR rolling_std_cv >= 0),
ADD CONSTRAINT chk_ljung_box_pvalue CHECK (ljung_box_pvalue IS NULL OR (ljung_box_pvalue >= 0 AND ljung_box_pvalue <= 1)),
ADD CONSTRAINT chk_record_count CHECK (record_count IS NULL OR record_count >= 0),
ADD CONSTRAINT chk_test_window CHECK (test_window >= 10),
ADD CONSTRAINT chk_arch_lags CHECK (arch_lags >= 1 AND arch_lags <= 20);

-- ============================================================================
-- DROP EXISTING FUNCTIONS (to ensure clean recreation)
-- ============================================================================

DROP FUNCTION IF EXISTS get_stable_features_for_modeling(DATE, INTEGER);
DROP FUNCTION IF EXISTS get_variance_stability_status(DATE);
DROP FUNCTION IF EXISTS compute_features_for_symbol(VARCHAR, DATE, DATE);
DROP FUNCTION IF EXISTS test_variance_stability(VARCHAR, DATE);

-- ============================================================================
-- CREATE HELPER FUNCTIONS
-- ============================================================================

-- Function to get stable features for modeling
CREATE OR REPLACE FUNCTION get_stable_features_for_modeling(
    start_date DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    limit_count INTEGER DEFAULT 1000
)
RETURNS TABLE (
    symbol VARCHAR(10),
    "timestamp" TIMESTAMP,
    log_close DECIMAL(15,6),
    log_return DECIMAL(15,6),
    z_score DECIMAL(15,6),
    rolling_std DECIMAL(15,6),
    rolling_mean DECIMAL(15,6),
    volatility_annualized DECIMAL(15,6),
    feature_date DATE,
    is_stable BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.symbol,
        f."timestamp",
        f.log_close,
        f.log_return,
        f.z_score,
        f.rolling_std,
        f.rolling_mean,
        f.volatility_annualized,
        f.feature_date,
        v.is_stable
    FROM market_data_features f
    JOIN variance_stability_tracking v ON f.symbol = v.symbol 
        AND f.feature_date = v.test_date
    WHERE v.is_stable = true 
        AND f.feature_date >= start_date
    ORDER BY f.symbol, f."timestamp"
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get variance stability status for a specific date
CREATE OR REPLACE FUNCTION get_variance_stability_status(target_date DATE DEFAULT CURRENT_DATE)
RETURNS TABLE (
    symbol VARCHAR(10),
    test_date DATE,
    is_stable BOOLEAN,
    filter_reason TEXT,
    arch_test_pvalue DECIMAL(10,6),
    rolling_std_cv DECIMAL(10,6),
    record_count INTEGER,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        v.symbol,
        v.test_date,
        v.is_stable,
        v.filter_reason,
        v.arch_test_pvalue,
        v.rolling_std_cv,
        v.record_count,
        v.created_at
    FROM variance_stability_tracking v
    WHERE v.test_date = target_date
    ORDER BY v.is_stable DESC, v.symbol;
END;
$$ LANGUAGE plpgsql;

-- Function to get feature computation summary
CREATE OR REPLACE FUNCTION get_feature_computation_summary(
    start_date DATE DEFAULT CURRENT_DATE - INTERVAL '7 days',
    end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    feature_date DATE,
    symbols_with_features INTEGER,
    total_records BIGINT,
    avg_log_return DECIMAL(15,6),
    avg_volatility DECIMAL(15,6)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.feature_date,
        COUNT(DISTINCT f.symbol) as symbols_with_features,
        COUNT(*) as total_records,
        AVG(f.log_return) as avg_log_return,
        AVG(f.volatility_annualized) as avg_volatility
    FROM market_data_features f
    WHERE f.feature_date BETWEEN start_date AND end_date
    GROUP BY f.feature_date
    ORDER BY f.feature_date DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get variance stability trends
CREATE OR REPLACE FUNCTION get_variance_stability_trends(
    days_back INTEGER DEFAULT 30
)
RETURNS TABLE (
    test_date DATE,
    total_symbols INTEGER,
    stable_symbols INTEGER,
    unstable_symbols INTEGER,
    stability_rate DECIMAL(5,4),
    avg_arch_pvalue DECIMAL(10,6),
    avg_rolling_std_cv DECIMAL(10,6)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        v.test_date,
        COUNT(*) as total_symbols,
        COUNT(*) FILTER (WHERE v.is_stable = true) as stable_symbols,
        COUNT(*) FILTER (WHERE v.is_stable = false) as unstable_symbols,
        ROUND(
            COUNT(*) FILTER (WHERE v.is_stable = true)::DECIMAL / COUNT(*), 
            4
        ) as stability_rate,
        AVG(v.arch_test_pvalue) as avg_arch_pvalue,
        AVG(v.rolling_std_cv) as avg_rolling_std_cv
    FROM variance_stability_tracking v
    WHERE v.test_date >= CURRENT_DATE - INTERVAL '1 day' * days_back
    GROUP BY v.test_date
    ORDER BY v.test_date DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- CREATE VIEWS
-- ============================================================================

-- View for current stable symbols
CREATE OR REPLACE VIEW current_stable_symbols AS
SELECT 
    v.symbol,
    v.test_date,
    v.is_stable,
    v.filter_reason,
    v.arch_test_pvalue,
    v.rolling_std_cv,
    v.record_count,
    f.feature_date,
    COUNT(f.id) as feature_count
FROM variance_stability_tracking v
LEFT JOIN market_data_features f ON v.symbol = f.symbol 
    AND v.test_date = f.feature_date
WHERE v.test_date = (
    SELECT MAX(test_date) 
    FROM variance_stability_tracking 
    WHERE symbol = v.symbol
)
GROUP BY v.symbol, v.test_date, v.is_stable, v.filter_reason, 
         v.arch_test_pvalue, v.rolling_std_cv, v.record_count, f.feature_date
ORDER BY v.is_stable DESC, v.symbol;

-- View for feature quality metrics
CREATE OR REPLACE VIEW feature_quality_metrics AS
SELECT 
    f.symbol,
    f.feature_date,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE f.log_close IS NOT NULL) as log_close_count,
    COUNT(*) FILTER (WHERE f.log_return IS NOT NULL) as log_return_count,
    COUNT(*) FILTER (WHERE f.z_score IS NOT NULL) as z_score_count,
    COUNT(*) FILTER (WHERE f.rolling_std IS NOT NULL) as rolling_std_count,
    COUNT(*) FILTER (WHERE f.volatility_annualized IS NOT NULL) as volatility_count,
    AVG(f.log_return) as avg_log_return,
    STDDEV(f.log_return) as std_log_return,
    AVG(f.volatility_annualized) as avg_volatility,
    MIN(f."timestamp") as first_timestamp,
    MAX(f."timestamp") as last_timestamp
FROM market_data_features f
GROUP BY f.symbol, f.feature_date
ORDER BY f.feature_date DESC, f.symbol;

-- ============================================================================
-- CREATE TRIGGERS
-- ============================================================================

-- Trigger to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for market_data_features
DROP TRIGGER IF EXISTS update_market_data_features_updated_at ON market_data_features;
CREATE TRIGGER update_market_data_features_updated_at
    BEFORE UPDATE ON market_data_features
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INSERT SAMPLE DATA (for testing)
-- ============================================================================

-- Note: This section can be commented out in production
-- Uncomment to add sample data for testing

/*
-- Sample variance stability tracking data
INSERT INTO variance_stability_tracking (symbol, test_date, record_count, arch_test_pvalue, rolling_std_cv, is_stable, filter_reason) VALUES
('AAPL', CURRENT_DATE, 1000, 0.1234, 0.2345, true, NULL),
('MSFT', CURRENT_DATE, 1000, 0.5678, 0.3456, true, NULL),
('GOOGL', CURRENT_DATE, 1000, 0.0123, 0.4567, false, 'arch_test_failed');

-- Sample market data features (if you have sample price data)
-- INSERT INTO market_data_features (symbol, timestamp, log_close, log_return, z_score, feature_date) VALUES
-- ('AAPL', '2025-01-15 09:30:00', 5.123456, 0.001234, 0.567890, CURRENT_DATE);
*/

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Display summary
DO $$
BEGIN
    RAISE NOTICE 'Migration 012 completed successfully!';
    RAISE NOTICE 'Created tables: market_data_features, variance_stability_tracking';
    RAISE NOTICE 'Created functions: get_stable_features_for_modeling, get_variance_stability_status, get_feature_computation_summary, get_variance_stability_trends';
    RAISE NOTICE 'Created views: current_stable_symbols, feature_quality_metrics';
    RAISE NOTICE 'Created triggers: update_market_data_features_updated_at';
END $$; 