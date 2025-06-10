# Sync iCloud Git

A simple tool to synchronize between iCloud and Git repositories.

## Requirements

- Python 3.10 or higher

## Installation

```bash
# Install with pipx (recommended for end users)
pipx install sync-icloud-git
```

## Development Setup

```bash
# Clone the repository
git clone https://github.com/pweiss/sync-icloud-git.git
cd sync-icloud-git

# Run the setup script (creates virtual env and installs dependencies)
./run/setup_env.sh

# Activate the virtual environment
source .venv/bin/activate
```

## Usage

```bash
# Basic usage will be documented here
```

## Docker

You can build and run the application in a Docker container:

```bash
# Build and run the Docker container
./run/docker_build_and_run.sh
```

## Testing

The project includes comprehensive test suites for all modules. See [TESTING.md](TESTING.md) for detailed testing documentation.

### Quick Testing

```bash
# Run all tests
./run/test_all.sh

# Run config tests only
./run/test_config.sh
```

### Test Coverage

- **91% coverage** for configuration module
- Comprehensive unit tests for all components
- Automated test runners with coverage reporting
