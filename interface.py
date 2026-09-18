from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

class SovereignInterfaceHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/wallet':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            data = {
                "address": "0xSTRUCT_SOVEREIGN_PRIMARY_TREASURY_001",
                "balance_mtrx": 142.50,
                "reward_rate": "0.05 MTRX/unit",
                "status": "Active Mining"
            }
            self.wfile.write(json.dumps(data).encode('utf-8'))
        else:
            super().do_GET()

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8090), SovereignInterfaceHandler)
    print("Dashboard interface running on http://localhost:8090")
    server.serve_forever()
