.PHONY: help setup install test test-quick test-cov format lint typecheck quality clean build

help: ## Show this help message
	@echo 'shared-contracts Development Toolkit - Makefile Help'
	@echo ''
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Development Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^(setup|install|test|test-quick|test-cov|format|lint|typecheck|quality):.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ''
	@echo 'Build Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^(build|clean):.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Install dependencies
	poetry install

install: setup ## Alias for setup

test-quick: ## Run fast subset of tests
	poetry run pytest tests/ -k "not slow" --tb=short

test: ## Run all tests with verbose output
	poetry run pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage report
	poetry run pytest tests/ --cov=src/shared_contracts --cov-report=html --cov-report=term

format: ## Format code with black and ruff
	poetry run black src/ tests/
	poetry run ruff check --fix src/ tests/

format-check: ## Check if code is formatted correctly
	poetry run black --check src/ tests/

lint: ## Lint code with ruff
	poetry run ruff check src/ tests/

typecheck: ## Type check with mypy
	poetry run mypy src/

quality: format lint typecheck ## Run all quality checks

clean: ## Clean build artifacts
	rm -rf build/ dist/ **/*.egg-info/ *.egg-info/
	rm -f *.whl **/*.whl
	rm -rf .coverage* htmlcov/ .pytest_cache/ **/.pytest_cache/
	rm -rf .mypy_cache/ **/.mypy_cache/
	rm -rf .ruff_cache/ **/.ruff_cache/
	rm -rf **/__pycache__/ __pycache__/
	rm -f **/*.py[cod] *.py[cod]
	@echo "Cleaned build artifacts and caches"

build: ## Build packages
	@echo "Building shared-contracts packages..."
	@poetry build --format wheel
	@echo "Packages built in dist/"
