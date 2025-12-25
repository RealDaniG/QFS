import sys

try:
    import ascon
except ImportError:
    # If not installed globally, add backend path
    sys.path.append("backend")
    try:
        import ascon
    except ImportError:
        sys.stderr.write("Error: ascon module not found\n")
        sys.exit(1)

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
nonce = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
ad = b""  # Empty AD
plaintext = b"Hello P2P"

logger.info("Python Generating Ciphertext for Empty AD...")
try:
    ciphertext = ascon.encrypt(key, nonce, ad, plaintext, variant="Ascon-128")
    logger.info(f"Ciphertext (Hex): {ciphertext.hex()}")
except Exception as e:
    logger.error(f"Error: {e}")
