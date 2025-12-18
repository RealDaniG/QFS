"""
PQC_Core.py - Phase-3 Module 2.1
Production-Ready Post-Quantum Cryptography Core

Zero-Simulation Compliant, Dilithium5 Integration, Deterministic Wrappers
"""
import hashlib
from typing import Any, Optional, Dict, List, Union
from dataclasses import dataclass
try:
    from dilithium import Dilithium as DilithiumBase
    import dilithium

    class Dilithium5Impl:
        """Adapter for dilithium-py Dilithium implementation (Dilithium5 parameters)"""

        @staticmethod
        def keygen(seed: bytes):
            """Generate Dilithium keypair (deterministic with seed)"""
            if len(seed) != 32:
                raise ValueError(f'Seed must be 32 bytes, got {len(seed)}')
            d = DilithiumBase(dilithium.DEFAULT_PARAMETERS['dilithium5'])
            d.set_drbg_seed(seed)
            public_key, private_key = d.keygen()
            return (private_key, public_key)

        @staticmethod
        def sign(private_key: bytes, message: bytes):
            """Sign message with Dilithium private key"""
            d = DilithiumBase(dilithium.DEFAULT_PARAMETERS['dilithium5'])
            return d.sign(private_key, message)

        @staticmethod
        def verify(public_key: bytes, message: bytes, signature: bytes):
            """Verify Dilithium signature"""
            d = DilithiumBase(dilithium.DEFAULT_PARAMETERS['dilithium5'])
            return d.verify(public_key, message, signature)
except (ImportError, Exception) as e:
    Dilithium5Impl = None
