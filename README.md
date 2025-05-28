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
  - Health monitoring and alerting

## Development
- All core and advanced features (link extraction, filtering, notification formatting, duplicate prevention, quality scoring) are covered by tests and implemented using TDD.
- In-memory and persistent deduplication are both supported.
- The system is ready for end-to-end integration and production deployment.
[Development setup following instructions.md implementation guidelines]
