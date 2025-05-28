from http.server import BaseHTTPRequestHandler, HTTPServer
import os

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
    port = int(os.environ.get('HEALTH_PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"Health server running on port {port}")
    server.serve_forever()
