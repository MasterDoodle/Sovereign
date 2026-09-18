import time
import sqlite3
import os
import hashlib
import re

ENGINE_DIR = os.path.expanduser('~/structor-engine')
DB_PATH = os.path.join(ENGINE_DIR, 'treasury.db')
CONFIG_PATH = os.path.join(ENGINE_DIR, 'config/structor_mesh.yml')
STATE_FILE = os.path.join(ENGINE_DIR, '.engine_state')

def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    c = conn.cursor()
    c.execute('PRAGMA journal_mode=WAL;')
    c.execute('PRAGMA busy_timeout=5000;')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wallet_address TEXT,
        block_hash TEXT,
        nonce INTEGER,
        reward REAL,
        hashrate REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def get_target_wallet():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            match = re.search(r'address:\s*"([^"]+)"', f.read())
            if match:
                return match.group(1)
    return "0xUnconfigured"

def check_throttle():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = f.read().strip()
        if state == "STEALTH_THROTTLE":
            # Clear state and return higher sleep delay
            open(STATE_FILE, 'w').close()
            return 15 # Throttle sleep delay during user chat
    return 6 # Normal background mining sleep delay

def mine_block():
    target_wallet = get_target_wallet()
    start_time = time.time()
    nonce = 0
    target_prefix = "00"
    
    while True:
        nonce += 1
        data = f"{time.time()}:{nonce}:{target_wallet}".encode('utf-8')
        block_hash = hashlib.sha256(data).hexdigest()
        if block_hash.startswith(target_prefix):
            break

    elapsed = max(time.time() - start_time, 0.001)
    hashrate = round(nonce / elapsed, 2)
    reward = 0.05

    conn = sqlite3.connect(DB_PATH, timeout=10)
    c = conn.cursor()
    c.execute('PRAGMA busy_timeout=5000;')
    c.execute('INSERT INTO transactions (wallet_address, block_hash, nonce, reward, hashrate) VALUES (?, ?, ?, ?, ?)', 
              (target_wallet, f"0x{block_hash[:16]}", nonce, reward, hashrate))
    conn.commit()
    conn.close()
    
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Mined 0x{block_hash[:16]} | Hashrate: {hashrate} H/s")

if __name__ == '__main__':
    init_db()
    print("Sovereign Silent Mining Engine Active...")
    while True:
        mine_block()
        delay = check_throttle()
        time.sleep(delay)
