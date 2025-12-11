"""
Canonical Encoding - CBOR-based Deterministic State Hashing

Zero-Simulation Compliant
Phase-4 CEE v3

This module provides canonical encoding utilities for deterministic state hashing.
Uses CBOR (RFC 8949) with strict ordering and type constraints.
"""

import hashlib
import cbor2
from typing import Any, Dict, List, Union
from decimal import Decimal
import sys
import os

# Add parent directory for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from libs.BigNum128 import BigNum128


class CanonicalEncoder:
    """
    Canonical encoding for deterministic state hashing.
    
    Guarantees:
    - Same object → same encoding → same hash (bit-for-bit)
    - Deterministic dict ordering (lexicographic by key)
    - No floating-point numbers (rejected with TypeError)
    - Fixed-point decimals only
    - UTC timestamps as int (nanoseconds since epoch)
    
    Zero-Simulation Compliant
    """
    
    # Supported types for canonical encoding
    SUPPORTED_TYPES = (int, str, bytes, bool, type(None), list, dict, Decimal, BigNum128)
    
    @staticmethod
    def encode(obj: Any) -> bytes:
        """
        Encode object to canonical CBOR bytes.
        
        Args:
            obj: Object to encode
            
        Returns:
            Canonical CBOR bytes
            
        Raises:
            TypeError: If object contains unsupported types (e.g., float)
            
        Deterministic Guarantee:
            Same obj → same bytes across all runs and nodes
        """
        # Validate and normalize object
        normalized = CanonicalEncoder._normalize(obj)
        
        # Encode with canonical CBOR (sorted keys)
        return cbor2.dumps(normalized, canonical=True)
    
    @staticmethod
    def canonical_hash(obj: Any) -> bytes:
        """
        Compute deterministic hash of any object.
        
        Args:
            obj: Object to hash
            
        Returns:
            SHA3-512 hash of canonical encoding
            
        Deterministic Guarantee:
            Same obj → same hash across all runs and nodes
        """
        encoded = CanonicalEncoder.encode(obj)
        return hashlib.sha3_512(encoded).digest()
    
    @staticmethod
    def canonical_hash_hex(obj: Any) -> str:
        """
        Compute deterministic hash as hex string.
        
        Args:
            obj: Object to hash
            
        Returns:
            Hex string of SHA3-512 hash
        """
        return CanonicalEncoder.canonical_hash(obj).hex()
    
    @staticmethod
    def _normalize(obj: Any) -> Any:
        """
        Normalize object for canonical encoding.
        
        Converts special types (Decimal, BigNum128) to canonical forms.
        Validates no floats or unsupported types.
        """
        # Reject floats explicitly
        if isinstance(obj, float):
            raise TypeError(
                f"Float types are not allowed in canonical encoding (got {obj}). "
                "Use Decimal or fixed-point integers instead."
            )
        
        # Handle None, bool, int, str, bytes
        if obj is None or isinstance(obj, (bool, int, str, bytes)):
            return obj
        
        # Handle Decimal (convert to string for determinism)
        if isinstance(obj, Decimal):
            # Use string representation for exact precision
            return {"__decimal__": str(obj)}
        
        # Handle BigNum128
        if isinstance(obj, BigNum128):
            # Use deterministic string representation
            return {"__bignum128__": obj.to_decimal_string()}
        
        # Handle list
        if isinstance(obj, list):
            return [CanonicalEncoder._normalize(item) for item in obj]
        
        # Handle dict
        if isinstance(obj, dict):
            # Normalize all values
            normalized = {}
            for key, value in obj.items():
                # Validate key type
                if not isinstance(key, (str, int)):
                    raise TypeError(
                        f"Dict keys must be str or int, got {type(key).__name__}"
                    )
                normalized[key] = CanonicalEncoder._normalize(value)
            return normalized
        
        # Reject unsupported types
        raise TypeError(
            f"Unsupported type for canonical encoding: {type(obj).__name__}. "
            f"Supported types: {', '.join(t.__name__ for t in CanonicalEncoder.SUPPORTED_TYPES)}"
        )
    
    @staticmethod
    def verify_determinism(obj: Any, n_iterations: int = 1000) -> bool:
        """
        Verify that encoding is deterministic across multiple iterations.
        
        Args:
            obj: Object to test
            n_iterations: Number of iterations to test
            
        Returns:
            True if all encodings are identical
        """
        hashes = set()
        for _ in range(n_iterations):
            h = CanonicalEncoder.canonical_hash(obj)
            hashes.add(h)
        
        return len(hashes) == 1


# Convenience functions
def canonical_hash(obj: Any) -> bytes:
    """Compute canonical hash of object (SHA3-512)"""
    return CanonicalEncoder.canonical_hash(obj)


def canonical_hash_hex(obj: Any) -> str:
    """Compute canonical hash as hex string"""
    return CanonicalEncoder.canonical_hash_hex(obj)


def canonical_encode(obj: Any) -> bytes:
    """Encode object to canonical CBOR bytes"""
    return CanonicalEncoder.encode(obj)
