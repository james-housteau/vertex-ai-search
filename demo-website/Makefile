.PHONY: setup test test-quick test-cov format lint typecheck quality build clean deploy

setup:
	poetry install

test:
	poetry run pytest -v

test-quick:
	poetry run pytest -v -k "test_health or test_static"

test-cov:
	poetry run pytest -v --cov=src/demo_website --cov-report=html --cov-report=term-missing

format:
	poetry run black src/ tests/
	poetry run ruff check --fix src/ tests/

lint:
	poetry run ruff check src/ tests/

typecheck:
	poetry run mypy src/ tests/

quality: format lint typecheck

build:
	docker build -t demo-website:latest .

clean:
	rm -rf .pytest_cache htmlcov .coverage .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

deploy:
	@echo "Deploying to Cloud Run..."
	gcloud run deploy demo-website \
		--source . \
		--platform managed \
		--region us-central1 \
		--allow-unauthenticated
