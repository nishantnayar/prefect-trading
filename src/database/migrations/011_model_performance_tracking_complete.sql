-- Migration 011: Complete Model Performance Tracking System
-- This migration creates the complete system for tracking ML model performance
-- Run this manually: psql -d your_database -f src/database/migrations/011_model_performance_tracking_complete.sql

-- ============================================================================
-- CREATE TABLES
-- ============================================================================

-- Create model_performance table
CREATE TABLE IF NOT EXISTS model_performance (
    id SERIAL PRIMARY KEY,
    pair_symbol VARCHAR(20) NOT NULL,
    model_run_id VARCHAR(255) NOT NULL,
    experiment_name VARCHAR(255) NOT NULL,
    training_date TIMESTAMP NOT NULL,
    f1_score DECIMAL(5,4),
    accuracy DECIMAL(5,4),
    "precision" DECIMAL(5,4),
    recall DECIMAL(5,4),
    auc_score DECIMAL(5,4),
    loss DECIMAL(10,6),
    val_loss DECIMAL(10,6),
    epochs_trained INTEGER,
    early_stopped BOOLEAN DEFAULT FALSE,
    model_path VARCHAR(500),
    hyperparameters JSONB,
    feature_importance JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create model_rankings table for historical rankings
CREATE TABLE IF NOT EXISTS model_rankings (
    id SERIAL PRIMARY KEY,
    ranking_date DATE NOT NULL,
    pair_symbol VARCHAR(20) NOT NULL,
    rank_position INTEGER NOT NULL,
    f1_score DECIMAL(5,4) NOT NULL,
    model_run_id VARCHAR(255) NOT NULL,
    experiment_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ranking_date, pair_symbol)
);

-- Create model_trends table for performance trends
CREATE TABLE IF NOT EXISTS model_trends (
    id SERIAL PRIMARY KEY,
    pair_symbol VARCHAR(20) NOT NULL,
    trend_date DATE NOT NULL,
    avg_f1_7d DECIMAL(5,4),
    avg_f1_30d DECIMAL(5,4),
    best_f1_7d DECIMAL(5,4),
    best_f1_30d DECIMAL(5,4),
    model_count_7d INTEGER,
    model_count_30d INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(pair_symbol, trend_date)
);

-- ============================================================================
-- CREATE INDEXES
-- ============================================================================

-- Performance table indexes
CREATE INDEX IF NOT EXISTS idx_model_performance_pair_symbol ON model_performance(pair_symbol);
CREATE INDEX IF NOT EXISTS idx_model_performance_training_date ON model_performance(training_date);
CREATE INDEX IF NOT EXISTS idx_model_performance_f1_score ON model_performance(f1_score DESC);
CREATE INDEX IF NOT EXISTS idx_model_performance_experiment ON model_performance(experiment_name);

-- Rankings table indexes
CREATE INDEX IF NOT EXISTS idx_model_rankings_date ON model_rankings(ranking_date);
CREATE INDEX IF NOT EXISTS idx_model_rankings_pair ON model_rankings(pair_symbol);
CREATE INDEX IF NOT EXISTS idx_model_rankings_position ON model_rankings(rank_position);

-- Trends table indexes
CREATE INDEX IF NOT EXISTS idx_model_trends_pair_date ON model_trends(pair_symbol, trend_date);
CREATE INDEX IF NOT EXISTS idx_model_trends_date ON model_trends(trend_date);

-- ============================================================================
-- DROP EXISTING CONSTRAINTS (to avoid conflicts)
-- ============================================================================

DO $$ 
BEGIN
    -- Drop model_performance constraints
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_f1_score' AND table_name = 'model_performance') THEN
        ALTER TABLE model_performance DROP CONSTRAINT chk_f1_score;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_accuracy' AND table_name = 'model_performance') THEN
        ALTER TABLE model_performance DROP CONSTRAINT chk_accuracy;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_precision' AND table_name = 'model_performance') THEN
        ALTER TABLE model_performance DROP CONSTRAINT chk_precision;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_recall' AND table_name = 'model_performance') THEN
        ALTER TABLE model_performance DROP CONSTRAINT chk_recall;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_auc_score' AND table_name = 'model_performance') THEN
        ALTER TABLE model_performance DROP CONSTRAINT chk_auc_score;
    END IF;
    
    -- Drop model_rankings constraints
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_rank_position' AND table_name = 'model_rankings') THEN
        ALTER TABLE model_rankings DROP CONSTRAINT chk_rank_position;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'chk_ranking_f1_score' AND table_name = 'model_rankings') THEN
        ALTER TABLE model_rankings DROP CONSTRAINT chk_ranking_f1_score;
    END IF;
