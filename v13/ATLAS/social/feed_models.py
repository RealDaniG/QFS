"""
ATLAS Social Schemas
read-optimized models for aggregated user feeds and dashboards.
Strict Zero-Sim compliance: Derived deterministically from EconomicEvents.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class FeedItem(BaseModel):
    """
    A single item in a user's feed (e.g., a post, a space join, a chat msg).
    """

    item_id: str  # Deterministic ID (often the source event ID)
    item_type: str  # 'wall_post', 'space_event', 'chat_message'
    timestamp: int
    source_id: str  # space_id, chat_session_id, etc.
    author_wallet: str
    summary_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UserFeed(BaseModel):
    """
    Aggregated view for a specific user.
    """

    user_wallet: str
    generated_at: int
    items: List[FeedItem] = Field(default_factory=list)


class SpaceDashboard(BaseModel):
    """
    Holistic view of a Space's activity.
    """

    space_id: str
    generated_at: int
    active_member_count: int
    recent_posts: List[FeedItem] = Field(default_factory=list)
    active_chats: List[str] = Field(
        default_factory=list
    )  # List of session_ids linked to this space
