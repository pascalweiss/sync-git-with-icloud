#!/bin/bash

# This script runs tests for the sync-icloud-git project

# Run the tests
if [ "$1" = "--cov" ]; then
    pytest --cov=sync_icloud_git
else
    pytest
fi
