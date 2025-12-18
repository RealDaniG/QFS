"""
Unit tests for Wall Posts Module
"""

import pytest
from typing import Dict, Any, List
from v13.atlas.spaces.wall_posts import WallPostManager, WallPost
from v13.atlas.spaces.wall_posts_events import (
    emit_post_created,
    emit_post_liked,
    emit_post_replied,
    EconomicEvent,
)
from v13.libs.CertifiedMath import CertifiedMath
from v13.libs.BigNum128 import BigNum128


class MockCertifiedMath:
    def imul(self, a, b, log_list=None):
        return BigNum128.from_string(
            str(int(a.to_decimal_string().replace(".", "")) * b)
        )  # Simplistic mock


@pytest.fixture
def cm():
    return CertifiedMath()  # logic is self-contained or mocked if heavily dependent


@pytest.fixture
def wall_manager(cm):
    return WallPostManager(cm)


def test_create_post(wall_manager):
    log_list = []
    post = wall_manager.create_post(
        space_id="space123",
        author_wallet="walletA",
        content="Hello World",
        timestamp=1000,
        log_list=log_list,
    )

    assert post.space_id == "space123"
    assert post.author_wallet == "walletA"
    assert post.content == "Hello World"
    assert post.post_id is not None
    assert len(log_list) == 1
    assert log_list[0]["operation"] == "wall_post_created"

    # Determinism check
    post2 = wall_manager.create_post(
        space_id="space123",
        author_wallet="walletA",
        content="Hello World",
        timestamp=1000,
        log_list=[],
    )
    assert post.post_id == post2.post_id


def test_like_post(wall_manager):
    post = wall_manager.create_post("space1", "user1", "msg", 1000)
    log_list = []

    wall_manager.like_post(post.post_id, "user2", 1010, log_list)

    assert post.is_liked_by("user2")
    assert post.get_like_count() == 1
    assert len(log_list) == 1
    assert log_list[0]["operation"] == "wall_post_liked"

    # Idempotency
    wall_manager.like_post(post.post_id, "user2", 1020, log_list)
    assert post.get_like_count() == 1  # Count shouldn't increase


def test_reply_to_post(wall_manager):
    parent = wall_manager.create_post("space1", "user1", "msg", 1000)
    log_list = []

    reply = wall_manager.reply_to_post(
        parent.post_id, "user2", "reply msg", 1010, log_list
    )

    assert reply.space_id == parent.space_id
    assert reply.metadata["parent_post_id"] == parent.post_id
    assert reply.post_id in parent.replies
    assert len(log_list) == 2  # created + reply_linked


def test_post_creation_event(cm):
    post = WallPost("post1", "space1", "user1", "msg", 1000)
    log_list = []

    event = emit_post_created(post, cm, log_list)

    assert event.event_type == "wall_post_created"
    assert event.amount == "500000000000000000"  # 0.5 FLX
    assert len(log_list) == 1


def test_post_liked_event(cm):
    log_list = []
    event = emit_post_liked("post1", "user2", "user1", 1010, cm, log_list)

    assert event.event_type == "wall_post_liked"
    assert event.wallet_id == "user1"  # Author rewarded
    assert event.amount == "1000000000000000"  # 0.001 CHR


def test_post_reply_events(cm):
    parent_author = "user1"
    reply_post = WallPost(
        "reply1", "space1", "user2", "reply", 1010, metadata={"parent_post_id": "post1"}
    )
    log_list = []

    events = emit_post_replied(reply_post, parent_author, cm, log_list)

    assert len(events) == 2
    # 1. Creation reward
    assert events[0].event_type == "wall_reply_created"
    assert events[0].wallet_id == "user2"

    # 2. Engagement reward
    assert events[1].event_type == "wall_post_reply_received"
    assert events[1].wallet_id == "user1"
