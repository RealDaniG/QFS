"""
Test Suite for ATLAS Wall Posts Module

Tests deterministic post lifecycle, feed resolution, and event emission.
"""

import pytest
from typing import List, Dict, Any

from v13.libs.BigNum128 import BigNum128
from v13.libs.CertifiedMath import CertifiedMath
from v13.atlas.wall import (
    WallService,
    FeedResolver,
    Post,
    PostType,
    Visibility,
    emit_post_created,
    emit_post_quoted,
    emit_post_pinned,
    emit_post_reacted,
)
from v13.atlas.spaces import SpacesManager


@pytest.fixture
def cm():
    """CertifiedMath instance"""
    return CertifiedMath()


@pytest.fixture
def spaces_manager(cm):
    """SpacesManager instance"""
    return SpacesManager(cm, max_participants=10)


@pytest.fixture
def wall_service(cm, spaces_manager):
    """WallService instance"""
    return WallService(cm, spaces_manager)


@pytest.fixture
def feed_resolver(wall_service):
    """FeedResolver instance"""
    return FeedResolver(wall_service)


@pytest.fixture
def log_list():
    """Empty log list for tests"""
    return []


class TestWallService:
    """Test WallService functionality"""

    def test_create_post_deterministic_id(self, wall_service, log_list):
        """Test that post IDs are deterministic"""
        # Create same post twice with same inputs
        post1 = wall_service.create_post(
            author_wallet="author123",
            content="Test post",
            timestamp=1000000,
            log_list=log_list,
        )

        # Reset service
        wall_service.posts.clear()

        post2 = wall_service.create_post(
            author_wallet="author123",
            content="Test post",
            timestamp=1000000,
            log_list=log_list,
        )

        assert post1.post_id == post2.post_id
        assert post1.content_hash == post2.content_hash
        assert post1.created_at == post2.created_at

    def test_create_post_with_space_link(self, wall_service, spaces_manager, log_list):
        """Test post creation linked to space"""
        # Create space first
        space = spaces_manager.create_space(
            host_wallet="host123",
            title="Test Space",
            timestamp=1000000,
            log_list=log_list,
        )

        # Create post linked to space
        post = wall_service.create_post(
            author_wallet="author123",
            content="Space post",
            timestamp=1000100,
            space_id=space.space_id,
            visibility=Visibility.SPACE_ONLY,
            log_list=log_list,
        )

        assert post.space_id == space.space_id
        assert post.visibility == Visibility.SPACE_ONLY

    def test_create_post_invalid_space(self, wall_service, log_list):
        """Test that creating post with invalid space fails"""
        with pytest.raises(ValueError, match="not found"):
            wall_service.create_post(
                author_wallet="author123",
                content="Test",
                timestamp=1000000,
                space_id="invalid_space_id",
                log_list=log_list,
            )

    def test_quote_post(self, wall_service, log_list):
        """Test quoting another post"""
        # Create original post
        original = wall_service.create_post(
            author_wallet="author1",
            content="Original post",
            timestamp=1000000,
            log_list=log_list,
        )

        # Quote the post
        quote = wall_service.quote_post(
            author_wallet="author2",
            parent_post_id=original.post_id,
            content="Quoting this!",
            timestamp=1000100,
            log_list=log_list,
        )

        assert quote.post_type == PostType.QUOTE
        assert quote.parent_post_id == original.post_id
        assert quote.is_quote()
        assert quote.visibility == original.visibility

    def test_quote_invalid_post(self, wall_service, log_list):
        """Test that quoting invalid post fails"""
        with pytest.raises(ValueError, match="not found"):
            wall_service.quote_post(
                author_wallet="author123",
                parent_post_id="invalid_post_id",
                content="Quote",
                timestamp=1000000,
                log_list=log_list,
            )

    def test_pin_post(self, wall_service, spaces_manager, log_list):
        """Test pinning a post"""
        # Create space
        space = spaces_manager.create_space(
            host_wallet="host123",
            title="Test Space",
            timestamp=1000000,
            log_list=log_list,
        )

        # Create post in space
        post = wall_service.create_post(
            author_wallet="author123",
            content="Test post",
            timestamp=1000100,
            space_id=space.space_id,
            log_list=log_list,
        )

        # Pin post (as host)
        pinned = wall_service.pin_post(
            post_id=post.post_id,
            pinner_wallet="host123",
            timestamp=1000200,
            log_list=log_list,
        )

        assert pinned.is_pinned()
        assert pinned.pin_timestamp == 1000200

    def test_pin_post_non_host(self, wall_service, spaces_manager, log_list):
        """Test that non-host cannot pin posts"""
        # Create space
        space = spaces_manager.create_space(
            host_wallet="host123",
            title="Test Space",
            timestamp=1000000,
            log_list=log_list,
        )

        # Create post
        post = wall_service.create_post(
            author_wallet="author123",
            content="Test",
            timestamp=1000100,
            space_id=space.space_id,
            log_list=log_list,
        )

        # Try to pin as non-host
        with pytest.raises(ValueError, match="Only space host"):
            wall_service.pin_post(
                post_id=post.post_id,
                pinner_wallet="not_host",
                timestamp=1000200,
                log_list=log_list,
            )

    def test_add_reaction(self, wall_service, log_list):
        """Test adding reactions to post"""
        post = wall_service.create_post(
            author_wallet="author123",
            content="Test post",
            timestamp=1000000,
            log_list=log_list,
        )

        # Add reaction
        wall_service.add_reaction(
            post_id=post.post_id,
            reactor_wallet="reactor1",
            emoji="👍",
            log_list=log_list,
        )

        assert post.reactions["👍"] == 1

        # Add same reaction again
        wall_service.add_reaction(
            post_id=post.post_id,
            reactor_wallet="reactor2",
            emoji="👍",
            log_list=log_list,
        )

        assert post.reactions["👍"] == 2


