#!/bin/bash

# This script sources the .env file and builds the Docker image,
# then runs the container

# Source the environment variables
source .env

# Build the Docker image
./run/build_docker.sh

# Run the container
echo "Building completed, now running the container..."
podman run -it localhost/${IMAGE_NAME}:${TAG}
