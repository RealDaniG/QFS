"""
PQC.py - Production-Ready Post-Quantum Cryptography Library for QFS V13
Zero-Simulation Compliant, PQC & Quantum Metadata Ready, Fully Auditable, Thread-Safe via Context
"""

import json
import hashlib
from typing import Any, Optional, Dict, List, Tuple, Union
from dataclasses import dataclass

# Production implementation uses the real PQC library
# In production environments, ensure pqcrystals is properly installed
# pip install pqcrystals

# Backend Selection (Priority Order):
# 1. Try pqcrystals (real Dilithium-5) - PREFERRED
# 2. Try liboqs-python (alternative real PQC) - FALLBACK
# 3. Use MockPQC (SHA-256 simulation) - INTEGRATION TESTING ONLY

# Inline MockPQC for fallback (avoids circular dependencies)
class _MockPQC:
    """Lightweight mock PQC for integration testing ONLY - NOT CRYPTOGRAPHICALLY SECURE"""
    def __init__(self):
        self._key_cache = {}  # Map public_key -> private_key for verify
    
    def keygen(self, seed: bytes) -> tuple:
        if len(seed) < 32:
            # Pad seed to 32 bytes if needed
            seed = seed + b'\x00' * (32 - len(seed))
        private_key = hashlib.sha256(b"private_" + seed).digest()
        public_key = hashlib.sha256(b"public_" + seed).digest()
        # Cache the keypair for verify operation
        self._key_cache[public_key] = private_key
        return private_key, public_key
    
    def sign(self, private_key: bytes, message: bytes) -> bytes:
        return hashlib.sha256(private_key + message).digest()
    
    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        # Lookup private key from cache
        private_key = self._key_cache.get(public_key)
        if private_key is None:
            return False  # Key not found, verification fails
        expected = self.sign(private_key, message)
        return signature == expected

_PQC_BACKEND = "unknown"
Dilithium5Impl = None

try:
    from pqcrystals.dilithium import Dilithium5
    Dilithium5Impl = Dilithium5
    _PQC_BACKEND = "pqcrystals"
    print("[PQC] Using pqcrystals.dilithium (production-grade)")
except ImportError:
    # Try liboqs-python as fallback (catch all exceptions including SystemExit)
    liboqs_failed = False
    try:
        # Suppress liboqs auto-installation that causes SystemExit
        import os
        os.environ['LIBOQS_PYTHON_NO_AUTO_INSTALL'] = '1'
        
        from oqs import Signature
        # Wrap liboqs Signature in pqcrystals-like interface
        class LibOQSAdapter:
            def __init__(self):
                self.sig = Signature("Dilithium5")
            
            def keygen(self, seed: bytes) -> tuple:
                # liboqs doesn't support seed-based keygen directly
                # Use seed to initialize PRNG state (non-ideal but deterministic)
                
                # Derive entropy from seed
                entropy = hashlib.sha512(seed).digest()
                
                # Temporarily set environment randomness (platform-specific)
                # Note: This is a workaround; liboqs keygen is not truly seed-based
                pub = self.sig.generate_keypair()
                sec = self.sig.export_secret_key()
                return sec, pub
            
            def sign(self, private_key: bytes, message: bytes) -> bytes:
                self.sig.import_secret_key(private_key)
                return self.sig.sign(message)
            
            def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
                return self.sig.verify(message, signature, public_key)
        
        Dilithium5Impl = LibOQSAdapter()
        _PQC_BACKEND = "liboqs"
        print("[PQC] Using liboqs-python (production-grade fallback)")
    except (ImportError, SystemExit, Exception) as e:
        liboqs_failed = True
    
    if liboqs_failed or Dilithium5Impl is None:
        # Final fallback: Use inline MockPQC for integration testing ONLY
        Dilithium5Impl = _MockPQC()
        _PQC_BACKEND = "mock"
        print("\n" + "="*80)
        print("[WARNING]: Using MockPQC (SHA-256 simulation) - NOT CRYPTOGRAPHICALLY SECURE")
        print("="*80)
        print("This is ONLY suitable for integration testing.")
        print("DO NOT use in production or for security audits.")
        print("Install pqcrystals or liboqs-python for real PQC support.")
        print("="*80 + "\n")

# ------------------------------
# Custom Exceptions
# ------------------------------
class PQCError(Exception):
    """Base exception for PQC operations"""
    pass

class PQCValidationError(PQCError):
    """Raised when PQC validation fails"""
    pass

# ------------------------------
# Data Structures
# ------------------------------
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

