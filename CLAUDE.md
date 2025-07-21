# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
```bash
# Run all tests with coverage
./run/test_all.sh

# Run tests with pytest directly
pytest tests/ -v --cov=sync_icloud_git --cov-report=term-missing

# Run specific test file
pytest tests/test_config.py -v
```

### Package Management
```bash
# Install in development mode with dev dependencies
pip install -e .[dev]

# Build package
python -m build

# Install from source
pip install -e .
```

### Docker Operations
```bash
# Build Docker image
./run/docker_build.sh

# Build and run Docker container
./run/docker_build_and_run.sh

# Run existing Docker image
./run/docker_run.sh
```

## Architecture Overview

### Core Components

**Main Entry Point (`cli.py`)**
- Step-based pipeline architecture using abstract `Step` classes
- Each operation (clone, update, sync, commit, push) is a separate step
- `StepPipeline` orchestrates execution based on `--step` parameter
- Steps: `all`, `clone`, `update`, `sync`

**Configuration Management (`config.py`)**
- `SyncConfig` class handles all configuration via environment variables and CLI args
- Environment variables use `SYNC_ICLOUD_GIT__` prefix
- Required: Git credentials, rclone config, remote folder
- Default exclude patterns for Git files (`.git/`, `.gitignore`, etc.)

**Git Operations (`git_operations.py`)**
- `GitOperations` class manages all Git interactions using GitPython
- Handles cloning, updating, committing, and pushing
- Automatic Git identity configuration from config
- Repository loading and validation

**iCloud Operations (`icloud_operations.py`)**
- `ICloudOperations` class manages rclone-based iCloud sync
- Read-only operations from iCloud to local Git repo
- Uses rclone WebDAV backend for iCloud Drive access
- Temporary config file management for rclone

### Key Design Patterns

- **Step Pattern**: Each major operation is encapsulated in a `Step` class with `execute()` method
- **Configuration Injection**: All classes receive `SyncConfig` instance for consistent configuration
- **External Tool Integration**: Uses GitPython for Git and rclone-python for iCloud operations

### Environment Variables

All configuration can be provided via environment variables with `SYNC_ICLOUD_GIT__` prefix:
- `GIT_REMOTE_URL`, `GIT_USERNAME`, `GIT_PAT` (required)
- `RCLONE_CONFIG_CONTENT`, `RCLONE_REMOTE_FOLDER` (required)
- `GIT_REPO_PATH`, `GIT_COMMIT_MESSAGE`, `GIT_COMMIT_USERNAME`, `GIT_COMMIT_EMAIL` (optional)

### CLI Usage Patterns

```bash
# Complete workflow
sync-icloud-git --step all

# Sync only (assumes existing repo)
sync-icloud-git --step sync

# Clone repository only
sync-icloud-git --step clone
```

### Dependencies

- **GitPython**: Git operations
- **rclone-python**: iCloud Drive access via WebDAV
- **pytest + pytest-cov**: Testing framework (dev dependency)