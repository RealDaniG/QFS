"""
ATLAS v14 Canonical Schemas (Contracts)
Defines the stable, public-facing data API for the Social Layer.
Consumers (Gateway, UI, external agents) should rely on these models,
not on the internal Logic classes.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


# --- Enums (Re-exported or Redefined for Stability) ---
class ContractParticipantRole(str, Enum):
    HOST = "host"
    MODERATOR = "moderator"
    SPEAKER = "speaker"
    LISTENER = "listener"


class ContractParticipantStatus(str, Enum):
    ACTIVE = "active"
    MUTED = "muted"
    KICKED = "kicked"


class ContractSpaceStatus(str, Enum):
    ACTIVE = "active"
    ENDED = "ended"
    PAUSED = "paused"


# --- Data Models ---


class AtlasParticipant(BaseModel):
    """Public view of a Space Participant."""

    wallet_id: str
    role: ContractParticipantRole
    status: ContractParticipantStatus
    joined_at: int
    speak_duration_seconds: int = 0


class AtlasSpace(BaseModel):
    """Public view of an ATLAS Space."""

    space_id: str
    host_wallet: str
    title: str
    created_at: int
    status: ContractSpaceStatus
    participant_count: int
    # We do NOT expose full participant list here for brevity in list views,
    # but could be fetched separately. For v14, maybe we include top-level metadata.
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AtlasWallPost(BaseModel):
    """Public view of a Wall Post."""

    post_id: str
    space_id: str
    author_wallet: str
    content: str
    timestamp: int
    like_count: int
    reply_count: int
    is_pinned: bool = False
    is_recap: bool = False
    linked_space_id: Optional[str] = None
    quoted_post_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AtlasChatMessage(BaseModel):
    """Public view of a Chat Message."""

    message_id: str
    session_id: str
    author_wallet: str
    timestamp: int
    content: str  # Decrypted or Encrypted? Contract usually implies "what user sees".
    # But if E2EE, this might be encrypted blob.
    # For v14 simulation, we treated it as string.
    references: List[str] = Field(default_factory=list)
    sequence_number: int


class AtlasChatSession(BaseModel):
    """Public view of a Chat Session."""

    session_id: str
    owner_wallet: str
    created_at: int
    member_count: int
    is_active: bool
    title: Optional[str] = None
    ttl_seconds: int = 0


# --- Adapters ---


def space_to_contract(internal_space: Any) -> AtlasSpace:
    """Convert internal Space object to Contract."""
    return AtlasSpace(
        space_id=internal_space.space_id,
        host_wallet=internal_space.host_wallet,
        title=internal_space.title,
        created_at=internal_space.created_at,
        status=ContractSpaceStatus(internal_space.status.value),
        participant_count=len(internal_space.participants),
        metadata=internal_space.metadata,
    )


def post_to_contract(internal_post: Any) -> AtlasWallPost:
    """Convert internal WallPost object to Contract."""
    return AtlasWallPost(
        post_id=internal_post.post_id,
        space_id=internal_post.space_id,
        author_wallet=internal_post.author_wallet,
        content=internal_post.content,
        timestamp=internal_post.timestamp,
        like_count=len(internal_post.likes),
        reply_count=len(internal_post.replies),
        is_pinned=internal_post.is_pinned,
        is_recap=internal_post.metadata.get("is_recap", False),
        linked_space_id=internal_post.metadata.get("linked_space_id"),
        quoted_post_id=internal_post.quoted_post_id
        or None,  # explicit None if empty string
        metadata=internal_post.metadata,
    )


def message_to_contract(internal_msg: Any) -> AtlasChatMessage:
    """Convert internal ChatMessage to Contract."""
    return AtlasChatMessage(
        message_id=internal_msg.message_id,
        session_id=internal_msg.session_id,
        author_wallet=internal_msg.author_wallet,
        timestamp=internal_msg.timestamp,
        content=internal_msg.content_encrypted,  # Following internal naming
        references=internal_msg.references or [],
        sequence_number=internal_msg.sequence_number,
    )
