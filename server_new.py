import http.server
import socketserver
import threading
import json
import http.cookies
import uuid
import os
import hashlib

PORT = 5000
DATA_FILE = "users.json"
session_store = {}  # Speichert Session-Daten
lock = threading.Lock()

# Nutzer speichern/laden
def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(DATA_FILE, "w") as file:
        json.dump(users, file)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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
        """Handle POST requests for register, login, writing a value"""
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data)
        
        if self.path == "/register":
            username = request_data.get("username")
            password = request_data.get("password")
            
            if not username or not password:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing username or password"}).encode("utf-8"))
                return
            
            users = load_users()
            if username in users:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "User already exists"}).encode("utf-8"))
                return
            
            users[username] = hash_password(password)
            save_users(users)
            
            self.send_response(201)
            self.end_headers()
            self.wfile.write(json.dumps({"message": "User registered successfully"}).encode("utf-8"))
            return
        
        if self.path == "/login":
            username = request_data.get("username")
            password = request_data.get("password")
            
            users = load_users()
            if username in users and users[username] == hash_password(password):
                session_id = str(uuid.uuid4())
                session_store[session_id] = {"username": username}
                
                self.send_response(200)
                self.send_session_cookie(session_id)
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Login successful"}).encode("utf-8"))
                return
            else:
                self.send_response(401)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid credentials"}).encode("utf-8"))
                return
        
        if self.path == "/write":
            session_id = self.get_session_id()
            if not session_id or session_id not in session_store:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
                return
            
            varname = request_data.get("varname")
            value = request_data.get("value")
            
            if not varname or value is None:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing varname or value"}).encode("utf-8"))
                return
            
            with lock:
                session_store[session_id][varname] = value
            
            self.send_response(200)
            self.send_session_cookie(session_id)
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Value stored", varname: value}).encode("utf-8"))
            return
        
        self.send_response(404)
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests for reading a value"""
        session_id = self.get_session_id()
        if not session_id or session_id not in session_store:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
            return
        
        if self.path.startswith("/read/"):
            varname = self.path.split("/")[-1]
            
            with lock:
                session_data = session_store.get(session_id, {})
                value = session_data.get(varname, "Variable not found")
            
            self.send_response(200)
            self.send_session_cookie(session_id)
            self.end_headers()
            self.wfile.write(json.dumps({varname: value}).encode("utf-8"))
            return
        
        self.send_response(404)
        self.end_headers()

def run_server():
    with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), CustomHandler) as httpd:
        print(f"[*] Server running on port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
