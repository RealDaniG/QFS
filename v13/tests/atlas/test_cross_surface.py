"""
Test Cross-Surface Logic (v14)
Verifies Recaps (Space->Wall) and References (Chat->Wall).
"""

import pytest

try:
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.atlas.spaces.wall_posts import WallPostManager
    from v13.atlas.chat.chat_session import ChatSessionManager
except ImportError:
    import sys
    import os

    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    )
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.atlas.spaces.wall_posts import WallPostManager
    from v13.atlas.chat.chat_session import ChatSessionManager


def test_recap_post_logic():
    """Verify Space Recaps are created and identifiable."""
    cm = CertifiedMath()
    manager = WallPostManager(cm)
    space_id = "space_recap_test"

    # Create Recap
    recap = manager.create_post(
        space_id, "host_wallet", "Incredible Space Summary", 1000, is_recap=True
    )

    assert recap.metadata.get("is_recap") is True
    assert recap.metadata.get("linked_space_id") == space_id

    # Create Normal Post
    normal = manager.create_post(space_id, "user_wallet", "Just a post", 2000)

    assert normal.metadata.get("is_recap") is None

    print(">>> Recap Post Logic Verified")
    return recap.post_id


def test_chat_references_logic():
    """Verify Chat referencing Wall Posts."""
    cm = CertifiedMath()
    chat_mgr = ChatSessionManager(cm)
    timestamp = 3000

    # Mock Post ID from previous test logic
    target_post_id = "mock_post_id_123"

    # 1. Create Session
    session = chat_mgr.create_session("owner_wallet", timestamp, [])

    # 2. Join Member
    chat_mgr.join_session(session.session_id, "member_wallet", timestamp, [])

    # 3. Send Message with Reference
    log_list = []
    msg = chat_mgr.send_message(
        session.session_id,
        "member_wallet",
        "Check this out",
        timestamp,
        "sig",
        log_list,
        references=[target_post_id],
    )

    # Verify Content
    assert msg.references == [target_post_id]

    # Verify Log
    log_entry = next(l for l in log_list if l["operation"] == "chat_message_dist")
    assert log_entry["references"] == [target_post_id]

    print(">>> Chat References Logic Verified")


if __name__ == "__main__":
    test_recap_post_logic()
    test_chat_references_logic()
