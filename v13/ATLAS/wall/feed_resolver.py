"""
ATLAS Wall Posts Module - Feed Resolver

Deterministic feed resolution and ordering.
"""

from typing import List, Optional

try:
    from .wall_service import WallService
    from .wall_models import Post, PostType
except ImportError:
    from v13.atlas.wall.wall_service import WallService
    from v13.atlas.wall.wall_models import Post, PostType


class FeedResolver:
    """Resolves feeds with deterministic ordering"""

    def __init__(self, wall_service: WallService):
        self.wall_service = wall_service

    def resolve_feed(
        self,
        viewer_wallet: str,
        space_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Post]:
        """
        Resolve feed with deterministic ordering:
        1. Pinned posts first (by pin_timestamp DESC, post_id ASC)
        2. Regular posts by (created_at DESC, post_id ASC)
        """
        all_posts = list(self.wall_service.posts.values())

        # Filter by space if specified
        if space_id:
            all_posts = [p for p in all_posts if p.space_id == space_id]

        # Separate pinned and regular posts
        pinned = [p for p in all_posts if p.is_pinned()]
        regular = [p for p in all_posts if not p.is_pinned()]

        # Sort pinned by pin_timestamp DESC, then post_id ASC
        pinned_sorted = sorted(
            pinned,
            key=lambda p: (-p.pin_timestamp if p.pin_timestamp else 0, p.post_id),
        )

        # Sort regular by created_at DESC, then post_id ASC
        regular_sorted = sorted(regular, key=lambda p: (-p.created_at, p.post_id))

        # Combine: pinned first, then regular
        feed = pinned_sorted + regular_sorted

        # Apply pagination
        return feed[offset : offset + limit]

    def resolve_space_feed(
        self, space_id: str, viewer_wallet: str, limit: int = 50
    ) -> List[Post]:
        """Resolve feed for specific space"""
        return self.resolve_feed(
            viewer_wallet=viewer_wallet, space_id=space_id, limit=limit
        )

    def resolve_user_posts(self, author_wallet: str, limit: int = 50) -> List[Post]:
        """Resolve posts by specific author"""
        user_posts = [
            p
            for p in self.wall_service.posts.values()
            if p.author_wallet == author_wallet
        ]

        # Sort by created_at DESC, post_id ASC
        sorted_posts = sorted(user_posts, key=lambda p: (-p.created_at, p.post_id))

        return sorted_posts[:limit]
