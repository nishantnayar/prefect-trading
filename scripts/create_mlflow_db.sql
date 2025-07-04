-- scripts/create_mlflow_db.sql
-- SQL script to create the mlflow_db database for MLflow tracking
-- Run this script as a superuser or a user with CREATEDB privileges

-- Check if the database exists, and create it if it does not
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_database WHERE datname = 'mlflow_db'
    ) THEN
        PERFORM dblink_exec('dbname=' || current_database(), 'CREATE DATABASE mlflow_db');
    END IF;
END$$;

-- Note: If dblink is not available, you can simply run:
-- CREATE DATABASE mlflow_db;
-- and ignore the error if it already exists.

-- To run this script:
--   psql -U postgres -h localhost -d trading_system -f scripts/create_mlflow_db.sql 