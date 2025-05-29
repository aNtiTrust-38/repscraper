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
COPY config.yaml ./src/config/config.yaml

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create logs and data dirs with correct permissions
RUN mkdir -p /app/logs /app/data && chmod 700 /app/logs /app/data

# Expose ports for health and web config
EXPOSE 8000 8080

# Default environment
ENV APP_MODE=scraper

ENTRYPOINT ["/entrypoint.sh"]