class TestFeedResolver:
    """Test FeedResolver functionality"""

    def test_resolve_feed_deterministic_order(
        self, wall_service, feed_resolver, log_list
    ):
        """Test that feed ordering is deterministic"""
        # Create multiple posts
        post1 = wall_service.create_post(
            author_wallet="author1",
            content="Post 1",
            timestamp=1000000,
            log_list=log_list,
        )

        post2 = wall_service.create_post(
            author_wallet="author2",
            content="Post 2",
            timestamp=1000100,
            log_list=log_list,
        )

        post3 = wall_service.create_post(
            author_wallet="author3",
            content="Post 3",
            timestamp=1000050,
            log_list=log_list,
        )

        # Resolve feed
        feed = feed_resolver.resolve_feed(viewer_wallet="viewer123")

        # Should be ordered by created_at DESC
        assert len(feed) == 3
        assert feed[0].post_id == post2.post_id  # Most recent
        assert feed[1].post_id == post3.post_id
        assert feed[2].post_id == post1.post_id  # Oldest

    def test_resolve_feed_pinned_first(
        self, wall_service, feed_resolver, spaces_manager, log_list
    ):
        """Test that pinned posts appear first"""
        # Create space
        space = spaces_manager.create_space(
            host_wallet="host123",
            title="Test Space",
            timestamp=1000000,
            log_list=log_list,
        )

        # Create posts
        post1 = wall_service.create_post(
            author_wallet="author1",
            content="Post 1",
            timestamp=1000100,
            space_id=space.space_id,
            log_list=log_list,
        )

        post2 = wall_service.create_post(
            author_wallet="author2",
            content="Post 2",
            timestamp=1000200,
            space_id=space.space_id,
            log_list=log_list,
        )

        # Pin first post (older)
        wall_service.pin_post(
            post_id=post1.post_id,
            pinner_wallet="host123",
            timestamp=1000300,
            log_list=log_list,
        )

        # Resolve feed
        feed = feed_resolver.resolve_feed(
            viewer_wallet="viewer123", space_id=space.space_id
        )

        # Pinned post should be first
        assert len(feed) == 2
        assert feed[0].post_id == post1.post_id  # Pinned
        assert feed[1].post_id == post2.post_id  # Regular

    def test_resolve_space_feed(
        self, wall_service, feed_resolver, spaces_manager, log_list
    ):
        """Test space-specific feed"""
        # Create two spaces
        space1 = spaces_manager.create_space(
            host_wallet="host1", title="Space 1", timestamp=1000000, log_list=log_list
        )

        space2 = spaces_manager.create_space(
            host_wallet="host2", title="Space 2", timestamp=1000100, log_list=log_list
        )

        # Create posts in different spaces
        post1 = wall_service.create_post(
            author_wallet="author1",
            content="Space 1 post",
            timestamp=1000200,
            space_id=space1.space_id,
            log_list=log_list,
        )

        post2 = wall_service.create_post(
            author_wallet="author2",
            content="Space 2 post",
            timestamp=1000300,
            space_id=space2.space_id,
            log_list=log_list,
        )

        # Resolve space 1 feed
        feed = feed_resolver.resolve_space_feed(
            space_id=space1.space_id, viewer_wallet="viewer123"
        )

        assert len(feed) == 1
        assert feed[0].post_id == post1.post_id

    def test_resolve_user_posts(self, wall_service, feed_resolver, log_list):
        """Test resolving posts by specific author"""
        # Create posts by different authors
        post1 = wall_service.create_post(
            author_wallet="author1",
            content="Author 1 post 1",
            timestamp=1000000,
            log_list=log_list,
        )

        post2 = wall_service.create_post(
            author_wallet="author2",
            content="Author 2 post",
            timestamp=1000100,
            log_list=log_list,
        )

        post3 = wall_service.create_post(
            author_wallet="author1",
            content="Author 1 post 2",
            timestamp=1000200,
            log_list=log_list,
        )

        # Resolve author1 posts
        feed = feed_resolver.resolve_user_posts(author_wallet="author1")

        assert len(feed) == 2
        assert feed[0].post_id == post3.post_id  # Most recent
        assert feed[1].post_id == post1.post_id


