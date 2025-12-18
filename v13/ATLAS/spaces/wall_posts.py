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
    from .wall_posts_events import emit_post_created
except ImportError:
    from v13.libs.BigNum128 import BigNum128
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.libs.deterministic_helpers import DeterministicID
    from v13.atlas.spaces.wall_posts_events import emit_post_created


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
    is_pinned: bool = False
    quoted_post_id: str = ""
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
        quoted_post_id: str = "",
        is_recap: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> WallPost:
        if log_list is None:
            log_list = []

        final_metadata = metadata or {}
        if is_recap:
            final_metadata["is_recap"] = True
            final_metadata["linked_space_id"] = space_id  # Explicit link check

        # Deterministic ID: space_id + author + timestamp + content_hash
        seed_data = f"{space_id}:{author_wallet}:{timestamp}:{content[:16]}"
        post_id = DeterministicID.from_string(seed_data)

        post = WallPost(
            post_id=post_id,
            space_id=space_id,
            author_wallet=author_wallet,
            content=content,
            timestamp=timestamp,
            quoted_post_id=quoted_post_id,
            metadata=final_metadata,
        )

        self.posts[post_id] = post

        # Emit Economic Event (Creation Reward)
        # Note: In future, if is_recap is true, maybe different event? For now, standard reward logic applies or can be filtered inside event.
        # But wait, audit says "naked" mutation.
        # Requirement: Recap might be free or handled differently.
        # Let's call standard emit_post_created for now, assuming all posts interact with economy.
        emit_post_created(post, self.cm, log_list)

        log_operation = "wall_post_recap_created" if is_recap else "wall_post_created"
        log_list.append(
            {
                "operation": log_operation,
                "post_id": post_id,
                "space_id": space_id,
                "author": author_wallet,
                "timestamp": timestamp,
                "quoted_post_id": quoted_post_id,
                "is_recap": is_recap,
            }
        )
        return post

    def pin_post(
        self,
        post_id: str,
        actor_wallet: str,
        timestamp: int,
        is_authorized: bool,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Pin a post to the top of the space's wall."""
        if log_list is None:
            log_list = []

        post = self.posts.get(post_id)
        if not post:
            raise ValueError(f"Post {post_id} not found")

        if not is_authorized:
            raise ValueError(
                f"Actor {actor_wallet} is not authorized to pin in space {post.space_id}"
            )

        post.is_pinned = True
        log_list.append(
            {
                "operation": "wall_post_pinned",
                "post_id": post_id,
                "pinner_wallet": actor_wallet,
                "space_id": post.space_id,
                "timestamp": timestamp,
            }
        )

    def unpin_post(
        self,
        post_id: str,
        actor_wallet: str,
        is_authorized: bool,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Unpin a post."""
        if log_list is None:
            log_list = []

        post = self.posts.get(post_id)
        if not post:
            raise ValueError(f"Post {post_id} not found")

        if not is_authorized:
            raise ValueError(
                f"Actor {actor_wallet} is not authorized to unpin in space {post.space_id}"
            )

        post.is_pinned = False
        log_list.append(
            {
                "operation": "wall_post_unpinned",
                "post_id": post_id,
                "actor": actor_wallet,
                "space_id": post.space_id,
            }
        )

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
        """Returns all posts for a given space, sorted by Pinned DESC, then Newest First."""
        space_posts = [p for p in self.posts.values() if p.space_id == space_id]
        # Sort: is_pinned (True=1, False=0) DESC, then timestamp DESC
        # Python sort is stable.
        return sorted(space_posts, key=lambda p: (not p.is_pinned, -p.timestamp))
