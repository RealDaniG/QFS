"""
SessionManager (v18.5 Stateless)

Manages user sessions with Ascon-protected stateless tokens.
Tokens are self-contained and can be validated on any cluster node.
"""

import hashlib
import time
import json
from typing import Dict, Optional, TypedDict

from v15.evidence.bus import EvidenceBus
from v18.crypto.wallet_auth_crypto import (
    wallet_auth_crypto,
    AsconContext,
    AsconCiphertext,
)


class SessionData(TypedDict):
    wallet_address: str
    created_at: float
    expires_at: float
    scopes: list[str]


class SessionManager:
    """
    Manages active user sessions with Ascon Edge Crypto (v18.5).

    STATELESS DESIGN (v18.9 Multi-Node Ready):
    - All session data embedded in encrypted token payload
    - No server-side session storage required for validation
    - Tokens validated by any node with same key_id
    - Optional revocation list for early termination
    """

    def __init__(self, session_ttl_seconds: int = 3600 * 24):
        self._ttl = session_ttl_seconds
        # Optional revocation list (session_id -> revocation timestamp)
        # This allows early termination without breaking stateless validation
        self._revoked: Dict[str, float] = {}
        self._token_counter = 0  # For deterministic session IDs

    def create_session(self, wallet_address: str, scopes: list[str]) -> str:
        """
        Create a stateless session token.

        Token contains all session data in encrypted payload:
        - wallet_address: User identity
        - scopes: Authorization grants
        - created_at: Issuance timestamp
        - expires_at: Expiry timestamp

        Format: ascon1.<session_id>.<ciphertext_hex>.<tag_hex>
        """
        # Deterministic session ID (for revocation tracking and nonce derivation)
        session_id = hashlib.sha256(
            f"{wallet_address}:{self._token_counter}:{time.time()}".encode()
        ).hexdigest()[:16]
        self._token_counter += 1

        # Timestamps
        now = time.time()
        expires_at = now + self._ttl

        # Session data to embed in token
        session_data: SessionData = {
            "wallet_address": wallet_address,
            "scopes": scopes,
            "created_at": now,
            "expires_at": expires_at,
        }

        # Serialize to JSON (deterministic field ordering)
        payload = json.dumps(
            session_data, sort_keys=True, separators=(",", ":")
        ).encode()

        # Encrypt via Ascon with deterministic context
        envelope = wallet_auth_crypto.encrypt_session_token(
            session_id=session_id,
            key_id="v1",
            token_bytes=payload,
            evidence_seq=self._token_counter - 1,
        )

        # Public token format: ascon1.<session_id>.<ciphertext_hex>.<tag_hex>
        token = f"ascon1.{session_id}.{envelope.ciphertext_hex}.{envelope.tag_hex}"

        # Emit Evidence
        EvidenceBus.emit(
            "AUTH_LOGIN",
            {
                "wallet": wallet_address,
                "session_id": session_id,
                "v18_crypto": "ascon-v18.5",
                "stateless": True,
            },
        )

        return token

    def validate_session(self, token: str) -> Optional[SessionData]:
        """
        Validate a stateless Ascon-protected session token.

        Validation steps:
        1. Parse token format
        2. Decrypt and verify AEAD tag
        3. Deserialize claims
        4. Check expiry
        5. Check revocation list (optional)

        No server-side session lookup required.
        """
        self._cleanup_revocations()

        if not token.startswith("ascon1."):
            return None  # Invalid token format

        try:
            parts = token.split(".")
            if len(parts) != 4:
                return None

            _, session_id, ct_hex, tag_hex = parts

            # Check revocation list first (fast path)
            if session_id in self._revoked:
                return None

            # Reconstruct context for decryption
            ctx = AsconContext(
                node_id="tier-a-primary",
                channel_id="wallet_session",
                evidence_seq=0,  # Not used for stateless validation
                key_id="v1",
            )

            # Perform decryption/verification
            envelope = AsconCiphertext(
                ciphertext_hex=ct_hex, tag_hex=tag_hex, context=ctx
            )

            # Decrypt and verify tag
            plaintext = wallet_auth_crypto.decrypt_session_token(
                envelope, session_id, "v1"
            )

            # Deserialize claims
            session_data = json.loads(plaintext.decode())

            # Validate expiry
            if session_data["expires_at"] < time.time():
                return None

            # Return typed session data
            return SessionData(
                wallet_address=session_data["wallet_address"],
                scopes=session_data["scopes"],
                created_at=session_data["created_at"],
                expires_at=session_data["expires_at"],
            )

        except (ValueError, KeyError, json.JSONDecodeError):
            # Decryption failed, invalid JSON, or missing required fields
            return None
        except Exception:
            # Any other error (malformed token, etc.)
            return None

    def revoke_session(self, token: str) -> bool:
        """
        Revoke a session token.

        For stateless tokens, this adds the session_id to a revocation list.
        The token will continue to be cryptographically valid but will be
        rejected during validation.
        """
        if not token.startswith("ascon1."):
            return False

        try:
            session_id = token.split(".")[1]
        except IndexError:
            return False

        # Add to revocation list
        self._revoked[session_id] = time.time()

        EvidenceBus.emit(
            "AUTH_LOGOUT",
            {
                "session_id": session_id,
                "stateless": True,
            },
        )
        return True

    def _cleanup_revocations(self):
        """
        Remove expired entries from revocation list.

        Once a token has expired naturally, we don't need to keep it
        in the revocation list anymore.
        """
        now = time.time()
        # Remove revocations older than the longest possible TTL
        cutoff = now - (self._ttl * 2)
        expired = [
            sid for sid, revoked_at in self._revoked.items() if revoked_at < cutoff
        ]
        for sid in expired:
            del self._revoked[sid]
