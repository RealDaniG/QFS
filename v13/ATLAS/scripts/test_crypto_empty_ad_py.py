import sys

try:
    import ascon
except ImportError:
    # If not installed globally, add backend path
    sys.path.append("backend")
    try:
        import ascon
    except ImportError:
        print("Error: ascon module not found")
        sys.exit(1)

key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
nonce = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
ad = b""  # Empty AD
plaintext = b"Hello P2P"

print("Python Generating Ciphertext for Empty AD...")
try:
    ciphertext = ascon.encrypt(key, nonce, ad, plaintext, variant="Ascon-128")
    print(f"Ciphertext (Hex): {ciphertext.hex()}")
except Exception as e:
    print(f"Error: {e}")
