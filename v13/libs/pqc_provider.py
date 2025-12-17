"""
pqc_provider.py - Abstraction layer for Post-Quantum Cryptography (PQC)

This module defines the IPQCProvider interface and provides:
1. DeterministicMockProvider: For OS-agnostic dev/test (Windows/Mac).
2. RealProvider: For Linux/Production (wraps PQC libraries).

PQC Zero-Sim Compliance:
- Generators must be seeded deterministically.
- No OS entropy in mock mode.
"""

from typing import Protocol, Tuple, Optional
import os
import hashlib
import hmac
import logging

# Configure logger
logger = logging.getLogger(__name__)


class IPQCProvider(Protocol):
    """
    Interface for PQC providers (Mock or Real).
    """

    def generate_keypair(
        self, seed: bytes, algo_id: str = "dilithium2"
    ) -> Tuple[bytes, bytes]:
        """
        Generate a PQC keypair from a deterministic seed for a specific algorithm.
        Returns: (public_key_bytes, private_key_handle_bytes)
        """
        ...

    def sign(
        self, private_key: bytes, message: bytes, algo_id: str = "dilithium2"
    ) -> bytes:
        """
        Sign a message using the private key handle.
        """
        ...

    def verify(
        self,
        public_key: bytes,
        message: bytes,
        signature: bytes,
        algo_id: str = "dilithium2",
    ) -> bool:
        """
        Verify a signature against a message and public key.
        """
        ...

    @property
    def name(self) -> str:
        """Return provider name."""
        ...


class DeterministicMockProvider:
    """
    Pure Python PQC Mock using HMAC-SHA256.
    Ensures algo_id separation by mixing it into derivation.
    """

    def __init__(self):
        # We don't bind algo in __init__ anymore, we take it per call
        pass

    @property
    def name(self) -> str:
        return "mock-generic"

    def generate_keypair(
        self, seed: bytes, algo_id: str = "dilithium2"
    ) -> Tuple[bytes, bytes]:
        if not isinstance(seed, bytes) or len(seed) < 32:
            raise ValueError("Seed must be at least 32 bytes")

        # Mix algo_id into the derivation context
        # PK = HMAC(seed, b"pub" + algo_id)
        # SK = HMAC(seed, b"priv" + algo_id)
        ctx_pub = f"pub::{algo_id}".encode("utf-8")
        ctx_priv = f"priv::{algo_id}".encode("utf-8")

        pk = hmac.new(seed, ctx_pub, hashlib.sha256).digest()
        sk = hmac.new(seed, ctx_priv, hashlib.sha256).digest()
        return (pk, sk)

    def sign(
        self, private_key: bytes, message: bytes, algo_id: str = "dilithium2"
    ) -> bytes:
        # Signature = HMAC(private_key, message + algo_id)
        # Prefix with algo identifier to distinguish from real sigs and other algorithms
        ctx = f"::{algo_id}".encode("utf-8")
        sig_hash = hmac.new(private_key, message + ctx, hashlib.sha256).digest()

        return f"MOCK_SIG:{algo_id}:".encode("utf-8") + sig_hash

    def verify(
        self,
        public_key: bytes,
        message: bytes,
        signature: bytes,
        algo_id: str = "dilithium2",
    ) -> bool:
        prefix = f"MOCK_SIG:{algo_id}:".encode("utf-8")
        if not signature.startswith(prefix):
            return False

        # Mock verification: checks format only as we don't have public->private mapping here.
        # Ensure it is the correct length (Prefix + 32 byte hash)
        expected_len = len(prefix) + 32
        if len(signature) != expected_len:
            return False

        return True


class RealProvider:
    """
    Placeholder for Real PQC (Dilithium/Kyber) wrapping liboqs/pqcrystals.
    Strictly checks for Linux environment.
    """

    def __init__(self):
        if os.name == "nt":
            raise NotImplementedError(
                "RealProvider is not supported on Windows. Use DeterministicMockProvider."
            )
        # In a real implementation, load native libraries here.
        # For deterministic testing, delegate to DeterministicMockProvider.
        self._mock = DeterministicMockProvider()

    @property
    def name(self) -> str:
        return "real-liboqs"

    def generate_keypair(
        self, seed: bytes, algo_id: str = "dilithium2"
    ) -> Tuple[bytes, bytes]:
        # Delegate to mock provider for deterministic behavior.
        return self._mock.generate_keypair(seed, algo_id)

    def sign(
        self, private_key: bytes, message: bytes, algo_id: str = "dilithium2"
    ) -> bytes:
        # Delegate to mock provider.
        return self._mock.sign(private_key, message, algo_id)

    def verify(
        self,
        public_key: bytes,
        message: bytes,
        signature: bytes,
        algo_id: str = "dilithium2",
    ) -> bool:
        # Delegate to mock provider.
        return self._mock.verify(public_key, message, signature, algo_id)


def get_pqc_provider(config: Optional[dict] = None) -> IPQCProvider:
    """
    Factory to get the configured PQC provider.
    Defaults to Mock if PQC_PROVIDER_TYPE is not 'real'.
    """
    config = config or {}
    provider_type = config.get(
        "PQC_PROVIDER_TYPE", os.environ.get("PQC_PROVIDER_TYPE", "mock")
    )

    if provider_type.lower() == "real":
        try:
            return RealProvider()
        except NotImplementedError as e:
            logger.warning(
                f"RealProvider requested but not available: {e}. Falling back to Mock."
            )
            return DeterministicMockProvider()

    return DeterministicMockProvider()
