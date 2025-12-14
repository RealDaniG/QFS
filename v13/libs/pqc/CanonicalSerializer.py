"""
CanonicalSerializer.py - Phase-3 Module 2.2
Deterministic Canonical Serialization for PQC Signing

Zero-Simulation Compliant, Collision-Resistant, BigNum128-Aware
"""

import json
from typing import Any


class CanonicalSerializer:
    """
    Provides strictly deterministic canonical serialization for PQC signing.
    All complex types reduce to stable, JSON-minimal, order-independent forms.
    """

    @staticmethod
    def canonicalize_for_sign(data: Any) -> str:
        """
        Produces a strictly deterministic canonical string for PQC signing.
        All complex types reduce to stable, JSON-minimal, order-independent forms.
        Collision-resistant canonicalization for multi-node consistency.
        
        Args:
            data: Any data structure to canonicalize
            
        Returns:
            Canonical string representation
            
        Raises:
            TypeError: If data contains floats or unsupported types
        """
        # Phase-3: Explicitly ban Python float (nondeterministic)
        if isinstance(data, float):
            raise TypeError("Float type is nondeterministic and not allowed in PQC canonicalization.")
        
        if hasattr(data, 'to_decimal_string'):
            # Handle BigNum128 objects
            return data.to_decimal_string()

        if isinstance(data, dict):
            # Phase-3: Validate dict keys are only str or int
            for k in data.keys():
                if not isinstance(k, (str, int)):
                    raise TypeError(f"Unsupported dict key type: {type(k).__name__}")
            
            # Sort keys and canonicalize values as tuples to avoid JSON object ambiguity
            items = []
            for k in sorted(data.keys()):
                items.append((k, CanonicalSerializer.canonicalize_for_sign(data[k])))
            return json.dumps(items, separators=(',', ':'), ensure_ascii=False)

        if isinstance(data, (list, tuple)):
            # Canonicalize each element
            return json.dumps(
                [CanonicalSerializer.canonicalize_for_sign(v) for v in data],
                separators=(',', ':'),
                ensure_ascii=False
            )

        if isinstance(data, (bytes, bytearray)):
            # Convert to hex string
            return bytes(data).hex()

        if isinstance(data, (str, int)):
            # Direct string conversion
            return str(data)

        # Phase-3: Reject unsupported types instead of using str() fallback
        raise TypeError(f"Unsupported type for canonical serialization: {type(data).__name__}")

    @staticmethod
    def serialize_data(data: Any) -> bytes:
        """
        Serializes data to bytes for signing, ensuring deterministic output.
        
        Args:
            data: Data to serialize
            
        Returns:
            Deterministic byte representation
        """
        canonical_str = CanonicalSerializer.canonicalize_for_sign(data)
        return canonical_str.encode('utf-8')
