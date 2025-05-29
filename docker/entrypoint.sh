#!/bin/sh
set -e

if [ "$APP_MODE" = "scraper" ]; then
    echo "[Entrypoint] Starting FashionReps Scraper (main app)"
    exec python src/main.py
elif [ "$APP_MODE" = "web_config" ]; then
    echo "[Entrypoint] Starting Web Config UI (FastAPI)"
    exec uvicorn src.web_config.app:app --host 0.0.0.0 --port 8080
else
    echo "[Entrypoint] Unknown APP_MODE: $APP_MODE" >&2
    exit 1
fi
