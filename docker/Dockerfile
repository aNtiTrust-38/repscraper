# syntax=docker/dockerfile:1
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
# Ensure the config directory exists before copying or mounting
RUN mkdir -p /app/src/config
# Copy the entire config directory to ensure config.yaml is present
COPY src/config/ ./src/config/

# Copy entrypoint script from local docker/ directory into the image
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create logs and data dirs with correct permissions
RUN mkdir -p /app/logs /app/data && chmod 700 /app/logs /app/data

# Expose ports for health and web config
EXPOSE 8000 8080

# Default environment
ENV APP_MODE=scraper

ENTRYPOINT ["/entrypoint.sh"]
