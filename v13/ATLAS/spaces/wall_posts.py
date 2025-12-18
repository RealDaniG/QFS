"""
ATLAS Wall Posts Module - Persistent Space-Linked Posts

Manages posts linked to specific Spaces (live or ended).
Enforces determinism and Zero-Sim compliance.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

try:
    from ...libs.BigNum128 import BigNum128
    from ...libs.CertifiedMath import CertifiedMath
    from ...libs.deterministic_helpers import DeterministicID
except ImportError:
    from v13.libs.BigNum128 import BigNum128
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.libs.deterministic_helpers import DeterministicID


@dataclass
class WallPost:
    """A persistent post on a Space's wall"""

    post_id: str
    space_id: str
    author_wallet: str
    content: str  # content hash or short text
    timestamp: int
    likes: Dict[str, int] = field(default_factory=dict)  # wallet -> timestamp
    replies: List[str] = field(default_factory=list)  # list of post_ids
    metadata: Dict[str, Any] = field(default_factory=dict)
    pqc_signature: str = ""

    def get_like_count(self) -> int:
        return len(self.likes)

    def is_liked_by(self, wallet_id: str) -> bool:
        return wallet_id in self.likes


class WallPostManager:
    """Manages Wall Posts for Spaces"""

    def __init__(self, cm: CertifiedMath):
        self.cm = cm
        self.posts: Dict[str, WallPost] = {}  # post_id -> WallPost
        # Index for faster lookup by space_id? For now, simple filter is OK for MVP.
        # In prod, use a proper DB index or separate dict: space_id -> List[post_id]

    def create_post(
        self,
        space_id: str,
        author_wallet: str,
        content: str,
        timestamp: int,
        metadata: Optional[Dict[str, Any]] = None,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> WallPost:
        if log_list is None:
            log_list = []

        # Deterministic ID: space_id + author + timestamp + content_hash (simulated by content len/prefix for now)
        # In real prod, hash the content.
        seed_data = f"{space_id}:{author_wallet}:{timestamp}:{content[:16]}"
        post_id = DeterministicID.from_string(seed_data)

        post = WallPost(
            post_id=post_id,
            space_id=space_id,
            author_wallet=author_wallet,
            content=content,
            timestamp=timestamp,
            metadata=metadata or {},
        )

        self.posts[post_id] = post
        log_list.append(
            {
                "operation": "wall_post_created",
                "post_id": post_id,
                "space_id": space_id,
                "author": author_wallet,
            }
        )
        return post

    def like_post(
        self,
        post_id: str,
        user_wallet: str,
        timestamp: int,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        if log_list is None:
            log_list = []

        post = self.posts.get(post_id)
        if not post:
            raise ValueError(f"Post {post_id} not found")

        if user_wallet in post.likes:
            # Idempotent or error? Let's say idempotent but log a note, or raise.
            # Usually double-like is a no-op.
            return

        post.likes[user_wallet] = timestamp
        log_list.append(
            {
                "operation": "wall_post_liked",
                "post_id": post_id,
                "user": user_wallet,
            }
        )

    def reply_to_post(
        self,
        parent_post_id: str,
        author_wallet: str,
        content: str,
        timestamp: int,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> WallPost:
        """Creates a reply post and links it to the parent."""
        if log_list is None:
            log_list = []

        parent_post = self.posts.get(parent_post_id)
        if not parent_post:
            raise ValueError(f"Parent post {parent_post_id} not found")

        # Create the reply as a normal post, linked to the same space
        reply_post = self.create_post(
            space_id=parent_post.space_id,
            author_wallet=author_wallet,
            content=content,
            timestamp=timestamp,
            metadata={"parent_post_id": parent_post_id},
            log_list=log_list,
        )

        parent_post.replies.append(reply_post.post_id)
        log_list.append(
            {
                "operation": "wall_post_reply_linked",
                "parent_post_id": parent_post_id,
                "reply_post_id": reply_post.post_id,
            }
        )
        return reply_post

    def get_post(self, post_id: str) -> Optional[WallPost]:
        return self.posts.get(post_id)

    def get_posts_by_space(self, space_id: str) -> List[WallPost]:
        """Returns all posts for a given space, sorted by timestamp."""
        space_posts = [p for p in self.posts.values() if p.space_id == space_id]
        return sorted(space_posts, key=lambda p: (p.timestamp, p.post_id))
