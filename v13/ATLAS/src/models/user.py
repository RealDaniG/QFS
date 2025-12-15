
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    wallet: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    last_active: datetime
    coherence_score: float = 0.0
    genesis_points: int = 0
    referral_code: str
    referral_count: int = 0
    referrer_wallet: Optional[str] = None

class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=2, max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500)