class TestWallEvents:
    """Test event emission for wall posts"""

    def test_emit_post_created(self, cm, log_list):
        """Test post_created event emission"""
        post = Post(
            post_id="test_post_id",
            author_wallet="author123",
            content="Test post",
            content_hash="abc123",
            created_at=1000000,
        )

        event = emit_post_created(post, cm, log_list)

        assert event.event_type == "post_created"
        assert event.wallet_id == "author123"
        assert event.token_type == "CHR"
        assert event.timestamp == 1000000

        # Verify reward (0.5 CHR)
        expected_reward = BigNum128.from_string("500000000000000000")
        actual_reward = BigNum128.from_string(event.amount)
        assert actual_reward.value == expected_reward.value

    def test_emit_post_quoted_reward(self, cm, log_list):
        """Test post_quoted event with correct reward"""
        parent = Post(
            post_id="parent_id",
            author_wallet="author1",
            content="Original",
            content_hash="abc",
            created_at=1000000,
        )

        quote = Post(
            post_id="quote_id",
            author_wallet="author2",
            content="Quote",
            content_hash="def",
            created_at=1000100,
            parent_post_id="parent_id",
            post_type=PostType.QUOTE,
        )

        event = emit_post_quoted(quote, parent, cm, log_list)

        assert event.event_type == "post_quoted"
        assert event.wallet_id == "author2"
        assert event.token_type == "CHR"

        # Verify reward (0.3 CHR)
        expected_reward = BigNum128.from_string("300000000000000000")
        actual_reward = BigNum128.from_string(event.amount)
        assert actual_reward.value == expected_reward.value

    def test_emit_post_pinned(self, cm, log_list):
        """Test post_pinned event emission"""
        post = Post(
            post_id="test_post_id",
            author_wallet="author123",
            content="Test",
            content_hash="abc",
            created_at=1000000,
            post_type=PostType.PINNED,
            pin_timestamp=1000100,
        )

        event = emit_post_pinned(post, "host123", cm, log_list)

        assert event.event_type == "post_pinned"
        assert event.wallet_id == "host123"
        assert event.token_type == "CHR"

        # Verify reward (0.2 CHR)
        expected_reward = BigNum128.from_string("200000000000000000")
        actual_reward = BigNum128.from_string(event.amount)
        assert actual_reward.value == expected_reward.value

    def test_emit_post_reacted(self, cm, log_list):
        """Test post_reacted event emission"""
        event = emit_post_reacted(
            post_id="test_post",
            reactor_wallet="reactor123",
            emoji="👍",
            timestamp=1000000,
            cm=cm,
            log_list=log_list,
        )

        assert event.event_type == "post_reacted"
        assert event.wallet_id == "reactor123"
        assert event.token_type == "FLX"

        # Verify reward (0.01 FLX)
        expected_reward = BigNum128.from_string("10000000000000000")
        actual_reward = BigNum128.from_string(event.amount)
        assert actual_reward.value == expected_reward.value


class TestWallIntegration:
    """Integration tests for full wall lifecycle"""

    def test_full_post_lifecycle_with_events(self, wall_service, cm, log_list):
        """Test complete post lifecycle with event emission"""
        # Create post
        post = wall_service.create_post(
            author_wallet="author123",
            content="Integration test post",
            timestamp=1000000,
            log_list=log_list,
        )

        event1 = emit_post_created(post, cm, log_list)
        assert event1.event_type == "post_created"

        # Quote post
        quote = wall_service.quote_post(
            author_wallet="author456",
            parent_post_id=post.post_id,
            content="Great post!",
            timestamp=1000100,
            log_list=log_list,
        )

        event2 = emit_post_quoted(quote, post, cm, log_list)
        assert event2.event_type == "post_quoted"

        # Add reaction
        wall_service.add_reaction(
            post_id=post.post_id,
            reactor_wallet="reactor789",
            emoji="❤️",
            log_list=log_list,
        )

        event3 = emit_post_reacted(
            post_id=post.post_id,
            reactor_wallet="reactor789",
            emoji="❤️",
            timestamp=1000200,
            cm=cm,
            log_list=log_list,
        )
        assert event3.event_type == "post_reacted"

        # Verify all events logged
        event_logs = [
            log for log in log_list if log.get("operation") == "event_emitted"
        ]
        assert len(event_logs) == 3
