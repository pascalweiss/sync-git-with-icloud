#!/usr/bin/env bash

# Simple script to run existing Docker container with podman
# Sources .env file for image name, tag, and required environment variables

set -e

# Navigate to project root
cd "$(dirname "$0")/.."

# Source environment variables
if [ -f ".env" ]; then
    source .env
else
    echo "Error: .env file not found"
    exit 1
fi

# Set defaults
IMAGE_NAME=${IMAGE_NAME:-"sync-icloud-git"}
TAG=${TAG:-"latest"}

echo "🚀 Running Docker container with podman: $IMAGE_NAME:$TAG"

# Run the container with all required environment variables
# Use --network=host to allow container to access localhost services on the host
podman run -it --rm \
    --network=host \
    -e "SYNC_ICLOUD_GIT__GIT_REMOTE_URL=$SYNC_ICLOUD_GIT__GIT_REMOTE_URL" \
    -e "SYNC_ICLOUD_GIT__GIT_USERNAME=$SYNC_ICLOUD_GIT__GIT_USERNAME" \
    -e "SYNC_ICLOUD_GIT__GIT_EMAIL=$SYNC_ICLOUD_GIT__GIT_EMAIL" \
    -e "SYNC_ICLOUD_GIT__GIT_PAT=$SYNC_ICLOUD_GIT__GIT_PAT" \
    -e "SYNC_ICLOUD_GIT__GIT_COMMIT_MESSAGE=$SYNC_ICLOUD_GIT__GIT_COMMIT_MESSAGE" \
    -e "SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER=$SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER" \
    -e "SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT=$SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT" \
    "$IMAGE_NAME:$TAG"
