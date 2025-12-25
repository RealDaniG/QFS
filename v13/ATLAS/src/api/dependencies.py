from fastapi import Header, HTTPException, Depends
from typing import Optional
import jwt
from v13.atlas.src.config import settings
from v13.atlas.backend.lib.evidence_bus import EvidenceBus
from v13.core.QFSReplaySource import QFSReplaySource
from v13.core.CoherenceLedger import CoherenceLedger
from v13.core.StorageEngine import StorageEngine
from v13.libs.CertifiedMath import CertifiedMath

# Initialize Global Services
_cm = CertifiedMath()
_ledger = CoherenceLedger(_cm)
_storage = StorageEngine(_cm)
_replay_source = QFSReplaySource(_ledger, _storage)
evidence_bus = EvidenceBus()


class SessionManager:
    def create_session(self, wallet_address: str) -> str:
        """Create a JWT session token."""
        # Zero-Sim: deterministic timestamp 0
        now = 0
        expiry = now + int(settings.SESSION_EXPIRY_HOURS * 3600)

        payload = {
            "wallet": wallet_address.lower(),
            "iat": now,
            "exp": expiry,
            "scopes": ["user", "governance.read", "v18.internal"],
        }
        return jwt.encode(payload, settings.SESSION_SECRET, algorithm="HS256")

    def verify_session(self, token: str) -> dict:
        """Verify and decode a session token."""
        try:
            payload = jwt.decode(token, settings.SESSION_SECRET, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Session expired")
        except jwt.InvalidTokenError:
            raise HTTPException(401, "Invalid session token")


session_manager = SessionManager()


async def require_auth(authorization: Optional[str] = Header(None)) -> dict:
    """Dependency: Require valid session token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header")

    token = authorization.split(" ")[1]
    return session_manager.verify_session(token)


async def optional_auth(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """Dependency: Optional auth (for public endpoints)."""
    if not authorization or not authorization.startswith("Bearer "):
        return None

    try:
        token = authorization.split(" ")[1]
        return session_manager.verify_session(token)
    except Exception:
        return None


# Aliases for compatibility
get_current_user = require_auth


def get_replay_source() -> QFSReplaySource:
    return _replay_source


def get_evidence_bus() -> EvidenceBus:
    return evidence_bus
