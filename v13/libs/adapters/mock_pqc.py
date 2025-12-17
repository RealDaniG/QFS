"""
Mock PQC - Lightweight Deterministic Mock for Simulation

Zero-Simulation Compliant
"""
import hashlib
from typing import Tuple
from ..interfaces.pqc_interface import PQCInterface

class MockPQC:
    """
    Lightweight mock PQC implementation for deterministic simulation.
    Uses SHA-256 for fast, deterministic operations.
    
    WARNING: NOT CRYPTOGRAPHICALLY SECURE - SIMULATION ONLY
    """

    def keygen(self, seed: bytes) -> Tuple[bytes, bytes]:
        """
        Generate mock keypair from seed.
        
        Uses deterministic hashing to create fake keys.
        """
        if len(seed) != 32:
            raise ValueError(f'Seed must be 32 bytes, got {len(seed)}')
        private_key = hashlib.sha256(b'private_' + seed).digest()
        public_key = hashlib.sha256(b'public_' + seed).digest()
        return (private_key, public_key)

    def sign(self, private_key: bytes, message: bytes) -> bytes:
        """
        Create mock signature.
        
        Simply hashes the private key + message for determinism.
        """
        return hashlib.sha256(private_key + message).digest()

    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        """
        Verify mock signature.
        
        Recomputes expected signature and compares.
        """
        private_key = hashlib.sha256(b'derive_' + public_key).digest()
        expected = self.sign(private_key, message)
        return signature == expected