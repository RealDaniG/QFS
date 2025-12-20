from typing import Optional, Any
from .ascon_adapter import ascon_adapter, AsconContext, AsconCiphertext, AsconDigest


class WalletAuthCryptoAdapter:
    """
    Specialized Ascon adapter for wallet session and authentication security.
    Implements Phase 1 of the v18.5 Ascon Integration Plan.
    """

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.ascon_adapter = ascon_adapter

    def encrypt_session_token(
        self, session_id: str, key_id: str, token_bytes: bytes, evidence_seq: int = 0
    ) -> AsconCiphertext:
        """Encrypts a session token using deterministic Ascon AEAD."""
        context = AsconContext(
            node_id=self.node_id,
            channel_id="wallet_session",
            evidence_seq=evidence_seq,
            key_id=key_id,
        )
        key = self._derive_session_key(session_id, key_id)
        return ascon_adapter.ascon_aead_encrypt(context, token_bytes, b"wallet_v1", key)

    def decrypt_session_token(
        self, ciphertext: AsconCiphertext, session_id: str, key_id: str
    ) -> bytes:
        """Decrypts and verifies a session token."""
        key = self._derive_session_key(session_id, key_id)
        return ascon_adapter.ascon_aead_decrypt(
            ciphertext.context, ciphertext, b"wallet_v1", key
        )

    def hash_challenge(self, session_id: str, challenge_bytes: bytes) -> AsconDigest:
        """Computes a deterministic digest for an auth challenge."""
        context = AsconContext(
            node_id=self.node_id,
            channel_id="auth_challenge",
            evidence_seq=0,
            key_id="none",
        )
        return ascon_adapter.ascon_hash(context, session_id.encode() + challenge_bytes)

    def _derive_session_key(self, session_id: str, key_id: str) -> bytes:
        """
        Deterministic hierarchical key derivation.
        In production, this would use a HSM-backed master key.
        """
        import hashlib

        base = f"session_master:{self.node_id}:{key_id}:{session_id}"
        return hashlib.sha3_256(base.encode()).digest()[:16]


# Global instance for Tier A
wallet_auth_crypto = WalletAuthCryptoAdapter(node_id="tier-a-primary")
