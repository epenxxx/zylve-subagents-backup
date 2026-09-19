import sys
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

TARGET = "http://40.50.60.2:20128"
API_KEY = "sk-58cfc75c95fa1662-n3z136-0e8b36e4"

class LoggingProxy(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"[GET] {self.path}")
        print(f"[Headers] {dict(self.headers)}")
        url = f"{TARGET}{self.path}"
        headers = dict(self.headers)
        headers["Authorization"] = f"Bearer {API_KEY}"
        headers["x-goog-api-key"] = API_KEY
        r = requests.get(url, headers=headers)
        self.send_response(r.status_code)
        for k, v in r.headers.items():
            if k.lower() not in ["content-encoding", "transfer-encoding", "content-length"]:
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(r.content)

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len)
        print(f"[POST] {self.path}")
        print(f"[Headers] {dict(self.headers)}")
        print(f"[Body sample] {body[:200]}")
        url = f"{TARGET}{self.path}"
        headers = dict(self.headers)
        headers["Authorization"] = f"Bearer {API_KEY}"
        headers["x-goog-api-key"] = API_KEY
        # Strip host header
        headers.pop("host", None)
        headers.pop("Host", None)
        
        r = requests.post(url, data=body, headers=headers, stream=True)
        print(f"[Response status] {r.status_code}")
        self.send_response(r.status_code)
        for k, v in r.headers.items():
            if k.lower() not in ["content-encoding", "transfer-encoding"]:
                self.send_header(k, v)
        self.end_headers()
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                self.wfile.write(chunk)
                self.wfile.flush()

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8085), LoggingProxy)
    print("Proxy listening on 8085...")
    server.serve_forever()
