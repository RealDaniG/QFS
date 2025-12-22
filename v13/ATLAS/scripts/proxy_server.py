import http.server
import socketserver
import urllib.request
import os

PORT = 3000
BACKEND_URL = "http://127.0.0.1:8001"
DIRECTORY = "out"


# Configure logging
import logging

logging.basicConfig(
    filename="proxy_debug.log", level=logging.DEBUG, format="%(asctime)s %(message)s"
)


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        logging.debug(f"GET request for path: {self.path}")
        print(f"DEBUG: GET request for path: {self.path}")
        if self.path.startswith("/api/"):
            logging.debug("Proxying to backend")
            print("DEBUG: Proxying to backend")
            self.proxy_request()
        else:
            # Fallback for SPA routing: if file not found, serve index.html
            # But first try default behavior
            path = self.translate_path(self.path)
            if not os.path.exists(path) and not self.path.startswith("/_next"):
                self.path = "/"
            super().do_GET()

    def do_POST(self):
        print(f"DEBUG: POST request for path: {self.path}")
        if self.path.startswith("/api/"):
            self.proxy_request()
        else:
            self.send_error(405)

    def proxy_request(self):
        url = f"{BACKEND_URL}{self.path}"
        try:
            req = urllib.request.Request(url, method=self.command)
            # Forward headers (simplified)
            for k, v in self.headers.items():
                if k.lower() != "host":
                    req.add_header(k, v)

            # Forward body if POST/PUT
            if self.command in ["POST", "PUT"]:
                content_len = int(self.headers.get("Content-Length", 0))
                req.data = self.rfile.read(content_len)

            with urllib.request.urlopen(req) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            # Forward backend HTTP errors (404, 401, 500 from backend)
            self.send_response(e.code)
            for k, v in e.headers.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            print(f"PROXY ERROR: {e}")
            self.send_error(500, str(e))


print(f"Serving {DIRECTORY} on port {PORT} with proxy to {BACKEND_URL}")
with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
    httpd.serve_forever()
