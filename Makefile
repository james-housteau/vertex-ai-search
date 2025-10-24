.PHONY: help setup install dev test test-quick test-cov format format-check lint typecheck quality check-org clean build publish download update version-show version-sync bump-patch bump-minor bump-major release

# Auto-discover test directories (excluding hidden dirs like .venv, .git)
TEST_PATHS := $(shell find . -type d -name "tests" -not -path "*/.venv/*" -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/dist/*" -not -path "*/build/*" | sed 's|^\./||' | sort)

help: ## Show this help message
	@echo '🚀 Genesis Development Toolkit - Makefile Help'
	@echo ''
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Development Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^(setup|install|dev|test|test-quick|test-cov|format|format-check|lint|typecheck|quality):.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ''
	@echo 'Version Management:'
	@awk 'BEGIN {FS = ":.*?## "} /^(version-show|version-sync|bump-patch|bump-minor|bump-major|release):.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ''
	@echo 'Genesis Management:'
	@awk 'BEGIN {FS = ":.*?## "} /^(download|update|build|publish):.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ''
	@echo 'Utility Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^(clean|check-org):.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ''
	@echo '💡 Quick Start:'
	@echo '  make setup           # Install project dependencies'
	@echo '  make test            # Run quick tests'
	@echo '  make quality         # Check code quality'
	@echo '  make install         # Install Genesis from GitHub'

setup: ## Install project dependencies for development
	poetry install

install: ## Install Genesis CLI from GitHub releases
	@echo "📥 Installing Genesis from latest GitHub release..."
	@gh release download --pattern 'genesis_cli-*.whl' --repo jhousteau/genesis --clobber
	@python3.13 -m pip install genesis_cli-*.whl --force-reinstall --break-system-packages --ignore-installed 2>/dev/null || python3.13 -m pip install genesis_cli-*.whl --force-reinstall --ignore-installed
	@rm -f genesis_cli-*.whl
	@echo "✅ Genesis installed!"
	@genesis --version

dev: setup ## Alias for setup (deprecated, use setup instead)

test-quick: ## Run quick tests (excludes slow/integration tests)
	poetry run python -m pytest $(TEST_PATHS) -v --tb=short -m "not slow and not integration" --continue-on-collection-errors || true

test: ## Run fast subset of tests (no integration/slow tests)
	poetry run python -m pytest $(TEST_PATHS) -v --tb=short -m "not slow and not integration" --continue-on-collection-errors --maxfail=10

test-cov: ## Run ALL tests with coverage report (includes slow/integration tests)
	poetry run python -m pytest $(TEST_PATHS) --cov=genesis --cov-report=html --cov-report=term --continue-on-collection-errors

format: ## Format code with black and ruff
	poetry run black .
	poetry run ruff check --fix .

format-check: ## Check if code is formatted correctly (no changes)
	poetry run black --check .

lint: ## Lint code with ruff
	poetry run ruff check .

typecheck: ## Type check with mypy
	poetry run mypy .

quality: format lint typecheck ## Run all quality checks

check-org: ## Check project file organization
	@if [ -f .genesis/scripts/validation/check-file-organization.sh ]; then \
		./.genesis/scripts/validation/check-file-organization.sh; \
	else \
		echo "⚠️  Organization check script not found"; \
	fi

clean: ## Clean build artifacts and caches
	@echo "🧹 Cleaning build artifacts..."
	@genesis clean || (rm -rf build/ dist/ **/*.egg-info/ __pycache__/ **/__pycache__/ .pytest_cache/ **/.pytest_cache/ .mypy_cache/ **/.mypy_cache/ .ruff_cache/ **/.ruff_cache/ && echo "✅ Cleaned manually")

