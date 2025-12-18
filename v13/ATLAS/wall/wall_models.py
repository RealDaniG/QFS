"""
ATLAS Wall Posts Module - Models

Data models for wall posts, comments, and reactions.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class PostType(Enum):
    """Type of wall post"""

    STANDARD = "standard"  # Regular post
    PINNED = "pinned"  # Pinned to top of feed
    RECAP = "recap"  # AI-generated recap (advisory only)
    QUOTE = "quote"  # Quote of another post


class Visibility(Enum):
    """Post visibility level"""

    PUBLIC = "public"  # Everyone can see
    SPACE_ONLY = "space_only"  # Only space participants
    FOLLOWERS = "followers"  # Only followers


@dataclass
class Post:
    """Wall post model"""

    post_id: str  # Deterministic ID
    author_wallet: str
    content: str
    content_hash: str  # SHA-256 of content
    created_at: int  # Deterministic timestamp
    space_id: Optional[str] = None  # Link to Spaces
    parent_post_id: Optional[str] = None  # For quotes/replies
    post_type: PostType = PostType.STANDARD
    visibility: Visibility = Visibility.PUBLIC
    reactions: Dict[str, int] = field(default_factory=dict)  # {emoji: count}
    comment_count: int = 0
    pin_timestamp: Optional[int] = None  # When pinned (for ordering)
    metadata: Dict[str, Any] = field(default_factory=dict)
    pqc_signature: str = ""

    def is_pinned(self) -> bool:
        """Check if post is pinned"""
        return self.post_type == PostType.PINNED

    def is_quote(self) -> bool:
        """Check if post is a quote"""
        return self.post_type == PostType.QUOTE and self.parent_post_id is not None

    def is_recap(self) -> bool:
        """Check if post is AI recap (advisory)"""
        return self.post_type == PostType.RECAP

    def add_reaction(self, emoji: str) -> None:
        """Add reaction to post"""
        self.reactions[emoji] = self.reactions.get(emoji, 0) + 1

    def remove_reaction(self, emoji: str) -> None:
        """Remove reaction from post"""
        if emoji in self.reactions and self.reactions[emoji] > 0:
            self.reactions[emoji] -= 1
            if self.reactions[emoji] == 0:
                del self.reactions[emoji]
