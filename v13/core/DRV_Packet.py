"""
DRV_Packet.py - Deterministic Replayable Validation Packet for QFS V13

Implements the DRV_Packet class for creating deterministic, replayable validation packets
that are compliant with Zero-Simulation requirements and Post-Quantum Cryptography.
"""

import hashlib
import json
from typing import Dict, Any, Optional, NamedTuple, List

# Import PQC from the correct location
from ..libs.PQC import PQC


class DRVError(Exception):
    """Base exception for DRV_Packet operations."""
    pass


class DRVSerializationError(DRVError):
    """Raised when serialization or deserialization fails."""
    pass


class DRVValidationError(DRVError):
    """Raised when validation of packet data fails."""
    pass


class DRVChainError(DRVError):
    """Raised when chain validation or linking fails."""
    pass


# Constants
_ZERO_HASH = "0" * 64


def _log_drv_packet_operation(log_list: List[Dict[str, Any]], operation: str, details: Dict[str, Any], pqc_cid: Optional[str] = None, 
                           quantum_metadata: Optional[Dict[str, Any]] = None,
                           timestamp: Optional[int] = None):
    """
    Log a DRV_Packet operation to the audit trail with enhanced audit fields.
    
    Args:
        log_list: List to append log entries to
        operation: Operation name (create, sign, verify, validate_chain)
        details: Operation details
        pqc_cid: PQC correlation ID
        quantum_metadata: Quantum metadata
        timestamp: Deterministic timestamp (optional)
    """
    # Calculate log index
    log_index = len(log_list)
    
    # Get previous hash
    prev_hash = log_list[-1]["entry_hash"] if log_list else _ZERO_HASH
    
    entry = {
        "log_index": log_index,
        "operation": operation,
        "timestamp": timestamp if timestamp is not None else 0,  # Use 0 as default for deterministic behavior
        "details": details,
        "pqc_cid": pqc_cid,
        "quantum_metadata": quantum_metadata,
        "prev_hash": prev_hash
    }
    
    # Calculate entry hash (excluding prev_hash to avoid circular dependency)
    entry_for_hash = entry.copy()
    entry_for_hash.pop("prev_hash", None)
    entry_for_hash.pop("entry_hash", None)
    serialized_entry = json.dumps(entry_for_hash, sort_keys=True, separators=(',', ':'))
    entry_hash = hashlib.sha256(serialized_entry.encode("utf-8")).hexdigest()
    entry["entry_hash"] = entry_hash
    
    log_list.append(entry)


class ValidationResult(NamedTuple):
    is_valid: bool
    error_code: Optional[int] = None
    error_message: Optional[str] = None


class ValidationErrorCode:
    OK = 0
    INVALID_SEQUENCE = 1
    INVALID_TTS_TIMESTAMP = 2
    INVALID_SIGNATURE = 3
    INVALID_CHAIN = 4
    VERSION_MISMATCH = 5


