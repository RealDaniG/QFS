"""
ConcretePQCProvider.py - Concrete implementation of IPQCProvider
Extends the existing PQC implementation with algo_id and PrivKeyHandle support
"""

import hashlib
import json
from typing import Any, Optional, Dict, List, Tuple, Union
from dataclasses import dataclass
from .IPQCProvider import IPQCProvider, PrivKeyHandle, KeyPair, ValidationResult
from .PQC_Core import (
    PQC as LegacyPQC,
    KeyPair as LegacyKeyPair,
    PQCError,
    Dilithium5Impl,
)


class ConcretePQCProvider(IPQCProvider):
    """
    Concrete implementation of IPQCProvider that wraps the existing PQC implementation.
    Adds algo_id and PrivKeyHandle support while maintaining backward compatibility.
    """

    def __init__(self, algorithm: str = IPQCProvider.DILITHIUM5):
        """
        Initialize the concrete PQC provider.

        Args:
            algorithm: Algorithm to use (defaults to Dilithium5)
        """
        self.algorithm = algorithm
        self._algo_map = {
            IPQCProvider.DILITHIUM5: LegacyPQC.DILITHIUM5,
            IPQCProvider.FALCON1024: LegacyPQC.DILITHIUM5,
            IPQCProvider.SPHINCS256: LegacyPQC.DILITHIUM5,
        }
        self._legacy_algo = self._algo_map.get(algorithm, LegacyPQC.DILITHIUM5)
        self._use_mock = Dilithium5Impl is None

    def get_algo_id(self) -> str:
        """
        Get the algorithm identifier for this provider.

        Returns:
            Algorithm identifier string
        """
        return self.algorithm

    def generate_keypair(
        self,
        log_list: List[Dict[str, Any]],
        seed: bytes,
        parameters: Optional[Dict[str, Any]] = None,
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> KeyPair:
        """
        Generates a deterministic PQC keypair using the provider's algorithm.

        Args:
            log_list: List to append audit log entries
            seed: Deterministic seed for key generation
            parameters: Algorithm-specific parameters
            pqc_cid: Correlation ID for tracing
            quantum_metadata: Additional quantum-related metadata
            deterministic_timestamp: Timestamp for deterministic operations

        Returns:
            KeyPair with opaque private key handle

        Raises:
            PQCError: If key generation fails
        """
        if parameters is None:
            parameters = {}
        if self._use_mock:
            return self._generate_mock_keypair(
                log_list,
                seed,
                parameters,
                pqc_cid,
                quantum_metadata,
                deterministic_timestamp,
            )
        try:
            legacy_keypair = LegacyPQC.generate_keypair(
                log_list=log_list,
                seed=seed,
                algorithm=self._legacy_algo,
                parameters=parameters,
                pqc_cid=pqc_cid,
                quantum_metadata=quantum_metadata,
                deterministic_timestamp=deterministic_timestamp,
            )
            handle_id = hashlib.sha256(
                legacy_keypair.public_key + self.algorithm.encode("utf-8")
            ).hexdigest()
            private_key_handle = PrivKeyHandle(
                handle_id=handle_id,
                algo_id=self.algorithm,
                metadata={
                    "legacy_private_key": bytes(legacy_keypair.private_key),
                    "creation_timestamp": deterministic_timestamp,
                    "parameters": parameters,
                },
            )
            return KeyPair(
                private_key_handle=private_key_handle,
                public_key=legacy_keypair.public_key,
                algo_id=self.algorithm,
                parameters=legacy_keypair.parameters,
            )
        except Exception as e:
            raise PQCError(f"Failed to generate keypair: {str(e)}") from e

    def _generate_mock_keypair(
        self,
        log_list: List[Dict[str, Any]],
        seed: bytes,
        parameters: Optional[Dict[str, Any]] = None,
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> KeyPair:
        """Generate a mock keypair when real backend is not available."""
        if len(seed) < 32:
            seed = seed + b"\x00" * (32 - len(seed))
        private_key = hashlib.sha256(b"private_" + seed).digest()
        public_key = hashlib.sha256(b"public_" + seed).digest()
        handle_id = hashlib.sha256(
            public_key + self.algorithm.encode("utf-8")
        ).hexdigest()
        private_key_handle = PrivKeyHandle(
            handle_id=handle_id,
            algo_id=self.algorithm,
            metadata={
                "legacy_private_key": private_key,
                "creation_timestamp": deterministic_timestamp,
                "parameters": parameters or {},
            },
        )
        return KeyPair(
            private_key_handle=private_key_handle,
            public_key=public_key,
            algo_id=self.algorithm,
            parameters=parameters or {},
        )

    def sign_data(
        self,
        private_key_handle: PrivKeyHandle,
        data: Any,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> bytes:
        """
        Signs data using the provided private key handle.

        Args:
            private_key_handle: Opaque handle to private key
            data: Data to sign (will be canonically serialized)
            log_list: List to append audit log entries
            pqc_cid: Correlation ID for tracing
            quantum_metadata: Additional quantum-related metadata
            deterministic_timestamp: Timestamp for deterministic operations

        Returns:
            Signature bytes

        Raises:
            PQCError: If signing fails
        """
        if "legacy_private_key" not in private_key_handle.metadata:
            raise PQCError("Invalid private key handle: missing legacy private key")
        private_key = private_key_handle.metadata["legacy_private_key"]
        if self._use_mock:
            serialized_data = LegacyPQC.serialize_data(data)
            return hashlib.sha256(private_key + serialized_data).digest()
        return LegacyPQC.sign_data(
            private_key=private_key,
            data=data,
            log_list=log_list,
            pqc_cid=pqc_cid,
            quantum_metadata=quantum_metadata,
            deterministic_timestamp=deterministic_timestamp,
        )

    def verify_signature(
        self,
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

        Args:
            public_key: Public key bytes
            data: Data that was signed (will be canonically serialized)
            signature: Signature to verify
            log_list: List to append audit log entries
            pqc_cid: Correlation ID for tracing
            quantum_metadata: Additional quantum-related metadata
            deterministic_timestamp: Timestamp for deterministic operations

        Returns:
            ValidationResult with verification outcome
        """
        if self._use_mock:
            return ValidationResult(
                is_valid=False,
                error_message="Cross-provider verification not supported in mock mode",
                quantum_metadata=quantum_metadata,
            )
        legacy_result = LegacyPQC.verify_signature(
            public_key=public_key,
            data=data,
            signature=signature,
            log_list=log_list,
            pqc_cid=pqc_cid,
            quantum_metadata=quantum_metadata,
            deterministic_timestamp=deterministic_timestamp,
        )
        return ValidationResult(
            is_valid=legacy_result.is_valid,
            error_message=legacy_result.error_message,
            quantum_metadata=legacy_result.quantum_metadata,
        )

    def get_backend_info(self) -> Dict[str, Any]:
        """
        Get information about the currently active PQC backend.

        Returns:
            Dictionary with backend information
        """
        if self._use_mock:
            return {
                "backend": "MockPQC",
                "algo_id": self.algorithm,
                "algorithm": "SHA-256 (simulation only)",
                "security_level": "NONE - NOT CRYPTOGRAPHICALLY SECURE",
                "production_ready": False,
                "quantum_resistant": False,
                "deterministic": True,
                "warning": "INTEGRATION TESTING ONLY - DO NOT USE IN PRODUCTION",
            }
        legacy_info = LegacyPQC.get_backend_info()
        legacy_info["algo_id"] = self.algorithm
        return legacy_info


class MockPQCProvider(ConcretePQCProvider):
    """
    Deterministic mock PQC provider for DEV and tests.
    Uses SHA-256 simulation for consistent, predictable results.
    """

    def __init__(self, algorithm: str = IPQCProvider.DILITHIUM5):
        """
        Initialize the mock PQC provider.

        Args:
            algorithm: Algorithm to simulate (defaults to Dilithium5)
        """
        super().__init__(algorithm)
        self._use_mock = True
        self._key_cache = {}

    def generate_keypair(
        self,
        log_list: List[Dict[str, Any]],
        seed: bytes,
        parameters: Optional[Dict[str, Any]] = None,
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> KeyPair:
        """
        Generates a deterministic mock keypair.
        """
        if parameters is None:
            parameters = {}
        if len(seed) < 32:
            seed = seed + b"\x00" * (32 - len(seed))
        private_key = hashlib.sha256(b"private_" + seed).digest()
        public_key = hashlib.sha256(b"public_" + seed).digest()
        self._key_cache[public_key] = private_key
        handle_id = hashlib.sha256(
            public_key + self.algorithm.encode("utf-8")
        ).hexdigest()
        private_key_handle = PrivKeyHandle(
            handle_id=handle_id,
            algo_id=self.algorithm,
            metadata={
                "legacy_private_key": private_key,
                "creation_timestamp": deterministic_timestamp,
                "parameters": parameters,
            },
        )
        if log_list is not None:
            log_entry = {
                "operation": "generate_keypair",
                "algorithm": self.algorithm,
                "timestamp": deterministic_timestamp,
                "pqc_cid": pqc_cid,
            }
            log_list.append(log_entry)
        return KeyPair(
            private_key_handle=private_key_handle,
            public_key=public_key,
            algo_id=self.algorithm,
            parameters=parameters,
        )

    def sign_data(
        self,
        private_key_handle: PrivKeyHandle,
        data: Any,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> bytes:
        """
        Signs data using deterministic SHA-256.
        """
        if "legacy_private_key" not in private_key_handle.metadata:
            raise PQCError("Invalid private key handle: missing legacy private key")
        private_key = private_key_handle.metadata["legacy_private_key"]
        serialized_data = LegacyPQC.serialize_data(data)
        signature = hashlib.sha256(private_key + serialized_data).digest()
        if log_list is not None:
            log_entry = {
                "operation": "sign_data",
                "algorithm": self.algorithm,
                "timestamp": deterministic_timestamp,
                "pqc_cid": pqc_cid,
            }
            log_list.append(log_entry)
        return signature

    def verify_signature(
        self,
        public_key: bytes,
        data: Any,
        signature: bytes,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> ValidationResult:
        """
        Verifies a signature using deterministic SHA-256.
        """
        private_key = self._key_cache.get(public_key)
        if private_key is None:
            if log_list is not None:
                log_entry = {
                    "operation": "verify_signature",
                    "algorithm": self.algorithm,
                    "timestamp": deterministic_timestamp,
                    "pqc_cid": pqc_cid,
                    "result": "failed",
                    "reason": "key_not_found",
                }
                log_list.append(log_entry)
            return ValidationResult(
                is_valid=False,
                error_message="Public key not found in cache",
                quantum_metadata=quantum_metadata,
            )
        serialized_data = LegacyPQC.serialize_data(data)
        expected = hashlib.sha256(private_key + serialized_data).digest()
        is_valid = signature == expected
        if log_list is not None:
            log_entry = {
                "operation": "verify_signature",
                "algorithm": self.algorithm,
                "timestamp": deterministic_timestamp,
                "pqc_cid": pqc_cid,
                "result": "success" if is_valid else "failed",
            }
            log_list.append(log_entry)
        return ValidationResult(is_valid=is_valid, quantum_metadata=quantum_metadata)

    def get_backend_info(self) -> Dict[str, Any]:
        """
        Get information about the mock PQC backend.
        """
        return {
            "backend": "MockPQC",
            "algo_id": self.algorithm,
            "algorithm": "SHA-256 (simulation only)",
            "security_level": "NONE - NOT CRYPTOGRAPHICALLY SECURE",
            "production_ready": False,
            "quantum_resistant": False,
            "deterministic": True,
            "warning": "INTEGRATION TESTING ONLY - DO NOT USE IN PRODUCTION",
        }
