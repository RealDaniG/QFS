"""
DRV_Packet.py - Deterministic Replayable Validation Packet for QFS V13

This module implements the DRV_Packet class which encapsulates deterministic,
replayable validation packets used across the QFS V13 system.

Features:
- Deterministic timestamp and sequence management (assigned by SDK/API)
- PQC signing and verification (placeholder, ready for real PQC library integration)
- Optional quantum metadata for Phase 3 audit logging
- Versioning for future-proofing
- Optional hash chaining for tamper-evident audit chains
- Deterministic JSON serialization excluding signature
- Full validation methods for sequence, timestamp, signature, metadata, and chain integrity
"""

import json
import hashlib
from typing import Optional, Dict, Any, Union, NamedTuple

# ---------------- PQC PLACEHOLDER -----------------
# Replace this with actual PQC library, e.g., pqcrystals.dilithium
class PQCKeyPair:
    """Placeholder PQC key pair for signing and verification."""
    def __init__(self, private_key_bytes: bytes, public_key_bytes: bytes):
        self.private_key = private_key_bytes
        self.public_key = public_key_bytes

    @staticmethod
    def generate() -> 'PQCKeyPair':
        """Generate dummy key pair (replace with real PQC generation)."""
        import os
        # In production, use a real PQC library to generate keys
        # e.g., priv, pub = dilithium.generate_keypair()
        # return PQCKeyPair(priv, pub)
        # For simulation, generate dummy bytes
        return PQCKeyPair(os.urandom(32), os.urandom(32))

# ---------------- Validation Result -----------------
# Optional: Use a more structured result for is_valid
class ValidationResult(NamedTuple):
    is_valid: bool
    error_code: Optional[int] = None
    error_message: Optional[str] = None

# Error codes for validation
class ValidationErrorCode:
    OK = 0
    INVALID_SEQUENCE = 1
    INVALID_TIMESTAMP = 2
    INVALID_SIGNATURE = 3
    INVALID_CHAIN = 4
    VERSION_MISMATCH = 5

