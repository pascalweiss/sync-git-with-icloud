FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install rclone
RUN curl -fsSL https://rclone.org/install.sh | bash

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

# Create directories with proper permissions
RUN mkdir -p /app && chown -R appuser:appuser /app
RUN mkdir -p /home/appuser/.config && chown -R appuser:appuser /home/appuser

# Copy the application files
COPY --chown=appuser:appuser . .

# Install the application and its dependencies using pip
RUN pip install .

# Switch to non-root user
USER appuser

# Command to run the application
ENTRYPOINT ["sync-icloud-git"]
