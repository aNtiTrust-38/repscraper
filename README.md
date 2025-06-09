# FashionReps Scraper

A production-grade, Dockerized Reddit scraper for r/FashionReps with a modern web-based configuration UI, robust error handling, Telegram notifications, SQLite persistence, and a focus on maintainability, testability, and operational robustness.

## Features
- Reddit API integration (PRAW), batch scraping, config-driven
- Link extraction with platform priority matrix
- Quality filtering and scoring (upvotes, comments, author karma, content, awards)
- Telegram notification formatting and sending
- SQLite persistence and deduplication
- End-to-end integration tests (Reddit → Processing → Telegram)
- Docker Compose with healthcheck, restart policy, resource limits, and volume mounts
- `/health` endpoint implemented and tested
- Environment variable validation, robust logging (loguru), secure secrets handling
- Telegram alerting utility, integrated error alerting and health monitoring
- Periodic health checks with alerting and logging
- Modern web-based configuration UI (FastAPI backend, HTML5/CSS3/JS frontend, Pydantic validation, PyYAML I/O)
- Real-time validation, test connections, responsive design, tooltips, confirmation dialogs, and robust security
- API endpoints: `/config` (GET/POST), `/config/validate`, `/config/defaults`, `/config/test-reddit`, `/config/test-telegram`, `/health`
- Config backup/restore (atomic, UI + API), with tests and documentation

## Quick Start

1. **Clone the repo and enter the directory:**
   ```sh
   git clone <repo-url>
   cd FashionReps\ Scraper
   ```
2. **Create a `.env` file in the project root:**
   ```env
   REDDIT_CLIENT_ID=your_reddit_client_id
   REDDIT_CLIENT_SECRET=your_reddit_client_secret
   REDDIT_USER_AGENT=your_reddit_user_agent
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=your_telegram_chat_id
   ```
3. **Build and start the stack:**
   ```sh
   docker-compose -f docker/docker-compose.yml up -d --build
   ```
4. **Access the web config UI:**
   - Open [http://localhost:8080](http://localhost:8080) in your browser.

## Troubleshooting

- **Environment variables not picked up:**
  - Ensure `.env` is in the project root and you run Docker Compose from the root.
  - Use `${VAR}` syntax in `docker-compose.yml`.
- **File/Directory mount errors:**
  - Mount the entire `src/config` directory, not just `config.yaml`.
- **Entrypoint or import errors:**
  - Set `PYTHONPATH=/app` in `entrypoint.sh`.
  - Ensure all main scripts and FastAPI app imports are correct.
- **Web UI not found at `/`:**
  - The root route now serves the UI (`index.html`).
- **See logs for details:**
  - `docker-compose -f docker/docker-compose.yml logs -f`

## Telegram Command Interface

Interact with the scraper in real-time using these commands:

| Command | Description |
|---------|-------------|
| `/run-batch` | Run a scraping batch immediately. Use this to force an on-demand scan instead of waiting for the scheduled interval. |
| `/status` | Check current system status. Returns total processed posts, number processed today, and the timestamp of the last successful batch run. |

Key points:
- **Real-time control:** Execute tasks or check health instantly without altering the schedule.
- **Auto-listening:** The bot automatically starts polling for commands after startup—no extra setup required.
- **Security:** The bot *only* processes commands originating from the `TELEGRAM_CHAT_ID` configured in your environment. Messages from any other chat are ignored and logged.

Use these commands in your Telegram chat to manage the scraper effortlessly.

## Roadmap
- Advanced filtering, analytics, export, multi-user, integrations, and rich Telegram features (see scratchpad for details).

## License
Personal use only.
