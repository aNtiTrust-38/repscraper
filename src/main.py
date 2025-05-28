from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import sys
from loguru import logger
from src.processors.quality_filter import filter_by_flair, basic_filter
from src.notifications.telegram_bot import TelegramBot
import datetime

REQUIRED_ENV_VARS = [
    'REDDIT_CLIENT_ID',
    'REDDIT_CLIENT_SECRET',
    'REDDIT_USER_AGENT',
    'TELEGRAM_BOT_TOKEN',
    'TELEGRAM_CHAT_ID',
]

def setup_logging():
    log_file = os.environ.get('LOG_FILE', 'logs/app.log')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.add(log_file, rotation="10 MB", retention="5 days", level="INFO")

def validate_env():
    missing = [var for var in REQUIRED_ENV_VARS if not os.environ.get(var)]
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
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
    now = datetime.datetime.utcnow()
    # Placeholder: mock posts (replace with real scraping later)
    posts = [
        {'id': '1', 'flair': 'QC', 'upvotes': 10, 'comments': 3, 'created_utc': now, 'author': 'user1', 'title': 'QC Shoes', 'platform': 'taobao', 'url': 'https://item.taobao.com/item.htm?id=1'},
        {'id': '2', 'flair': 'Haul', 'upvotes': 5, 'comments': 2, 'created_utc': now, 'author': 'user2', 'title': 'Haul Bag', 'platform': 'weidian', 'url': 'https://weidian.com/item.html?id=2'},
        {'id': '3', 'flair': 'W2C', 'upvotes': 8, 'comments': 2, 'created_utc': now, 'author': 'user3', 'title': 'W2C Shirt', 'platform': '1688', 'url': 'https://detail.1688.com/offer/3.html'},
        {'id': '4', 'flair': 'QC', 'upvotes': 2, 'comments': 1, 'created_utc': now, 'author': 'user4', 'title': 'Low Upvotes', 'platform': 'yupoo', 'url': 'https://x.yupoo.com/albums/4'},
        {'id': '5', 'flair': 'QC', 'upvotes': 10, 'comments': 3, 'created_utc': now, 'author': 'user5', 'title': 'Duplicate', 'platform': 'pandabuy', 'url': 'https://pandabuy.com/item/5'},
    ]
    allowed_flairs = ['QC', 'Haul', 'Review']
    min_upvotes = 5
    min_comments = 2
    processed_ids = {'5'}  # Simulate already processed
    def is_duplicate(post_id):
        return post_id in processed_ids
    # 1. Flair filter
    filtered = filter_by_flair(posts, allowed_flairs)
    # 2. Quality filter
    filtered = basic_filter(filtered, min_upvotes, min_comments, max_age_hours=24, now=now)
    # 3. Deduplication
    filtered = [p for p in filtered if not is_duplicate(p['id'])]
    # 4. Notification
    token = os.environ.get('TELEGRAM_BOT_TOKEN', 'dummy')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', 'dummy')
    bot = TelegramBot(token, chat_id)
    for post in filtered:
        bot.send_item_notification(post)

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
        sys.exit(1)
