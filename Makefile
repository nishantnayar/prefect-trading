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
	PYTHONDONTWRITEBYTECODE=1 pytest tests/ -v --cov=src --cov-report=term-missing

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-e2e:
	pytest tests/e2e/ -v

# Streamlit-specific tests
test-streamlit:
	pytest test/unit/ui/ test/integration/test_streamlit_integration.py test/e2e/test_streamlit_e2e.py -v

test-streamlit-unit:
	pytest test/unit/ui/ -v

test-streamlit-integration:
	pytest test/integration/test_streamlit_integration.py -v

test-streamlit-e2e:
	pytest test/e2e/test_streamlit_e2e.py -v

test-streamlit-check:
	pytest test/unit/ui/ --collect-only

test-coverage:
	pytest tests/ -v --cov=src --cov-report=html:build/htmlcov --cov-report=term-missing

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
	PYTHONDONTWRITEBYTECODE=1 streamlit run src/ui/streamlit_app.py

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

db-reset:
	@echo "Resetting database..."
	dropdb trading_db || true
	createdb trading_db
	$(MAKE) db-migrate

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