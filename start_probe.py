#!/usr/bin/env python3
import os
import traceback
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get('PORT', '5000'))

def dump_env():
    print("\n=== ENVIRONMENT DUMP ===")
    for k in sorted(os.environ.keys()):
        # hide obvious secrets
        if (k == 'DATABASE_URL') or ('KEY' in k) or ('SECRET' in k) or ('PASSWORD' in k):
            print(f"{k}=***")
        else:
            print(f"{k}={os.environ.get(k)}")
    print("=== END ENVIRONMENT DUMP ===\n")

def try_create_app():
    try:
        # Import and initialize the Flask app to trigger any startup errors
        from revmark import create_app
        app = create_app()
        print("✅ create_app() initialized successfully (no exception raised)")
    except Exception:
        print("!!! create_app() raised an exception:")
        traceback.print_exc()

class ProbeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/__status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"ok","probe":true}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # forward to stdout
        sys.stdout.write("[probe] %s - - %s\n" % (self.client_address[0], format%args))

def run_probe():
    server = HTTPServer(('0.0.0.0', PORT), ProbeHandler)
    print(f"Probe HTTP server listening on 0.0.0.0:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

if __name__ == '__main__':
    dump_env()
    try_create_app()
    run_probe()
