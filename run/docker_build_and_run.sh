#!/bin/env bash

# This script sources the .env file and builds the Docker image,
# then runs the container

set -e

DIR=$(dirname "$0")/..
cd "$DIR" || exit 1


# Source the environment variables
source .env

# Build the Docker image
./run/docker_build.sh

# Run the container
echo "Building completed, now running the container..."
podman run -it localhost/${IMAGE_NAME}:${TAG}
