"""
Social Schemas (v17)

Pydantic models for deterministic social interactions (Threads, Comments).
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class Thread(BaseModel):
    """Deterministic discussion thread."""

    thread_id: str = Field(..., description="Deterministic thread ID")
    space_id: str = Field(..., description="Space where thread exists")

    title: str = Field(..., description="Thread title")
    created_by: str = Field(..., description="Creator wallet")
    created_at: int = Field(..., description="Timestamp")

    # Binding
    reference_id: Optional[str] = Field(
        None, description="Linked Entity ID (Proposal/Bounty)"
    )
    reference_type: Optional[str] = Field(
        None, description="Entity type: 'proposal' | 'bounty'"
    )

    metadata: Optional[Dict[str, Any]] = Field(default=None)


class Comment(BaseModel):
    """Deterministic comment/reply."""

    comment_id: str = Field(..., description="Deterministic comment ID")
    thread_id: str = Field(..., description="Parent thread ID")

    author_wallet: str = Field(..., description="Author wallet")
    content: str = Field(..., description="Content body")
    timestamp: int = Field(..., description="Timestamp")

    reply_to_id: Optional[str] = Field(None, description="Parent comment ID if reply")
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class ThreadState(BaseModel):
    """Reconstructed thread state."""

    thread: Thread
    comments: List[Comment] = Field(default_factory=list)


class Dispute(BaseModel):
    """Formal dispute against a governance or bounty entity."""

    dispute_id: str = Field(..., description="Deterministic dispute ID")
    target_id: str = Field(..., description="ID of disputed entity")
    target_type: str = Field(..., description="'proposal' | 'bounty'")

    raised_by: str = Field(..., description="Wallet raising dispute")
    reason: str = Field(..., description="Reason for dispute")
    timestamp: int = Field(..., description="Timestamp")

    status: str = Field(default="OPEN", description="OPEN | RESOLVED | DISMISSED")
    resolution_note: Optional[str] = Field(None, description="Resolution details")
