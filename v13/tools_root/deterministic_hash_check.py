#!/usr/bin/env python3
"""
Deterministic Hash Check Tool for QFS V13
Verifies that serialization functions produce deterministic output.
"""

import sys
import json
import hashlib
from typing import Any, Dict

def canonicalize_for_hash(data: Any) -> str:
    """
    Convert data to a canonical string representation for hashing.
    This ensures deterministic serialization.
    """
    if hasattr(data, 'to_decimal_string'):
        # Handle BigNum128 objects
        return data.to_decimal_string()
    elif isinstance(data, dict):
        # Recursively canonicalize dictionary values
        canonical_dict = {}
        for key, value in sorted(data.items()):
            canonical_dict[key] = canonicalize_for_hash(value)
        return json.dumps(canonical_dict, sort_keys=True, separators=(',', ':'))
    elif isinstance(data, (list, tuple)):
        # Recursively canonicalize list/tuple items
        canonical_list = [canonicalize_for_hash(item) for item in data]
        return json.dumps(canonical_list, separators=(',', ':'))
    else:
        # For other types, use standard JSON serialization
        return json.dumps(data, sort_keys=True, separators=(',', ':'))

def test_deterministic_hashing():
    """
    Test that the same input always produces the same hash.
    """
    # Test data
    test_data = {
        "chr_state": {
            "coherence_metric": "1.618033988749894848",
            "balance": "1000.000000000000000000"
        },
        "flx_state": {
            "scaling_metric": "0.950000000000000000",
            "velocity": "0.100000000000000000"
        },
        "timestamp": 1234567890,
        "pqc_cid": "test_cid_001"
    }
    
    # Run serialization multiple times
    hashes = []
    for i in range(5):
        canonical_str = canonicalize_for_hash(test_data)
        hash_result = hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()
        hashes.append(hash_result)
        print(f"Run {i+1}: {hash_result}")
    
    # Check if all hashes are identical
    if len(set(hashes)) == 1:
        print("✅ Deterministic hashing test PASSED")
        return True
    else:
        print("❌ Deterministic hashing test FAILED")
        return False

def main():
    """
    Main entry point for the deterministic hash check tool.
    """
    print("Running Deterministic Hash Check...")
    
    if test_deterministic_hashing():
        print("✅ All deterministic hash checks PASSED")
        sys.exit(0)
    else:
        print("❌ Deterministic hash checks FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()