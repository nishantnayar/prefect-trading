-- PostgreSQL Optimization for Prefect Workers
-- This script optimizes PostgreSQL settings to handle multiple concurrent Prefect workers
-- and reduce the likelihood of deadlocks

-- 1. Increase max_connections to handle multiple workers
ALTER SYSTEM SET max_connections = 200;

-- 2. Optimize deadlock_timeout (default is 1 second, increase to 5 seconds)
ALTER SYSTEM SET deadlock_timeout = '5s';

-- 3. Increase shared_buffers for better performance
ALTER SYSTEM SET shared_buffers = '256MB';

-- 4. Optimize work_mem for concurrent operations
ALTER SYSTEM SET work_mem = '4MB';

-- 5. Increase maintenance_work_mem
ALTER SYSTEM SET maintenance_work_mem = '64MB';

-- 6. Optimize checkpoint settings
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';

-- 7. Increase effective_cache_size
ALTER SYSTEM SET effective_cache_size = '1GB';

-- 8. Optimize random_page_cost for SSD storage
ALTER SYSTEM SET random_page_cost = 1.1;

-- 9. Increase max_wal_size for better performance
ALTER SYSTEM SET max_wal_size = '2GB';

-- 10. Optimize autovacuum settings
ALTER SYSTEM SET autovacuum_max_workers = 3;
ALTER SYSTEM SET autovacuum_naptime = '10s';

-- 11. Increase lock_timeout to prevent premature timeouts
ALTER SYSTEM SET lock_timeout = '30s';

-- 12. Optimize for concurrent connections
ALTER SYSTEM SET max_prepared_transactions = 100;

-- Reload configuration
SELECT pg_reload_conf();

-- Show current settings
SELECT name, setting, unit FROM pg_settings 
WHERE name IN (
    'max_connections',
    'deadlock_timeout',
    'shared_buffers',
    'work_mem',
    'maintenance_work_mem',
    'checkpoint_completion_target',
    'wal_buffers',
    'effective_cache_size',
    'random_page_cost',
    'max_wal_size',
    'autovacuum_max_workers',
    'autovacuum_naptime',
    'lock_timeout',
    'max_prepared_transactions'
) ORDER BY name; 