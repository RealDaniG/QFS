"""
User model for ATLAS authentication and authorization.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any


class User(BaseModel):
    """User model for ATLAS"""

    id: str
    username: str
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
    created_at: Optional[str] = None
    last_login: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class UserCreate(BaseModel):
    """User creation model"""

    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """User update model"""

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    """User response model (without sensitive data)"""

    id: str
    username: str
    email: EmailStr
    is_active: bool
    is_verified: bool
    created_at: Optional[str] = None
    last_login: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
