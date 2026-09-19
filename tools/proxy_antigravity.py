#!/usr/bin/env python3
"""
proxy_antigravity.py
Proxy lokal ringan untuk Antigravity.
Menerima request dari Antigravity di http://127.0.0.1:8085/v1
dan meneruskannya ke http://40.50.60.2:20128/v1 dengan menyuntikkan Bearer API Key.
"""
import sys
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

TARGET_URL = "http://40.50.60.2:20128/v1"
API_KEY = "sk-58cfc75c95fa1662-n3z136-0e8b36e4"
DEFAULT_MODEL = "ag/claude-sonnet-4-6"
PORT = 8085

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok": true}')
            return
        
        url = f"{TARGET_URL}{self.path}"
        headers = {"Authorization": f"Bearer {API_KEY}"}
        try:
            r = requests.get(url, headers=headers, timeout=30)
            self.send_response(r.status_code)
            for k, v in r.headers.items():
                if k.lower() not in ["content-encoding", "transfer-encoding", "content-length"]:
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(r.content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len)
        try:
            data = json.loads(body.decode("utf-8"))
            # Jika model dari Antigravity tidak dikenali, arahkan ke DEFAULT_MODEL
            if "model" not in data or data["model"] in ["custom", "default", ""]:
                data["model"] = DEFAULT_MODEL
            body = json.dumps(data).encode("utf-8")
        except Exception:
            pass

        url = f"{TARGET_URL}{self.path}"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            r = requests.post(url, data=body, headers=headers, stream=True, timeout=120)
            self.send_response(r.status_code)
            for k, v in r.headers.items():
                if k.lower() not in ["content-encoding", "transfer-encoding"]:
                    self.send_header(k, v)
            self.end_headers()
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    self.wfile.write(chunk)
                    self.wfile.flush()
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

def run():
    server = HTTPServer(("127.0.0.1", PORT), ProxyHandler)
    print(f"[*] Antigravity Custom Proxy berjalan di http://127.0.0.1:{PORT}")
    print(f"[*] Target Remote: {TARGET_URL}")
    print(f"[*] Health Check: http://127.0.0.1:{PORT}/health")
    server.serve_forever()

if __name__ == "__main__":
    run()
