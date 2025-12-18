"""
IPQCProvider.py - Interface for Post-Quantum Cryptography Provider
Defines the contract for PQC implementations in QFS V13.8+
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Tuple, Union
from dataclasses import dataclass

@dataclass
class PrivKeyHandle:
    """
    Opaque handle for private key material.
    Ensures private keys are never exposed as raw bytes in core logic.
    """
    handle_id: str
    algo_id: str
    metadata: Dict[str, Any]

@dataclass
class KeyPair:
    """Container for PQC key pair with opaque private key handle."""
    private_key_handle: PrivKeyHandle
    public_key: bytes
    algo_id: str
    parameters: Dict[str, Any]

@dataclass
class ValidationResult:
    """Result of a PQC validation operation."""
    is_valid: bool
    error_message: Optional[str] = None
    quantum_metadata: Optional[Dict[str, Any]] = None

class IPQCProvider(ABC):
    """
    Interface for Post-Quantum Cryptography providers.
    All PQC implementations must conform to this interface.
    """
    DILITHIUM5 = 'Dilithium5'
    FALCON1024 = 'Falcon1024'
    SPHINCS256 = 'SPHINCS+256'

    @abstractmethod
    def get_algo_id(self) -> str:
        """
        Get the algorithm identifier for this provider.
        
        Returns:
            Algorithm identifier string
        """
        pass

    @abstractmethod
    def generate_keypair(self, log_list: List[Dict[str, Any]], seed: bytes, parameters: Optional[Dict[str, Any]]=None, pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0) -> KeyPair:
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
        pass

    @abstractmethod
    def sign_data(self, private_key_handle: PrivKeyHandle, data: Any, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0) -> bytes:
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
        pass

    @abstractmethod
    def verify_signature(self, public_key: bytes, data: Any, signature: bytes, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0) -> ValidationResult:
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
        pass

    @abstractmethod
    def get_backend_info(self) -> Dict[str, Any]:
        """
        Get information about the currently active PQC backend.
        
        Returns:
            Dictionary with backend information including:
                - backend: Backend name
                - algorithm: Algorithm name
                - security_level: Security level description
                - production_ready: Whether backend is production-ready
                - quantum_resistant: Whether algorithm is quantum-resistant
                - deterministic: Whether operations are deterministic
        """
        pass
