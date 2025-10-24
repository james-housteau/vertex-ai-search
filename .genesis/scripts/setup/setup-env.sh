#!/bin/bash
# Alternative environment setup for Genesis development
# Source this file when direnv is not available: source .genesis/scripts/setup/setup-env.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

echo "🔧 Setting up Genesis development environment..."

# Basic environment variables
export PROJECT_NAME="${PWD##*/}"
export PROJECT_MODE="development"
export ENV="development"
export SERVICE="${PWD##*/}"
export AI_SAFETY_MODE="enforced"
export LOG_LEVEL="info"
export LOG_JSON="false"
export LOG_TIMESTAMP="true"
export LOG_CALLER="false"

# Genesis development mode
export GENESIS_DEV_MODE="true"

# Circuit breaker configuration
export CB_FAILURE_THRESHOLD="5"
export CB_TIMEOUT="60.0"
export CB_HALF_OPEN_MAX_CALLS="5"
export CB_SUCCESS_THRESHOLD="1"
export CB_SLIDING_WINDOW_SIZE="10"

# Retry configuration
export RETRY_MAX_ATTEMPTS="3"
export RETRY_INITIAL_DELAY="1.0"
export RETRY_MAX_DELAY="60.0"
export RETRY_EXPONENTIAL_BASE="2.0"

# AutoFix configuration
export AUTOFIX_MAX_ITERATIONS="3"
export AUTOFIX_MAX_RUNS="5"

# File limits
export AI_MAX_FILES="550"
export MAX_PROJECT_FILES="1000"

# Project paths
export PROJECT_ROOT="$PROJECT_ROOT"
export PROJECT_TYPE="genesis-toolkit"
export TEMPLATES_DIR="${PROJECT_ROOT}/templates"
export SHARED_PYTHON_DIR="${PROJECT_ROOT}/genesis"
export CLI_DIR="${PROJECT_ROOT}/genesis"

# Add shared-core to Python path for development mode import resolution
export PYTHONPATH="${PROJECT_ROOT}/shared-python/src:${PYTHONPATH}"

# Activate Poetry virtual environment if it exists
if [[ -d "$PROJECT_ROOT/.venv" ]]; then
    export VIRTUAL_ENV="$PROJECT_ROOT/.venv"
    export PATH="${VIRTUAL_ENV}/bin:$PATH"
    export VIRTUAL_ENV_PROMPT="(${PROJECT_NAME}) "
fi

echo "✅ Genesis development environment configured"
echo "📦 PYTHONPATH includes shared-core: ${PROJECT_ROOT}/shared-python/src"
echo "🐍 Virtual environment: ${VIRTUAL_ENV:-not found}"
echo ""
echo "🧪 Test with: make test"
echo "🔍 Import test: python -c \"from shared_core.ai_safety_constants import DEFAULT_AI_SAFETY_CHECK_TYPE; print(f'✅ Import successful: {DEFAULT_AI_SAFETY_CHECK_TYPE}')\""
