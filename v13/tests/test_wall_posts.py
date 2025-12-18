"""
Unit tests for Wall Posts Module
Strict Zero-Sim Compliance: Real Math, Determinism, Error Scenarios
"""

import pytest
from typing import Dict, Any, List
from v13.atlas.spaces.wall_posts import WallPostManager, WallPost
from v13.atlas.spaces.wall_posts_events import (
    emit_post_created,
    emit_post_liked,
    emit_post_replied,
)

from v13.atlas.economic_event import EconomicEvent
from v13.libs.CertifiedMath import CertifiedMath
from v13.libs.BigNum128 import BigNum128


@pytest.fixture
def cm():
    """Real CertifiedMath instance for strict testing"""
    return CertifiedMath()


@pytest.fixture
def wall_manager(cm):
    return WallPostManager(cm)


def test_create_post_determinism(wall_manager, cm):
    """Verify that posting with identical inputs produces identical IDs and state."""
    log_list = []

    # First creation
    post1 = wall_manager.create_post(
        space_id="space_det_1",
        author_wallet="wallet_A",
        content="Deterministic Content",
        timestamp=1000000,
        log_list=log_list,
    )

    # Reset manager but keep inputs
    wall_manager2 = WallPostManager(cm)

    # Second creation
    post2 = wall_manager2.create_post(
        space_id="space_det_1",
        author_wallet="wallet_A",
        content="Deterministic Content",
        timestamp=1000000,
        log_list=[],
    )

    assert post1.post_id == post2.post_id, "Post IDs must be deterministic"
    assert post1.space_id == post2.space_id
    assert post1.content == post2.content
    assert post1.timestamp == post2.timestamp


def test_like_post_idempotency_and_logic(wall_manager):
    """Verify linking logic and idempotency."""
    post = wall_manager.create_post("space_1", "user_1", "content", 1000)
    log_list = []

    # First like
    wall_manager.like_post(post.post_id, "user_2", 1010, log_list)
    assert post.is_liked_by("user_2")
    assert post.get_like_count() == 1
    assert log_list[0]["operation"] == "wall_post_liked"

    # Second like (Idempotent)
    wall_manager.like_post(post.post_id, "user_2", 1020, log_list)
    assert post.get_like_count() == 1
    assert len(log_list) == 1  # Should not log duplicate action


def test_reply_structure(wall_manager):
    """Verify parent-child linking."""
    parent = wall_manager.create_post("space_1", "user_1", "parent", 1000)

    child = wall_manager.reply_to_post(parent.post_id, "user_2", "child", 1010)

    assert child.space_id == parent.space_id
    assert child.metadata["parent_post_id"] == parent.post_id
    assert child.post_id in parent.replies


def test_error_conditions(wall_manager):
    """Verify error handling for invalid operations."""

    # Like non-existent post
    with pytest.raises(ValueError, match="not found"):
        wall_manager.like_post("fake_id", "user_1", 1000)

    # Reply to non-existent post
    with pytest.raises(ValueError, match="not found"):
        wall_manager.reply_to_post("fake_id", "user_1", "reply", 1000)


def test_economic_event_correctness(cm):
    """Verify EconomicEvents have correct types and BigNum amounts."""
    post = WallPost("post_id_1", "space_id_1", "author_1", "content", 1000)
    log_list = []

    # 1. Post Creation (0.5 FLX)
    event = emit_post_created(post, cm, log_list)

    assert event.event_type == "wall_post_created"
    assert event.token_type == "FLX"
    # 0.5 * 10^18 = 500000000000000000
    expected_flx = BigNum128.from_string("0.5").to_decimal_string()
    assert BigNum128.from_string(event.amount).to_decimal_string() == expected_flx

    # 2. Like (0.001 CHR)
    event_like = emit_post_liked("post_id_1", "liker", "author_1", 1010, cm, log_list)
    assert event_like.event_type == "wall_post_liked"
    assert event_like.token_type == "CHR"
    assert event_like.wallet_id == "author_1"  # Recipient is author

    expected_chr = BigNum128.from_string("0.001").to_decimal_string()
    assert BigNum128.from_string(event_like.amount).to_decimal_string() == expected_chr


def test_event_determinism_deep(cm):
    """Verify strict structural equality of events on re-emission."""
    post = WallPost("post_det", "space_det", "author_det", "content", 2000)

    # Run 1
    log1 = []
    event1 = emit_post_created(post, cm, log1, pqc_cid="CID_1")

    # Run 2
    log2 = []
    event2 = emit_post_created(post, cm, log2, pqc_cid="CID_1")

    assert event1.event_id == event2.event_id
    assert event1.amount == event2.amount
    assert event1.metadata == event2.metadata
    assert event1 == event2  # Dataclass equality


def test_full_engagement_flow(wall_manager, cm):
    """Integration scenario: Create -> Like -> Reply -> Reply Received."""
    log_list = []

    # 1. Author creates post
    post = wall_manager.create_post(
        "space_flow", "author", "Hello", 1000, log_list=log_list
    )
    evt_create = emit_post_created(post, cm, log_list)

    assert evt_create.wallet_id == "author"

    # 2. Liker likes
    wall_manager.like_post(post.post_id, "liker", 1010, log_list=log_list)
    evt_like = emit_post_liked(post.post_id, "liker", "author", 1010, cm, log_list)

    assert evt_like.wallet_id == "author"  # Author gets reward

    # 3. Replier replies
    reply = wall_manager.reply_to_post(
        post.post_id, "replier", "Hi", 1020, log_list=log_list
    )
    reply_events = emit_post_replied(reply, "author", cm, log_list)

    # Verify reply events
    assert len(reply_events) == 2

    # Event A: Replier Creation Reward
    assert reply_events[0].event_type == "wall_reply_created"
    assert reply_events[0].wallet_id == "replier"

    # Event B: Author Engagement Reward
    assert reply_events[1].event_type == "wall_post_reply_received"
    assert reply_events[1].wallet_id == "author"

    # Log integrity
    ops = [l["operation"] for l in log_list]
    assert "wall_post_created" in ops
    assert "wall_post_liked" in ops
    assert "wall_post_reply_linked" in ops
    assert "event_emitted" in ops
