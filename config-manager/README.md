# config-manager

Configuration management module for Vertex AI search functionality


## Features

- **Pydantic Configuration Models**: Type-safe configuration with validation
- **YAML Configuration Loading**: Support for hierarchical configuration files
- **Environment Variable Overrides**: Runtime configuration via environment variables
- **Multiple Environment Support**: Development, staging, production configurations
- **Configuration Validation**: Schema validation with detailed error messages
- **CLI Tools**: Command-line interface for configuration management
- **Caching**: Performance-optimized configuration loading with caching

## Installation

### Prerequisites

- Python 3.13+
- Poetry

### Install from Source

```bash
# Clone and install
git clone <repository-url>
cd config-manager
poetry install
```

### Install as Package

```bash
pip install config-manager
```

## Usage

### CLI Usage

After installation, you can use the `config-manager` command:

```bash
# Show help
config-manager --help

# Load and display configuration for development environment
config-manager load --environment development --config-dir config

# List available environments
config-manager list-environments --config-dir config

# Validate configuration
config-manager validate --environment production --config-dir config
```

### Python API Usage

```python
from config_manager import load_config, AppConfig, ConfigManager

# Load configuration for development
config = load_config("development", config_dir=Path("config"))
print(f"App: {config.app_name}, Debug: {config.debug}")

# Use ConfigManager for advanced scenarios
manager = ConfigManager(config_dir=Path("config"))
config = manager.load_config("production")
available_envs = manager.get_available_environments()
```

## Configuration Structure

### YAML Files

Place your configuration files in a `config/` directory:

```
config/
├── defaults.yaml      # Base configuration
├── development.yaml   # Development overrides
├── staging.yaml       # Staging overrides
└── production.yaml    # Production overrides
```

### Environment Variables

Override any configuration value using environment variables with the `CONFIG_` prefix:

```bash
export CONFIG_DEBUG=true
export CONFIG_PORT=9000
export CONFIG_LOG_LEVEL=DEBUG
```

## Available Commands

- `load` - Load and display configuration for an environment
- `list-environments` - List available environment configurations
- `validate` - Validate configuration for an environment

## Development

```bash
# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Run the CLI in development
poetry run config-manager --help

# Run tests
make test

# Run tests with coverage
make test-cov

# Code quality checks
make quality

# Build package
make build
```

## Building and Distribution

```bash
# Build the package
poetry build

# Publish to PyPI (if configured)
poetry publish
```

## Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run all quality checks
make quality
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the quality checks
6. Submit a pull request
