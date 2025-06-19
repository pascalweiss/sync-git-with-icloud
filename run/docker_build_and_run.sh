#!/usr/bin/env bash

# Simple script to build and run Docker container with podman
# Sources .env file and builds then runs the container

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

echo "Building and running Docker container with podman..."
echo "Image: $IMAGE_NAME:$TAG"
echo

# Build the image
./run/docker_build.sh

# Run the container
echo "🚀 Starting container..."
podman run -it --rm \
    -e "SYNC_ICLOUD_GIT__GIT_REMOTE_URL=$SYNC_ICLOUD_GIT__GIT_REMOTE_URL" \
    -e "SYNC_ICLOUD_GIT__GIT_USERNAME=$SYNC_ICLOUD_GIT__GIT_USERNAME" \
    -e "SYNC_ICLOUD_GIT__GIT_EMAIL=$SYNC_ICLOUD_GIT__GIT_EMAIL" \
    -e "SYNC_ICLOUD_GIT__GIT_PAT=$SYNC_ICLOUD_GIT__GIT_PAT" \
    -e "SYNC_ICLOUD_GIT__GIT_COMMIT_MESSAGE=$SYNC_ICLOUD_GIT__GIT_COMMIT_MESSAGE" \
    -e "SYNC_ICLOUD_GIT__GIT_COMMIT_USERNAME=$SYNC_ICLOUD_GIT__GIT_COMMIT_USERNAME" \
    -e "SYNC_ICLOUD_GIT__GIT_COMMIT_EMAIL=$SYNC_ICLOUD_GIT__GIT_COMMIT_EMAIL" \
    -e "SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER=$SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER" \
    -e "SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT=$SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT" \
    "$IMAGE_NAME:$TAG"
