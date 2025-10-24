.PHONY: help setup install dev test test-cov format lint typecheck quality check-org clean build run-dev

help: ## Show this help message
	@echo '🚀 vertex-ai-search Development Toolkit - Makefile Help'
	@echo ''
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Development Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^(setup|install|dev|test|test-cov|format|lint|typecheck|quality):.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ''
	@echo 'CLI Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^(run-dev|build):.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ''
	@echo 'Utility Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^(clean|check-org):.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ''
	@echo '💡 Quick Start:'
	@echo '  make setup           # Initial setup'
	@echo '  make run-dev         # Run CLI tool'
	@echo '  make test            # Run tests'
	@echo '  make quality         # Check code quality'

setup: ## Run initial project setup
	./scripts/setup.sh

install: ## Install dependencies only
	poetry install

dev: setup ## Alias for setup (install with development dependencies)

# Test path detection - works for both traditional and module structures
TEST_PATH := $(shell if [ -d "tests" ]; then echo "tests"; elif [ -d "vertex_ai_search/tests" ]; then echo "vertex_ai_search/tests"; else echo "tests"; fi)
SRC_PATH := $(shell if [ -d "src" ]; then echo "src"; elif [ -d "vertex_ai_search" ]; then echo "vertex_ai_search"; else echo "."; fi)

test-quick: ## Run fast subset of tests for rapid feedback
	poetry run python -m pytest $(TEST_PATH) -k "not integration and not slow" --tb=short -p no:asyncio

test: ## Run all tests with verbose output (no coverage)
	poetry run python -m pytest $(TEST_PATH) -v --tb=short --continue-on-collection-errors -p no:asyncio

test-cov: ## Run tests with coverage report (slower, detailed metrics)
	poetry run python -m pytest $(TEST_PATH) --cov=$(SRC_PATH) --cov-report=html --cov-report=term --continue-on-collection-errors -p no:asyncio

format: ## Format code with black and ruff
	poetry run black $(SRC_PATH)/ tests/
	poetry run ruff check --fix $(SRC_PATH)/ tests/

format-check: ## Check if code is formatted correctly (no changes)
	poetry run black --check $(SRC_PATH)/ tests/

lint: ## Lint code with ruff
	poetry run ruff check $(SRC_PATH)/ tests/

typecheck: ## Type check with mypy
	poetry run mypy $(SRC_PATH)/

quality: format lint typecheck ## Run all quality checks

check-org: ## Check project file organization
	./.genesis/scripts/check-file-organization.sh

clean: ## Clean build artifacts and backup files
	# Python build artifacts
	rm -rf build/ dist/ **/*.egg-info/ *.egg-info/

	# Remove downloaded wheel files from root directory
	# (use glob patterns to handle wheel files properly)
	rm -f *.whl **/*.whl

	# Test and coverage artifacts
	rm -rf .coverage* htmlcov/ .pytest_cache/ **/.pytest_cache/
	rm -rf .tox/ **/.tox/

	# Type checking and linting caches
	rm -rf .mypy_cache/ **/.mypy_cache/
	rm -rf .ruff_cache/ **/.ruff_cache/

	# Python bytecode and caches
	rm -rf **/__pycache__/ __pycache__/
	rm -f **/*.py[cod] *.py[cod]
	rm -f **/*.pyo *.pyo
	rm -f **/*.pyd *.pyd
	rm -f **/*.so *.so

	# Backup and temporary files
	rm -rf **/*.bak *.bak
	rm -rf **/*.tmp *.tmp
	rm -rf **/*.temp *.temp
	rm -rf **/*~ *~
	rm -rf **/.DS_Store .DS_Store

	# IDE and editor files
	rm -rf .idea/ **/.idea/
	rm -rf .vscode/ **/.vscode/
	rm -f **/*.swp *.swp
	rm -f **/*.swo *.swo

	@echo "🧹 Cleaned build artifacts, cache files, and backup files"

build: ## Build packages
	@echo "🔨 Building vertex-ai-search packages..."
	@poetry build --format wheel
	@echo "📦 Packages built in dist/"

run-dev: ## Run CLI in development mode
	poetry run vertex-ai-search
