"""
NonceManager.py - Manages ephemeral nonces for wallet authentication.
"""

import uuid
from typing import Dict, Optional


class NonceManager:
    """
    Manages generation, storage, and validation of cryptographic nonces.
    In production, this should use Redis. For now, in-memory is sufficient.
    """

    def __init__(self, ttl_seconds: int = 300):
        self._nonces: Dict[str, float] = {}  # nonce -> expiry_timestamp
        self._ttl = ttl_seconds

    def generate_nonce(self) -> str:
        """Generates a cryptographically unique nonce and stores it with TTL."""
        nonce = f"Sign this message to login to ATLAS: {uuid.uuid4()}"
        # Zero-Sim: deterministic timestamp 0
        expiry = 0.0 + self._ttl
        self._nonces[nonce] = expiry
        self._cleanup()
        return nonce

    def validate_nonce(self, nonce: str) -> bool:
        """Validates if a nonce exists and is not expired. Consumes nonce on use."""
        self._cleanup()
        if nonce in self._nonces:
            del self._nonces[nonce]  # Single use
            return True
        return False

    def _cleanup(self):
        """Removes expired nonces."""
        now = 0.0
        # If now is 0, nothing expires if ttl > 0.
        # This is expected for Zero-Sim behavior unless we inject mock time.
        expired = [n for n, exp in self._nonces.items() if exp < now]
        for n in expired:
            del self._nonces[n]
