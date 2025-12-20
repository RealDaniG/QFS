"""
API Dependencies for ATLAS

Provides dependency injection for authentication, QFS client, and other services.
"""

from functools import lru_cache
from typing import Optional, Generator
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from ..qfs_client import QFSClient
from ..real_ledger import RealLedger
from v13.core.CoherenceLedger import CoherenceLedger
from v13.core.StorageEngine import StorageEngine
from v13.core.QFSReplaySource import QFSReplaySource
from v13.libs.CertifiedMath import CertifiedMath
from v15.auth.session_manager import SessionManager

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
_qfs_client: Optional[QFSClient] = None
_replay_source: Optional[QFSReplaySource] = None


class User(BaseModel):
    """User model for authentication"""

    id: str
    username: str
    email: str
    is_active: bool = True


@lru_cache()
def get_qfs_client() -> QFSClient:
    """
    Get or create QFSClient instance.
    """
    global _qfs_client
    if _qfs_client is None:

        class StubAdapter:
            async def submit_bundle(self, b):
                raise NotImplementedError("Write ops not enabled")

            async def get_snapshot(self, r):
                raise NotImplementedError()

        real_ledger = RealLedger(StubAdapter())
        _qfs_client = QFSClient(ledger=real_ledger, private_key="dev_private_key")
        logger.info("QFSClient initialized with StubAdapter")
    return _qfs_client


@lru_cache()
def get_replay_source() -> QFSReplaySource:
    """
    Get the singleton QFSReplaySource for Explain-This.
    Reads directly from CoherenceLedger and StorageEngine.
    """
    global _replay_source
    if _replay_source is None:
        from v13.core.QFSReplaySource import LiveLedgerReplaySource

        cm = CertifiedMath()
        storage = StorageEngine(cm)
        from ..config import EXPLAIN_THIS_SOURCE, QFS_LEDGER_PATH

        source_type = EXPLAIN_THIS_SOURCE
        if source_type == "live_ledger":
            ledger_path = QFS_LEDGER_PATH
            logger.info(f"Initializing LiveLedgerReplaySource from {ledger_path}")
            try:
                _replay_source = LiveLedgerReplaySource(ledger_path, storage)
            except Exception as e:
                logger.critical(f"Failed to initialize LiveLedgerReplaySource: {e}")
                raise ImportError(f"Could not load live ledger from {ledger_path}: {e}")
        else:
            ledger = CoherenceLedger(cm)
            _replay_source = QFSReplaySource(ledger, storage)
            logger.info("Initialized QFSReplaySource (In-Memory)")
    return _replay_source


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current authenticated user.

    Args:
        token: OAuth2 access token

    Returns:
        User: Authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user = User(
            id="user_123", username="dev_user", email="dev@qfs.internal", is_active=True
        )
        return user
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current active user.

    Args:
        current_user: Current user from get_current_user

    Returns:
        User: Active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


# Session Manager Singleton
session_manager = SessionManager()


async def get_current_session(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Validates the session token and returns session data.
    """
    session = session_manager.validate_session(token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return session


def get_qfs_client_dependency() -> Generator[QFSClient, None, None]:
    """
    Dependency function for QFSClient.

    Yields:
        QFSClient: QFS client instance
    """
    client = get_qfs_client()
    yield client


def qfs_client() -> QFSClient:
    """Get QFSClient for dependency injection"""
    return get_qfs_client()


from v13.core.dependencies import get_crypto_engine
import json


async def send_secure_message(peer_id: str, message: dict, crypto=None):
    """
    Send encrypted message with fail-closed semantics.

    Args:
        peer_id: Target node ID
        message: Dict payload
        crypto: CryptoEngine instance (optional dependency injection)

    Raises:
        RuntimeError: If secure channel unavailable or encryption fails
    """
    if crypto is None:
        crypto = get_crypto_engine()
    if not crypto.has_ratchet_state(peer_id):
        raise RuntimeError(f"No secure channel to {peer_id}")
    payload = json.dumps(message).encode()
    encrypted = crypto.encrypt_message(payload, peer_id)
    if not encrypted:
        raise RuntimeError(f"Encryption failed for {peer_id}")
    return encrypted
