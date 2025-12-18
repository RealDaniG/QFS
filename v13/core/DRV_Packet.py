"""
DRV_Packet.py - Deterministic Replayable Validation Packet for QFS V13

Implements the DRV_Packet class for creating deterministic, replayable validation packets
that are compliant with Zero-Simulation requirements and Post-Quantum Cryptography.
"""

import hashlib
import json
from typing import Dict, Any, Optional, NamedTuple, List

try:
    from ..libs.PQC import PQC
except ImportError:
    try:
        from v13.libs.PQC import PQC
    except ImportError:
        from v13.libs.PQC import PQC


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


_ZERO_HASH = "0" * 64


def _log_drv_packet_operation(
    log_list: List[Dict[str, Any]],
    operation: str,
    details: Dict[str, Any],
    pqc_cid: Optional[str] = None,
    quantum_metadata: Optional[Dict[str, Any]] = None,
    timestamp: Optional[int] = None,
):
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
    log_index = len(log_list)
    prev_hash = log_list[-1]["entry_hash"] if log_list else _ZERO_HASH
    entry = {
        "log_index": log_index,
        "operation": operation,
        "timestamp": timestamp if timestamp is not None else 0,
        "details": details,
        "pqc_cid": pqc_cid,
        "quantum_metadata": quantum_metadata,
        "prev_hash": prev_hash,
    }
    entry_for_hash = entry.copy()
    entry_for_hash.pop("prev_hash", None)
    entry_for_hash.pop("entry_hash", None)
    serialized_entry = json.dumps(entry_for_hash, sort_keys=True, separators=(",", ":"))
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

    def __init__(
        self,
        ttsTimestamp: int,
        sequence: int,
        seed: str,
        log_list: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        previous_hash: Optional[str] = None,
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
    ):
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
        if not isinstance(ttsTimestamp, int) or ttsTimestamp < 0:
            raise ValueError("ttsTimestamp must be a non-negative integer")
        if not isinstance(sequence, int) or sequence < 0:
            raise ValueError("sequence must be a non-negative integer")
        if not isinstance(seed, str) or not seed:
            raise ValueError("seed must be a non-empty string")
        self.seed_bytes = seed.encode("utf-8")
        if metadata is not None and (not isinstance(metadata, dict)):
            raise ValueError("metadata must be a dictionary or None")
        if previous_hash is not None and (not isinstance(previous_hash, str)):
            raise ValueError("previous_hash must be a string or None")
        self.version = self.VERSION
        self.ttsTimestamp = ttsTimestamp
        self.sequence = sequence
        self.seed = seed
        self.seed_bytes = seed.encode("utf-8")
        self.metadata = metadata or {}
        self.previous_hash = previous_hash
        self.pqc_signature: Optional[bytes] = None
        if log_list is not None:
            _log_drv_packet_operation(
                log_list,
                "create",
                {
                    "ttsTimestamp": ttsTimestamp,
                    "sequence": sequence,
                    "seed": seed,
                    "metadata": metadata,
                    "previous_hash": previous_hash,
                },
                pqc_cid,
                quantum_metadata,
                ttsTimestamp,
            )

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
            "previous_hash": self.previous_hash,
        }
        if include_signature and self.pqc_signature is not None:
            data["pqc_signature"] = self.pqc_signature.hex()
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    def get_canonical_bytes(self) -> bytes:
        """Return the exact bytes that are PQC-signed."""
        return self.serialize(include_signature=False).encode("utf-8")

    def get_hash(self) -> str:
        """
        Calculate deterministic SHA-256 hash of the packet. (Section 4.2)
        Chain hash = SHA-256 of PQC-signed canonical bytes.

        Returns:
            Hex string of the SHA-256 hash
        """
        return hashlib.sha256(self.get_canonical_bytes()).hexdigest()

    def sign(
        self,
        private_key_bytes: bytes,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Sign the packet with a private key using the configured PQC provider.

        Args:
            private_key_bytes: Private key as bytes
            log_list: List to append log entries to
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
        """
        data_to_sign = self.to_dict(include_signature=False)
        temp_log = []
        signature = PQC.sign_data(
            private_key_bytes,
            data_to_sign,
            temp_log,
            pqc_cid,
            quantum_metadata,
            self.ttsTimestamp,
        )
        self.pqc_signature = signature
        _log_drv_packet_operation(
            log_list,
            "sign",
            {
                "packet_hash": self.get_hash(),
                "signature_length": len(signature) if signature else 0,
            },
            pqc_cid,
            quantum_metadata,
            self.ttsTimestamp,
        )

    def verify_signature(
        self,
        public_key_bytes: bytes,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Verify the packet's signature with a public key using the configured PQC provider.

        Args:
            public_key_bytes: Public key as bytes
            log_list: List to append log entries to
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail

        Returns:
            bool: True if signature is valid, False otherwise
        """
        if self.pqc_signature is None:
            _log_drv_packet_operation(
                log_list,
                "verify",
                {
                    "packet_hash": self.get_hash(),
                    "result": False,
                    "error": "No signature to verify",
                },
                pqc_cid,
                quantum_metadata,
                self.ttsTimestamp if hasattr(self, "ttsTimestamp") else 0,
            )
            return False
        data_to_verify = self.to_dict(include_signature=False)
        temp_log = []
        validation_result = PQC.verify_signature(
            public_key_bytes,
            data_to_verify,
            self.pqc_signature,
            temp_log,
            pqc_cid,
            quantum_metadata,
            self.ttsTimestamp,
        )
        result = validation_result.is_valid
        _log_drv_packet_operation(
            log_list,
            "verify",
            {"packet_hash": self.get_hash(), "result": result},
            pqc_cid,
            quantum_metadata,
            self.ttsTimestamp if hasattr(self, "ttsTimestamp") else 0,
        )
        return result

    def validate_sequence(self) -> ValidationResult:
        """Validate sequence number is non-negative."""
        if self.sequence < 0:
            return ValidationResult(
                False,
                ValidationErrorCode.INVALID_SEQUENCE,
                f"Sequence {self.sequence} is negative",
            )
        return ValidationResult(True, ValidationErrorCode.OK)

    def validate_ttsTimestamp(self) -> ValidationResult:
        """Validate ttsTimestamp is within a reasonable range."""
        if not 0 <= self.ttsTimestamp <= 9223372036854775807:
            return ValidationResult(
                False,
                ValidationErrorCode.INVALID_TTS_TIMESTAMP,
                f"ttsTimestamp {self.ttsTimestamp} out of range",
            )
        return ValidationResult(True, ValidationErrorCode.OK)

    @staticmethod
    def validate_chain(
        previous_packet: Optional["DRV_Packet"],
        current_packet: "DRV_Packet",
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Validate hash chain integrity and sequence monotonicity."""
        if previous_packet is None:
            result = ValidationResult(True, ValidationErrorCode.OK)
            return result
        if current_packet.previous_hash != previous_packet.get_hash():
            result = ValidationResult(
                False,
                ValidationErrorCode.INVALID_CHAIN,
                f"Chain hash mismatch: got {current_packet.previous_hash}, expected {previous_packet.get_hash()}",
            )
            return result
        if current_packet.sequence != previous_packet.sequence + 1:
            result = ValidationResult(
                False,
                ValidationErrorCode.INVALID_SEQUENCE,
                f"Sequence non-monotonic: got {current_packet.sequence}, expected {previous_packet.sequence + 1}",
            )
            return result
        result = ValidationResult(True, ValidationErrorCode.OK)
        return result

    def is_valid(
        self,
        public_key_bytes: bytes,
        log_list: List[Dict[str, Any]],
        previous_packet: Optional["DRV_Packet"] = None,
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
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
        result = self.validate_ttsTimestamp()
        if not result.is_valid:
            _log_drv_packet_operation(
                log_list,
                "validate",
                {
                    "packet_hash": self.get_hash(),
                    "result": False,
                    "error_code": result.error_code,
                    "error_message": result.error_message,
                },
                pqc_cid,
                quantum_metadata,
                self.ttsTimestamp,
            )
            return result
        result = self.validate_sequence()
        if not result.is_valid:
            _log_drv_packet_operation(
                log_list,
                "validate",
                {
                    "packet_hash": self.get_hash(),
                    "result": False,
                    "error_code": result.error_code,
                    "error_message": result.error_message,
                },
                pqc_cid,
                quantum_metadata,
                self.ttsTimestamp,
            )
            return result
        if previous_packet is not None:
            result = DRV_Packet.validate_chain(previous_packet, self)
            if not result.is_valid:
                _log_drv_packet_operation(
                    log_list,
                    "validate_chain",
                    {
                        "packet_hash": self.get_hash(),
                        "previous_packet_hash": previous_packet.get_hash()
                        if previous_packet
                        else None,
                        "result": False,
                        "error_code": result.error_code,
                        "error_message": result.error_message,
                    },
                    pqc_cid,
                    quantum_metadata,
                    self.ttsTimestamp,
                )
                return result
        if not self.verify_signature(
            public_key_bytes, log_list, pqc_cid, quantum_metadata
        ):
            result = ValidationResult(
                False,
                ValidationErrorCode.INVALID_SIGNATURE,
                "PQC signature verification failed",
            )
            _log_drv_packet_operation(
                log_list,
                "validate",
                {
                    "packet_hash": self.get_hash(),
                    "result": False,
                    "error_code": result.error_code,
                    "error_message": result.error_message,
                },
                pqc_cid,
                quantum_metadata,
                self.ttsTimestamp,
            )
            return result
        _log_drv_packet_operation(
            log_list,
            "validate",
            {"packet_hash": self.get_hash(), "result": True},
            pqc_cid,
            quantum_metadata,
            self.ttsTimestamp,
        )
        return ValidationResult(True, ValidationErrorCode.OK)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DRV_Packet":
        """
        Create packet from dictionary representation.
        """
        version = data.get("version", "1.0")
        if version != cls.VERSION:
            raise ValueError(
                f"Unsupported DRV_Packet version: {version}. Expected {cls.VERSION}"
            )
        ttsTimestamp = data["ttsTimestamp"]
        sequence = data["sequence"]
        seed = data["seed"]
        previous_hash = data.get("previous_hash")
        metadata = data.get("metadata")
        packet = cls(
            ttsTimestamp=ttsTimestamp,
            sequence=sequence,
            seed=seed,
            previous_hash=previous_hash,
            metadata=metadata,
        )
        sig_hex = data.get("pqc_signature")
        if sig_hex:
            packet.pqc_signature = bytes.fromhex(sig_hex)
        return packet

    def to_dict(self, include_signature: bool = False) -> Dict[str, Any]:
        """
        Convert packet to dictionary representation.
        """
        data = {
            "version": self.version,
            "ttsTimestamp": self.ttsTimestamp,
            "sequence": self.sequence,
            "seed": self.seed,
            "metadata": self.metadata,
            "previous_hash": self.previous_hash,
        }
        if include_signature and self.pqc_signature is not None:
            data["pqc_signature"] = self.pqc_signature.hex()
        return data

    def __repr__(self) -> str:
        """String representation of the packet."""
        sig_repr = f"b'{self.pqc_signature.hex()}'" if self.pqc_signature else None
        meta_repr = self.metadata if self.metadata is not None else "None"
        return f"DRV_Packet(version={self.version}, ttsTimestamp={self.ttsTimestamp}, sequence={self.sequence}, seed='{self.seed}', pqc_signature={sig_repr}, metadata={meta_repr}, previous_hash={self.previous_hash})"
