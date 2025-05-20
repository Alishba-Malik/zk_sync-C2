# utils.py
from nacl.public import PrivateKey
import base64

def generate_keypair():
    private_key = PrivateKey.generate()
    public_key = private_key.public_key
    # Export as base64 for easy transport
    return base64.b64encode(bytes(private_key)).decode(), base64.b64encode(bytes(public_key)).decode()

if __name__ == "__main__":
    priv, pub = generate_keypair()
    print("Private Key:", priv)
    print("Public Key:", pub)
