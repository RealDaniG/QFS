"""
MOCKPQC Key Management - Placeholder for Real PQC
Deterministic "signatures" using hashes (no real crypto).
"""

from dataclasses import dataclass
import hashlib
from typing import Optional, Dict, Any


@dataclass
class MockPQCKey:
    """
    Placeholder PQC key record.
    Will be replaced with real Dilithium/SPHINCS+ in future.
    """

    key_id: str
    public_stub: str  # Placeholder public key
    derivation_seed_ref: str  # Reference to EvidenceBus seed event
    created_at: int

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage."""
        return {
            "key_id": self.key_id,
            "public_stub": self.public_stub,
            "derivation_seed_ref": self.derivation_seed_ref,
            "created_at": self.created_at,
        }


class MockPQCProvider:
    """
    Deterministic "PQC" operations using hashes.
    NOT SECURE - For schema rehearsal only.
    """

    @staticmethod
    def generate_key(wallet_address: str, seed_ref: str, timestamp: int) -> MockPQCKey:
        """
        Generate deterministic MOCKPQC key.

        Args:
            wallet_address: Owner's wallet
            seed_ref: Reference to deterministic seed in EvidenceBus
            timestamp: Creation time

        Returns:
            MockPQCKey instance
        """
        # Deterministic key ID
        key_id = hashlib.sha3_256(
            f"{wallet_address}||{seed_ref}||{timestamp}".encode()
        ).hexdigest()[:32]

        # Placeholder "public key"
        public_stub = hashlib.sha3_512(f"MOCKPQC_PUB||{key_id}".encode()).hexdigest()

        return MockPQCKey(
            key_id=key_id,
            public_stub=public_stub,
            derivation_seed_ref=seed_ref,
            created_at=timestamp,
        )

    @staticmethod
    def sign(key: MockPQCKey, message: str) -> str:
        """
        "Sign" message with MOCKPQC (deterministic hash).

        Args:
            key: MockPQCKey
            message: Message to "sign"

        Returns:
            Deterministic "signature" (hash)
        """
        signature_input = f"{key.key_id}||{key.public_stub}||{message}"
        signature = hashlib.sha3_512(signature_input.encode()).hexdigest()
        return signature

    @staticmethod
    def verify(key: MockPQCKey, message: str, signature: str) -> bool:
        """
        Verify MOCKPQC "signature".

        Args:
            key: MockPQCKey
            message: Original message
            signature: Signature to verify

        Returns:
            True if valid
        """
        expected_signature = MockPQCProvider.sign(key, message)
        return signature == expected_signature
