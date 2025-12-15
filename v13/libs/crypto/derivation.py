"""
derivation.py - Deterministic Wallet Derivation for QFS System Creator
Zero-Simulation Compliant
"""

import hashlib
import hmac
from typing import Tuple

def hkdf_extract(salt: bytes, input_key_material: bytes) -> bytes:
    """HKDF-Extract (RFC 5869)"""
    if salt is None:
        salt = bytes([0] * hashlib.sha256().digest_size)
    return hmac.new(salt, input_key_material, hashlib.sha256).digest()

def hkdf_expand(pseudo_random_key: bytes, info: bytes, length: int = 32) -> bytes:
    """HKDF-Expand (RFC 5869)"""
    t = b""
    okm = b""
    i = 0
    while len(okm) < length:
        i += 1
        t = hmac.new(pseudo_random_key, t + info + bytes([i]), hashlib.sha256).digest()
        okm += t
    return okm[:length]

def derive_creator_keypair(scope: str) -> Tuple[str, str]:
    """
    Derive the SYSTEM_CREATOR wallet keys deterministically.
    
    Args:
        scope: "DEV" or "TESTNET"
        
    Returns:
        (private_key_hex, public_address)
    """
    if scope not in ["DEV", "TESTNET"]:
        raise ValueError("Invalid scope for System Creator derivation")
        
    derivation_source = f"QFS::SYSTEM_CREATOR::{scope}".encode("utf-8")
    salt = "GENESIS_LEDGER_V1".encode("utf-8")
    # Including HD path in context info to bind it to the derivation
    context_info = "QFS_ATLAS_CREATOR_WALLET|m/44'/9999'/0'/0/0".encode("utf-8")
    
    # 1. Extract
    prk = hkdf_extract(salt, derivation_source)
    
    # 2. Expand
    # We derive enough bytes for a private key (32 bytes)
    private_key_bytes = hkdf_expand(prk, context_info, 32)
    private_key_hex = private_key_bytes.hex()
    
    # 3. Derive Public Address
    # In a real ECDSA scenario, we'd multiply G * priv.
    # For this system, we'll use a deterministic hash of the private key as the public address for now
    # to avoid introducing ECDSA dependencies just for the ID if not strictly required by the rest of the stack yet.
    # However, to be consistent with standard crypto wallets, we should ideally use ECDSA public key.
    # Assuming 'wallet' field in ledger is just an ID.
    public_key_bytes = hashlib.sha256(private_key_bytes).digest()
    public_address = "0x" + public_key_bytes.hex()
    
    return private_key_hex, public_address
