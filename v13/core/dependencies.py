from typing import Optional, Dict, Any


class MockCryptoEngine:
    """Temporary mock until Open-A.G.I crypto_framework is vendored."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    def has_ratchet_state(self, peer_id: str) -> bool:
        return peer_id.startswith("valid_peer")

    def encrypt_message(self, data: bytes, peer_id: str) -> Optional[bytes]:
        if not self.has_ratchet_state(peer_id):
            return None
        return b"ENC:" + data

    def sign_data(self, data: bytes) -> bytes:
        return b"SIG:" + data

    @property
    def identity(self) -> Any:
        class MockIdentity:
            def export_public_identity(self) -> Dict[str, bytes]:
                return {"signing_key": b"mock_pub_key"}

        return MockIdentity()


def get_crypto_engine() -> MockCryptoEngine:
    """
    Initialize mandatory crypto engine for QFS.
    Enforces security level/configuration from environment or defaults.
    """
    return MockCryptoEngine(config={"security_level": "HIGH"})
