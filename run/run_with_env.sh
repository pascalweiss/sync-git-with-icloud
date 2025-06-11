#!/usr/bin/env bash

# This script runs tests for the sync-icloud-git project

# Run the tests
LOC="$(dirname "$0")"

cd $LOC/..

rm -rf synced_repo


source .env
sync-icloud-git --step=all


ls -lath synced_repo