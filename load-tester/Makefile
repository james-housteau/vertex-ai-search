# Load Tester - End-to-End Load Testing Module
.PHONY: help setup test test-quick test-cov build clean lint format typecheck quality run-dev install-dev

# Default target
help:
	@echo "Load Tester - End-to-End Load Testing Module"
	@echo ""
	@echo "Available commands:"
	@echo "  setup      - Install dependencies and setup development environment"
	@echo "  test       - Run all tests with verbose output"
	@echo "  test-quick - Run tests without coverage for rapid feedback"
	@echo "  test-cov   - Run tests with coverage report (80% minimum required)"
	@echo "  build      - Build wheel packages"
	@echo "  clean      - Clean all artifacts and caches"
	@echo "  lint       - Run ruff linting"
	@echo "  format     - Format code with black and isort"
	@echo "  typecheck  - Run mypy type checking"
	@echo "  quality    - Run all quality checks (format + lint + typecheck)"
	@echo "  run-dev    - Run CLI in development mode"

# Setup development environment
setup:
	poetry install
	poetry run pip install --upgrade pip

# Install development dependencies
install-dev:
	poetry install --with dev

# Run all tests with verbose output
test:
	poetry run pytest -v

# Run tests without coverage for rapid feedback
test-quick:
	poetry run pytest -v --no-cov

# Run tests with coverage report
test-cov:
	poetry run pytest -v --cov=src/load_tester --cov-report=term-missing --cov-report=html

# Build wheel packages
build:
	poetry build

# Clean all artifacts and caches
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Run ruff linting
lint:
	poetry run ruff check src/ tests/

# Format code with black and isort
format:
	poetry run black src/ tests/
	poetry run isort src/ tests/

# Run mypy type checking
typecheck:
	poetry run mypy src/

# Run all quality checks
quality: format lint typecheck

# Run CLI in development mode
run-dev:
	poetry run load-tester --help

# Validate module independence (used by CI)
validate-independence:
	@echo "Validating load-tester module independence..."
	@if [ ! -f pyproject.toml ]; then echo "❌ Missing pyproject.toml"; exit 1; fi
	@if [ ! -f Makefile ]; then echo "❌ Missing Makefile"; exit 1; fi
	@if [ ! -d src/load_tester ]; then echo "❌ Missing src/load_tester"; exit 1; fi
	@if [ ! -d tests ]; then echo "❌ Missing tests directory"; exit 1; fi
	@echo "✅ Module structure validation passed"
	@echo "🧪 Running test suite..."
	@make test-quick
	@echo "🏗️  Running build..."
	@make build
	@echo "✅ load-tester module independence validated"
