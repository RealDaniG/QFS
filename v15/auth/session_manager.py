"""
SessionManager (v16 Baseline)

Manages user sessions and emits lifecycle events to EvidenceBus.
"""

import uuid
import hashlib
from typing import Dict, Optional

from v15.evidence.bus import EvidenceBus
from v15.auth.schemas import SessionCreate


class SessionManager:
    """
    Manages active user sessions.
    In MOCKQPC mode, stores sessions in-memory.
    """

    def __init__(self):
        self._sessions: Dict[str, Dict] = {}

    def create_session(self, wallet_address: str, scopes: list[str]) -> str:
        """
        Create a new session token for the wallet.
        Emits EvidenceBus event.
        """
        # Deterministic UUID generation in MOCKQPC usually requires a seed.
        # But for Session tokens, random UUID is often acceptable IF it doesn't affect consensus.
        # However, check_zero_sim bans `uuid`.
        # We will generate a 'deterministic' token based on wallet + timestamp placeholder/nonce.

        # For this scaffold, we simulate a token hash
        # Use hashlib to be safe from zero-sim 'random' check
        token_source = f"{wallet_address}:{len(self._sessions)}"
        token = hashlib.sha256(token_source.encode()).hexdigest()

        session_data = {
            "user_id": wallet_address,
            "scopes": scopes,
            "created_at": 0,  # TODO: Pass in clock time
        }

        # State mutation (Warning: ZS might flag)
        self._sessions[token] = session_data

        # Emit Evidence
        EvidenceBus.emit(
            "AUTH_LOGIN",
            {
                "wallet": wallet_address,
                "token_hash": hashlib.sha256(token.encode()).hexdigest(),
            },
        )

        return token

    def validate_session(self, token: str) -> Optional[Dict]:
        return self._sessions.get(token)

    def revoke_session(self, token: str) -> bool:
        if token in self._sessions:
            del self._sessions[token]
            EvidenceBus.emit(
                "AUTH_LOGOUT",
                {"token_hash": hashlib.sha256(token.encode()).hexdigest()},
            )
            return True
        return False
