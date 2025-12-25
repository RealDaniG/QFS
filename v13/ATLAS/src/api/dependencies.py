from fastapi import Header, HTTPException, Depends
from typing import Optional
import jwt
from v13.atlas.src.config import settings
from v13.atlas.backend.lib.evidence_bus import EvidenceBus
from v13.core.QFSReplaySource import QFSReplaySource
from v13.core.CoherenceLedger import CoherenceLedger
from v13.core.StorageEngine import StorageEngine
from v13.libs.CertifiedMath import CertifiedMath

from v15.auth.session_manager import SessionManager

# Initialize Global Services
_cm = CertifiedMath()
_ledger = CoherenceLedger(_cm)
_storage = StorageEngine(_cm)
_replay_source = QFSReplaySource(_ledger, _storage)
evidence_bus = EvidenceBus()


# Instantiate Certified SessionManager (V15/V18)
session_manager = SessionManager(session_ttl_seconds=3600 * 24)


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
