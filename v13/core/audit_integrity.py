"""
Audit Integrity Module for QFS V13.8

Provides cryptographic verification for Explain-This artifacts to ensure
Zero-Simulation compliance and tamper evidence.
"""

import hashlib
import json
from typing import Dict, Any, Union

def verify_explanation_integrity(explanation_data: Dict[str, Any], integrity_hash: str) -> bool:
    """
    Verify that an explanation object matches its claimed integrity hash.
    
    Args:
        explanation_data: The raw dictionary of the explanation (excluding the hash).
        integrity_hash: The SHA-256 hash to verify against.
        
    Returns:
        True if the data produces the same hash, False otherwise.
    """
    # 1. Deterministic Serialization
    # Must match the serialization logic used in generators (sort_keys=True, separators=(',', ':'))
    json_str = json.dumps(explanation_data, sort_keys=True, separators=(',', ':'))
    
    # 2. Hash computation
    computed_hash = hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    # 3. Constant-time comparison (secure)
    return constant_time_compare(computed_hash, integrity_hash)

def constant_time_compare(val1: str, val2: str) -> bool:
    """
    Constant-time string comparison to prevent timing attacks.
    """
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(val1, val2):
        result |= ord(x) ^ ord(y)
    return result == 0

def detect_tampering(record: Dict[str, Any], previous_hash: str) -> Dict[str, Any]:
    """
    Check a chain entry for tampering.
    
    Args:
        record: The current audit log entry.
        previous_hash: The hash of the previous entry in the chain.
        
    Returns:
        Dict with 'valid' (bool) and 'error' (str, optional).
    """
    # Verify strict chaining
    if record.get("prev_hash") != previous_hash:
        return {"valid": False, "error": "BROKEN_CHAIN_LINK"}
        
    # Recalculate own hash
    # Exclude 'hash' field from calculation
        # Deterministic hashing of record fields (excluding hash itself)
        # Sort items by key
        sorted_items = sorted(record.items())
        data_to_hash = {}
        for i in range(len(sorted_items)):
            k, v = sorted_items[i]
            if k != "hash":
                data_to_hash[k] = v
    verified = verify_explanation_integrity(data_to_hash, record.get("hash", ""))
    
    if not verified:
        return {"valid": False, "error": "INTEGRITY_HASH_MISMATCH"}
        
    return {"valid": True}