END $$;

-- ============================================================================
-- ADD CONSTRAINTS
-- ============================================================================

-- Performance table constraints
ALTER TABLE model_performance 
ADD CONSTRAINT chk_f1_score CHECK (f1_score >= 0 AND f1_score <= 1),
ADD CONSTRAINT chk_accuracy CHECK (accuracy >= 0 AND accuracy <= 1),
ADD CONSTRAINT chk_precision CHECK ("precision" >= 0 AND "precision" <= 1),
ADD CONSTRAINT chk_recall CHECK (recall >= 0 AND recall <= 1),
ADD CONSTRAINT chk_auc_score CHECK (auc_score >= 0 AND auc_score <= 1);

-- Rankings table constraints
ALTER TABLE model_rankings
ADD CONSTRAINT chk_rank_position CHECK (rank_position > 0),
ADD CONSTRAINT chk_ranking_f1_score CHECK (f1_score >= 0 AND f1_score <= 1);

-- ============================================================================
-- DROP EXISTING FUNCTIONS (to ensure clean recreation)
-- ============================================================================

DROP FUNCTION IF EXISTS get_best_performing_pairs(INTEGER);
DROP FUNCTION IF EXISTS get_pair_performance_trends(VARCHAR, INTEGER);
DROP FUNCTION IF EXISTS get_recent_pair_performance(VARCHAR, INTEGER);
DROP FUNCTION IF EXISTS update_model_rankings();
DROP FUNCTION IF EXISTS update_model_trends();

-- ============================================================================
-- CREATE HELPER FUNCTIONS
-- ============================================================================

