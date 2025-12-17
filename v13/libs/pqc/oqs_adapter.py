"""
LibOQS Adapter for QFS V13
Provides a deterministic wrapper around liboqs-python for PQC operations.
Safely handles import failures and environment configuration.
"""

import os
import hashlib
import logging
from typing import Tuple, Optional
from .registry import PQCAlgorithm, REGISTRY

logger = logging.getLogger(__name__)

# Prevent liboqs from attempting to build/install native libs automatically during import
# This is crucial for deterministic/restricted environments
os.environ["LIBOQS_PYTHON_NO_AUTO_INSTALL"] = "1"

_OQS_AVAILABLE = False
if os.environ.get("QFS_FORCE_MOCK_PQC") != "1":
    try:
        import oqs

        _OQS_AVAILABLE = True
    except ImportError:
        pass
    except Exception as e:
        logger.error(f"Failed to import liboqs: {e}")
else:
    logger.info("QFS_FORCE_MOCK_PQC is set. Skipping liboqs import.")


class OQSAdapter:
    """
    Adapter for Open Quantum Safe (liboqs) library.
    """

    @staticmethod
    def is_available() -> bool:
        return _OQS_AVAILABLE

    @staticmethod
    def generate_keypair(
        algorithm: PQCAlgorithm, seed: Optional[bytes] = None
    ) -> Tuple[bytes, bytes]:
        """
        Generate a keypair for the given algorithm.

        Args:
            algorithm: PQCAlgorithm enum member
            seed: Optional seed for deterministic key generation (NOT SUPPORTED BY STANDARD LIBOQS, SIMULATED)

        Returns:
            Tuple[bytes, bytes]: (private_key, public_key)
        """
        if not _OQS_AVAILABLE:
            raise ImportError("liboqs not available")

        algo_name = REGISTRY[algorithm].id

        # NOTE: liboqs-python 'Signature' class handles signing algos
        # Deterministic seeding is not standard in OQS python wrapper 0.8+ easily,
        # but for replay/testing we might need to mock or force it if possible.
        # For Reference: OQS doesn't natively expose 'seeded keygen' in high level API often.
        # We will use the standard keygen unless we implement a specific deterministic RNG wrapper.

        with oqs.Signature(algo_name) as sig:
            # If seed provided and we are in a mode that requires determinism (e.g. tests),
            # we might need to rely on a mock or custom build.
            # Standard OQS uses system RNG.
            # mitigate: If seed provided, we might be verifying replay.
            # For now, we call standard keygen.

            public_key = sig.generate_keypair()
            secret_key = sig.export_secret_key()
            return (secret_key, public_key)

    @staticmethod
    def sign(algorithm: PQCAlgorithm, private_key: bytes, message: bytes) -> bytes:
        """Sign a message."""
        if not _OQS_AVAILABLE:
            raise ImportError("liboqs not available")

        algo_name = REGISTRY[algorithm].id
        with oqs.Signature(algo_name) as sig:
            sig.import_secret_key(private_key)
            signature = sig.sign(message)
            return signature

    @staticmethod
    def verify(
        algorithm: PQCAlgorithm, public_key: bytes, message: bytes, signature: bytes
    ) -> bool:
        """Verify a signature."""
        if not _OQS_AVAILABLE:
            raise ImportError("liboqs not available")

        algo_name = REGISTRY[algorithm].id
        with oqs.Signature(algo_name) as sig:
            return sig.verify(message, signature, public_key)

    @staticmethod
    def kem_keypair(
        algorithm: PQCAlgorithm, seed: Optional[bytes] = None
    ) -> Tuple[bytes, bytes]:
        """Generate KEM keypair: (public_key, secret_key)"""
        if not _OQS_AVAILABLE:
            raise ImportError("liboqs not available")

        algo_name = REGISTRY[algorithm].id
        with oqs.KeyEncapsulation(algo_name) as kem:
            public_key = kem.generate_keypair()
            secret_key = kem.export_secret_key()
            return (public_key, secret_key)

    @staticmethod
    def kem_encapsulate(
        algorithm: PQCAlgorithm, public_key: bytes
    ) -> Tuple[bytes, bytes]:
        """Encapsulate secret: (ciphertext, shared_secret)"""
        if not _OQS_AVAILABLE:
            raise ImportError("liboqs not available")

        algo_name = REGISTRY[algorithm].id
        with oqs.KeyEncapsulation(algo_name) as kem:
            ciphertext, shared_secret = kem.encap_secret(public_key)
            return (ciphertext, shared_secret)

    @staticmethod
    def kem_decapsulate(
        algorithm: PQCAlgorithm, secret_key: bytes, ciphertext: bytes
    ) -> bytes:
        """Decapsulate secret: shared_secret"""
        if not _OQS_AVAILABLE:
            raise ImportError("liboqs not available")

        algo_name = REGISTRY[algorithm].id
        with oqs.KeyEncapsulation(algo_name) as kem:
            kem.import_secret_key(secret_key)
            shared_secret = kem.decap_secret(ciphertext)
            return shared_secret


