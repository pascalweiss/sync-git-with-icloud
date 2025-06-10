#!/usr/bin/env bash

# Simple Docker build script using podman
# Sources .env file for IMAGE_NAME and TAG variables

set -e

# Navigate to project root
cd "$(dirname "$0")/.."

# Set defaults
IMAGE_NAME=${IMAGE_NAME:-"sync-icloud-git"}
TAG=${TAG:-"latest"}

# Source environment variables if .env exists (optional)
if [ -f ".env" ]; then
    source .env
    # Re-apply defaults in case .env doesn't define them
    IMAGE_NAME=${IMAGE_NAME:-"sync-icloud-git"}
    TAG=${TAG:-"latest"}
fi

echo "Building Docker image with podman: $IMAGE_NAME:$TAG"

# Build with podman
podman build -t "$IMAGE_NAME:$TAG" .

echo "✅ Build completed successfully!"