-- Function to get current best performing pairs
CREATE OR REPLACE FUNCTION get_best_performing_pairs(limit_count INTEGER DEFAULT 10)
RETURNS TABLE (
    pair_symbol VARCHAR(20),
    best_f1_score DECIMAL(5,4),
    avg_f1_score DECIMAL(5,4),
    model_count BIGINT,
    latest_training_date TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        mp.pair_symbol,
        MAX(mp.f1_score) as best_f1_score,
        AVG(mp.f1_score) as avg_f1_score,
        COUNT(*) as model_count,
        MAX(mp.training_date) as latest_training_date
    FROM model_performance mp
    WHERE mp.f1_score IS NOT NULL
    GROUP BY mp.pair_symbol
    ORDER BY best_f1_score DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get performance trends for a pair
CREATE OR REPLACE FUNCTION get_pair_performance_trends(
    target_pair VARCHAR(20),
    days_back INTEGER DEFAULT 30
)
RETURNS TABLE (
    trend_date DATE,
    avg_f1_7d DECIMAL(5,4),
    avg_f1_30d DECIMAL(5,4),
    best_f1_7d DECIMAL(5,4),
    best_f1_30d DECIMAL(5,4),
    model_count_7d INTEGER,
    model_count_30d INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        mt.trend_date,
        mt.avg_f1_7d,
        mt.avg_f1_30d,
        mt.best_f1_7d,
        mt.best_f1_30d,
        mt.model_count_7d,
        mt.model_count_30d
    FROM model_trends mt
    WHERE mt.pair_symbol = target_pair
    AND mt.trend_date >= CURRENT_DATE - INTERVAL '1 day' * days_back
    ORDER BY mt.trend_date DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get recent model performance for a pair
CREATE OR REPLACE FUNCTION get_recent_pair_performance(
    target_pair VARCHAR(20),
    days_back INTEGER DEFAULT 7
)
RETURNS TABLE (
    training_date TIMESTAMP,
    f1_score DECIMAL(5,4),
    accuracy DECIMAL(5,4),
    "precision" DECIMAL(5,4),
    recall DECIMAL(5,4),
    model_run_id VARCHAR(255),
    experiment_name VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        mp.training_date,
        mp.f1_score,
        mp.accuracy,
        mp."precision",
        mp.recall,
        mp.model_run_id,
        mp.experiment_name
    FROM model_performance mp
    WHERE mp.pair_symbol = target_pair
    AND mp.training_date >= CURRENT_TIMESTAMP - INTERVAL '1 day' * days_back
    ORDER BY mp.training_date DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to update model rankings (with UPSERT)
CREATE OR REPLACE FUNCTION update_model_rankings()
RETURNS VOID AS $$
BEGIN
    -- Insert new rankings based on best F1 scores with UPSERT
    INSERT INTO model_rankings (ranking_date, pair_symbol, rank_position, f1_score, model_run_id, experiment_name)
    SELECT 
        CURRENT_DATE as ranking_date,
        pair_symbol,
        ROW_NUMBER() OVER (ORDER BY f1_score DESC) as rank_position,
        f1_score,
        model_run_id,
        experiment_name
    FROM (
        SELECT DISTINCT ON (pair_symbol)
            pair_symbol,
            f1_score,
            model_run_id,
            experiment_name
        FROM model_performance
        WHERE f1_score IS NOT NULL
        ORDER BY pair_symbol, f1_score DESC
    ) ranked_pairs
    ON CONFLICT (ranking_date, pair_symbol) DO UPDATE SET
        rank_position = EXCLUDED.rank_position,
        f1_score = EXCLUDED.f1_score,
        model_run_id = EXCLUDED.model_run_id,
        experiment_name = EXCLUDED.experiment_name;
    
    -- Log the number of rankings inserted/updated
    RAISE NOTICE 'Updated rankings for date %', CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- Function to update model trends (with UPSERT)
CREATE OR REPLACE FUNCTION update_model_trends()
RETURNS VOID AS $$
BEGIN
    -- Insert new trends with UPSERT
    INSERT INTO model_trends (pair_symbol, trend_date, avg_f1_7d, avg_f1_30d, best_f1_7d, best_f1_30d, model_count_7d, model_count_30d)
    SELECT 
        pair_symbol,
        CURRENT_DATE as trend_date,
        AVG(f1_score) FILTER (WHERE DATE(training_date) >= CURRENT_DATE - INTERVAL '7 days') as avg_f1_7d,
        AVG(f1_score) FILTER (WHERE DATE(training_date) >= CURRENT_DATE - INTERVAL '30 days') as avg_f1_30d,
        MAX(f1_score) FILTER (WHERE DATE(training_date) >= CURRENT_DATE - INTERVAL '7 days') as best_f1_7d,
        MAX(f1_score) FILTER (WHERE DATE(training_date) >= CURRENT_DATE - INTERVAL '30 days') as best_f1_30d,
        COUNT(*) FILTER (WHERE DATE(training_date) >= CURRENT_DATE - INTERVAL '7 days') as model_count_7d,
        COUNT(*) FILTER (WHERE DATE(training_date) >= CURRENT_DATE - INTERVAL '30 days') as model_count_30d
    FROM model_performance
    WHERE f1_score IS NOT NULL
    GROUP BY pair_symbol
    ON CONFLICT (pair_symbol, trend_date) DO UPDATE SET
        avg_f1_7d = EXCLUDED.avg_f1_7d,
        avg_f1_30d = EXCLUDED.avg_f1_30d,
        best_f1_7d = EXCLUDED.best_f1_7d,
        best_f1_30d = EXCLUDED.best_f1_30d,
        model_count_7d = EXCLUDED.model_count_7d,
        model_count_30d = EXCLUDED.model_count_30d;
    
    -- Log the number of trends inserted/updated
    RAISE NOTICE 'Updated trends for date %', CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- CREATE VIEWS
-- ============================================================================

-- Create a view for easy access to current best models
CREATE OR REPLACE VIEW current_best_models AS
SELECT DISTINCT ON (pair_symbol)
    pair_symbol,
    f1_score,
    accuracy,
    "precision",
    recall,
    training_date,
    model_run_id,
    experiment_name
FROM model_performance
WHERE f1_score IS NOT NULL
ORDER BY pair_symbol, f1_score DESC;

-- ============================================================================
-- INSERT SAMPLE DATA (only if tables are empty)
-- ============================================================================

-- Insert sample data for testing (optional) - only if table is empty
INSERT INTO model_performance (pair_symbol, model_run_id, experiment_name, training_date, f1_score, accuracy, "precision", recall, auc_score, loss, val_loss, epochs_trained, early_stopped, hyperparameters)
SELECT * FROM (VALUES
    ('AAPL-MSFT', 'run_001', 'pytorch_gru_pairs', CURRENT_TIMESTAMP - INTERVAL '1 day', 0.7445, 0.7200, 0.7500, 0.7400, 0.7600, 0.3200, 0.3500, 50, FALSE, '{"learning_rate": 0.001, "hidden_size": 64}'::jsonb),
    ('GOOGL-META', 'run_002', 'pytorch_gru_pairs', CURRENT_TIMESTAMP - INTERVAL '2 days', 0.7320, 0.7100, 0.7300, 0.7350, 0.7450, 0.3300, 0.3600, 45, TRUE, '{"learning_rate": 0.001, "hidden_size": 128}'::jsonb),
    ('NVDA-AMD', 'run_003', 'pytorch_gru_pairs', CURRENT_TIMESTAMP - INTERVAL '3 days', 0.7180, 0.7000, 0.7200, 0.7150, 0.7300, 0.3400, 0.3700, 60, FALSE, '{"learning_rate": 0.0005, "hidden_size": 64}'::jsonb),
    ('TSLA-NIO', 'run_004', 'pytorch_gru_pairs', CURRENT_TIMESTAMP - INTERVAL '4 days', 0.7020, 0.6800, 0.7050, 0.7000, 0.7150, 0.3500, 0.3800, 40, TRUE, '{"learning_rate": 0.002, "hidden_size": 96}'::jsonb),
    ('AMZN-NFLX', 'run_005', 'pytorch_gru_pairs', CURRENT_TIMESTAMP - INTERVAL '5 days', 0.6950, 0.6700, 0.6900, 0.7000, 0.7050, 0.3600, 0.3900, 55, FALSE, '{"learning_rate": 0.001, "hidden_size": 128}'::jsonb)
) AS v(pair_symbol, model_run_id, experiment_name, training_date, f1_score, accuracy, "precision", recall, auc_score, loss, val_loss, epochs_trained, early_stopped, hyperparameters)
WHERE NOT EXISTS (SELECT 1 FROM model_performance LIMIT 1);

-- ============================================================================
-- INITIALIZE RANKINGS AND TRENDS
-- ============================================================================

-- Update rankings and trends with sample data
SELECT update_model_rankings();
SELECT update_model_trends();

-- ============================================================================
-- GRANT PERMISSIONS (uncomment and adjust as needed)
-- ============================================================================

-- GRANT SELECT, INSERT, UPDATE ON model_performance TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE ON model_rankings TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE ON model_trends TO your_app_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO your_app_user;

-- ============================================================================
-- ADD COMMENTS
-- ============================================================================

COMMENT ON TABLE model_performance IS 'Stores performance metrics for trained ML models';
COMMENT ON TABLE model_rankings IS 'Historical rankings of pairs by model performance';
COMMENT ON TABLE model_trends IS 'Performance trends and averages for pairs over time';
COMMENT ON FUNCTION get_best_performing_pairs(INTEGER) IS 'Returns the best performing pairs ranked by F1 score';
COMMENT ON FUNCTION get_pair_performance_trends(VARCHAR, INTEGER) IS 'Returns performance trends for a specific pair';
COMMENT ON FUNCTION get_recent_pair_performance(VARCHAR, INTEGER) IS 'Returns recent model performance for a specific pair';
COMMENT ON FUNCTION update_model_rankings() IS 'Updates the model rankings table with current best performers';
COMMENT ON FUNCTION update_model_trends() IS 'Updates the model trends table with current averages';
COMMENT ON VIEW current_best_models IS 'View showing the best performing model for each pair';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Show final results
SELECT 'Rankings' as table_name, COUNT(*) as count FROM model_rankings WHERE ranking_date = CURRENT_DATE
UNION ALL
SELECT 'Trends' as table_name, COUNT(*) as count FROM model_trends WHERE trend_date = CURRENT_DATE
UNION ALL
SELECT 'Performance' as table_name, COUNT(*) as count FROM model_performance; 