# ---------------- DRV_Packet CLASS -----------------
class DRV_Packet:
    """
    Deterministic Replayable Validation Packet for QFS V13.

    Fields:
        - version: Schema version
        - timestamp: Deterministic timestamp assigned by SDK/API
        - sequence: Monotonically increasing sequence number
        - seed: Quantum/deterministic entropy source
        - pqc_signature: PQC signature bytes (None until signed)
        - metadata: Optional quantum metadata dictionary (Phase 3)
        - previous_hash: Optional previous packet hash for audit chain
    """
    VERSION = "1.0"

    def __init__(self,
                 timestamp: int,
                 sequence: int,
                 seed: str,
                 pqc_signature: Optional[bytes] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 previous_hash: Optional[str] = None):
        # Validate inputs during construction (Zero-Simulation compliance check)
        if not isinstance(timestamp, int) or timestamp <= 0:
            raise ValueError("timestamp must be a positive integer")
        if not isinstance(sequence, int) or sequence < 0:
            raise ValueError("sequence must be a non-negative integer")
        if not isinstance(seed, str) or not seed:
            raise ValueError("seed must be a non-empty string")
        if metadata is not None and not isinstance(metadata, dict):
            raise ValueError("metadata must be a dictionary or None")
        if previous_hash is not None and not isinstance(previous_hash, str):
            raise ValueError("previous_hash must be a string or None")

        self.timestamp = timestamp
        self.sequence = sequence
        self.seed = seed
        self.pqc_signature = pqc_signature # Stored as bytes internally
        self.metadata = metadata
        self.previous_hash = previous_hash

    # ----------------- Serialization & Hashing -----------------
    def to_dict(self, include_signature: bool = False) -> Dict[str, Any]:
        """
        Convert packet to dict (optionally including signature as hex string).
        This is the canonical representation *excluding* the signature for signing/verification.
        """
        data = {
            "version": self.VERSION,
            "timestamp": self.timestamp,
            "sequence": self.sequence,
            "seed": self.seed,
            "previous_hash": self.previous_hash,
        }
        if self.metadata is not None:
            data["metadata"] = self.metadata
        if include_signature and self.pqc_signature is not None:
            # Store signature as hex string in dict for JSON compatibility
            data["pqc_signature"] = self.pqc_signature.hex()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DRV_Packet':
        """
        Create a DRV_Packet instance from a dictionary.
        Does not verify the signature; verification happens separately.
        Raises ValueError if version is unsupported.
        """
        version = data.get("version", "1.0")
        if version != cls.VERSION:
            # Raise an exception for unsupported versions as per refinement
            raise ValueError(f"Unsupported DRV_Packet version: {version}. Expected {cls.VERSION}")

        timestamp = data["timestamp"]
        sequence = data["sequence"]
        seed = data["seed"]
        previous_hash = data.get("previous_hash") # Optional
        metadata = data.get("metadata")           # Optional

        # Load signature from hex string if present
        sig_hex = data.get("pqc_signature")
        pqc_signature = bytes.fromhex(sig_hex) if sig_hex is not None else None

        # Create packet instance
        packet = cls(
            timestamp=timestamp,
            sequence=sequence,
            seed=seed,
            previous_hash=previous_hash,
            metadata=metadata
        )
        # Assign the signature separately after construction validation
        packet.pqc_signature = pqc_signature
        return packet

    def serialize(self, include_signature: bool = False) -> str:
        """
        Deterministic JSON serialization (sorted keys).
        Excludes signature by default to ensure data being signed is consistent.
        """
        return json.dumps(self.to_dict(include_signature), sort_keys=True, separators=(',', ':'))

    def get_hash(self) -> str:
        """
        Deterministic SHA-256 hash of the packet data (excluding signature).
        Used for audit chain links (previous_hash) and potentially PQC signing input.
        """
        serialized = self.serialize(include_signature=False)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    # ----------------- PQC SIGNING & VERIFICATION (SIMULATION) -----------------
    def sign(self, key_pair: PQCKeyPair) -> None:
        """
        Sign the packet with PQC private key.
        NOTE: This is a SIMULATION using SHA-256. Replace with real PQC signing.

        Args:
            key_pair: PQCKeyPair containing the private key.
        """
        # Data to sign is the serialized packet *excluding* the signature itself
        data_to_sign = self.serialize(include_signature=False).encode('utf-8')
        # --- SIMULATION ONLY ---
        # Replace this with actual PQC signing library call
        # Example: self.pqc_signature = dilithium.sign(key_pair.private_key, data_to_sign)
        self.pqc_signature = hashlib.sha256(data_to_sign + key_pair.private_key).digest()
        # --- END SIMULATION ---

    def verify_signature(self, public_key_bytes: bytes) -> bool:
        """
        Verify the PQC signature of the packet using the public key.
        NOTE: This is a SIMULATION using SHA-256. Replace with real PQC verification.

        Args:
            public_key_bytes: The public key bytes corresponding to the signing private key.

        Returns:
            True if signature is valid, False otherwise.
        """
        if self.pqc_signature is None:
            return False # No signature to verify

        # Data to verify against is the serialized packet *excluding* the signature itself
        data_to_verify = self.serialize(include_signature=False).encode('utf-8')
        # --- SIMULATION ONLY ---
        # Replace this with actual PQC verification library call
        # Example: return dilithium.verify(public_key_bytes, self.pqc_signature, data_to_verify)
        expected_sig = hashlib.sha256(data_to_verify + public_key_bytes).digest()
        return self.pqc_signature == expected_sig
        # --- END SIMULATION ---

    # ----------------- Validation -----------------
    def validate_sequence(self, expected_sequence: int) -> bool:
        """
        Validate sequence number integrity against an expected value.
        This check is performed by the receiving layer (SDK/API).
        """
        return self.sequence == expected_sequence

    def validate_timestamp(self, max_drift_seconds: int = 300) -> bool:
        """
        Validate timestamp coherence.
        NOTE: This check is relevant if using potentially non-deterministic time sources.
              For QFS V13, timestamps should be deterministic (e.g., from sequence or QRNG/VDF).
              This check might be relaxed or removed if upstream generation is guaranteed deterministic.
        """
        # A purely deterministic check might just ensure it's a reasonable positive integer
        # as the source (SDK/API) should provide the deterministic value.
        return 0 < self.timestamp < 2**63  # Valid Unix timestamp range

    def validate_chain(self, previous_packet_hash: Optional[str]) -> bool:
        """
        Validate the hash chain integrity.
        Checks if the 'previous_hash' field matches the provided hash of the preceding packet.
        """
        return self.previous_hash == previous_packet_hash

    def is_valid(self,
                 expected_sequence: int,
                 public_key_bytes: bytes,
                 previous_packet_hash: Optional[str] = None,
                 max_drift_seconds: int = 300) -> ValidationResult:
        """
        Comprehensive validation of the DRV_Packet.
        This check is performed by the receiving layer (SDK/API).
        Returns a ValidationResult object for more detailed feedback.

        Args:
            expected_sequence: Expected sequence number based on previous state.
            public_key_bytes: Public key bytes for PQC signature verification.
            previous_packet_hash: Expected hash of the previous packet in the chain (optional).
            max_drift_seconds: Maximum allowed timestamp drift (for reference).

        Returns:
            ValidationResult object indicating success/failure and details.
        """
        # Validate sequence
        if not self.validate_sequence(expected_sequence):
            return ValidationResult(False, ValidationErrorCode.INVALID_SEQUENCE, f"Sequence mismatch: got {self.sequence}, expected {expected_sequence}")
        
        # Validate timestamp
        if not self.validate_timestamp(max_drift_seconds):
            return ValidationResult(False, ValidationErrorCode.INVALID_TIMESTAMP, f"Timestamp {self.timestamp} is out of valid range")
        
        # Verify signature
        if not self.verify_signature(public_key_bytes):
            return ValidationResult(False, ValidationErrorCode.INVALID_SIGNATURE, "PQC signature verification failed")
        
        # Validate chain
        if not self.validate_chain(previous_packet_hash):
            return ValidationResult(False, ValidationErrorCode.INVALID_CHAIN, f"Chain validation failed: got {self.previous_hash}, expected {previous_packet_hash}")
        
        # All checks passed
        return ValidationResult(True, ValidationErrorCode.OK)

    # ----------------- Equality & Representation -----------------
    def __eq__(self, other) -> bool:
        """
        Equality comparison based on content (excluding signature).
        Useful for deterministic replay verification.
        """
        if not isinstance(other, DRV_Packet):
            return False
        # Compare all fields except the signature
        return (self.timestamp == other.timestamp and
                self.sequence == other.sequence and
                self.seed == other.seed and
                self.metadata == other.metadata and
                self.previous_hash == other.previous_hash)

    def __repr__(self) -> str:
        """String representation of the packet."""
        sig_repr = f"b'{self.pqc_signature.hex()}'" if self.pqc_signature else None
        meta_repr = self.metadata if self.metadata is not None else "None"
        return (f"DRV_Packet(version={self.VERSION}, timestamp={self.timestamp}, "
                f"sequence={self.sequence}, seed='{self.seed}', "
                f"pqc_signature={sig_repr}, metadata={meta_repr}, "
                f"previous_hash={self.previous_hash})")


