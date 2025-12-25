"""
Session Store
Persists session state. For Alpha, using in-memory with optional JSON dump.
"""

from typing import Dict, Optional
from v15.auth.session import Session


class SessionStore:
    def __init__(self) -> None:
        self._sessions: Dict[str, Session] = {}

    def save(self, session: Session) -> None:
        """Save session to store."""
        self._sessions[session.session_id] = session
        # TODO: Implement optional disk persistence for recovery

    def get(self, session_id: str) -> Optional[Session]:
        """Retrieve session by ID."""
        return self._sessions.get(session_id)

    def revoke(self, session_id: str) -> None:
        """Remove session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
