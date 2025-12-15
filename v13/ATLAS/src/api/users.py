
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import random
import string
from fastapi import APIRouter, HTTPException, Depends, status

from v13.ATLAS.src.models.user import UserProfile, UserProfileUpdate
from v13.ATLAS.src.models.user import UserProfile, UserProfileUpdate
from v13.ATLAS.src.security.crypto_utils import verify_signature

# Mock Database for V1 (Replace with Postgres/Redis in V2)
# {wallet: UserProfile}
_user_db: Dict[str, UserProfile] = {}

router = APIRouter(prefix="/v1/users", tags=["users"])

def generate_referral_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_or_create_user(wallet: str) -> UserProfile:
    if wallet in _user_db:
        return _user_db[wallet]
    
    # Create new profile
    new_user = UserProfile(
        wallet=wallet,
        created_at=datetime.now(timezone.utc),
        last_active=datetime.now(timezone.utc),
        referral_code=generate_referral_code(),
        genesis_points=0 # Start with 0 (or 10 if referral used, logic handled elsewhere)
    )
    _user_db[wallet] = new_user
    return new_user

@router.get("/{wallet}", response_model=UserProfile)
async def get_user_profile(wallet: str):
    """
    Get public profile for a wallet.
    Auto-creates profile if it doesn't exist (simplification for V1).
    """
    wallet = wallet.lower()
    return get_or_create_user(wallet)

@router.put("/{wallet}", response_model=UserProfile)
async def update_user_profile(wallet: str, update: UserProfileUpdate):
    """
    Update user profile (display name, avatar).
    In a real app, this would require JWT authentication to ensure owner matches wallet.
    For V1 scope, we assume the API Gateway or Depends(get_current_user) handles auth.
    """
    wallet = wallet.lower()
    user = get_or_create_user(wallet)
    
    if update.display_name is not None:
        user.display_name = update.display_name
    
    if update.avatar_url is not None:
        user.avatar_url = update.avatar_url
        
    user.last_active = datetime.now(timezone.utc)
    _user_db[wallet] = user
    return user

@router.get("/{wallet}/coherence", response_model=dict)
async def get_coherence_score(wallet: str):
    """
    Proxy to QFS Coherence Ledger.
    """
    wallet = wallet.lower()
    user = get_or_create_user(wallet)
    return {
        "score": user.coherence_score,
        "trust_level": "VERIFIED" if user.coherence_score > 0.5 else "UNKNOWN",
        "last_evaluated": user.last_active.isoformat()
    }
