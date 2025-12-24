from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator
import hashlib

# -----------------------------------------------------------------------------
# Enums
# -----------------------------------------------------------------------------


class SignalType(str, Enum):
    """Types of advisory signals fram Open-A.G.I."""

    CONTENT_QUALITY = "content_quality"
    ECONOMIC_RISK = "economic_risk"
    COMMUNITY_TREND = "community_trend"
    SECURITY_ALERT = "security_alert"


class EventType(str, Enum):
    """Types of economic events in QFS."""

    REWARD = "REWARD"
    PENALTY = "PENALTY"
    TRANSFER = "TRANSFER"
    MINT = "MINT"
    BURN = "BURN"
    STAKE = "STAKE"


class TokenType(str, Enum):
    """Supported QFS token types."""

    CHR = "CHR"  # Chronos (Store of Value)
    ATR = "ATR"  # Atropine (Gas/Utility)
    NUD = "NUD"  # Nodus (Governance)
    RES = "RES"  # Resonance (Reputation)


# -----------------------------------------------------------------------------
# Identity Models
# -----------------------------------------------------------------------------


class UserIdentity(BaseModel):
    """
    Canonical representation of a user across QFS, ATLAS, and Open-A.G.I.
    """

    user_id: str = Field(
        ..., description="Deterministic ID derived from wallet (e.g., user_sha256)"
    )
    wallet_address: str = Field(..., description="Primary EVM wallet address")
    public_key: Optional[str] = Field(None, description="PQC Public Key (Dilithium-5)")
    roles: List[str] = Field(
        default_factory=list, description="User roles (USER, GUARD, ADMIN)"
    )
    created_at_tick: int = Field(
        ..., description="Deterministic logical timestamp of creation"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional profile data"
    )

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        if not v.startswith("user_"):
            raise ValueError("user_id must start with 'user_'")
        return v


# -----------------------------------------------------------------------------
# Content Models
# -----------------------------------------------------------------------------


class ContentMetadata(BaseModel):
    """
    Metadata for social content ingested by ATLAS/QFS.
    """

    content_id: str = Field(..., description="Unique content identifier")
    author_id: str = Field(..., description="Reference to UserIdentity.user_id")
    platform: str = Field(..., description="Source platform (ATLAS, DISCORD, TELEGRAM)")
    content_hash: str = Field(..., description="SHA3-256 hash of content body")
    timestamp_tick: int = Field(..., description="Deterministic creation timestamp")
    context_tags: List[str] = Field(default_factory=list, description="Topic tags")
    parent_id: Optional[str] = Field(None, description="Parent content ID if reply")


# -----------------------------------------------------------------------------
# Economic Models
# -----------------------------------------------------------------------------


class EconomicEvent(BaseModel):
    """
    A unified structure for any value movement or mutation in QFS.
    """

    event_id: str = Field(..., description="Unique deterministic event ID")
    event_type: EventType
    token_type: TokenType
    amount: str = Field(..., description="Decimal string of BigNum128 amount")
    source_account: str = Field(..., description="Sender UserID or System Account")
    target_account: str = Field(..., description="Receiver UserID or System Account")
    timestamp_tick: int = Field(..., description="Logical timestamp")
    reference_content_id: Optional[str] = Field(None, description="Related content ID")
    memo: str = Field("", description="Transaction note")

    @property
    def is_system_event(self) -> bool:
        return self.source_account.startswith("sys_")


# -----------------------------------------------------------------------------
# Signal Models (Open-A.G.I)
# -----------------------------------------------------------------------------


class AdvisorySignal(BaseModel):
    """
    Read-only insight provided by Open-A.G.I.
    Must be PQC signed to be accepted by QFS/ATLAS.
    """

    signal_id: str = Field(..., description="Unique signal ID")
    signal_type: SignalType
    source_ai_id: str = Field(..., description="ID of the AI model providing signal")
    target_object_id: str = Field(
        ..., description="Content ID or User ID being analyzed"
    )
    recommendation: str = Field(..., description="Human-readable insight")
    confidence_score: str = Field(..., description="AI confidence 0-1 (Decimal string)")
    impact_metrics: Dict[str, str] = Field(
        default_factory=dict, description="Projected impact (Decimal strings)"
    )
    pqc_signature: str = Field(
        ..., description="Dilithium signature of the signal payload"
    )
    created_at_tick: int = Field(..., description="Logical timestamp")

    def verify_signature(self, public_key: str) -> bool:
        # Placeholder for actual PQC verification logic
        # In a real implementation, this would call v13.libs.PQC
        return True
