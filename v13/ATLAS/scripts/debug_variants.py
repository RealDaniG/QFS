import sys

sys.path.append("backend")
import ascon

# TS Ciphertext from Step 850
ts_ciphertext_hex = "f4e663d29c813529b955c392b1952ae1c9535028f1263cefb2"
ts_ciphertext = bytes.fromhex(ts_ciphertext_hex)

key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
nonce = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
ad = b"test_ad"

variants = ["Ascon-128", "Ascon-128a", "Ascon-80pq"]

print(f"Testing TS Ciphertext: {ts_ciphertext_hex}")

for v in variants:
    try:
        print(f"Trying {v}...")
        decrypted = ascon.decrypt(key, nonce, ad, ts_ciphertext, variant=v)
        if decrypted == b"Hello P2P":
            print(f"SUCCESS: MATCH FOUND with variant {v}")
            sys.exit(0)
        else:
            print(f"Decrypted, but content mismatch: {decrypted}")
    except Exception as e:
        print(f"Failed with {v}: {e}")

print("FAILURE: No variant matched.")
sys.exit(1)
