import sys
import os
import json
import hashlib
from typing import Dict

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from lib.message_envelope import EnvelopeFactory, MessageEnvelope


def main():
    print("--- Python Envelope Generator ---")

    # Constants
    wallet_priv = bytes.fromhex("01" * 32)
    session_key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    space_id = "parity-test-space"
    sender_pub = "02" * 32
    payload = {"message": "hello world", "timestamp": 1234567890}
    intent = "chat.message"

    print(f"Session Key: {session_key.hex()}")

    factory = EnvelopeFactory(wallet_priv)

    # Create Envelope
    envelope = factory.create_envelope(
        space_id=space_id,
        sender_pubkey=sender_pub,
        payload=payload,
        intent=intent,
        session_key=session_key,
    )

    print("\n[Generated Envelope]")
    env_dict = envelope.dict()
    if isinstance(env_dict.get("payload_ciphertext"), bytes):
        env_dict["payload_ciphertext"] = env_dict["payload_ciphertext"].hex()
    print(json.dumps(env_dict, indent=2))

    print(f"\nLocked Ciphertext: {env_dict['payload_ciphertext']}")
    print(f"Locked Hash: {envelope.payload_hash}")

    # Verify Self
    print(
        f"\nSelf-Verification: {factory.verify_envelope(envelope, sender_public_key=bytes.fromhex(sender_pub))}"
    )

    # Decrypt Self
    decrypted = factory.decrypt_payload(envelope, session_key)
    print(f"Self-Decrypted: {decrypted}")


if __name__ == "__main__":
    main()
