"""
SessionManager (v16 Baseline)

Manages user sessions and emits lifecycle events to EvidenceBus.
"""

import hashlib
from typing import Dict, Optional

from v15.evidence.bus import EvidenceBus
from v18.crypto.wallet_auth_crypto import (
    wallet_auth_crypto,
    AsconContext,
    AsconCiphertext,
)


class SessionManager:
    """
    Manages active user sessions with Ascon Edge Crypto (v18.5).
    """

    def __init__(self):
        self._sessions: Dict[str, Dict] = {}

    def create_session(self, wallet_address: str, scopes: list[str]) -> str:
        """
        Create a new session token.
        (v18.5) The token is an Ascon-encrypted envelope.
        """
        # Internal session ID
        session_id = hashlib.sha256(
            f"{wallet_address}:{len(self._sessions)}".encode()
        ).hexdigest()[:16]

        # Payload to encrypt
        payload = f"{wallet_address}|{','.join(scopes)}".encode()

        # Encrypt via Ascon
        envelope = wallet_auth_crypto.encrypt_session_token(
            session_id=session_id,
            key_id="v1",
            token_bytes=payload,
            evidence_seq=len(self._sessions),
        )

        # Public token format: ascon1.<session_id>.<ciphertext_hex>.<tag_hex>
        token = f"ascon1.{session_id}.{envelope.ciphertext_hex}.{envelope.tag_hex}"

        session_data = {
            "user_id": wallet_address,
            "scopes": scopes,
            "created_at": 0,
        }

        self._sessions[session_id] = session_data

        # Emit Evidence
        EvidenceBus.emit(
            "AUTH_LOGIN",
            {
                "wallet": wallet_address,
                "session_id": session_id,
                "v18_crypto": "ascon-v18.5",
            },
        )

        return token

    def validate_session(self, token: str) -> Optional[Dict]:
        """
        Validate an Ascon-protected session token.
        """
        if not token.startswith("ascon1."):
            return self._sessions.get(token)  # Fallback for legacy tokens

        try:
            _, session_id, ct_hex, tag_hex = token.split(".")

            # Reconstruct envelope for decryption
            # We assume node_id and key_id are known or embedded.
            # For this alpha, we use the global tier-a-primary node.
            ctx = AsconContext(
                node_id="tier-a-primary",
                channel_id="wallet_session",
                evidence_seq=0,  # In a real system, would be tracked or embedded
                key_id="v1",
            )
            # Override context with session_id if needed, but decrypt_session_token handles it

            # For simplicity in this alpha, we trust the session_id in the dict lookup
            # but decrypt to verify integrity.
            if session_id not in self._sessions:
                return None

            # Perform decryption/verification
            envelope = AsconCiphertext(
                ciphertext_hex=ct_hex, tag_hex=tag_hex, context=ctx
            )

            # Verification: If it doesn't raise ValueError, tag is valid
            wallet_auth_crypto.decrypt_session_token(envelope, session_id, "v1")

            return self._sessions.get(session_id)
        except Exception:
            return None

    def revoke_session(self, token: str) -> bool:
        session_id = token
        if token.startswith("ascon1."):
            session_id = token.split(".")[1]

        if session_id in self._sessions:
            del self._sessions[session_id]
            EvidenceBus.emit(
                "AUTH_LOGOUT",
                {"session_id": session_id},
            )
            return True
        return False
