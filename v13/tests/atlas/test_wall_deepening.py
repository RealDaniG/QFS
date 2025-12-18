"""
Test Wall Deepening (v14)
Verifies Pinned Posts (Sort Order, Auth) and Quote Posts.
"""

import pytest

try:
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.atlas.spaces.wall_posts import WallPostManager
except ImportError:
    import sys
    import os

    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    )
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.atlas.spaces.wall_posts import WallPostManager


def test_pinned_posts_logic():
    """Verify pinned posts sort first and obey auth."""
    cm = CertifiedMath()
    manager = WallPostManager(cm)
    space_id = "space_x"

    log_list = []
    # Create posts
    # P1: Oldest
    p1 = manager.create_post(space_id, "user_a", "Content 1", 1000, log_list=log_list)
    # P2: Middle
    p2 = manager.create_post(space_id, "user_b", "Content 2", 2000, log_list=log_list)
    # P3: Newest
    p3 = manager.create_post(space_id, "user_c", "Content 3", 3000, log_list=log_list)

    # 1. Verify Default Order (Newest First)
    # wait, get_posts_by_space sorts by timestamp (p.timestamp).
    # key=lambda p: (not p.is_pinned, -p.timestamp)
    # -p.timestamp means DESC (Newest first).
    posts = manager.get_posts_by_space(space_id)
    assert posts == [p3, p2, p1]

    # 2. Pin P1 (Oldest)
    # Auth fail first
    with pytest.raises(ValueError, match="not authorized"):
        manager.pin_post(p1.post_id, "user_a", 3100, is_authorized=False)

    # Auth success
    manager.pin_post(p1.post_id, "host_wallet", 3105, is_authorized=True)
    assert p1.is_pinned is True

    # 3. Verify Sort Order: Panned P1 should be first, then P3, P2
    posts = manager.get_posts_by_space(space_id)
    assert posts[0] == p1  # Pinned
    assert posts[1] == p3  # Newest remaining
    assert posts[2] == p2

    # 4. Unpin P1
    manager.unpin_post(p1.post_id, "host_wallet", 3200, is_authorized=True)
    assert p1.is_pinned is False
    posts = manager.get_posts_by_space(space_id)
    assert posts == [p3, p2, p1]  # Back to normal order

    print(">>> Pinned Posts Logic Verified")


def test_quote_posts_logic():
    """Verify quote post linking."""
    cm = CertifiedMath()
    manager = WallPostManager(cm)
    space_id = "space_y"

    log_list = []
    # Original
    original = manager.create_post(
        space_id, "user_a", "Original Wisdom", 1000, log_list=log_list
    )

    # Quote
    quote = manager.create_post(
        space_id,
        "user_b",
        "This is cool",
        2000,
        quoted_post_id=original.post_id,
        log_list=log_list,
    )

    assert quote.quoted_post_id == original.post_id
    # Quote posts are just normal posts with metadata in this layer
    # The FeedGenerator layer (future) would expand Ids.

    print(">>> Quote Posts Logic Verified")


if __name__ == "__main__":
    test_pinned_posts_logic()
    test_quote_posts_logic()
