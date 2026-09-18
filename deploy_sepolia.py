import os
import json
from web3 import Web3
from solcx import compile_source, install_solc

ENGINE_DIR = os.path.expanduser('~/structor-engine')
CONTRACT_PATH = os.path.join(ENGINE_DIR, 'contracts/MTRXToken.sol')

RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

print(f"Connecting to Sepolia RPC... Connected: {w3.is_connected()}")

if not os.path.exists(CONTRACT_PATH):
    raise FileNotFoundError(f"Contract file missing at {CONTRACT_PATH}")

with open(CONTRACT_PATH, 'r') as f:
    contract_source = f.read()

print("Compiling MTRXToken.sol...")
install_solc('0.8.20')
compiled_sol = compile_source(contract_source, solc_version='0.8.20')
contract_interface = compiled_sol['<stdin>:MTRXToken']

abi_path = os.path.join(ENGINE_DIR, 'MTRXToken_abi.json')
with open(abi_path, 'w') as f:
    json.dump(contract_interface['abi'], f)

print(f"[SUCCESS] Contract compiled successfully. ABI saved to {abi_path}")
