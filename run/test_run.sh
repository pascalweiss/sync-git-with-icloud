#!/usr/bin/env bash

# This script runs tests for the sync-icloud-git project

set -e

# Run the tests
if [ "$1" = "--cov" ]; then
    pytest --cov=sync_icloud_git
else
    pytest
fi
