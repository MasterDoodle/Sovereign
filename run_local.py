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
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Schema Migration Guard: ensure 'hashrate' column exists
    c.execute("PRAGMA table_info(transactions)")
    columns = [col[1] for col in c.fetchall()]
    if 'hashrate' not in columns:
        c.execute("ALTER TABLE transactions ADD COLUMN hashrate REAL DEFAULT 0.0")
    if 'nonce' not in columns:
        c.execute("ALTER TABLE transactions ADD COLUMN nonce INTEGER DEFAULT 0")
        
    conn.commit()
    conn.close()

def get_target_wallet():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            match = re.search(r'address:\s*"([^"]+)"', f.read())
            if match:
                return match.group(1)
    return "0x6b6c0e...FfD57" # Default fallback

def check_throttle():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = f.read().strip()
        if state == "STEALTH_THROTTLE":
            open(STATE_FILE, 'w').close()
            return 5
    return 2

def mine_block():
    target_wallet = get_target_wallet()
    start_time = time.time()
    nonce = 0
    target_prefix = "0"  # Lightweight target to ensure high hash yield
    
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
    
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Block 0x{block_hash[:12]} Mined for {target_wallet[:10]}... | {hashrate} H/s")

if __name__ == '__main__':
    init_db()
    print("Sovereign Mining Core Active...")
    while True:
        try:
            mine_block()
        except Exception as e:
            print(f"Mining recovery trigger: {e}")
        delay = check_throttle()
        time.sleep(delay)
