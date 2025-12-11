"""
PQC Interface - Abstract PQC Operations for Swappable Implementations

Zero-Simulation Compliant
"""

from typing import Protocol, Tuple


class PQCInterface(Protocol):
    """
    Abstract interface for Post-Quantum Cryptography operations.
    Allows swapping between production (Dilithium5) and simulation (Mock) implementations.
    
    All implementations MUST be deterministic given the same seed.
    """
    
    def keygen(self, seed: bytes) -> Tuple[bytes, bytes]:
        """
        Generate a keypair from a 32-byte deterministic seed.
        
        Args:
            seed: Exactly 32 bytes for deterministic key generation
            
        Returns:
            Tuple of (private_key, public_key) as bytes
            
        Raises:
            ValueError: If seed is not exactly 32 bytes
            
        Deterministic Guarantee:
            Same seed → same keypair across all runs and nodes
        """
        ...
    
    def sign(self, private_key: bytes, message: bytes) -> bytes:
        """
        Sign a message with a private key.
        
        Args:
            private_key: Private key bytes
            message: Message bytes to sign
            
        Returns:
            Signature bytes
            
        Deterministic Guarantee:
            Same (private_key, message) → same signature
        """
        ...
    
    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        """
        Verify a signature against a message and public key.
        
        Args:
            public_key: Public key bytes
            message: Original message bytes
            signature: Signature to verify
            
        Returns:
            True if signature is valid, False otherwise
            
        Deterministic Guarantee:
            Same inputs → same verification result
        """
        ...
