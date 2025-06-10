#!/usr/bin/env bash

# Exit immediately if a command exits with non-zero status
set -e

# This script pushes the docker image to registry
# Required environment variables must be set before running this script:
# - IMAGE_NAME: Name of the docker image
# - TAG: Tag for the docker image
# - DOCKER_REGISTRY: URL of the docker registry
# - NEXUS_USERNAME: Username for registry authentication
# - NEXUS_PASSWORD: Password for registry authentication

DIR=$(dirname "$0")/..
cd "$DIR" || exit 1

# Verify required environment variables are set
for VAR in IMAGE_NAME TAG DOCKER_REGISTRY NEXUS_USERNAME NEXUS_PASSWORD; do
    if [ -z "${!VAR}" ]; then
        echo "Error: $VAR environment variable is not set"
        exit 1
    fi
done

# Set image name and tag
LOCAL_IMAGE_NAME="localhost/$IMAGE_NAME:$TAG"
REMOTE_IMAGE_NAME="$DOCKER_REGISTRY/$IMAGE_NAME:$TAG"

# Tag the image for the registry
echo "Tagging image as $REMOTE_IMAGE_NAME..."
podman tag "$LOCAL_IMAGE_NAME" "$REMOTE_IMAGE_NAME"

# Login to registry using saved credentials
echo "Logging into registry $DOCKER_REGISTRY..."
echo "$NEXUS_PASSWORD" | podman login -u "$NEXUS_USERNAME" --password-stdin "$DOCKER_REGISTRY"

# Push the image
echo "Pushing image to $REMOTE_IMAGE_NAME..."
podman push "$REMOTE_IMAGE_NAME"
echo "Image successfully pushed to $REMOTE_IMAGE_NAME"
