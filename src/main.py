from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import sys

REQUIRED_ENV_VARS = [
    'REDDIT_CLIENT_ID',
    'REDDIT_CLIENT_SECRET',
    'REDDIT_USER_AGENT',
    'TELEGRAM_BOT_TOKEN',
    'TELEGRAM_CHAT_ID',
]

def validate_env():
    missing = [var for var in REQUIRED_ENV_VARS if not os.environ.get(var)]
    if missing:
        sys.stderr.write(f"Missing required environment variables: {', '.join(missing)}\n")
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
    validate_env()
    port = int(os.environ.get('HEALTH_PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"Health server running on port {port}")
    server.serve_forever()
