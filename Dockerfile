FROM python:3.10-slim

WORKDIR /app

# Copy the application files
COPY . .

# Install the application and its dependencies using pip
RUN pip install .

# Command to run the application
ENTRYPOINT ["sync-icloud-git"]
