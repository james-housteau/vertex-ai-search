#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Setting up answer-service development environment...${NC}"

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}❌ Poetry is not installed. Please install Poetry first.${NC}"
    echo -e "${YELLOW}   Visit: https://python-poetry.org/docs/#installation${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Poetry found${NC}"

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
poetry install

# Verify installation
echo -e "${BLUE}🔍 Verifying installation...${NC}"
if poetry run python -c "import answer_service" 2>/dev/null; then
    echo -e "${GREEN}✓ Package imports successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Package not yet importable (expected for new modules)${NC}"
fi

# Check if tests can run
echo -e "${BLUE}🧪 Checking test setup...${NC}"
if poetry run python -m pytest --collect-only > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Test framework configured${NC}"
else
    echo -e "${YELLOW}⚠️  Tests not yet runnable (expected for new modules)${NC}"
fi

echo -e "${GREEN}🎉 Setup complete! You can now:${NC}"
echo -e "  ${BLUE}make test${NC}      - Run tests"
echo -e "  ${BLUE}make format${NC}    - Format code"
echo -e "  ${BLUE}make lint${NC}      - Lint code"
echo -e "  ${BLUE}make run-dev${NC}   - Run CLI tool"
