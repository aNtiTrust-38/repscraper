from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import sys
from loguru import logger
from src.processors.quality_filter import filter_by_flair, basic_filter
from src.notifications.telegram_bot import TelegramBot
import datetime
from src.scrapers.reddit_scraper import RedditScraper
import time
from src.database.crud import PersistentDeduper

REQUIRED_ENV_VARS = [
    'REDDIT_CLIENT_ID',
    'REDDIT_CLIENT_SECRET',
    'REDDIT_USER_AGENT',
    'TELEGRAM_BOT_TOKEN',
    'TELEGRAM_CHAT_ID',
]

def setup_logging():
    log_file = os.environ.get('LOG_FILE', 'logs/app.log')
    log_dir = os.path.dirname(log_file)
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        print(f"[setup_logging] Failed to create log directory {log_dir}: {e}", file=sys.stderr)
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    try:
        logger.add(log_file, rotation="10 MB", retention="5 days", level="INFO")
    except Exception as e:
        print(f"[setup_logging] Failed to add log file {log_file}: {e}", file=sys.stderr)

def validate_env():
    missing = [var for var in REQUIRED_ENV_VARS if not os.environ.get(var)]
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        log_file = os.environ.get('LOG_FILE', 'logs/app.log')
        log_dir = os.path.dirname(log_file)
        print(f"[validate_env] LOG_FILE path: {log_file}", file=sys.stderr)
        print(f"[validate_env] Log dir exists: {os.path.exists(log_dir)}", file=sys.stderr)
        print(f"[validate_env] PID: {os.getpid()} CWD: {os.getcwd()}", file=sys.stderr)
        try:
            with open(log_file, 'a') as f:
                f.write(f"[validate_env] Missing required environment variables: {', '.join(missing)}\n")
            print(f"[validate_env] After write, file exists: {os.path.exists(log_file)}", file=sys.stderr)
            print(f"[validate_env] Dir contents: {os.listdir(log_dir)}", file=sys.stderr)
        except Exception as file_exc:
            print(f"[validate_env] Exception writing to log file: {file_exc}", file=sys.stderr)
        # Try writing to /tmp/app.log for diagnostics
        try:
            with open('/tmp/app.log', 'a') as f:
                f.write(f"[validate_env] /tmp/app.log test\n")
            print(f"[validate_env] /tmp/app.log exists: {os.path.exists('/tmp/app.log')}", file=sys.stderr)
        except Exception as tmp_exc:
            print(f"[validate_env] Exception writing to /tmp/app.log: {tmp_exc}", file=sys.stderr)
        try:
            logger.complete()
            logger.remove()
        except Exception:
            pass
        time.sleep(1)
        sys.exit(1)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'ok')
        else:
            self.send_response(404)
            self.end_headers()

def run_batch():
    # Load config from environment or config.yaml (simplified for now)
    config = {
        'client_id': os.environ['REDDIT_CLIENT_ID'],
        'client_secret': os.environ['REDDIT_CLIENT_SECRET'],
        'user_agent': os.environ['REDDIT_USER_AGENT'],
        'batch_interval_hours': int(os.environ.get('BATCH_INTERVAL_HOURS', 2)),
        'subreddits': [os.environ.get('SUBREDDIT', 'FashionReps')],
        'max_posts_per_batch': int(os.environ.get('MAX_POSTS_PER_BATCH', 5)),
    }
    try:
        scraper = RedditScraper(config)
        posts = scraper.fetch_batch()
    except Exception as e:
        logger.error(f"Reddit API fetch failed: {e}")
        posts = []
    allowed_flairs = ['QC', 'Haul', 'Review']
    min_upvotes = 5
    min_comments = 2
    # Persistent deduplication
    deduper = PersistentDeduper('data/fashionreps.db')
    # 1. Flair filter
    filtered = filter_by_flair(posts, allowed_flairs)
    # 2. Quality filter
    now = datetime.datetime.utcnow()
    filtered = basic_filter(filtered, min_upvotes, min_comments, max_age_hours=24, now=now)
    # 3. Deduplication (persistent)
    filtered = [p for p in filtered if not deduper.is_duplicate(p['id'])]
    # 4. Notification and mark as processed
    token = os.environ.get('TELEGRAM_BOT_TOKEN', 'dummy')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', 'dummy')
    bot = TelegramBot(token, chat_id)
    for post in filtered:
        bot.send_item_notification(post)
        deduper.mark_processed(post['id'])

if __name__ == '__main__':
    setup_logging()
    try:
        validate_env()
        run_batch()  # Run the batch once on startup
        port = int(os.environ.get('HEALTH_PORT', 8000))
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        logger.info(f"Health server running on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        log_file = os.environ.get('LOG_FILE', 'logs/app.log')
        log_dir = os.path.dirname(log_file)
        print(f"[main except] LOG_FILE path: {log_file}", file=sys.stderr)
        print(f"[main except] Log dir exists: {os.path.exists(log_dir)}", file=sys.stderr)
        print(f"[main except] PID: {os.getpid()} CWD: {os.getcwd()}", file=sys.stderr)
        try:
            with open(log_file, 'a') as f:
                f.write(f"[main except] Fatal error: {e}\n")
            print(f"[main except] After write, file exists: {os.path.exists(log_file)}", file=sys.stderr)
            print(f"[main except] Dir contents: {os.listdir(log_dir)}", file=sys.stderr)
        except Exception as file_exc:
            print(f"[main except] Exception writing to log file: {file_exc}", file=sys.stderr)
        # Try writing to /tmp/app.log for diagnostics
        try:
            with open('/tmp/app.log', 'a') as f:
                f.write(f"[main except] /tmp/app.log test\n")
            print(f"[main except] /tmp/app.log exists: {os.path.exists('/tmp/app.log')}", file=sys.stderr)
        except Exception as tmp_exc:
            print(f"[main except] Exception writing to /tmp/app.log: {tmp_exc}", file=sys.stderr)
        # Telegram alerting logic
        alert_on_error = os.environ.get('TELEGRAM_ALERT_ON_ERROR', '').lower() in ('1', 'true')
        token = os.environ.get('TELEGRAM_BOT_TOKEN')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        if alert_on_error or (token and chat_id and os.environ.get('TELEGRAM_ALERT_ON_ERROR', '') == ''):
            try:
                from src.notifications.health_monitor import send_telegram_alert
                send_telegram_alert(f"Fatal error: {e}", token, chat_id)
            except Exception as alert_exc:
                logger.error(f"Failed to send Telegram alert: {alert_exc}")
        try:
            logger.complete()
            logger.remove()
        except Exception:
            pass
        time.sleep(1)
        sys.exit(1)
