from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import sqlite3
import os
import re

# Lock working directory to engine root
ENGINE_DIR = os.path.expanduser('~/structor-engine')
os.chdir(ENGINE_DIR)

DB_PATH = os.path.join(ENGINE_DIR, 'treasury.db')
CONFIG_PATH = os.path.join(ENGINE_DIR, 'config/structor_mesh.yml')

def get_configured_wallet():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            match = re.search(r'address:\s*"([^"]+)"', f.read())
            if match:
                return match.group(1)
    return "0xNotConfigured"

class SovereignInterfaceHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/wallet':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('SELECT COUNT(*), COALESCE(SUM(reward), 0) FROM transactions')
            count, total = c.fetchone()
            conn.close()

            data = {
                "address": get_configured_wallet(),
                "balance_mtrx": round(142.50 + total, 4),
                "blocks_mined": count,
                "reward_rate": "0.05 MTRX/unit",
                "status": "Active Mining"
            }
            self.wfile.write(json.dumps(data).encode('utf-8'))
        else:
            super().do_GET()

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8090), SovereignInterfaceHandler)
    print("Dashboard running on http://localhost:8090")
    server.serve_forever()
