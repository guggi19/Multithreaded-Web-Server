import http.server
import socketserver

# Define the port
PORT = 8080

# Custom request handler
class ThreadedHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            print(f"Received request: {self.path}")
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Moin Oli! This is our multithreaded server.")
        except Exception as e:
            print(f"Error handling request: {e}")

# Create a multi-threaded HTTP server
class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True  # Ensures threads exit when main server stops

# Set up the server
with ThreadedHTTPServer(("", PORT), ThreadedHTTPRequestHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
