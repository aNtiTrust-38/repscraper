# FashionReps Scraper

## Overview
Personal Reddit scraper for r/FashionReps with intelligent link extraction and Telegram notifications.
**Reference: See instructions.md for complete technical specifications**

## Features
- 2-hour batch processing of r/FashionReps posts
- Weighted platform priority (Taobao → Weidian → 1688 → Yupoo)
- Rich Telegram notifications with images and buttons
- Jadeship link conversion (AllChinaBuy → CNFans → Mulebuy priority)
- SQLite persistence with quality learning
- Docker containerized deployment
- **Duplicate prevention:** In-memory (MVP) and persistent (SQLite) deduplication supported
- **Quality scoring:** Posts are scored for relevance and quality before notification
- **Robust logging:** All errors and important events are logged to `logs/app.log` with rotation and retention (loguru)
- **Secure secrets handling:** Secrets are never logged or exposed, verified by automated tests
- [x] Reddit API integration: The RedditScraper now supports authenticated batch fetching from r/FashionReps, with error handling and batch size configuration per instructions.md. This is fully covered by integration tests using TDD.

**Detailed Requirements: See instructions.md sections 'Platform Priority Matrix' and 'Link Conversion Priority'**

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aNtiTrust-38/repscraper.git
   cd repscraper
   ```
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
3. **Configure environment variables:**
   - Copy `.env.example` to `.env` and fill in your Reddit and Telegram credentials.
4. **Edit `config.yaml`** as needed for batch interval, filters, and platform priorities.
5. **Run tests:**
   ```bash
   pytest
   ```
6. **Run the application:**
   ```bash
   python src/main.py
   ```

## Docker Installation

1. **Build the Docker image:**
   ```bash
   docker build -t fashionreps-scraper .
   ```
2. **Run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```
3. **Check health:**
   ```bash
   curl http://localhost:8000/health
   ```

## Docker Healthcheck & Production Deployment

- The Docker Compose file includes a healthcheck that pings the `/health` endpoint every 30 seconds.
- The container uses `restart: unless-stopped` for resilience.
- Data and logs are persisted via volume mounts (`./data`, `./logs`).
- Resource limits are set for CPU and memory (customize as needed).
- To check container health:
  ```bash
  docker-compose ps
  # Look for "healthy" status in the output
  ```
- For production, ensure secrets are set via environment variables and not hardcoded.

## Logging & Secrets Handling

- All logs are written to `logs/app.log` (configurable via `LOG_FILE` env var).
- Log rotation and retention are enabled (10MB per file, 5 days retention).
- Errors and important events are logged with stack traces.
- **Secrets are never logged or exposed. This is verified by automated tests.**
- **Best practice:** Always load secrets from environment variables or secure config files. Never log or print secrets.

## Health Monitoring & Alerting

- The system includes a periodic health check (default: every 60 seconds) that monitors core dependencies (e.g., database, API connectivity).
- Health check failures (e.g., DB unreachable) trigger a Telegram alert if alerting is enabled.
- **Only critical errors** (not warnings or recoverable issues) trigger Telegram alerts.
- All health check events (start, success, failure) are logged to `logs/app.log`.
- Health monitoring and alerting can be configured in `config.yaml` under the `health` section:
  ```yaml
  health:
    enabled: true
    port: 8000
    telegram_alerts: true
    discord_webhook: ""
    pushbullet_token: ""
  ```
- To enable/disable Telegram alerts, set `telegram_alerts` in `config.yaml` or use the `TELEGRAM_ALERT_ON_ERROR` environment variable (`1`/`true` to enable).
- The health check interval can be customized by calling `start_periodic_health_check(interval_sec=YOUR_INTERVAL)` in `src/notifications/health_monitor.py`.
- To test health monitoring, run:
  ```bash
  python src/notifications/health_monitor.py
  # Or run the full app and simulate a failure
  ```
- All health check and alert events are logged for auditing and troubleshooting.

## Telegram Bot Registration

1. Message [@BotFather](https://t.me/BotFather) in Telegram.
2. Send `/newbot` and follow the prompts to create a bot.
3. Save the bot token and add it to your `.env` file as `TELEGRAM_BOT_TOKEN`.
4. Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot).
5. Add your chat ID to `.env` as `TELEGRAM_CHAT_ID`.

## Configuration

- All configuration options are in `config.yaml`:
  - Batch interval, subreddit, max posts per batch
  - Quality filters (min upvotes, min comments, max age)
  - Platform priorities and weights
  - Jadeship API and agent priorities
  - Database and logging settings
  - **Health monitoring and alerting (see `health` section for options)**

## Development
- All core and advanced features (link extraction, filtering, notification formatting, duplicate prevention, quality scoring) are covered by tests and implemented using TDD.
- In-memory and persistent deduplication are both supported.
- The system is ready for end-to-end integration and production deployment.
[Development setup following instructions.md implementation guidelines]
- Note: Some integration tests for log file creation are marked xfail on macOS due to temp directory isolation; this is not a logic bug but an environment limitation. See CHANGELOG for details.
