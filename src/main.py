from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import sys
from loguru import logger

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

if __name__ == '__main__':
    setup_logging()
    try:
        validate_env()
        port = int(os.environ.get('HEALTH_PORT', 8000))
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        logger.info(f"Health server running on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
