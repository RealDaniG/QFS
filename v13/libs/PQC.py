"""
PQC.py - Production-Ready Post-Quantum Cryptography Library for QFS V13
Zero-Simulation Compliant, PQC & Quantum Metadata Ready, Fully Auditable, Thread-Safe via Context
"""

import json
import hashlib
from typing import Any, Optional, Dict, List, Tuple, Union
from dataclasses import dataclass

from .pqc.registry import PQCAlgorithm, REGISTRY
from .pqc.oqs_adapter import get_adapter

# Initialize backend
_adapter = get_adapter()
_PQC_BACKEND = "liboqs" if _adapter.__name__ == "OQSAdapter" else "mock"

# Backend info available via PQC.get_backend_info()


class PQCError(Exception):
    """Base exception for PQC operations"""

    pass


class PQCValidationError(PQCError):
    """Raised when PQC validation fails"""

    pass


@dataclass
class KeyPair:
    """Container for PQC key pair"""

    private_key: bytearray
    public_key: bytes
    algorithm: str
    parameters: Dict[str, Any]


@dataclass
class ValidationResult:
    """Result of a PQC validation operation"""

    is_valid: bool
    error_message: Optional[str] = None
    quantum_metadata: Optional[Dict[str, Any]] = None


class PQC:
    """
    Production-ready, deterministic PQC library for QFS V13.
    Provides Zero-Simulation compliant operations, PQC/quantum metadata support,
    and requires an external log list for auditability (via context manager or direct passing).
    This library does not maintain its own global state.
    """

    DILITHIUM5 = "Dilithium5"
    KYBER1024 = "Kyber1024"
    SYSTEM_FINGERPRINT = "qfs_v13_deterministic"
    ZERO_HASH = "0" * 64

    @staticmethod
    def _resolve_algorithm(algo_name: str) -> PQCAlgorithm:
        if algo_name == PQC.DILITHIUM5:
            return PQCAlgorithm.DILITHIUM5
        elif algo_name == PQC.KYBER1024:
            return PQCAlgorithm.KYBER1024
        else:
            raise ValueError(f"Unknown PQC algorithm: {algo_name}")

    @staticmethod
    def kem_generate_keypair(
        algorithm: str, seed: Optional[bytes] = None
    ) -> Tuple[bytes, bytes]:
        """Generate KEM keypair (public_key, secret_key)."""
        algo_enum = PQC._resolve_algorithm(algorithm)
        return _adapter.kem_keypair(algo_enum, seed)

    @staticmethod
    def kem_encapsulate(algorithm: str, public_key: bytes) -> Tuple[bytes, bytes]:
        """Encapsulate symmetric key: returns (ciphertext, shared_secret)."""
        algo_enum = PQC._resolve_algorithm(algorithm)
        return _adapter.kem_encapsulate(algo_enum, public_key)

    @staticmethod
    def kem_decapsulate(algorithm: str, secret_key: bytes, ciphertext: bytes) -> bytes:
        """Decapsulate symmetric key: returns shared_secret."""
        algo_enum = PQC._resolve_algorithm(algorithm)
        return _adapter.kem_decapsulate(algo_enum, secret_key, ciphertext)

    @staticmethod
    def get_backend_info() -> dict:
        """
        Get information about the currently active PQC backend.
        """
        if _PQC_BACKEND == "liboqs":
            return {
                "backend": "liboqs-python",
                "algorithm": "Dilithium-5 (OQS)",
                "security_level": "NIST Level 5",
                "production_ready": True,
                "quantum_resistant": True,
                "deterministic": False,
            }
        elif _PQC_BACKEND == "mock":
            return {
                "backend": "MockPQC",
                "algorithm": "Simulated-Dilithium",
                "security_level": "NONE",
                "production_ready": False,
                "quantum_resistant": False,
                "deterministic": True,
                "warning": "TESTING ONLY",
            }
        else:
            return {"backend": "unknown", "error": "No PQC backend loaded"}

    class LogContext:
        """
        Context manager for creating isolated, deterministic operation logs.
        Ensures thread-safety and coherence for a specific session or transaction bundle.
        """

        def __init__(self):
            self.log = []
            self._prev_hash = PQC.ZERO_HASH

        def __enter__(self):
            self.log = []
            self._prev_hash = PQC.ZERO_HASH
            return self.log

        def __exit__(self, exc_type, exc_val, exc_tb):
            for i in range(len(self.log)):
                if i == 0:
                    pass
                else:
                    self.log[i]["prev_hash"] = self.log[i - 1]["entry_hash"]

        def get_log(self):
            return self.log

        def get_hash(self):
            return PQC.get_pqc_audit_hash(self.log)

        def export(self, path: str):
            PQC.export_log(self.log, path)

    @staticmethod
    def _log_pqc_operation(
        operation: str,
        details: Dict[str, Any],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
        error: Optional[Exception] = None,
    ):
        """Appends a deterministic operation entry to the provided log_list with enhanced audit fields."""
        log_index = len(log_list)
        if log_index == 0:
            prev_hash = PQC.ZERO_HASH
        else:
            prev_hash = log_list[-1]["entry_hash"]
        entry = {
            "log_index": log_index,
            "operation": operation,
            "details": details,
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata,
            "timestamp": deterministic_timestamp,
            "system_fingerprint": PQC.SYSTEM_FINGERPRINT,
            "prev_hash": prev_hash,
        }
        if error:
            entry["error"] = {"type": type(error).__name__, "message": str(error)}
        entry_for_hash = entry.copy()
        entry_for_hash.pop("prev_hash", None)
        entry_for_hash.pop("entry_hash", None)
        serialized_entry = json.dumps(
            entry_for_hash, sort_keys=True, separators=(",", ":")
        )
        entry_hash = hashlib.sha3_512(serialized_entry.encode("utf-8")).hexdigest()
        entry["entry_hash"] = entry_hash
        log_list.append(entry)

    @staticmethod
    def get_pqc_audit_hash(log_list: List[Dict[str, Any]]) -> str:
        """Generate deterministic SHA3-512 hash of a given log list."""
        serialized_log = json.dumps(log_list, sort_keys=True, default=str)
        return hashlib.sha3_512(serialized_log.encode("utf-8")).hexdigest()

    @staticmethod
    def export_log(log_list: List[Dict[str, Any]], path: str):
        """Export the provided log list to a JSON file."""
        with open(path, "w") as f:
            json.dump(log_list, f, sort_keys=True, default=str)

    @staticmethod
    def _canonicalize_for_sign(data: Any) -> str:
        """
        Converts data to a canonical string representation suitable for signing.
        Ensures deterministic serialization of BigNum128 and other complex types.
        """
        if hasattr(data, "to_decimal_string"):
            return data.to_decimal_string()
        elif isinstance(data, dict):
            canonical_dict = {}
            for key, value in sorted(data.items()):
                canonical_dict[key] = PQC._canonicalize_for_sign(value)
            return json.dumps(canonical_dict, sort_keys=True, separators=(",", ":"))
        elif isinstance(data, (list, tuple)):
            canonical_list = [PQC._canonicalize_for_sign(item) for item in data]
            return json.dumps(canonical_list, separators=(",", ":"))
        elif isinstance(data, bytes):
            return data.hex()
        elif isinstance(data, bytearray):
            return bytes(data).hex()
        elif isinstance(data, str):
            return data
        elif isinstance(data, int):
            return str(data)
        else:
            return str(data)

    @staticmethod
    def serialize_data(data: Any) -> bytes:
        """
        Serializes data to bytes for signing, ensuring deterministic output.
        """
        canonical_str = PQC._canonicalize_for_sign(data)
        return canonical_str.encode("utf-8")

    @staticmethod
    def secure_zeroize_keypair(keypair: KeyPair) -> None:
        """
        Securely zeroizes a keypair's private key material IN-PLACE.
        """
        if isinstance(keypair.private_key, bytearray):
            PQC.zeroize_private_key(keypair.private_key)
        else:
            raise ValueError(
                "KeyPair.private_key must be bytearray for in-place zeroization"
            )

    @staticmethod
    def zeroize_private_key(private_key: Union[bytes, bytearray]) -> None:
        """
        Securely zeroizes private key material IN-PLACE.
        """
        if isinstance(private_key, bytearray):
            for i in range(len(private_key)):
                private_key[i] = 0
        elif isinstance(private_key, bytes):
            raise ValueError(
                "Cannot zeroize immutable bytes; convert to bytearray first"
            )
        else:
            raise TypeError(f"Expected bytes or bytearray, got {type(private_key)}")

    @staticmethod
    def generate_keypair(
        log_list: List[Dict[str, Any]],
        seed: bytes,
        algorithm: str = DILITHIUM5,
        parameters: Optional[Dict[str, Any]] = None,
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> KeyPair:
        """
        Generates a deterministic PQC keypair using the specified algorithm.
        """
        if log_list is None:
            raise ValueError("log_list is required for generate_keypair")
        if parameters is None:
            parameters = {}
        if not seed:
            raise ValueError("seed is required for deterministic key generation")
        seed_hash = hashlib.sha3_512(seed).hexdigest()
        if quantum_metadata is None:
            quantum_metadata = {}
        quantum_metadata["seed_hash"] = seed_hash
        try:
            if algorithm == PQC.DILITHIUM5:
                # Use the new adapter
                private_key, public_key = _adapter.generate_keypair(
                    PQCAlgorithm.DILITHIUM5, seed
                )
            else:
                raise PQCError(f"Unsupported algorithm: {algorithm}")

            # Helper to ensure private_key is bytearray as anticipated by old KeyPair usage
            if not isinstance(private_key, bytearray):
                private_key_array = bytearray(private_key)
            else:
                private_key_array = private_key

            result_keypair = KeyPair(
                private_key=private_key_array,
                public_key=public_key,
                algorithm=algorithm,
                parameters=parameters,
            )
            PQC._log_pqc_operation(
                operation="generate_keypair",
                details={
                    "algorithm": algorithm,
                    "parameters": parameters,
                    "public_key_size": len(public_key),
                    "seed_provided": True,
                },
                log_list=log_list,
                pqc_cid=pqc_cid,
                quantum_metadata=quantum_metadata,
                deterministic_timestamp=deterministic_timestamp,
            )
            return result_keypair
        except Exception as e:
            PQC._log_pqc_operation(
                operation="generate_keypair",
                details={
                    "algorithm": algorithm,
                    "parameters": parameters,
                    "error_occurred": True,
                },
                log_list=log_list,
                pqc_cid=pqc_cid,
                quantum_metadata=quantum_metadata,
                deterministic_timestamp=deterministic_timestamp,
                error=e,
            )
            raise PQCError(f"Failed to generate keypair: {str(e)}") from e

    @staticmethod
    def sign_data(
        private_key: Union[bytes, bytearray],
        data: Any,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> bytes:
        """
        Signs data using the provided private key.
        """
        if log_list is None:
            raise ValueError("log_list is required for sign_data")
        try:
            serialized_data = PQC.serialize_data(data)
            if isinstance(private_key, bytearray):
                private_key_bytes = bytes(private_key)
            else:
                private_key_bytes = private_key

            signature = _adapter.sign(
                PQCAlgorithm.DILITHIUM5, private_key_bytes, serialized_data
            )

            PQC._log_pqc_operation(
                operation="sign_data",
                details={
                    "data_hash": hashlib.sha3_512(serialized_data).hexdigest(),
                    "signature_size": len(signature),
                },
                log_list=log_list,
                pqc_cid=pqc_cid,
                quantum_metadata=quantum_metadata,
                deterministic_timestamp=deterministic_timestamp,
            )
            return signature
        except Exception as e:
            PQC._log_pqc_operation(
                operation="sign_data",
                details={"error_occurred": True},
                log_list=log_list,
                pqc_cid=pqc_cid,
                quantum_metadata=quantum_metadata,
                deterministic_timestamp=deterministic_timestamp,
                error=e,
            )
            raise PQCError(f"Failed to sign data: {str(e)}") from e

    @staticmethod
    def verify_signature(
        public_key: bytes,
        data: Any,
        signature: bytes,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> ValidationResult:
        """
        Verifies a signature against data using the provided public key.
        Returns a ValidationResult with verification outcome.
        """
        if log_list is None:
            raise ValueError("log_list is required for verify_signature")
        try:
            serialized_data = PQC.serialize_data(data)
            is_valid = _adapter.verify(
                PQCAlgorithm.DILITHIUM5, public_key, serialized_data, signature
            )
            result = ValidationResult(
                is_valid=is_valid, quantum_metadata=quantum_metadata
            )
            PQC._log_pqc_operation(
                operation="verify_signature",
                details={
                    "data_hash": hashlib.sha3_512(serialized_data).hexdigest(),
                    "signature_size": len(signature),
                    "is_valid": is_valid,
                },
                log_list=log_list,
                pqc_cid=pqc_cid,
                quantum_metadata=quantum_metadata,
                deterministic_timestamp=deterministic_timestamp,
            )
            return result
        except Exception as e:
            PQC._log_pqc_operation(
                operation="verify_signature",
                details={"error_occurred": True},
                log_list=log_list,
                pqc_cid=pqc_cid,
                quantum_metadata=quantum_metadata,
                deterministic_timestamp=deterministic_timestamp,
                error=e,
            )
            return ValidationResult(
                is_valid=False,
                error_message=f"Verification failed: {str(e)}",
                quantum_metadata=quantum_metadata,
            )
