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
from ..real_ledger import RealLedger, MockLedger
from ..models.user import User

logger = logging.getLogger(__name__)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Global QFS client instance
_qfs_client: Optional[QFSClient] = None

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
    
    Returns:
        QFSClient: Configured QFS client
    """
    global _qfs_client
    
    if _qfs_client is None:
        # Initialize MockLedger for development
        mock_ledger = MockLedger()
        real_ledger = RealLedger(mock_ledger)
        
        # Create QFS client with mock private key
        _qfs_client = QFSClient(
            ledger=real_ledger,
            private_key="mock_private_key_for_testing"
        )
        
        logger.info("QFSClient initialized with MockLedger")
    
    return _qfs_client

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
    # This is a mock implementation
    # In production, validate token against auth service
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Mock user for testing
    # In production, decode JWT and validate against database
    try:
        # For now, return a mock user
        user = User(
            id="user_123",
            username="testuser",
            email="test@example.com",
            is_active=True
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
    current_user: User = Depends(get_current_user)
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def get_qfs_client_dependency() -> Generator[QFSClient, None, None]:
    """
    Dependency function for QFSClient.
    
    Yields:
        QFSClient: QFS client instance
    """
    client = get_qfs_client()
    yield client

# Alias for easier use in route definitions
def qfs_client() -> QFSClient:
    """Get QFSClient for dependency injection"""
    return get_qfs_client()
