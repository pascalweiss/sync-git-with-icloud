#!/usr/bin/env bash

# Test runner script specifically for config.py tests
# This script runs only the configuration module tests

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Running sync-icloud-git config tests${NC}"
echo "=============================================="

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

echo -e "${BLUE}📍 Project root: $PROJECT_ROOT${NC}"
echo ""

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    echo -e "${YELLOW}🔄 Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Check if config test file exists
if [ ! -f "tests/test_config.py" ]; then
    echo -e "${RED}❌ Config test file not found!${NC}"
    exit 1
fi

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}❌ pytest not found. Installing pytest...${NC}"
    pip install pytest pytest-cov
    echo -e "${GREEN}✅ Development dependencies installed${NC}"
    echo ""
fi

# Run config tests specifically
echo -e "${BLUE}🔬 Running config.py tests...${NC}"
echo "-----------------------------"

# Run tests with verbose output and coverage for config module only
if pytest tests/test_config.py -v --cov=sync_icloud_git.config --cov-report=term-missing; then
    echo ""
    echo -e "${GREEN}✅ Config tests completed successfully!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ Config tests failed!${NC}"
    exit 1
fi
