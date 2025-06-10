#!/usr/bin/env bash

# Template test runner script for individual modules
# Usage: ./run/test_module.sh <module_name>
# Example: ./run/test_module.sh git_operations

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if module name is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}❌ Error: Module name required${NC}"
    echo "Usage: $0 <module_name>"
    echo "Example: $0 git_operations"
    exit 1
fi

MODULE_NAME="$1"

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${BLUE}🧪 Running sync-icloud-git $MODULE_NAME tests${NC}"
echo "=================================================="

# Change to project root
cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    echo -e "${YELLOW}🔄 Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Check if test file exists
TEST_FILE="tests/test_${MODULE_NAME}.py"
if [ ! -f "$TEST_FILE" ]; then
    echo -e "${RED}❌ Test file not found: $TEST_FILE${NC}"
    echo -e "${YELLOW}💡 Create the test file first, then run this script again.${NC}"
    exit 1
fi

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}❌ pytest not found. Installing pytest...${NC}"
    pip install pytest pytest-cov
    echo -e "${GREEN}✅ Development dependencies installed${NC}"
    echo ""
fi

echo -e "${BLUE}📍 Project root: $PROJECT_ROOT${NC}"
echo -e "${BLUE}🔬 Running ${MODULE_NAME} tests...${NC}"
echo "-----------------------------"

# Run tests with verbose output and coverage for specific module only
if pytest "$TEST_FILE" -v --cov="sync_icloud_git.${MODULE_NAME}" --cov-report=term-missing; then
    echo ""
    echo -e "${GREEN}✅ ${MODULE_NAME} tests completed successfully!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ ${MODULE_NAME} tests failed!${NC}"
    exit 1
fi
