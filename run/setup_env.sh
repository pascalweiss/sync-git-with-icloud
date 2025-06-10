#!/usr/bin/env bash

# This script sets up a development environment for sync-icloud-git
# It creates a virtual environment and installs the package with dev dependencies

set -e  # Exit immediately if a command exits with a non-zero status

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/.venv"

echo "Setting up development environment for sync-icloud-git..."
echo "Project root: $PROJECT_ROOT"

# Check if Python 3.10+ is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "Using Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists in $VENV_DIR"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install the package with dev dependencies
echo "Installing package with development dependencies..."
pip install -e ".[dev]"

echo ""
echo "Setup complete! Development environment is ready."
echo ""
echo "To activate the virtual environment in your shell, run:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "To run tests:"
echo "  ./run/test_all.sh"
echo "  ./run/test_all.sh --cov  # With coverage"
echo ""