# ----------------- EXAMPLE USAGE -----------------
if __name__ == "__main__":
    print("--- Example: DRV_Packet Creation, Signing, Verification, Serialization ---")

    # Generate dummy PQC keys (Replace with real PQC key generation)
    key_pair = PQCKeyPair.generate()
    print(f"Generated PQC Key Pair (Simulated)")

    # Create initial DRV_Packet (Timestamp and sequence must be deterministic upstream)
    packet1 = DRV_Packet(
        timestamp=1700000000, # Deterministic value from SDK/API
        sequence=1,           # Deterministic value from SDK/API counter
        seed="quantum-seed-001",
        metadata={"quantum_source_id": "qrng_v1", "vdf_output": "abc123"}, # Phase 3 example
        previous_hash=None    # First packet in a chain has no previous hash
    )
    print(f"Initial Packet 1: {packet1}")

    # Sign packet1 using the private key
    print("\nSigning Packet 1...")
    packet1.sign(key_pair)
    print(f"Packet 1 after signing: {packet1}")

    # Verify signature of packet1 using the public key
    print("\nVerifying signature of Packet 1...")
    is_valid_sig_p1 = packet1.verify_signature(key_pair.public_key)
    print(f"Packet 1 signature valid: {is_valid_sig_p1}")

    # Validate packet1 using the comprehensive is_valid method
    print("\nComprehensive validation of Packet 1...")
    val_result_p1 = packet1.is_valid(expected_sequence=1, public_key_bytes=key_pair.public_key, previous_packet_hash=None)
    print(f"Packet 1 validation result: {val_result_p1}")

    # Serialize packet1 to JSON string (for transmission/storage)
    print("\nSerializing Packet 1 (for transmission)...")
    serialized_packet1 = packet1.serialize(include_signature=True) # Include sig for transmission
    print(f"Serialized Packet 1: {serialized_packet1}")

    # Deserialize packet1 from JSON string (received/saved data)
    print("\nDeserializing Packet 1 (from received data)...")
    packet1_deserialized = DRV_Packet.from_dict(json.loads(serialized_packet1))
    print(f"Deserialized Packet 1: {packet1_deserialized}")

    # Verify equality (ignores signature, compares content)
    print(f"Original equals Deserialized (ignoring signature): {packet1 == packet1_deserialized}")

    # Verify signature of the deserialized packet
    print("\nVerifying signature of Deserialized Packet 1...")
    is_valid_sig_p1_deserialized = packet1_deserialized.verify_signature(key_pair.public_key)
    print(f"Deserialized Packet 1 signature valid: {is_valid_sig_p1_deserialized}")

    # Validate deserialized packet using the comprehensive is_valid method
    print("\nComprehensive validation of Deserialized Packet 1...")
    val_result_p1_deserialized = packet1_deserialized.is_valid(expected_sequence=1, public_key_bytes=key_pair.public_key, previous_packet_hash=None)
    print(f"Deserialized Packet 1 validation result: {val_result_p1_deserialized}")

    # Create second packet with hash chain link
    print("\n--- Example: Hash Chain ---")
    packet2 = DRV_Packet(
        timestamp=1700000100, # Deterministic value from SDK/API
        sequence=2,           # Deterministic value from SDK/API counter
        seed="quantum-seed-002",
        metadata={"quantum_source_id": "qrng_v2", "vdf_output": "def456"}, # Phase 3 example
        previous_hash=packet1.get_hash() # Link to previous packet's hash
    )
    packet2.sign(key_pair)

    # Validate packet2: sequence, signature, and chain integrity using the structured result
    print(f"Packet 2: {packet2}")
    print("\nValidating Packet 2 (sequence, signature, chain)...")
    val_result_p2 = packet2.is_valid(
        expected_sequence=2,
        public_key_bytes=key_pair.public_key,
        previous_packet_hash=packet1.get_hash() # Provide the expected previous hash
    )
    print(f"Packet 2 validation result: {val_result_p2}")
    print(f"Packet 2 fully valid: {val_result_p2.is_valid}")

    # Serialize/Deserialize packet2
    serialized_packet2 = packet2.serialize(include_signature=True)
    packet2_deserialized = DRV_Packet.from_dict(json.loads(serialized_packet2))
    print(f"Deserialized Packet 2 equals Original: {packet2 == packet2_deserialized}")

    print("\nExample completed.")