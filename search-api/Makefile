.PHONY: setup test test-quick test-cov format lint typecheck quality build clean

setup:
	poetry install

test:
	poetry run pytest

test-quick:
	poetry run pytest -x

test-cov:
	poetry run pytest --cov-report=html --cov-report=term

format:
	poetry run black src/ tests/
	poetry run ruff check --fix src/ tests/

lint:
	poetry run ruff check src/ tests/

typecheck:
	poetry run mypy src/

quality: format lint typecheck

build:
	poetry build

clean:
	rm -rf dist/ .pytest_cache/ htmlcov/ .coverage .mypy_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
