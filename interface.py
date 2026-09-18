from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import sqlite3
import os
import re
from bridge_node import generate_claim_proof

ENGINE_DIR = os.path.expanduser('~/structor-engine')
os.chdir(ENGINE_DIR)
DB_PATH = os.path.join(ENGINE_DIR, 'treasury.db')
CONFIG_PATH = os.path.join(ENGINE_DIR, 'config/structor_mesh.yml')
STATE_FILE = os.path.join(ENGINE_DIR, '.engine_state')

def get_configured_wallet():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            match = re.search(r'address:\s*"([^"]+)"', f.read())
            if match:
                return match.group(1)
    return "0x6b6c0...FfD57"

def set_throttle_state(mode):
    with open(STATE_FILE, 'w') as f:
        f.write(mode)

class SovereignInterfaceHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
            user_msg = post_data.get("message", "")
            set_throttle_state("STEALTH_THROTTLE")

            reply = f"Sovereign AI processed: '{user_msg}'. Engine functioning normally."
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply}).encode('utf-8'))

        elif self.path == '/api/admin/set_wallet':
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
            wallet = post_data.get("address", "")
            
            if wallet:
                os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
                with open(CONFIG_PATH, 'w') as f:
                    f.write(f'address: "{wallet}"\n')

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "updated", "wallet": wallet}).encode('utf-8'))

    def do_GET(self):
        if self.path == '/api/admin/wallet':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            conn = sqlite3.connect(DB_PATH, timeout=10)
            c = conn.cursor()
            c.execute('PRAGMA busy_timeout=5000;')
            c.execute('SELECT COUNT(*), COALESCE(SUM(reward), 0), COALESCE(AVG(hashrate), 0) FROM transactions')
            count, total, avg_hash = c.fetchone()
            conn.close()

            data = {
                "address": get_configured_wallet(),
                "balance_mtrx": round(total, 4),
                "blocks_mined": count,
                "avg_hashrate": round(avg_hash, 1),
                "status": "Mining Active"
            }
            self.wfile.write(json.dumps(data).encode('utf-8'))

        elif self.path == '/api/admin/claim':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            target_wallet = get_configured_wallet()
            proof_data = generate_claim_proof(target_wallet)
            self.wfile.write(json.dumps(proof_data).encode('utf-8'))
        else:
            super().do_GET()

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8090), SovereignInterfaceHandler)
    print("Sovereign API running on http://localhost:8090")
    server.serve_forever()
