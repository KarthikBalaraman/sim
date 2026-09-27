#!/usr/bin/env python3
"""
Court Booking Revenue Simulator — Secure Server
Tamper-Proof Server-Side Google OAuth 2.0 Authentication & Role Whitelist Gatekeeper.

Zero external dependencies required (uses Python 3 standard library only).
"""

import os
import sys
import json
import hmac
import hashlib
import base64
import time
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie

# --- Path Resolution & Directory Layout ---
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SERVER_DIR) if os.path.basename(SERVER_DIR) == 'server' else SERVER_DIR

CLIENT_DIR = os.path.join(PROJECT_ROOT, 'client')
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')

def get_file_path(filename, search_dirs):
    for d in search_dirs:
        p = os.path.join(d, filename)
        if os.path.exists(p):
            return p
    return os.path.join(PROJECT_ROOT, filename)

def load_env(env_path):
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    env_vars[key.strip()] = val.strip().strip('"').strip("'")
    return env_vars

# Load .env if present, fallback to OS environment
env_file = os.path.join(PROJECT_ROOT, '.env')
file_env = load_env(env_file)

def get_config(key, default=''):
    return os.environ.get(key, file_env.get(key, default))

GOOGLE_CLIENT_ID = get_config('GOOGLE_CLIENT_ID', '')
ALLOWED_USERS_RAW = get_config('ALLOWED_USERS', 'admin@example.com,founder@yourdomain.com')
ALLOWED_USERS = set(u.strip().lower() for u in ALLOWED_USERS_RAW.split(',') if u.strip())
ALLOWED_DOMAINS_RAW = get_config('ALLOWED_DOMAINS', '')
ALLOWED_DOMAINS = set(d.strip().lower() for d in ALLOWED_DOMAINS_RAW.split(',') if d.strip())

SESSION_SECRET = get_config('SESSION_SECRET', 'simulator-secret-key-change-in-production-12345').encode('utf-8')
PORT = int(get_config('PORT', '8000'))
DEV_MODE = get_config('DEV_MODE', 'true').lower() in ('true', '1', 'yes')
SESSION_DURATION_SEC = 60 * 60 * 24 * 7  # 7 days

print("=" * 60)
print("Court Booking Revenue Simulator — Server Starting")
print(f"Project Root:    {PROJECT_ROOT}")
print(f"Port:            {PORT}")
print(f"Google Client ID: {GOOGLE_CLIENT_ID if GOOGLE_CLIENT_ID else '[NOT SET - Demo/Dev Mode Active]'}")
print(f"Allowed Emails:  {', '.join(ALLOWED_USERS) if ALLOWED_USERS else '[None]'}")
if ALLOWED_DOMAINS:
    print(f"Allowed Domains: {', '.join(ALLOWED_DOMAINS)}")
print(f"Dev Mode Bypass: {DEV_MODE}")
print("=" * 60)

# --- Cryptographic Session Token Helper ---
def create_session_token(user_info):
    payload = {
        'email': user_info.get('email', '').lower(),
        'name': user_info.get('name', ''),
        'picture': user_info.get('picture', ''),
        'exp': int(time.time()) + SESSION_DURATION_SEC
    }
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode('utf-8')).decode('utf-8')
    sig = hmac.new(SESSION_SECRET, payload_b64.encode('utf-8'), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{sig}"

def verify_session_token(token):
    if not token or '.' not in token:
        return None
    try:
        payload_b64, sig = token.split('.', 1)
        expected_sig = hmac.new(SESSION_SECRET, payload_b64.encode('utf-8'), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode('utf-8')).decode('utf-8'))
        if payload.get('exp', 0) < time.time():
            return None  # Expired
        email = payload.get('email', '').lower()
        if not is_email_authorized(email):
            return None  # Revoked or unauthorized
        return payload
    except Exception:
        return None

def is_email_authorized(email):
    if not email:
        return False
    email = email.lower().strip()
    if email in ALLOWED_USERS:
        return True
    for domain in ALLOWED_DOMAINS:
        if email.endswith(domain if domain.startswith('@') else f"@{domain}"):
            return True
    return False

