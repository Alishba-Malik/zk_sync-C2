import os
import base64
import json
from nacl.public import PrivateKey, PublicKey, Box
from dotenv import load_dotenv

load_dotenv()

def decrypt_command(payload_json, priv_key_b64):
    payload = json.loads(payload_json)
    epk = base64.b64decode(payload["epk"])
    nonce = base64.b64decode(payload["nonce"])
    ciphertext = base64.b64decode(payload["ciphertext"])

    priv_key = PrivateKey(base64.b64decode(priv_key_b64))
    sender_pk = PublicKey(epk)
    box = Box(priv_key, sender_pk)
    decrypted = box.decrypt(ciphertext, nonce)
    return decrypted.decode()

if __name__ == "__main__":
    priv_key_b64 = os.getenv("BOT_PRIVATE_KEY")
    if not priv_key_b64:
        print("Missing BOT_PRIVATE_KEY in .env")
        exit(1)

    # Read encrypted command from input (or replace with contract fetch)
    payload_json = input("Paste encrypted JSON payload:\n> ")
    try:
        plaintext = decrypt_command(payload_json, priv_key_b64)
        print("Decrypted command:", plaintext)
    except Exception as e:
        print("Failed to decrypt:", str(e))
