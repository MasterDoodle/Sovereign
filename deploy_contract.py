import os
import json

DEPLOYMENT_CONFIG = {
    "network": "EVM-Testnet",
    "contract_name": "MTRXToken",
    "solidity_file": "contracts/MTRXToken.sol",
    "compiler_version": "0.8.20"
}

def generate_deployment_payload():
    engine_dir = os.path.expanduser('~/structor-engine')
    sol_path = os.path.join(engine_dir, DEPLOYMENT_CONFIG["solidity_file"])
    
    if os.path.exists(sol_path):
        with open(sol_path, 'r') as f:
            code = f.read()
        print(f"[SUCCESS] Prepared {DEPLOYMENT_CONFIG['contract_name']} for testnet deployment.")
        print(f"Contract Source Length: {len(code)} bytes")
        return True
    else:
        print("[ERROR] Solidity source file missing.")
        return False

if __name__ == '__main__':
    generate_deployment_payload()