# --- Request Handler ---
class SimulatorAuthHandler(BaseHTTPRequestHandler):

    def send_json(self, status_code, data, cookies=None):
        response_bytes = json.dumps(data).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(response_bytes)))
        if cookies:
            for cookie in cookies:
                self.send_header('Set-Cookie', cookie)
        self.end_headers()
        self.wfile.write(response_bytes)

    def send_file(self, file_path, content_type='text/html; charset=utf-8', status_code=200):
        if not os.path.exists(file_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")
            return
        with open(file_path, 'rb') as f:
            content = f.read()
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(content)

    def get_session_cookie(self):
        cookie_header = self.headers.get('Cookie')
        if not cookie_header:
            return None
        cookie = SimpleCookie()
        try:
            cookie.load(cookie_header)
            if 'sim_session' in cookie:
                return cookie['sim_session'].value
        except Exception:
            return None
        return None

    def make_cookie_header(self, token, max_age=SESSION_DURATION_SEC):
        return f"sim_session={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}"

    def make_clear_cookie_header(self):
        return "sim_session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"

    def read_json_body(self):
        content_len = int(self.headers.get('Content-Length', 0))
        if not content_len:
            return {}
        try:
            return json.loads(self.rfile.read(content_len).decode('utf-8'))
        except Exception:
            return {}

    def issue_session_and_respond(self, user_info):
        token = create_session_token(user_info)
        cookie_hdr = self.make_cookie_header(token)
        self.send_json(200, {'success': True, 'user': user_info}, cookies=[cookie_hdr])

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Health Check
        if path == '/api/health':
            self.send_json(200, {'status': 'healthy', 'time': int(time.time())})
            return

        # Current User API
        if path == '/api/me':
            token = self.get_session_cookie()
            user = verify_session_token(token)
            if user:
                self.send_json(200, {
                    'authenticated': True,
                    'user': {
                        'email': user['email'],
                        'name': user.get('name', ''),
                        'picture': user.get('picture', '')
                    }
                })
            else:
                self.send_json(200, {'authenticated': False})
            return

        # Public Auth Config (for client GIS init)
        if path == '/api/auth-config':
            self.send_json(200, {
                'clientId': GOOGLE_CLIENT_ID,
                'devMode': DEV_MODE,
                'allowedUsersList': list(ALLOWED_USERS) if DEV_MODE else []
            })
            return

        # Simulator Configuration API
        if path == '/api/config' or path == '/api/simulator-config':
            config_file = get_file_path('config.json', [CONFIG_DIR, PROJECT_ROOT])
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    self.send_json(200, config_data)
                    return
                except Exception as e:
                    self.send_json(500, {'error': f'Failed to parse config.json: {str(e)}'})
                    return
            self.send_json(404, {'error': 'config.json not found'})
            return

        # Logout Route
        if path == '/logout':
            self.send_response(302)
            self.send_header('Location', '/login')
            self.send_header('Set-Cookie', self.make_clear_cookie_header())
            self.end_headers()
            return

        # Login Page
        if path == '/login':
            token = self.get_session_cookie()
            if verify_session_token(token):
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
                return
            login_file = get_file_path('login.html', [CLIENT_DIR, PROJECT_ROOT])
            self.send_file(login_file)
            return

        # Protected Root Route: Serves Simulator.html ONLY IF authenticated & authorized
        if path in ('/', '/index.html', '/Simulator.html'):
            token = self.get_session_cookie()
            user = verify_session_token(token)
            if not user:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            simulator_file = get_file_path('Simulator.html', [CLIENT_DIR, PROJECT_ROOT])
            self.send_file(simulator_file)
            return

        # 404 for other routes
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"404 Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Google OAuth Token Verification Endpoint
        if path == '/auth/google':
            body = self.read_json_body()
            credential = body.get('credential')
            if not credential:
                self.send_json(400, {'success': False, 'error': 'Missing credential'})
                return

            try:
                verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={urllib.parse.quote(credential)}"
                req = urllib.request.Request(verify_url, headers={'User-Agent': 'Simulator-Auth-Server'})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    token_info = json.loads(resp.read().decode('utf-8'))

                email = token_info.get('email', '').lower()
                email_verified = token_info.get('email_verified')

                if str(email_verified).lower() not in ('true', '1'):
                    self.send_json(403, {'success': False, 'error': 'Google account email is not verified.'})
                    return

                if GOOGLE_CLIENT_ID and token_info.get('aud') != GOOGLE_CLIENT_ID:
                    self.send_json(403, {'success': False, 'error': 'Token audience mismatch (Invalid Client ID).'})
                    return

                if not is_email_authorized(email):
                    self.send_json(403, {
                        'success': False,
                        'error': f'Access Denied: Account {email} is not authorized to access this simulator. Contact administrator for permission.'
                    })
                    return

                self.issue_session_and_respond({
                    'email': email,
                    'name': token_info.get('name', email),
                    'picture': token_info.get('picture', '')
                })
                return
            except urllib.error.HTTPError as e:
                self.send_json(401, {'success': False, 'error': f'Google token verification failed: {e.reason}'})
                return
            except Exception as e:
                self.send_json(500, {'success': False, 'error': f'Internal verification error: {str(e)}'})
                return

        # Dev Mode Login Bypass (Only active if DEV_MODE=true)
        if path == '/auth/dev-login':
            if not DEV_MODE:
                self.send_json(403, {'success': False, 'error': 'Dev mode is disabled.'})
                return

            try:
                body = self.read_json_body()
                email = body.get('email', '').strip().lower()
                name = body.get('name', 'Developer User')

                if not email:
                    email = next(iter(ALLOWED_USERS)) if ALLOWED_USERS else 'developer@example.com'

                if not is_email_authorized(email):
                    self.send_json(403, {
                        'success': False,
                        'error': f'Access Denied: Account {email} is not in the ALLOWED_USERS whitelist.'
                    })
                    return

                self.issue_session_and_respond({'email': email, 'name': name, 'picture': ''})
                return
            except Exception as e:
                self.send_json(500, {'success': False, 'error': str(e)})
                return

        # Logout API
        if path == '/auth/logout':
            self.send_json(200, {'success': True}, cookies=[self.make_clear_cookie_header()])
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"404 Not Found")

def run(port=PORT):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, SimulatorAuthHandler)
    print(f"Server running at http://localhost:{port}/")
    print(f"Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully.")
        httpd.server_close()

if __name__ == '__main__':
    run()
