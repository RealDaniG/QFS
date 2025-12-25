import sys
import os
import json
import hashlib
from typing import Dict

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from lib.message_envelope import EnvelopeFactory, MessageEnvelope


def main():
    logger.info("--- Python Envelope Generator ---")

    # Constants
    wallet_priv = bytes.fromhex("01" * 32)
    session_key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    space_id = "parity-test-space"
    sender_pub = "01" * 32  # Must match priv for MOCKQPC self-verify
    payload = {"message": "hello world", "timestamp": 1234567890}
    intent = "chat.message"

    logger.info(f"Session Key: {session_key.hex()}")

    factory = EnvelopeFactory(wallet_priv)

    # Create Envelope
    envelope = factory.create_envelope(
        space_id=space_id,
        sender_pubkey=sender_pub,
        payload=payload,
        intent=intent,
        session_key=session_key,
    )

    env_dict = envelope.dict()
    if isinstance(env_dict.get("payload_ciphertext"), bytes):
        env_dict["payload_ciphertext"] = env_dict["payload_ciphertext"].hex()

    # OUTPUT_START marker for easy parsing
    logger.info("\nOUTPUT_START")
    json_out = json.dumps(env_dict)
    logger.info(json_out)
    logger.info("OUTPUT_END")

    with open("parity_vectors_clean.json", "w", encoding="utf-8") as f:
        f.write(json_out)


if __name__ == "__main__":
    main()
