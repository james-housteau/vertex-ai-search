# Metrics Collector Module Makefile
PYTHON := python3
POETRY := poetry

.PHONY: setup install test test-quick test-cov clean build format lint typecheck quality run-dev help

setup: ## Install dependencies and setup environment
	$(POETRY) install

install: setup ## Alias for setup

test: ## Run all tests with verbose output
	PYTHONPATH=src $(POETRY) run pytest -v

test-quick: ## Run fast subset of tests for rapid feedback
	PYTHONPATH=src $(POETRY) run pytest tests/test_models.py -v

test-cov: ## Run tests with coverage report
	PYTHONPATH=src $(POETRY) run pytest --cov=src/metrics_collector --cov-report=html --cov-report=term-missing

clean: ## Clean all build artifacts and caches
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build wheel packages
	$(POETRY) build

format: ## Format code with black and isort
	$(POETRY) run black src/ tests/
	$(POETRY) run isort src/ tests/

lint: ## Lint code with ruff
	$(POETRY) run ruff check src/ tests/

typecheck: ## Type check with mypy
	$(POETRY) run mypy src/

quality: format lint typecheck ## Run all quality checks

run-dev: ## Run the CLI tool in development mode
	$(POETRY) run metrics-collector

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
