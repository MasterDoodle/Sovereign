import time
import sqlite3
import os
import hashlib

DB_PATH = os.path.expanduser('~/structor-engine/treasury.db')

# Initialize treasury table
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, block_hash TEXT, reward REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
conn.commit()
conn.close()

def mine_block():
    timestamp = str(time.time()).encode('utf-8')
    block_hash = hashlib.sha256(timestamp).hexdigest()[:16]
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO transactions (block_hash, reward) VALUES (?, ?)', (f"0x{block_hash}", 0.05))
    conn.commit()
    conn.close()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Mined block 0x{block_hash} | Reward: +0.05 MTRX")

if __name__ == '__main__':
    print("Sovereign AI/DI Local Engine Started...")
    while True:
        mine_block()
        time.sleep(10)
