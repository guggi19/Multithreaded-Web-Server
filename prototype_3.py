import http.server
import socketserver
import threading
import json
import http.cookies
import uuid

PORT = 5000
data_store = {}  # Simpler Key-Value-Speicher
session_store = {}  # Speichert Session-Daten
user_store = {"admin": "password123"}  # Einfache Benutzerverwaltung
lock = threading.Lock()

class CustomHandler(http.server.BaseHTTPRequestHandler):
    def get_session_id(self):
        """Ermittelt oder erstellt eine Session-ID"""
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            cookies = http.cookies.SimpleCookie(cookie_header)
            if 'session_id' in cookies:
                return cookies['session_id'].value
        
        return None
    
    def send_session_cookie(self, session_id):
        """Sendet die Session-ID als Cookie"""
        self.send_header("Set-Cookie", f"session_id={session_id}; HttpOnly")
    
    def do_POST(self):
        """Handle POST requests for login, writing a value"""
        if self.path == "/login":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            try:
                request_data = json.loads(post_data)
                username = request_data.get("username")
                password = request_data.get("password")
                
                if username in user_store and user_store[username] == password:
                    session_id = str(uuid.uuid4())
                    session_store[session_id] = {"username": username}
                    
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_session_cookie(session_id)
                    self.end_headers()
                    self.wfile.write(json.dumps({"message": "Login successful", "session_id": session_id}).encode("utf-8"))
                else:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Invalid credentials"}).encode("utf-8"))
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))
        
        elif self.path == "/write":
            session_id = self.get_session_id()
            if not session_id or session_id not in session_store:
                self.send_response(403)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
                return
            
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            try:
                request_data = json.loads(post_data)
                varname = request_data.get("varname")
                value = request_data.get("value")
                
                if not varname or value is None:
                    raise ValueError("Missing varname or value")
                
                with lock:
                    session_store[session_id][varname] = value
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_session_cookie(session_id)
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
    
    def do_GET(self):
        """Handle GET requests for reading a value"""
        session_id = self.get_session_id()
        if not session_id or session_id not in session_store:
            self.send_response(403)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
            return
        
        if self.path.startswith("/read/"):
            varname = self.path.split("/")[-1]
            
            with lock:
                session_data = session_store.get(session_id, {})
                value = session_data.get(varname, "Variable not found")
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_session_cookie(session_id)
            self.end_headers()
            self.wfile.write(json.dumps({varname: value}).encode("utf-8"))
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