from .CanonicalSerializer import CanonicalSerializer
from .PQC_Logger import PQC_Logger

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
    Production-ready, deterministic PQC library for QFS V13 Phase-3.
    Provides Zero-Simulation compliant operations with modular architecture.
    
    Phase-3 Architecture:
    - PQC_Core: Deterministic wrappers around Dilithium5
    - CanonicalSerializer: Deterministic serialization
    - PQC_Logger: Audit logging framework
    - PQC_Audit: Hash generation and export
    - MemoryHygiene: Secure key zeroization
    """
    DILITHIUM5 = 'Dilithium5'
    LogContext = PQC_Logger.LogContext

    @staticmethod
    def generate_keypair(log_list: List[Dict[str, Any]], seed: bytes, algorithm: str=DILITHIUM5, parameters: Optional[Dict[str, Any]]=None, pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0) -> KeyPair:
        """
        Generates a deterministic PQC keypair using the specified algorithm.
        Production PQC.py must call real functions (Section 2.1)
        
        Args:
            log_list: List for audit logging
            seed: Deterministic seed (MUST be 32 bytes for Dilithium5)
            algorithm: PQC algorithm to use
            parameters: Optional algorithm parameters
            pqc_cid: Optional PQC correlation ID
            quantum_metadata: Optional quantum metadata
            deterministic_timestamp: Deterministic timestamp
            
        Returns:
            KeyPair object with private/public keys
            
        Raises:
            PQCValidationError: If seed length is invalid
            PQCError: If keypair generation fails
        """
        if not isinstance(log_list, list):
            raise TypeError('log_list must be a list for deterministic audit logging')
        if not isinstance(deterministic_timestamp, int):
            raise TypeError('deterministic_timestamp must be an int')
        if parameters is None:
            parameters = {}
        if not seed:
            raise ValueError('seed is required for deterministic key generation')
        if len(seed) != 32:
            raise PQCValidationError(f'Dilithium5 deterministic keygen requires 32-byte seed, got {len(seed)} bytes')
        seed_hash = hashlib.sha3_512(seed).hexdigest()
        if quantum_metadata is None:
            quantum_metadata = {}
        quantum_metadata['seed_hash'] = seed_hash
        try:
            if algorithm == PQC.DILITHIUM5:
                private_key, public_key = Dilithium5Impl.keygen(seed)
            else:
                raise PQCError(f'Unsupported algorithm: {algorithm}')
            private_key_array = bytearray(private_key)
            result_keypair = KeyPair(private_key=private_key_array, public_key=public_key, algorithm=algorithm, parameters=parameters)
            PQC_Logger.log_pqc_operation(operation='generate_keypair', details={'algorithm': algorithm, 'parameters': parameters, 'public_key_size': len(public_key), 'seed_provided': True}, log_list=log_list, pqc_cid=pqc_cid, quantum_metadata=quantum_metadata, deterministic_timestamp=deterministic_timestamp)
            return result_keypair
        except Exception as e:
            PQC_Logger.log_pqc_operation(operation='generate_keypair', details={'algorithm': algorithm, 'parameters': parameters, 'error_occurred': True}, log_list=log_list, pqc_cid=pqc_cid, quantum_metadata=quantum_metadata, deterministic_timestamp=deterministic_timestamp, error=e)
            raise PQCError(f'Failed to generate keypair: {str(e)}') from e

    @staticmethod
    def sign_data(private_key: Union[bytes, bytearray], data: Any, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0) -> bytes:
        """
        Signs data using the provided private key.
        Production PQC.py must call real functions (Section 2.1)
        
        Args:
            private_key: Private key for signing
            data: Data to sign
            log_list: List for audit logging
            pqc_cid: Optional PQC correlation ID
            quantum_metadata: Optional quantum metadata
            deterministic_timestamp: Deterministic timestamp
            
        Returns:
            Signature bytes
            
        Raises:
            PQCError: If signing fails
        """
        if not isinstance(log_list, list):
            raise TypeError('log_list must be a list for deterministic audit logging')
        if not isinstance(deterministic_timestamp, int):
            raise TypeError('deterministic_timestamp must be an int')
        try:
            serialized_data = CanonicalSerializer.serialize_data(data)
            if not isinstance(serialized_data, (bytes, bytearray)):
                raise PQCValidationError('CanonicalSerializer.serialize_data must return bytes')
            if isinstance(private_key, bytearray):
                private_key_bytes = bytes(private_key)
            else:
                private_key_bytes = private_key
            signature = Dilithium5Impl.sign(private_key_bytes, serialized_data)
            PQC_Logger.log_pqc_operation(operation='sign_data', details={'data_hash': hashlib.sha3_512(serialized_data).hexdigest(), 'signature_size': len(signature)}, log_list=log_list, pqc_cid=pqc_cid, quantum_metadata=quantum_metadata, deterministic_timestamp=deterministic_timestamp)
            return signature
        except Exception as e:
            PQC_Logger.log_pqc_operation(operation='sign_data', details={'error_occurred': True}, log_list=log_list, pqc_cid=pqc_cid, quantum_metadata=quantum_metadata, deterministic_timestamp=deterministic_timestamp, error=e)
            raise PQCError(f'Failed to sign data: {str(e)}') from e

    @staticmethod
    def verify_signature(public_key: bytes, data: Any, signature: bytes, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0) -> ValidationResult:
        """
        Verifies a signature against data using the provided public key.
        Returns a ValidationResult with verification outcome.
        Production PQC.py must call real functions (Section 2.1)
        
        Args:
            public_key: Public key for verification
            data: Data that was signed
            signature: Signature to verify
            log_list: List for audit logging
            pqc_cid: Optional PQC correlation ID
            quantum_metadata: Optional quantum metadata
            deterministic_timestamp: Deterministic timestamp
            
        Returns:
            ValidationResult with is_valid status
        """
        if not isinstance(log_list, list):
            raise TypeError('log_list must be a list for deterministic audit logging')
        if not isinstance(deterministic_timestamp, int):
            raise TypeError('deterministic_timestamp must be an int')
        if not isinstance(public_key, (bytes, bytearray)):
            raise TypeError('public_key must be bytes or bytearray')
        if not isinstance(signature, (bytes, bytearray)):
            raise TypeError('signature must be bytes or bytearray')
        try:
            serialized_data = CanonicalSerializer.serialize_data(data)
            if not isinstance(serialized_data, (bytes, bytearray)):
                raise PQCValidationError('CanonicalSerializer.serialize_data must return bytes')
            is_valid = Dilithium5Impl.verify(public_key, serialized_data, signature)
            result = ValidationResult(is_valid=is_valid, quantum_metadata=quantum_metadata)
            PQC_Logger.log_pqc_operation(operation='verify_signature', details={'data_hash': hashlib.sha3_512(serialized_data).hexdigest(), 'signature_size': len(signature), 'is_valid': is_valid}, log_list=log_list, pqc_cid=pqc_cid, quantum_metadata=quantum_metadata, deterministic_timestamp=deterministic_timestamp)
            return result
        except Exception as e:
            PQC_Logger.log_pqc_operation(operation='verify_signature', details={'is_valid': False, 'exception': str(e)}, log_list=log_list, pqc_cid=pqc_cid, quantum_metadata=quantum_metadata, deterministic_timestamp=deterministic_timestamp, error=e)
            return ValidationResult(is_valid=False, error_message=str(e), quantum_metadata=quantum_metadata)
