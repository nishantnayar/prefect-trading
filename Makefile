.PHONY: help install install-dev setup test test-unit test-integration test-e2e test-streamlit test-streamlit-unit test-streamlit-integration test-streamlit-e2e lint format clean docs run-ui run-prefect deploy

# Default target
help:
	@echo "Available commands:"
	@echo "  install        - Install production dependencies"
	@echo "  install-dev    - Install development dependencies"
	@echo "  setup          - Setup the project (install + configure)"
	@echo "  test           - Run all tests"
	@echo "  test-unit      - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-e2e       - Run end-to-end tests only"
	@echo "  test-streamlit - Run all Streamlit tests"
	@echo "  test-streamlit-unit - Run Streamlit unit tests only"
	@echo "  test-streamlit-integration - Run Streamlit integration tests only"
	@echo "  test-streamlit-e2e - Run Streamlit end-to-end tests only"
	@echo "  lint           - Run linting checks"
	@echo "  format         - Format code with black and isort"
	@echo "  clean          - Clean up temporary files"
	@echo "  docs           - Build documentation"
	@echo "  run-ui         - Start the Streamlit UI"
	@echo "  run-prefect    - Start Prefect server"
	@echo "  deploy         - Deploy Prefect workflows"
	@echo "  db-migrate     - Run original database migrations"
	@echo "  db-migrate-consolidated - Run consolidated database migrations"
	@echo "  db-verify      - Verify schema against consolidated migrations"
	@echo "  db-check       - Check current database schema"
	@echo "  db-reset       - Reset database with consolidated migrations"
	@echo "  test-pairs     - Test daily pair identification flow"
	@echo "  run-pairs      - Run daily pair identification flow"
	@echo "  run-start-day  - Run start of day flow (includes pair identification)"
	@echo ""
	@echo "ML Training (Sector-Specific):"
	@echo "  train-gru-models        - Train models for active sectors (from config)"
	@echo "  train-gru-models-tech   - Train models for Technology sector only"
	@echo "  train-gru-models-healthcare - Train models for Healthcare sector only"
	@echo "  train-gru-models-financial - Train models for Financial Services sector only"
	@echo "  train-gru-models-all-sectors - Train models for all sectors"
	@echo ""
	@echo "Sector Analysis:"
	@echo "  show-sector-summary     - Show symbol count by sector"
	@echo "  show-tech-symbols       - Show Technology sector symbols"
	@echo "  sector-summary          - Show detailed sector summary"
	@echo "  sector-symbols          - Show symbols for specific sector (SECTOR=name)"
	@echo "  sector-config           - Show current sector configuration"
	@echo "  set-active-sectors      - Set active sectors (SECTORS='sector1 sector2')"

# Installation
install:
	pip install -r config/requirements.txt

install-dev:
	pip install -r config/requirements.txt
	pip install -r config/requirements-dev.txt

setup: install-dev
	@echo "Setting up Prefect blocks..."
	@python -c "from prefect.blocks.system import String; print('Please configure your Prefect blocks manually')"
	@echo "Setup complete! Please configure your environment variables."

# Testing
test:
	python scripts/run_tests.py

test-unit:
	python -m pytest test/ -m "not integration and not e2e"

test-integration:
	python -m pytest test/ -m "integration"

test-e2e:
	python -m pytest test/ -m "e2e"

# Streamlit-specific tests
test-streamlit:
	python -m pytest test/ -m "ui"

test-streamlit-unit:
	python -m pytest test/ -m "ui and not integration and not e2e"

test-streamlit-integration:
	python -m pytest test/ -m "ui and integration"

test-streamlit-e2e:
	python -m pytest test/ -m "ui and e2e"

test-streamlit-check:
	python -m pytest test/ --collect-only

test-coverage:
	python -m pytest test/ --cov=src --cov-report=html:build/htmlcov --cov-report=term-missing

# Code Quality
lint:
	flake8 src/ tests/
	mypy src/
	bandit -r src/ -f json -o bandit-report.json

format:
	black src/ tests/
	isort src/ tests/

format-check:
	black --check src/ tests/
	isort --check-only src/ tests/

# Security
security-check:
	safety check
	bandit -r src/ -f json -o bandit-report.json

# Documentation
docs:
	cd docs && make html

# Development
run-ui:
	streamlit run src/ui/streamlit_app.py

run-prefect:
	prefect server start

deploy:
	prefect deploy

