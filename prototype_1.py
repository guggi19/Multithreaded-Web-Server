import http.server
import socketserver
import threading
import json

PORT = 5000
data_store = {}  # Simpler Key-Value-Speicher
lock = threading.Lock()

class CustomHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for reading a value"""
        if self.path.startswith("/read/"):
            varname = self.path.split("/")[-1]

            with lock:
                value = data_store.get(varname, "Variable not found")

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({varname: value}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Handle POST requests for writing a value"""
        if self.path == "/write":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            try:
                request_data = json.loads(post_data)
                varname = request_data.get("varname")
                value = request_data.get("value")

                if not varname or value is None:
                    raise ValueError("Missing varname or value")

                with lock:
                    data_store[varname] = value

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Value stored", varname: value}).encode("utf-8"))

            except (json.JSONDecodeError, ValueError) as e:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), CustomHandler) as httpd:
        print(f"[*] Server running on port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