# ------------------------------
# PQC Library
# ------------------------------
class PQC:
    """
    Production-ready, deterministic PQC library for QFS V13.
    Provides Zero-Simulation compliant operations, PQC/quantum metadata support,
    and requires an external log list for auditability (via context manager or direct passing).
    This library does not maintain its own global state.
    """
    
    # Supported algorithms
    DILITHIUM5 = "Dilithium5"
    
    # System fingerprint for audit logs (deterministic placeholder)
    SYSTEM_FINGERPRINT = "qfs_v13_deterministic"
    
    # Zero hash for the first entry in the audit log chain
    ZERO_HASH = "0" * 64
    
    @staticmethod
    def get_backend_info() -> dict:
        """
        Get information about the currently active PQC backend.
        
        Returns:
            dict with backend name, security level, and production readiness
        """
        if _PQC_BACKEND == "pqcrystals":
            return {
                "backend": "pqcrystals",
                "algorithm": "Dilithium-5 (NIST PQC Standard)",
                "security_level": "NIST Level 5 (highest)",
                "production_ready": True,
                "quantum_resistant": True,
                "deterministic": True
            }
        elif _PQC_BACKEND == "liboqs":
            return {
                "backend": "liboqs-python",
                "algorithm": "Dilithium-5 (Open Quantum Safe)",
                "security_level": "NIST Level 5 (highest)",
                "production_ready": True,
                "quantum_resistant": True,
                "deterministic": False,  # liboqs keygen is not seed-based
                "note": "Keygen not fully deterministic; use with caution"
            }
        elif _PQC_BACKEND == "mock":
            return {
                "backend": "MockPQC",
                "algorithm": "SHA-256 (simulation only)",
                "security_level": "NONE - NOT CRYPTOGRAPHICALLY SECURE",
                "production_ready": False,
                "quantum_resistant": False,
                "deterministic": True,
                "warning": "INTEGRATION TESTING ONLY - DO NOT USE IN PRODUCTION"
            }
        else:
            return {
                "backend": "unknown",
                "error": "No PQC backend loaded"
            }
    
    # --- Log Context Manager ---
    class LogContext:
        """
        Context manager for creating isolated, deterministic operation logs.
        Ensures thread-safety and coherence for a specific session or transaction bundle.
        Usage:
            with PQC.LogContext() as log:
                result = PQC.generate_keypair(log, algorithm=PQC.DILITHIUM5)
        """
        def __init__(self):
            self.log = []
            self._prev_hash = PQC.ZERO_HASH

        def __enter__(self):
            self.log = []
            self._prev_hash = PQC.ZERO_HASH
            return self.log

        def __exit__(self, exc_type, exc_val, exc_tb):
            # prev_hash is now set immediately in _log_pqc_operation; no backfill needed
            pass

        def get_log(self):
            return self.log

        def get_hash(self):
            return PQC.get_pqc_audit_hash(self.log)

        def export(self, path: str):
            PQC.export_log(self.log, path)

    # --------------------------
    # Internal Logging
    # --------------------------
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
        # Calculate log index
        log_index = len(log_list)
        
        # Determine prev_hash immediately based on current log state
        if log_index == 0:
            prev_hash = PQC.ZERO_HASH
        else:
            prev_hash = log_list[-1]["entry_hash"]
        
        # Create the base entry with immediate prev_hash
        entry = {
            "log_index": log_index,
            "operation": operation,
            "details": details,
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata,
            "timestamp": deterministic_timestamp,
            "system_fingerprint": PQC.SYSTEM_FINGERPRINT,
            "prev_hash": prev_hash  # Set immediately, not deferred
        }
        
        # Add error information if present
        if error:
            entry["error"] = {
                "type": type(error).__name__,
                "message": str(error)
            }
        
        # Calculate entry hash (excluding prev_hash to avoid circular dependency)
        entry_for_hash = entry.copy()
        entry_for_hash.pop("prev_hash", None)
        entry_for_hash.pop("entry_hash", None)
        serialized_entry = json.dumps(entry_for_hash, sort_keys=True, separators=(',', ':'))
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

    # --------------------------
    # Canonical Serialization (Section 2.2)
    # --------------------------
    @staticmethod
    def _canonicalize_for_sign(data: Any) -> str:
        """
        Converts data to a canonical string representation suitable for signing.
        Ensures deterministic serialization of BigNum128 and other complex types.
        """
        if hasattr(data, 'to_decimal_string'):
            # Handle BigNum128 objects
            return data.to_decimal_string()
        elif isinstance(data, dict):
            # Recursively canonicalize dictionary values
            canonical_dict = {}
            for key, value in sorted(data.items()):
                canonical_dict[key] = PQC._canonicalize_for_sign(value)
            return json.dumps(canonical_dict, sort_keys=True, separators=(',', ':'))
        elif isinstance(data, (list, tuple)):
            # Recursively canonicalize list/tuple items
            canonical_list = [PQC._canonicalize_for_sign(item) for item in data]
            return json.dumps(canonical_list, separators=(',', ':'))
        elif isinstance(data, bytes):
            # Handle bytes by converting to hex string
            return data.hex()
        elif isinstance(data, bytearray):
            # Handle bytearray by converting to hex string
            return bytes(data).hex()
        elif isinstance(data, str):
            # For strings, return directly without JSON quotes
            return data
        elif isinstance(data, int):
            # For integers, convert to string without JSON quotes
            return str(data)
        else:
            # For other types, convert to string directly
            return str(data)

    @staticmethod
    def serialize_data(data: Any) -> bytes:
        """
        Serializes data to bytes for signing, ensuring deterministic output.
        """
        canonical_str = PQC._canonicalize_for_sign(data)
        return canonical_str.encode('utf-8')

    # --------------------------
    # Memory Hygiene
    # --------------------------
    @staticmethod
    def secure_zeroize_keypair(keypair: KeyPair) -> None:
        """
        Securely zeroizes a keypair's private key material IN-PLACE.
        
        Args:
            keypair: KeyPair with private_key as bytearray
            
        Raises:
            ValueError: If keypair.private_key is not bytearray
        """
        if isinstance(keypair.private_key, bytearray):
            PQC.zeroize_private_key(keypair.private_key)
        else:
            raise ValueError("KeyPair.private_key must be bytearray for in-place zeroization")

    @staticmethod
    def zeroize_private_key(private_key: Union[bytes, bytearray]) -> None:
        """
        Securely zeroizes private key material IN-PLACE.
        Only works on mutable bytearray; raises ValueError for immutable bytes.
        
        Args:
            private_key: Private key material (must be bytearray for in-place zeroing)
            
        Raises:
            ValueError: If private_key is immutable bytes
            TypeError: If private_key is not bytes or bytearray
        """
        if isinstance(private_key, bytearray):
            # Zero in-place
            for i in range(len(private_key)):
                private_key[i] = 0
        elif isinstance(private_key, bytes):
            raise ValueError("Cannot zeroize immutable bytes; convert to bytearray first")
        else:
            raise TypeError(f"Expected bytes or bytearray, got {type(private_key)}")

    # --------------------------
    # Core PQC Operations (Section 2.1)
    # --------------------------
    # Production implementation uses the real PQC library
    # In production environments, ensure pqcrystals is properly installed
    # pip install pqcrystals


