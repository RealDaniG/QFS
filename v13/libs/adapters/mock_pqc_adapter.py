"""
MockPQCAdapter - Adapter for Mock PQC Implementation
Implements PQCInterfaceProtocol using MockPQC from PQC.py
"""
from typing import Tuple
import hashlib
from ..interfaces.pqc_interface import PQCInterface

class MockPQCAdapter(PQCInterface):
    """
    Adapter for the mock PQC implementation (SHA-256 simulation).
    Implements the PQCInterface protocol for testing environments.
    NOT CRYPTOGRAPHICALLY SECURE - for integration testing only.
    """

    def __init__(self):
        """Initialize the mock PQC adapter with a key cache."""
        self._key_cache = {}

    def keygen(self, seed: bytes) -> Tuple[bytes, bytes]:
        """
        Generate a keypair from a seed using SHA-256 simulation.
        
        Args:
            seed: Bytes for key generation (will be padded to 32 bytes if needed)
            
        Returns:
            Tuple of (private_key, public_key) as bytes
        """
        if len(seed) < 32:
            seed = seed + b'\x00' * (32 - len(seed))
        private_key = hashlib.sha256(b'private_' + seed).digest()
        public_key = hashlib.sha256(b'public_' + seed).digest()
        self._key_cache[public_key] = private_key
        return (private_key, public_key)

    def sign(self, private_key: bytes, message: bytes) -> bytes:
        """
        Sign a message with a private key using SHA-256 simulation.
        
        Args:
            private_key: Private key bytes
            message: Message bytes to sign
            
        Returns:
            Signature bytes
        """
        return hashlib.sha256(private_key + message).digest()

    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        """
        Verify a signature against a message and public key using SHA-256 simulation.
        
        Args:
            public_key: Public key bytes
            message: Original message bytes
            signature: Signature to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        private_key = self._key_cache.get(public_key)
        if private_key is None:
            return False
        expected = self.sign(private_key, message)
        return signature == expected
