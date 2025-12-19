"""
SessionManager.py - Manages authenticated user sessions.
"""

import uuid
import time
from typing import Dict, Optional, TypedDict


class SessionData(TypedDict):
    wallet_address: str
    created_at: float
    expires_at: float
    scopes: list[str]


class SessionManager:
    """
    Manages user sessions.
    In production, use Redis/JWT. In-memory for v15.4 MVP.
    """

    def __init__(self, session_ttl_seconds: int = 3600 * 24):
        self._sessions: Dict[str, SessionData] = {}  # token -> data
        self._ttl = session_ttl_seconds

    def create_session(self, wallet_address: str, scopes: list[str] = None) -> str:
        """Creates a new session for a wallet."""
        token = f"sess_{uuid.uuid4()}"
        now = time.time()
        self._sessions[token] = {
            "wallet_address": wallet_address,
            "created_at": now,
            "expires_at": now + self._ttl,
            "scopes": scopes or [],
        }
        self._cleanup()
        return token

    def validate_session(self, token: str) -> Optional[SessionData]:
        """Returns session data if valid, else None."""
        self._cleanup()
        if token in self._sessions:
            return self._sessions[token]
        return None

    def revoke_session(self, token: str):
        """Revokes a session."""
        if token in self._sessions:
            del self._sessions[token]

    def _cleanup(self):
        """Removes expired sessions."""
        now = time.time()
        expired = [t for t, data in self._sessions.items() if data["expires_at"] < now]
        for t in expired:
            del self._sessions[t]