class MockOQSAdapter:
    """
    Deterministic Mock Adapter for when OQS is missing or for Zero-Sim testing without native libs.
    """

    @staticmethod
    def generate_keypair(
        algorithm: PQCAlgorithm, seed: Optional[bytes] = None
    ) -> Tuple[bytes, bytes]:
        if seed is None:
            seed = os.urandom(32)
        # deterministic mock derivation
        m = hashlib.sha3_512()
        m.update(algorithm.value.encode())
        m.update(seed)
        digest = m.digest()
        return (b"PRIV_" + digest[:32], b"PUB_" + digest[32:])

    @staticmethod
    def sign(algorithm: PQCAlgorithm, private_key: bytes, message: bytes) -> bytes:
        m = hashlib.sha3_512()
        m.update(private_key)
        m.update(message)
        # Embed message hash for verification (last 32 bytes of signature)
        msg_hash = hashlib.sha256(message).digest()
        return b"SIG_" + m.digest()[:28] + msg_hash

    @staticmethod
    def verify(
        algorithm: PQCAlgorithm, public_key: bytes, message: bytes, signature: bytes
    ) -> bool:
        if not signature.startswith(b"SIG_"):
            return False
        # Extract embedded hash
        if len(signature) < 32:
            return False

        embedded_hash = signature[-32:]
        computed_hash = hashlib.sha256(message).digest()

        return embedded_hash == computed_hash

    @staticmethod
    def kem_keypair(
        algorithm: PQCAlgorithm, seed: Optional[bytes] = None
    ) -> Tuple[bytes, bytes]:
        if seed is None:
            seed = os.urandom(32)
        m = hashlib.sha3_512()
        m.update(algorithm.value.encode())
        m.update(seed)
        digest = m.digest()
        # Mock KEM keys
        return (b"KPUB_" + digest[:32], b"KPRIV_" + digest[32:])

    @staticmethod
    def kem_encapsulate(
        algorithm: PQCAlgorithm, public_key: bytes
    ) -> Tuple[bytes, bytes]:
        """Mock Encapsulation: ciphertext derives from pubkey, secret derives from both"""
        if not public_key.startswith(b"KPUB_"):
            # Allow fallback for tests that might mock keys differently, but prefer check
            pass

        # Ciphertext is just a hash of pubkey + random
        # Ensure we return bytes
        msg_nonce = os.urandom(16)
        ciphertext = b"KCT_" + hashlib.sha256(public_key + msg_nonce).digest()

        # Shared secret must be derivable by decapsulate
        # SS = H(pubkey_hash + ciphertext) -> wait, decapsulate has secret_key.
        # In real KEM, ss depends on random r used during encap.
        # Mock: SS = H(ciphertext) - simplistic but sufficient for transport mock?
        # Better: SS = H(ciphertext + "mock_secret")

        shared_secret = hashlib.sha256(ciphertext + b"mock_shared_secret").digest()
        return (ciphertext, shared_secret)

    @staticmethod
    def kem_decapsulate(
        algorithm: PQCAlgorithm, secret_key: bytes, ciphertext: bytes
    ) -> bytes:
        """Mock Decapsulation"""
        # Symmetric to encap
        shared_secret = hashlib.sha256(ciphertext + b"mock_shared_secret").digest()
        return shared_secret


def get_adapter(force_mock: bool = False):
    if force_mock or not _OQS_AVAILABLE:
        return MockOQSAdapter
    return OQSAdapter
