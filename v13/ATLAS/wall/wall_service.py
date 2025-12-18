"""
ATLAS Wall Posts Module - Service

Wall post creation, management, and lifecycle.
"""

from typing import Dict, Any, List, Optional
import hashlib

try:
    from ...libs.BigNum128 import BigNum128
    from ...libs.CertifiedMath import CertifiedMath
    from ...libs.deterministic_helpers import DeterministicID
    from .wall_models import Post, PostType, Visibility
except ImportError:
    from v13.libs.BigNum128 import BigNum128
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.libs.deterministic_helpers import DeterministicID
    from v13.atlas.wall.wall_models import Post, PostType, Visibility


class WallService:
    """Manages wall posts and interactions"""

    def __init__(self, cm: CertifiedMath, spaces_manager=None):
        self.cm = cm
        self.spaces_manager = spaces_manager
        self.posts: Dict[str, Post] = {}

    def create_post(
        self,
        author_wallet: str,
        content: str,
        timestamp: int,
        space_id: Optional[str] = None,
        post_type: PostType = PostType.STANDARD,
        visibility: Visibility = Visibility.PUBLIC,
        metadata: Optional[Dict[str, Any]] = None,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> Post:
        """Create a new post with deterministic ID"""
        if log_list is None:
            log_list = []

        # Generate deterministic content hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Generate deterministic post ID
        post_data = f"{author_wallet}:{timestamp}:{content_hash}"
        post_id = DeterministicID.from_string(post_data)

        # Verify space exists if linked
        if space_id and self.spaces_manager:
            space = self.spaces_manager.active_spaces.get(space_id)
            if not space:
                raise ValueError(f"Space {space_id} not found")

        post = Post(
            post_id=post_id,
            author_wallet=author_wallet,
            content=content,
            content_hash=content_hash,
            created_at=timestamp,
            space_id=space_id,
            post_type=post_type,
            visibility=visibility,
            metadata=metadata or {},
        )

        self.posts[post_id] = post
        log_list.append({"operation": "post_created", "post_id": post_id})
        return post

    def quote_post(
        self,
        author_wallet: str,
        parent_post_id: str,
        content: str,
        timestamp: int,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> Post:
        """Quote an existing post"""
        if log_list is None:
            log_list = []

        parent_post = self.posts.get(parent_post_id)
        if not parent_post:
            raise ValueError(f"Parent post {parent_post_id} not found")

        # Generate deterministic content hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Generate deterministic quote ID
        quote_data = f"{author_wallet}:{timestamp}:{parent_post_id}:{content_hash}"
        post_id = DeterministicID.from_string(quote_data)

        post = Post(
            post_id=post_id,
            author_wallet=author_wallet,
            content=content,
            content_hash=content_hash,
            created_at=timestamp,
            parent_post_id=parent_post_id,
            post_type=PostType.QUOTE,
            visibility=parent_post.visibility,  # Inherit visibility
            space_id=parent_post.space_id,  # Inherit space
        )

        self.posts[post_id] = post
        log_list.append(
            {
                "operation": "post_quoted",
                "post_id": post_id,
                "parent_id": parent_post_id,
            }
        )
        return post

    def pin_post(
        self,
        post_id: str,
        pinner_wallet: str,
        timestamp: int,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> Post:
        """Pin a post (requires host/admin role in space)"""
        if log_list is None:
            log_list = []

        post = self.posts.get(post_id)
        if not post:
            raise ValueError(f"Post {post_id} not found")

        # Verify pinner has permission (host of space)
        if post.space_id and self.spaces_manager:
            space = self.spaces_manager.active_spaces.get(post.space_id)
            if space and not space.is_host(pinner_wallet):
                raise ValueError("Only space host can pin posts")

        post.post_type = PostType.PINNED
        post.pin_timestamp = timestamp
        log_list.append({"operation": "post_pinned", "post_id": post_id})
        return post

    def add_reaction(
        self,
        post_id: str,
        reactor_wallet: str,
        emoji: str,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Add reaction to post"""
        if log_list is None:
            log_list = []

        post = self.posts.get(post_id)
        if not post:
            raise ValueError(f"Post {post_id} not found")

        post.add_reaction(emoji)
        log_list.append(
            {"operation": "reaction_added", "post_id": post_id, "emoji": emoji}
        )

    def get_post(self, post_id: str) -> Optional[Post]:
        """Retrieve post by ID"""
        return self.posts.get(post_id)

    def list_posts(self) -> List[Post]:
        """List all posts (deterministic ordering)"""
        return sorted(self.posts.values(), key=lambda p: (p.created_at, p.post_id))
