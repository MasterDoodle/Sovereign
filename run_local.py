import time
import sqlite3
import os
import hashlib
import re

ENGINE_DIR = os.path.expanduser('~/structor-engine')
DB_PATH = os.path.join(ENGINE_DIR, 'treasury.db')
CONFIG_PATH = os.path.join(ENGINE_DIR, 'config/structor_mesh.yml')

def get_target_wallet():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            match = re.search(r'address:\s*"([^"]+)"', f.read())
            if match:
                return match.group(1)
    return "0xUnconfigured"

# Initialize SQLite Ledger
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_address TEXT,
    block_hash TEXT,
    reward REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)''')
conn.commit()
conn.close()

def mine_block():
    target_wallet = get_target_wallet()
    timestamp = str(time.time()).encode('utf-8')
    block_hash = "0x" + hashlib.sha256(timestamp).hexdigest()[:16]
    reward = 0.05

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO transactions (wallet_address, block_hash, reward) VALUES (?, ?, ?)', 
              (target_wallet, block_hash, reward))
    conn.commit()
    conn.close()
    
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Mined {block_hash} -> {target_wallet[:10]}... | +{reward} MTRX")

if __name__ == '__main__':
    print(f"Sovereign AI/DI Autonomous Engine Active. Mining to {get_target_wallet()}...")
    while True:
        mine_block()
        time.sleep(10)
