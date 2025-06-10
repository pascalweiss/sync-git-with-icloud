#!/usr/bin/env bash

# Test runner script for sync-icloud-git
# This script runs all test suites from the tests folder

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${BLUE}🧪 Running sync-icloud-git test suite${NC}"
echo "Project root: $PROJECT_ROOT"
echo "Tests directory: $PROJECT_ROOT/tests"
echo

# Change to project root
cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    echo -e "${YELLOW}🔄 Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Check if tests directory exists
if [ ! -d "tests" ]; then
    echo -e "${RED}❌ Tests directory not found!${NC}"
    exit 1
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}⚠️  pytest not found. Installing pytest...${NC}"
    pip install pytest pytest-cov
fi

# Count test files
TEST_FILE_COUNT=$(find tests -name "test_*.py" | wc -l)
echo -e "${BLUE}Found $TEST_FILE_COUNT test file(s):${NC}"
find tests -name "test_*.py" | sed 's/^/  - /'
echo

# Run all tests with coverage
echo -e "${BLUE}🏃 Running all tests with coverage...${NC}"
echo "Command: pytest tests/ -v --tb=short --cov=sync_icloud_git --cov-report=term-missing"
echo

if pytest tests/ -v --tb=short --cov=sync_icloud_git --cov-report=term-missing; then
    echo
    echo -e "${GREEN}✅ All tests passed successfully!${NC}"
    exit 0
else
    echo
    echo -e "${RED}❌ Some tests failed!${NC}"
    exit 1
fi
