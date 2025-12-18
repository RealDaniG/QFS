from typing import Dict, Optional, Any, List
from enum import Enum
from pydantic import BaseModel, Field


class ContentType(str, Enum):
    POST = "post"
    COMMENT = "comment"
    REACTION = "reaction"
    SIGNAL = "signal"


class UserIdentity(BaseModel):
    """
    Standardized identity mapping.
    """

    user_id: str = Field(..., description="Unique immutable user identifier (UUID)")
    wallet_address: str = Field(..., description="Primary wallet address")
    public_key: str = Field(..., description="PQC public key for verification")
    profile: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional profile metadata"
    )


class ContentMetadata(BaseModel):
    """
    Schema for content objects (posts, comments, etc).
    """

    content_id: str = Field(..., description="Unique content identifier")
    author_id: str = Field(..., description="ID of the author (UserIdentity.user_id)")
    timestamp: int = Field(..., description="Unix timestamp of creation")
    type: ContentType = Field(..., description="Type of content")
    parent_id: Optional[str] = Field(
        None, description="Parent content ID if reply/reaction"
    )
    attributes: Optional[Dict[str, Any]] = Field(
        default=None, description="Arbitrary content attributes"
    )


class EconomicEvent(BaseModel):
    """
    Standardized header for economic events (rewards, penalties, transfers).
    """

    event_id: str = Field(..., description="Unique event identifier")
    source_id: str = Field(..., description="Origin of funds/event (System or User ID)")
    target_id: str = Field(..., description="Recipient User ID")
    amount: str = Field(
        ..., description="Amount as string to preserve BigNum128 precision"
    )
    token_type: str = Field(..., description="Token symbol or identifier (e.g. 'QFS')")
    reason: str = Field(..., description="Human-readable reason for the event")
    timestamp: int = Field(..., description="Unix timestamp of event")


class AdvisorySignal(BaseModel):
    """
    Open-A.G.I advisory signal format.
    """

    signal_id: str = Field(..., description="Unique signal identifier")
    issuer_id: str = Field(..., description="ID of the trusted AI issuer")
    payload: Dict[str, Any] = Field(..., description="Signal data/recommendation")
    signature: str = Field(..., description="PQC signature of the payload")
    timestamp: int = Field(..., description="Unix timestamp of issuance")
