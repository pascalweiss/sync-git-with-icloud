#!/usr/bin/env bash

# Exit immediately if a command exits with non-zero status
set -e

# This script builds the docker image using podman
# Required environment variables must be set before running this script:
# - IMAGE_NAME: Name of the docker image
# - TAG: Tag for the docker image

DIR=$(dirname "$0")/..
cd "$DIR" || exit 1

# Verify required environment variables are set
for VAR in IMAGE_NAME TAG; do
    if [ -z "${!VAR}" ]; then
        echo "Error: $VAR environment variable is not set"
        exit 1
    fi
done

# Set image name and tag
LOCAL_IMAGE_NAME="localhost/$IMAGE_NAME:$TAG"

echo "Building $LOCAL_IMAGE_NAME with Podman..."

# Build the image with fully qualified image name to avoid short-name resolution error
podman build --format docker -t "$LOCAL_IMAGE_NAME" -f Dockerfile .

echo "Build completed successfully!"