build: ## Build Genesis package (single wheel with everything)
	@echo "🔨 Building genesis-cli (includes shared-core)..."
	@rm -rf dist/
	@poetry build --format wheel
	@echo "📦 Build complete:"
	@ls -lh dist/*.whl
	@echo ""
	@echo "📤 To publish this build:"
	@echo "  make publish VERSION=v$(shell grep '^version = ' pyproject.toml | cut -d'"' -f2)"

download: ## Download latest Genesis wheel from GitHub
	@echo "📥 Downloading latest Genesis release..."
	@gh release download --pattern 'genesis_cli-*.whl' --repo jhousteau/genesis --clobber || echo "❌ Failed to download. Install 'gh' CLI or download manually."
	@ls -lh genesis_cli-*.whl 2>/dev/null || echo "No wheel files downloaded"

update: install ## Update Genesis to latest release (alias for install)

publish: build ## Build and publish Genesis to GitHub releases
	@echo "📤 Publishing Genesis package..."
	@if [ -z "$(VERSION)" ]; then \
		echo "❌ Error: VERSION is required. Usage: make publish VERSION=v2.0.5"; \
		exit 1; \
	fi
	@echo "Checking if release $(VERSION) exists..."
	@if gh release view $(VERSION) --repo jhousteau/genesis >/dev/null 2>&1; then \
		echo "🔄 Release $(VERSION) exists, deleting and recreating..."; \
		gh release delete $(VERSION) --repo jhousteau/genesis --yes; \
	fi
	@echo "Creating release $(VERSION)..."
	@gh release create $(VERSION) \
		--title "$(VERSION)" \
		--notes "Genesis CLI release $(VERSION)" \
		dist/genesis_cli-*.whl
	@echo "✅ Published to https://github.com/jhousteau/genesis/releases/tag/$(VERSION)"
	@echo ""
	@echo "📥 To download and install this release (requires gh CLI and Python 3.13+):"
	@echo "  gh release download $(VERSION) --pattern 'genesis_cli-*.whl' --repo jhousteau/genesis --clobber && python3.13 -m pip install genesis_cli-*.whl --force-reinstall --break-system-packages --ignore-installed && rm genesis_cli-*.whl"
	@echo ""
	@echo "Or use make command:"
	@echo "  make install"

version-show: ## Show current version
	@echo "📌 Current Genesis version: $(shell grep '^version = ' pyproject.toml | cut -d'"' -f2)"
	@poetry run python -c "from genesis.core.version_manager import get_all_versions; import json; print(json.dumps(get_all_versions(), indent=2))"

version-sync: ## Sync all version references across codebase
	@echo "🔄 Syncing version references..."
	@poetry run python -c "from genesis.core.version_manager import update_all_version_references; import json; result = update_all_version_references(); print(json.dumps(result, indent=2))"
	@echo "✅ Version sync complete"

bump-patch: ## Bump patch version (2.0.5 -> 2.0.6)
	@echo "⬆️  Bumping patch version..."
	@poetry version patch
	@$(MAKE) version-sync
	@echo "✅ Patch version bumped to $(shell grep '^version = ' pyproject.toml | cut -d'"' -f2)"

bump-minor: ## Bump minor version (2.0.5 -> 2.1.0)
	@echo "⬆️  Bumping minor version..."
	@poetry version minor
	@$(MAKE) version-sync
	@echo "✅ Minor version bumped to $(shell grep '^version = ' pyproject.toml | cut -d'"' -f2)"

bump-major: ## Bump major version (2.0.5 -> 3.0.0)
	@echo "⬆️  Bumping major version..."
	@poetry version major
	@$(MAKE) version-sync
	@echo "✅ Major version bumped to $(shell grep '^version = ' pyproject.toml | cut -d'"' -f2)"

release: ## Complete release workflow with version bump (use BUMP=patch|minor|major)
	@if [ -z "$(BUMP)" ]; then \
		echo "❌ Error: BUMP is required. Usage: make release BUMP=patch|minor|major"; \
		exit 1; \
	fi
	@echo "🚀 Starting release workflow ($(BUMP))..."
	@$(MAKE) bump-$(BUMP)
	@$(MAKE) quality
	@$(MAKE) test
	@NEW_VERSION=$$(grep '^version = ' pyproject.toml | cut -d'"' -f2); \
	echo "📦 Building and publishing v$$NEW_VERSION..."; \
	$(MAKE) publish VERSION=v$$NEW_VERSION
	@echo "✅ Release complete!"
