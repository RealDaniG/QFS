import sys

sys.path.append("backend")
from lib.message_envelope import ascon_decrypt, ascon_encrypt
import hashlib

# Test Vectors
key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
nonce = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
ad = b"test_ad"
plaintext = b"Hello P2P"

# Encrypt
print(f"Key: {key.hex()}")
print(f"Nonce: {nonce.hex()}")
print(f"AD: {ad.decode()}")
print(f"Plaintext: {plaintext.decode()}")

ciphertext = ascon_encrypt(key, nonce, ad, plaintext)
print(f"Ciphertext (Hex): {ciphertext.hex()}")

# Decrypt check
decrypted = ascon_decrypt(key, nonce, ad, ciphertext)
print(f"Decrypted: {decrypted.decode()}")
assert decrypted == plaintext
print("Python Ascon Check Passed.")