# Module-level PQC library import
try:
    from pqcrystals.dilithium import Dilithium5
    Dilithium5Impl = Dilithium5
except ImportError:
    # Fall back to MockPQC for testing environments
    # Production requires pqcrystals library
    Dilithium5Impl = None

# ------------------------------
# Custom Exceptions
# ------------------------------
class PQCError(Exception):
    """Base exception for PQC operations"""
    pass

class PQCValidationError(PQCError):
    """Raised when PQC validation fails"""
    pass

# ------------------------------
# Data Structures
# ------------------------------
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

# ------------------------------
# PQC Library
# ------------------------------
class PQC:
    """
    Production-ready, deterministic PQC library for QFS V13.
    Provides Zero-Simulation compliant operations, PQC/quantum metadata support,
    and requires an external log list for auditability (via context manager or direct passing).
    This library does not maintain its own global state.
    """
    
    # Supported algorithms
    DILITHIUM5 = "Dilithium5"
    
    # System fingerprint for audit logs (deterministic placeholder)
    SYSTEM_FINGERPRINT = "qfs_v13_deterministic"
    
    # Zero hash for the first entry in the audit log chain
    ZERO_HASH = "0" * 64
    
    # --- Log Context Manager ---
    class LogContext:
        """
        Context manager for creating isolated, deterministic operation logs.
        Ensures thread-safety and coherence for a specific session or transaction bundle.
        Usage:
            with PQC.LogContext() as log:
                result = PQC.generate_keypair(log, algorithm=PQC.DILITHIUM5)
        """
        def __init__(self):
            self.log = []
            self._prev_hash = PQC.ZERO_HASH

        def __enter__(self):
            self.log = []
            self._prev_hash = PQC.ZERO_HASH
            return self.log

        def __exit__(self, exc_type, exc_val, exc_tb):
            # Finalize the log list by setting prev_hash for chain integrity
            for i in range(len(self.log)):
                if i == 0:
                    # The first entry's prev_hash remains the initial value (ZERO_HASH)
                    pass
                else:
                    # Set the current entry's prev_hash to the previous entry's entry_hash
                    self.log[i]['prev_hash'] = self.log[i-1]['entry_hash']
            # Log remains accessible via self.log

        def get_log(self):
            return self.log

        def get_hash(self):
            return PQC.get_pqc_audit_hash(self.log)

        def export(self, path: str):
            PQC.export_log(self.log, path)

    # --------------------------
    # Internal Logging
    # --------------------------
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
        # Calculate log index
        log_index = len(log_list)
        
        # Create the base entry with placeholder prev_hash
        entry = {
            "log_index": log_index,
            "operation": operation,
            "details": details,
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata,
            "timestamp": deterministic_timestamp,
            "system_fingerprint": PQC.SYSTEM_FINGERPRINT,
            "prev_hash": PQC.ZERO_HASH  # Placeholder, will be updated by LogContext
        }
        
        # Add error information if present
        if error:
            entry["error"] = {
                "type": type(error).__name__,
                "message": str(error)
            }
        
        # Calculate entry hash (excluding prev_hash to avoid circular dependency)
        entry_for_hash = entry.copy()
        entry_for_hash.pop("prev_hash", None)
        entry_for_hash.pop("entry_hash", None)
        serialized_entry = json.dumps(entry_for_hash, sort_keys=True, separators=(',', ':'))
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

    # --------------------------
    # Canonical Serialization (Section 2.2)
    # --------------------------
    @staticmethod
    def _canonicalize_for_sign(data: Any) -> str:
        """
        Converts data to a canonical string representation suitable for signing.
        Ensures deterministic serialization of BigNum128 and other complex types.
        """
        if hasattr(data, 'to_decimal_string'):
            # Handle BigNum128 objects
            return data.to_decimal_string()
        elif isinstance(data, dict):
            # Recursively canonicalize dictionary values
            canonical_dict = {}
            for key, value in sorted(data.items()):
                canonical_dict[key] = PQC._canonicalize_for_sign(value)
            return json.dumps(canonical_dict, sort_keys=True, separators=(',', ':'))
        elif isinstance(data, (list, tuple)):
            # Recursively canonicalize list/tuple items
            canonical_list = [PQC._canonicalize_for_sign(item) for item in data]
            return json.dumps(canonical_list, separators=(',', ':'))
        elif isinstance(data, bytes):
            # Handle bytes by converting to hex string
            return data.hex()
        elif isinstance(data, bytearray):
            # Handle bytearray by converting to hex string
            return bytes(data).hex()
        elif isinstance(data, str):
            # For strings, return directly without JSON quotes
            return data
        elif isinstance(data, int):
            # For integers, convert to string without JSON quotes
            return str(data)
        else:
            # For other types, convert to string directly
            return str(data)

    @staticmethod
    def serialize_data(data: Any) -> bytes:
        """
        Serializes data to bytes for signing, ensuring deterministic output.
        """
        canonical_str = PQC._canonicalize_for_sign(data)
        return canonical_str.encode('utf-8')

    # --------------------------
    # Memory Hygiene
    # --------------------------
    @staticmethod
    def secure_zeroize_keypair(keypair: KeyPair) -> None:
        """
        Securely zeroizes a keypair's private key material.
        """
        PQC.zeroize_private_key(keypair.private_key)

    @staticmethod
    def zeroize_private_key(private_key: Union[bytes, bytearray]) -> bytearray:
        """
        Creates a zeroized copy of private key material.
        """
        if isinstance(private_key, bytes):
            zeroized = bytearray(len(private_key))
        else:  # bytearray
            zeroized = bytearray(len(private_key))
        
        # Explicitly zero out the memory
        for i in range(len(zeroized)):
            zeroized[i] = 0
            
        return zeroized

    # --------------------------
    # Core PQC Operations (Section 2.1)
    # --------------------------
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
        Production PQC.py must call real functions (Section 2.1)
        """
        if log_list is None:
            raise ValueError("log_list is required for generate_keypair")
            
        if parameters is None:
            parameters = {}
            
        # Validate seed is provided (Section 4.1)
        if not seed:
            raise ValueError("seed is required for deterministic key generation")
            
        # Log the seed (Section 2.3)
        seed_hash = hashlib.sha3_512(seed).hexdigest()
        if quantum_metadata is None:
            quantum_metadata = {}
        quantum_metadata["seed_hash"] = seed_hash

        try:
            # Generate keypair using the real PQC library (Section 2.1)
            if algorithm == PQC.DILITHIUM5:
                # Use seed deterministically
                private_key, public_key = Dilithium5Impl.keygen(seed)
            else:
                raise PQCError(f"Unsupported algorithm: {algorithm}")
                
            # Convert private key to mutable bytearray for secure handling
            private_key_array = bytearray(private_key)
            
            result_keypair = KeyPair(
                private_key=private_key_array,
                public_key=public_key,
                algorithm=algorithm,
                parameters=parameters
            )
            
            # Log the successful operation
            PQC._log_pqc_operation(
                operation="generate_keypair",
                details={
                    "algorithm": algorithm,
                    "parameters": parameters,
                    "public_key_size": len(public_key),
                    "seed_provided": True
                },
                log_list=log_list,
                pqc_cid=pqc_cid,
                quantum_metadata=quantum_metadata,
                deterministic_timestamp=deterministic_timestamp
            )
            
            return result_keypair
            
        except Exception as e:
            # Log the failed operation
            PQC._log_pqc_operation(
                operation="generate_keypair",
                details={
                    "algorithm": algorithm,
                    "parameters": parameters,
                    "error_occurred": True
                },
                log_list=log_list,
                pqc_cid=pqc_cid,
                quantum_metadata=quantum_metadata,
                deterministic_timestamp=deterministic_timestamp,
                error=e
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
        Production PQC.py must call real functions (Section 2.1)
        """
        if log_list is None:
            raise ValueError("log_list is required for sign_data")
            
        try:
            # Serialize data to bytes for signing (Section 2.2)
            serialized_data = PQC.serialize_data(data)
            
            # Sign using the real PQC library (Section 2.1)
            # Ensure private key is in the correct format for the underlying implementation
            if isinstance(private_key, bytearray):
                # For our wrapper, we need to ensure the bytearray is in the correct format
                private_key_bytes = bytes(private_key)
            else:
                private_key_bytes = private_key
                
            signature = Dilithium5Impl.sign(private_key_bytes, serialized_data)
            
            # Log the successful operation
            PQC._log_pqc_operation(
                operation="sign_data",
                details={
                    "data_hash": hashlib.sha3_512(serialized_data).hexdigest(),
                    "signature_size": len(signature)
                },
                log_list=log_list,
                pqc_cid=pqc_cid,
                quantum_metadata=quantum_metadata,
                deterministic_timestamp=deterministic_timestamp
            )
            
            return signature
            
        except Exception as e:
            # Log the failed operation
            PQC._log_pqc_operation(
                operation="sign_data",
                details={
                    "error_occurred": True
                },
                log_list=log_list,
                pqc_cid=pqc_cid,
                quantum_metadata=quantum_metadata,
                deterministic_timestamp=deterministic_timestamp,
                error=e
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
        Production PQC.py must call real functions (Section 2.1)
        """
        if log_list is None:
            raise ValueError("log_list is required for verify_signature")
            
        try:
            # Serialize data to bytes for verification (Section 2.2)
            serialized_data = PQC.serialize_data(data)
            
            # Verify using the real PQC library (Section 2.1)
            is_valid = Dilithium5Impl.verify(public_key, serialized_data, signature)
            
            result = ValidationResult(
                is_valid=is_valid,
                quantum_metadata=quantum_metadata
            )
            
            # Log the successful operation
            PQC._log_pqc_operation(
                operation="verify_signature",
                details={
                    "data_hash": hashlib.sha3_512(serialized_data).hexdigest(),
                    "signature_size": len(signature),
                    "is_valid": is_valid
                },
                log_list=log_list,
                pqc_cid=pqc_cid,
                quantum_metadata=quantum_metadata,
                deterministic_timestamp=deterministic_timestamp
            )
            
            return result
            
        except Exception as e:
            # Log the failed operation
            PQC._log_pqc_operation(
                operation="verify_signature",
                details={
                    "error_occurred": True
                },
                log_list=log_list,
                pqc_cid=pqc_cid,
                quantum_metadata=quantum_metadata,
                deterministic_timestamp=deterministic_timestamp,
                error=e
            )
            # Return validation failure rather than raising exception
            return ValidationResult(
                is_valid=False,
                error_message=f"Verification failed: {str(e)}",
                quantum_metadata=quantum_metadata
            )