class DRV_Packet:
    """
    Deterministic Replayable Validation Packet.
    
    Contains ttsTimestamp, sequence number, seed, and PQC signature for
    deterministic validation and replayability.
    """
    
    VERSION = "1.0"
    
    def __init__(self, ttsTimestamp: int, sequence: int, seed: str,
                 log_list: Optional[List[Dict[str, Any]]] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 previous_hash: Optional[str] = None,
                 pqc_cid: Optional[str] = None, quantum_metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a DRV packet.
        
        Args:
            ttsTimestamp: Time-to-Seed Timestamp (deterministic source)
            sequence: Monotonically increasing sequence number
            seed: Deterministic seed from QRNG/VDF oracle
            log_list: Optional list to append log entries to
            metadata: Optional metadata dictionary
            previous_hash: Previous packet's hash for chain linking
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
        """
        # Input Validation (Zero-Simulation Compliance Check)
        if not isinstance(ttsTimestamp, int) or ttsTimestamp < 0:  # Or check against TTS_MIN/MAX
            raise ValueError("ttsTimestamp must be a non-negative integer")
        if not isinstance(sequence, int) or sequence < 0:
            raise ValueError("sequence must be a non-negative integer")
        if not isinstance(seed, str) or not seed:  # Validate seed is a non-empty string
            raise ValueError("seed must be a non-empty string")
        # Convert seed to bytes for PQC operations
        self.seed_bytes = seed.encode('utf-8')
        if metadata is not None and not isinstance(metadata, dict):
            raise ValueError("metadata must be a dictionary or None")
        if previous_hash is not None and not isinstance(previous_hash, str):
            raise ValueError("previous_hash must be a string or None")

        self.version = self.VERSION
        self.ttsTimestamp = ttsTimestamp
        self.sequence = sequence
        self.seed = seed  # Store as string
        self.seed_bytes = seed.encode('utf-8')  # Store as bytes for PQC operations
        self.metadata = metadata or {}
        self.previous_hash = previous_hash  # Can be None or a hex string
        self.pqc_signature: Optional[bytes] = None
        
        # Log the packet creation
        if log_list is not None:
            _log_drv_packet_operation(log_list, "create", {
                "ttsTimestamp": ttsTimestamp,
                "sequence": sequence,
                "seed": seed,
                "metadata": metadata,
                "previous_hash": previous_hash
            }, pqc_cid, quantum_metadata, ttsTimestamp)
    
    def serialize(self, include_signature: bool = True) -> str:
        """
        Serialize the packet to a deterministic string representation.
        
        Args:
            include_signature: Whether to include the signature in serialization
            
        Returns:
            JSON string representation of the packet
        """
        data = {
            "version": self.version,
            "ttsTimestamp": self.ttsTimestamp,
            "sequence": self.sequence,
            "seed": self.seed,
            "metadata": self.metadata,
            "previous_hash": self.previous_hash
        }
        
        if include_signature and self.pqc_signature is not None:
            # Convert bytes signature to hex string for JSON
            data["pqc_signature"] = self.pqc_signature.hex()
            
        # Deterministic JSON serialization with sorted keys (Section 4.2)
        return json.dumps(data, sort_keys=True, separators=(',', ':'))
    
    def get_canonical_bytes(self) -> bytes:
        """Return the exact bytes that are PQC-signed."""
        return self.serialize(include_signature=False).encode('utf-8')
    
    def get_hash(self) -> str:
        """
        Calculate deterministic SHA-256 hash of the packet. (Section 4.2)
        Chain hash = SHA-256 of PQC-signed canonical bytes.
        
        Returns:
            Hex string of the SHA-256 hash
        """
        return hashlib.sha256(self.get_canonical_bytes()).hexdigest()
    
    def sign(self, private_key_bytes: bytes, log_list: List[Dict[str, Any]], pqc_cid: Optional[str] = None, quantum_metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Sign the packet with a private key using Dilithium-5.
        
        Args:
            private_key_bytes: Private key as bytes
            log_list: List to append log entries to
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
        """
        # BEGIN PQC SIGNING
        # Serialize the packet data (excluding the signature itself) for signing (Section 4.1)
        data_to_sign = self.to_dict(include_signature=False)
        
        # Use real Dilithium-5 signing with deterministic serialization
        # Create a temporary log list for this operation
        temp_log = []
        signature = PQC.sign_data(private_key_bytes, data_to_sign, temp_log, pqc_cid, quantum_metadata, self.ttsTimestamp)
        
        # Store the signature as bytes inside the packet
        self.pqc_signature = signature
        
        # Log the signing operation
        _log_drv_packet_operation(log_list, "sign", {
            "packet_hash": self.get_hash(),
            "signature_length": len(signature) if signature else 0
        }, pqc_cid, quantum_metadata, self.ttsTimestamp)
    
    def verify_signature(self, public_key_bytes: bytes, log_list: List[Dict[str, Any]], pqc_cid: Optional[str] = None, quantum_metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Verify the packet's signature with a public key using Dilithium-5.
        
        Args:
            public_key_bytes: Public key as bytes
            log_list: List to append log entries to
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        # BEGIN PQC VERIFICATION
        # Check if there's even a signature to verify
        if self.pqc_signature is None:
            _log_drv_packet_operation(log_list, "verify", {
                "packet_hash": self.get_hash(),
                "result": False,
                "error": "No signature to verify"
            }, pqc_cid, quantum_metadata, self.ttsTimestamp if hasattr(self, 'ttsTimestamp') else 0)
            return False

        # Serialize the packet data (excluding the signature itself) for verification (Section 4.1)
        data_to_verify = self.to_dict(include_signature=False)

        # Use real Dilithium-5 verification with deterministic serialization
        # Create a temporary log list for this operation
        temp_log = []
        validation_result = PQC.verify_signature(public_key_bytes, data_to_verify, self.pqc_signature, temp_log, pqc_cid, quantum_metadata, self.ttsTimestamp)
        result = validation_result.is_valid
        
        # Log the verification operation
        _log_drv_packet_operation(log_list, "verify", {
            "packet_hash": self.get_hash(),
            "result": result
        }, pqc_cid, quantum_metadata, self.ttsTimestamp if hasattr(self, 'ttsTimestamp') else 0)
        
        return result
    
    def validate_sequence(self) -> ValidationResult:
        """Validate sequence number is non-negative."""
        if self.sequence < 0:
            return ValidationResult(False, ValidationErrorCode.INVALID_SEQUENCE, f"Sequence {self.sequence} is negative")
        return ValidationResult(True, ValidationErrorCode.OK)

    def validate_ttsTimestamp(self) -> ValidationResult:
        """Validate ttsTimestamp is within a reasonable range."""
        # Checks for a valid 64-bit unsigned integer range (max unix time)
        if not (0 <= self.ttsTimestamp <= 2**63 - 1):  # Or use TTS_MIN/MAX constants
            return ValidationResult(False, ValidationErrorCode.INVALID_TTS_TIMESTAMP, f"ttsTimestamp {self.ttsTimestamp} out of range")
        return ValidationResult(True, ValidationErrorCode.OK)

    @staticmethod
    def validate_chain(previous_packet: Optional['DRV_Packet'], current_packet: 'DRV_Packet', 
                       pqc_cid: Optional[str] = None, quantum_metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate hash chain integrity and sequence monotonicity."""
        if previous_packet is None:
            # Genesis packet logic: could return OK if current_packet.sequence == 0
            # Or define a specific check. For now, assume OK if previous is None.
            result = ValidationResult(True, ValidationErrorCode.OK)
            return result

        # Check if the current packet's previous_hash matches the previous packet's hash
        if current_packet.previous_hash != previous_packet.get_hash():
            result = ValidationResult(False, ValidationErrorCode.INVALID_CHAIN, f"Chain hash mismatch: got {current_packet.previous_hash}, expected {previous_packet.get_hash()}")
            return result

        # Check if the sequence number is monotonic (Section 4.4)
        if current_packet.sequence != previous_packet.sequence + 1:
            result = ValidationResult(False, ValidationErrorCode.INVALID_SEQUENCE, f"Sequence non-monotonic: got {current_packet.sequence}, expected {previous_packet.sequence + 1}")
            return result

        result = ValidationResult(True, ValidationErrorCode.OK)
        return result

    def is_valid(self,
                 public_key_bytes: bytes,  # Pass public key for verification
                 log_list: List[Dict[str, Any]],  # Pass log list for audit trail
                 previous_packet: Optional['DRV_Packet'] = None,  # Pass previous packet for chain validation
                 pqc_cid: Optional[str] = None, quantum_metadata: Optional[Dict[str, Any]] = None  # Audit trail parameters
                 ) -> ValidationResult:
        """
        Validate the packet for coherence and integrity.
        This check is performed by the receiving layer (SDK/API).
        
        Args:
            public_key_bytes: Public key bytes for PQC signature verification.
            log_list: List to append log entries to
            previous_packet: The previous packet in the chain (optional for genesis).
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
        
        Returns:
            ValidationResult: Validation result with status and error code/message.
        """
        # Validate ttsTimestamp range
        result = self.validate_ttsTimestamp()
        if not result.is_valid:
            _log_drv_packet_operation(log_list, "validate", {
                "packet_hash": self.get_hash(),
                "result": False,
                "error_code": result.error_code,
                "error_message": result.error_message
            }, pqc_cid, quantum_metadata, self.ttsTimestamp)
            return result

        # Validate sequence number
        result = self.validate_sequence()
        if not result.is_valid:
            _log_drv_packet_operation(log_list, "validate", {
                "packet_hash": self.get_hash(),
                "result": False,
                "error_code": result.error_code,
                "error_message": result.error_message
            }, pqc_cid, quantum_metadata, self.ttsTimestamp)
            return result

        # Validate hash chain integrity (optional, if part of a chain)
        if previous_packet is not None:
            result = DRV_Packet.validate_chain(previous_packet, self)
            if not result.is_valid:
                _log_drv_packet_operation(log_list, "validate_chain", {
                    "packet_hash": self.get_hash(),
                    "previous_packet_hash": previous_packet.get_hash() if previous_packet else None,
                    "result": False,
                    "error_code": result.error_code,
                    "error_message": result.error_message
                }, pqc_cid, quantum_metadata, self.ttsTimestamp)
                return result

        # Verify PQC signature
        if not self.verify_signature(public_key_bytes, log_list, pqc_cid, quantum_metadata):
            result = ValidationResult(False, ValidationErrorCode.INVALID_SIGNATURE, "PQC signature verification failed")
            _log_drv_packet_operation(log_list, "validate", {
                "packet_hash": self.get_hash(),
                "result": False,
                "error_code": result.error_code,
                "error_message": result.error_message
            }, pqc_cid, quantum_metadata, self.ttsTimestamp)
            return result

        # All checks passed
        _log_drv_packet_operation(log_list, "validate", {
            "packet_hash": self.get_hash(),
            "result": True
        }, pqc_cid, quantum_metadata, self.ttsTimestamp)
        return ValidationResult(True, ValidationErrorCode.OK)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DRV_Packet':
        """
        Create packet from dictionary representation.
        """
        version = data.get("version", "1.0")
        if version != cls.VERSION:
            raise ValueError(f"Unsupported DRV_Packet version: {version}. Expected {cls.VERSION}")

        ttsTimestamp = data["ttsTimestamp"]
        sequence = data["sequence"]
        seed = data["seed"]  # Load as string
        previous_hash = data.get("previous_hash")  # Load as optional string
        metadata = data.get("metadata")  # Load as optional dict

        packet = cls(
            ttsTimestamp=ttsTimestamp,
            sequence=sequence,
            seed=seed,  # Pass string
            previous_hash=previous_hash,  # Pass optional string
            metadata=metadata  # Pass optional dict
        )

        # Load signature from hex string (if present) and convert it back to bytes (Section 4.3)
        sig_hex = data.get("pqc_signature")
        if sig_hex:
            packet.pqc_signature = bytes.fromhex(sig_hex)  # Convert hex string back to bytes

        return packet
    
    def to_dict(self, include_signature: bool = False) -> Dict[str, Any]:
        """
        Convert packet to dictionary representation.
        """
        data = {
            "version": self.version,  # Assuming self.version is set in __init__
            "ttsTimestamp": self.ttsTimestamp,
            "sequence": self.sequence,
            "seed": self.seed,  # Store as string
            "metadata": self.metadata,  # Store as dict
            "previous_hash": self.previous_hash  # Store as optional string
        }

        if include_signature and self.pqc_signature is not None:
            # Convert bytes signature to hex string for JSON
            data["pqc_signature"] = self.pqc_signature.hex()

        return data
    
    def __repr__(self) -> str:
        """String representation of the packet."""
        sig_repr = f"b'{self.pqc_signature.hex()}'" if self.pqc_signature else None
        meta_repr = self.metadata if self.metadata is not None else "None"
        return (f"DRV_Packet(version={self.version}, ttsTimestamp={self.ttsTimestamp}, "  # Use self.version
                f"sequence={self.sequence}, seed='{self.seed}', "  # seed is now a string
                f"pqc_signature={sig_repr}, metadata={meta_repr}, "
                f"previous_hash={self.previous_hash})")


# Example usage
if __name__ == "__main__":
    # Create a log list for audit trail
    log_list = []
    
    # Create a packet with audit trail
    packet = DRV_Packet(
        ttsTimestamp=1700000000,
        sequence=1,
        seed="12345",  # Now a string
        log_list=log_list,
        metadata={"source": "test", "version": "1.0"},
        previous_hash="0000000000000000000000000000000000000000000000000000000000000000",
        pqc_cid="DRV_001",
        quantum_metadata={"test": "metadata"}
    )
    
    print("Created packet:")
    print(packet)
    
    # Generate a keypair using real PQC with seed
    temp_log = []
    keypair = PQC.generate_keypair(temp_log, packet.seed_bytes, PQC.DILITHIUM5, None, pqc_cid="DRV_002", quantum_metadata={"test": "metadata"}, deterministic_timestamp=packet.ttsTimestamp)
    private_key_bytes = bytes(keypair.private_key)
    public_key_bytes = keypair.public_key
    
    print(f"\nGenerated Keypair:")
    print(f"Private Key: {private_key_bytes.hex()}")
    print(f"Public Key: {public_key_bytes.hex()}")
    
    # Sign the packet with audit trail
    packet.sign(private_key_bytes, log_list, pqc_cid="DRV_003", quantum_metadata={"test": "metadata"})
    print("\nSigned packet:")
    print(packet)
    
    # Verify the signature with audit trail
    is_valid = packet.verify_signature(public_key_bytes, log_list, pqc_cid="DRV_004", quantum_metadata={"test": "metadata"})
    print(f"\nSignature valid: {is_valid}")
    
    # Validate the packet with audit trail
    validation_result = packet.is_valid(public_key_bytes, log_list, None, pqc_cid="DRV_005", quantum_metadata={"test": "metadata"})
    print(f"Packet validation result: {validation_result}")
    
    # Test serialization/deserialization
    packet_dict = packet.to_dict(include_signature=True)
    reconstructed_packet = DRV_Packet.from_dict(packet_dict)
    print(f"\nReconstructed packet hash matches: {packet.get_hash() == reconstructed_packet.get_hash()}")
    
    # Demonstrate audit trail
    print("\nDRV_Packet Audit Trail:")
    for entry in log_list:
        print(f"  {entry['timestamp']}: {entry['operation']} (CID: {entry['pqc_cid']})")
    
    # Generate deterministic SHA-256 hash of the DRV_Packet audit log
    serialized_log = json.dumps(log_list, sort_keys=True, separators=(',', ':'))
    audit_hash = hashlib.sha256(serialized_log.encode('utf-8')).hexdigest()
    print(f"\nDRV_Packet Audit Hash: {audit_hash}")