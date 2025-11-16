"""
DRV_Packet.py - Deterministic Replayable Validation Packet for QFS V13

This module implements the DRV_Packet class which encapsulates deterministic,
replayable validation packets used across the QFS V13 system.
"""

import json
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime


class DRV_Packet:
    """
    Deterministic Replayable Validation Packet.
    
    Contains timestamp, sequence number, quantum seed, and PQC signature
    for deterministic validation across the QFS V13 system.
    """
    
    def __init__(self, 
                 timestamp: int,
                 sequence: int,
                 seed: str,
                 pqc_signature: Optional[str] = None):
        """
        Initialize a DRV_Packet.
        
        Args:
            timestamp: Unix timestamp in seconds (deterministic, not from time.time())
            sequence: Monotonically increasing sequence number
            seed: Quantum seed or deterministic entropy source
            pqc_signature: Post-Quantum Cryptography signature (optional until signed)
        """
        self.timestamp = timestamp
        self.sequence = sequence
        self.seed = seed
        self.pqc_signature = pqc_signature
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert packet to dictionary representation."""
        return {
            "timestamp": self.timestamp,
            "sequence": self.sequence,
            "seed": self.seed,
            "pqc_signature": self.pqc_signature
        }
    
    def serialize(self) -> str:
        """Serialize packet to deterministic JSON string."""
        # Sort keys for deterministic serialization
        return json.dumps(self.to_dict(), sort_keys=True, separators=(',', ':'))
    
    def get_hash(self) -> str:
        """Generate deterministic SHA-256 hash of the packet."""
        serialized = self.serialize()
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DRV_Packet':
        """Create DRV_Packet from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            sequence=data["sequence"],
            seed=data["seed"],
            pqc_signature=data.get("pqc_signature")
        )
    
    def sign(self, pqc_private_key: str) -> None:
        """
        Sign the packet with PQC signature.
        
        In a real implementation, this would use actual PQC signing.
        For now, we simulate the process.
        
        Args:
            pqc_private_key: Private key for PQC signing
        """
        # In a real implementation, this would use actual PQC signing
        # For simulation purposes, we create a deterministic signature
        # We need to serialize without the signature field for consistency
        data_to_sign = self.to_dict()
        data_to_sign["pqc_signature"] = None
        serialized_data = json.dumps(data_to_sign, sort_keys=True, separators=(',', ':'))
        signature_data = f"{serialized_data}:{pqc_private_key}"
        self.pqc_signature = hashlib.sha256(signature_data.encode('utf-8')).hexdigest()
    
    def verify_signature(self, pqc_public_key: str) -> bool:
        """
        Verify the PQC signature of the packet.
        
        In a real implementation, this would use actual PQC verification.
        For now, we simulate the process.
        
        Args:
            pqc_public_key: Public key for PQC verification
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.pqc_signature:
            return False
            
        # Recreate the expected signature using the same method as signing
        # In a real implementation, this would use actual PQC verification
        data_to_verify = self.to_dict()
        data_to_verify["pqc_signature"] = None
        serialized_data = json.dumps(data_to_verify, sort_keys=True, separators=(',', ':'))
        signature_data = f"{serialized_data}:{pqc_public_key}"
        expected_signature = hashlib.sha256(signature_data.encode('utf-8')).hexdigest()
        
        return self.pqc_signature == expected_signature

    def validate_sequence(self, expected_sequence: int) -> bool:
        """
        Validate sequence number integrity.
        
        Args:
            expected_sequence: Expected sequence number
            
        Returns:
            True if sequence is valid, False otherwise
        """
        return self.sequence == expected_sequence
    
    def validate_timestamp(self, max_drift_seconds: int = 300) -> bool:
        """
        Validate timestamp coherence.
        
        Args:
            max_drift_seconds: Maximum allowed timestamp drift in seconds
            
        Returns:
            True if timestamp is valid, False otherwise
        """
        # In a real implementation, this would compare against a trusted time source
        # For now, we just check that timestamp is reasonable (positive)
        return self.timestamp > 0 and self.timestamp < 2**63  # Valid Unix timestamp range
    
    def is_valid(self, 
                 expected_sequence: int,
                 pqc_public_key: str,
                 max_drift_seconds: int = 300) -> bool:
        """
        Comprehensive validation of the DRV_Packet.
        
        Args:
            expected_sequence: Expected sequence number
            pqc_public_key: Public key for PQC verification
            max_drift_seconds: Maximum allowed timestamp drift in seconds
            
        Returns:
            True if all validations pass, False otherwise
        """
        return (self.validate_sequence(expected_sequence) and
                self.validate_timestamp(max_drift_seconds) and
                self.verify_signature(pqc_public_key))
    
    def __repr__(self) -> str:
        """String representation of the packet."""
        return f"DRV_Packet(timestamp={self.timestamp}, sequence={self.sequence}, seed='{self.seed}')"
    
    def __eq__(self, other) -> bool:
        """Equality comparison based on content."""
        if not isinstance(other, DRV_Packet):
            return False
        return (self.timestamp == other.timestamp and
                self.sequence == other.sequence and
                self.seed == other.seed and
                self.pqc_signature == other.pqc_signature)


# Example usage
if __name__ == "__main__":
    # Create a DRV_Packet
    packet = DRV_Packet(
        timestamp=1700000000,  # Deterministic timestamp
        sequence=1,
        seed="quantum-seed-001"
    )
    
    print("Original packet:", packet)
    print("Serialized:", packet.serialize())
    print("Hash:", packet.get_hash())
    
    # Sign the packet
    key = "test-key"
    print("Before signing - pqc_signature:", packet.pqc_signature)
    packet.sign(key)
    print("After signing - pqc_signature:", packet.pqc_signature)
    print("Signed packet:", packet)
    
    # Verify signature
    is_valid = packet.verify_signature(key)
    print("Signature valid:", is_valid)
    
    # Validate packet
    is_valid_packet = packet.is_valid(expected_sequence=1, pqc_public_key=key)
    print("Packet valid:", is_valid_packet)