# Database
db-migrate:
	@echo "Running database migrations..."
	@for file in src/database/migrations/001_initial_schema/*.sql; do \
		echo "Running $$file..."; \
		psql -d trading_db -f $$file; \
	done

db-migrate-consolidated:
	@echo "Running consolidated database migrations..."
	@echo "Running 001_initial_schema_consolidated.sql..."
	@psql -d trading_db -f src/database/migrations/001_initial_schema_consolidated.sql
	@echo "Running 002_data_source_enhancement_consolidated.sql..."
	@psql -d trading_db -f src/database/migrations/002_data_source_enhancement_consolidated.sql
	@echo "Running 003_historical_data_consolidated.sql..."
	@psql -d trading_db -f src/database/migrations/003_historical_data_consolidated.sql

db-verify:
	@echo "Verifying database schema against consolidated migrations..."
	@python scripts/verify_migrations_simple.py

db-check:
	@echo "Checking current database schema..."
	@python scripts/check_db_direct.py

db-reset:
	@echo "Resetting database..."
	dropdb trading_db || true
	createdb trading_db
	$(MAKE) db-migrate-consolidated

# ML Training and Analysis
train-gru-models:
	@echo "Training PyTorch GRU models for active sectors..."
	@python -m src.ml.train_gru_models

train-gru-models-tech:
	@echo "Training PyTorch GRU models for Technology sector only..."
	@python -c "from src.ml.train_gru_models import run_gru_training; run_gru_training(sectors=['Technology'])"

train-gru-models-healthcare:
	@echo "Training PyTorch GRU models for Healthcare sector only..."
	@python -c "from src.ml.train_gru_models import run_gru_training; run_gru_training(sectors=['Healthcare'])"

train-gru-models-financial:
	@echo "Training PyTorch GRU models for Financial Services sector only..."
	@python -c "from src.ml.train_gru_models import run_gru_training; run_gru_training(sectors=['Financial Services'])"

train-gru-models-all-sectors:
	@echo "Training PyTorch GRU models for all sectors..."
	@python -c "from src.ml.train_gru_models import run_gru_training; run_gru_training(sectors=['Technology', 'Healthcare', 'Financial Services', 'Basic Materials', 'Communication Services', 'Consumer Cyclical', 'Consumer Defensive', 'Energy', 'Industrials', 'Real Estate'])"

show-sector-summary:
	@echo "Showing sector summary..."
	@python -c "from src.data.sources.symbol_manager import SymbolManager; sm = SymbolManager(); summary = sm.get_sector_summary(); print('Symbols by Sector:'); [print(f'  {sector}: {count} symbols') for sector, count in summary.items()]"

show-tech-symbols:
	@echo "Showing Technology sector symbols..."
	@python -c "from src.data.sources.symbol_manager import SymbolManager; sm = SymbolManager(); symbols = sm.get_symbols_by_sector('Technology'); print(f'Technology symbols ({len(symbols)}):'); [print(f'  {symbol}') for symbol in symbols[:20]]; print('...' if len(symbols) > 20 else '')"

sector-summary:
	@echo "Showing sector summary..."
	@python scripts/manage_sectors.py summary

sector-symbols:
	@echo "Showing symbols for specified sector..."
	@if [ -z "$(SECTOR)" ]; then \
		echo "Usage: make sector-symbols SECTOR=Technology"; \
		exit 1; \
	fi
	@python scripts/manage_sectors.py symbols $(SECTOR)

sector-config:
	@echo "Showing current sector configuration..."
	@python scripts/manage_sectors.py config

set-active-sectors:
	@echo "Setting active sectors..."
	@if [ -z "$(SECTORS)" ]; then \
		echo "Usage: make set-active-sectors SECTORS='Technology Healthcare'"; \
		exit 1; \
	fi
	@python scripts/manage_sectors.py set-active $(SECTORS)

run-start-day:
	@echo "Running start of day flow..."
	@python -c "from main import start_of_day_flow; start_of_day_flow()"

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

# Docker (if using Docker)
docker-build:
	docker build -t prefect-trading .

docker-run:
	docker run -p 8501:8501 -p 4200:4200 prefect-trading

# Pre-commit
pre-commit-install:
	pre-commit install

pre-commit-run:
	pre-commit run --all-files

# Performance
benchmark:
	pytest tests/performance/ -v

# Monitoring
logs:
	tail -f logs/trading_system.log

# Backup and restore
backup:
	pg_dump trading_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore:
	@echo "Usage: make restore BACKUP_FILE=backup_YYYYMMDD_HHMMSS.sql"
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "Please specify BACKUP_FILE"; \
		exit 1; \
	fi
	psql -d trading_db -f $(BACKUP_FILE) 