import sqlite3
import os
import json
import hashlib

ENGINE_DIR = os.path.expanduser('~/structor-engine')
DB_PATH = os.path.join(ENGINE_DIR, 'treasury.db')

def generate_claim_proof(wallet_address):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    c = conn.cursor()
    c.execute('PRAGMA busy_timeout=5000;')
    c.execute('SELECT COUNT(*), COALESCE(SUM(reward), 0) FROM transactions WHERE wallet_address = ?', (wallet_address,))
    count, total = c.fetchone()
    conn.close()

    if total <= 0:
        return {"status": "error", "message": "No claimable balance found"}

    raw_payload = f"{wallet_address}:{total}:{count}".encode('utf-8')
    proof_hash = "0x" + hashlib.sha256(raw_payload).hexdigest()

    return {
        "status": "success",
        "wallet": wallet_address,
        "claimable_mtrx": round(total, 4),
        "blocks_included": count,
        "proof_hash": proof_hash
    }

if __name__ == '__main__':
    print("Sovereign Bridge Node Ready.")
