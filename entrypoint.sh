#!/bin/sh
set -e

# Print the current mode
echo "Starting container in $APP_MODE mode..."

export PYTHONPATH=/app

if [ "$APP_MODE" = "web_config" ]; then
    # Start the web configuration server
    exec uvicorn web_config.main:app --host 0.0.0.0 --port 8080 --app-dir /app/src
else
    # Start the main scraper
    exec python /app/src/main.py
fi 