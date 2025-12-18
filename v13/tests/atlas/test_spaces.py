"""
Test Suite for ATLAS Spaces Module

Tests deterministic space lifecycle and event emission.
"""

import pytest
from typing import List, Dict, Any

from v13.libs.BigNum128 import BigNum128
from v13.libs.CertifiedMath import CertifiedMath
from v13.atlas.spaces.spaces_manager import (
    SpacesManager,
    Space,
    Participant,
    SpaceStatus,
    ParticipantRole,
)
from v13.atlas.spaces.spaces_events import (
    emit_space_created,
    emit_space_joined,
    emit_space_spoke,
    emit_space_ended,
)


@pytest.fixture
def cm():
    """CertifiedMath instance"""
    return CertifiedMath()


@pytest.fixture
def spaces_manager(cm):
    """SpacesManager instance"""
    return SpacesManager(cm, max_participants=10)


@pytest.fixture
def log_list():
    """Empty log list for tests"""
    return []


class TestSpacesManager:
    """Test SpacesManager functionality"""

    def test_create_space_deterministic_id(self, spaces_manager, log_list):
        """Test that space IDs are deterministic"""
        # Create same space twice with same inputs
        space1 = spaces_manager.create_space(
            host_wallet="wallet_123",
            title="Test Space",
            timestamp=1000000,
            log_list=log_list,
        )

        # Reset manager
        spaces_manager.active_spaces.clear()

        space2 = spaces_manager.create_space(
            host_wallet="wallet_123",
            title="Test Space",
            timestamp=1000000,
            log_list=log_list,
        )

        assert space1.space_id == space2.space_id
        assert space1.host_wallet == space2.host_wallet
        assert space1.created_at == space2.created_at

    def test_create_space_initializes_host(self, spaces_manager, log_list):
        """Test that host is added as participant on creation"""
        space = spaces_manager.create_space(
            host_wallet="host_wallet",
            title="Test Space",
            timestamp=1000000,
            log_list=log_list,
        )

        assert space.get_participant_count() == 1
        assert "host_wallet" in space.participants

        host_participant = space.get_participant("host_wallet")
        assert host_participant is not None
        assert host_participant.role == ParticipantRole.HOST

    def test_join_space(self, spaces_manager, log_list):
        """Test joining a space"""
        # Create space
        space = spaces_manager.create_space(
            host_wallet="host", title="Test", timestamp=1000000, log_list=log_list
        )

        # Join space
        participant = spaces_manager.join_space(
            space_id=space.space_id,
            participant_wallet="participant_1",
            timestamp=1000100,
            log_list=log_list,
        )

        assert participant.wallet_id == "participant_1"
        assert participant.role == ParticipantRole.LISTENER
        assert space.get_participant_count() == 2

    def test_join_space_max_participants(self, spaces_manager, log_list):
        """Test that max participants limit is enforced"""
        # Create space
        space = spaces_manager.create_space(
            host_wallet="host", title="Test", timestamp=1000000, log_list=log_list
        )

        # Fill space to max (10 total including host)
        for i in range(9):
            spaces_manager.join_space(
                space_id=space.space_id,
                participant_wallet=f"participant_{i}",
                timestamp=1000100 + i,
                log_list=log_list,
            )

        # Try to join when full
        with pytest.raises(ValueError, match="is full"):
            spaces_manager.join_space(
                space_id=space.space_id,
                participant_wallet="participant_overflow",
                timestamp=1001000,
                log_list=log_list,
            )

    def test_leave_space(self, spaces_manager, log_list):
        """Test leaving a space"""
        # Create and join
        space = spaces_manager.create_space(
            host_wallet="host", title="Test", timestamp=1000000, log_list=log_list
        )

        spaces_manager.join_space(
            space_id=space.space_id,
            participant_wallet="participant_1",
            timestamp=1000100,
            log_list=log_list,
        )

        assert space.get_participant_count() == 2

        # Leave
        spaces_manager.leave_space(
            space_id=space.space_id,
            participant_wallet="participant_1",
            timestamp=1000200,
            log_list=log_list,
        )

        assert space.get_participant_count() == 1
        assert "participant_1" not in space.participants

    def test_host_cannot_leave_with_participants(self, spaces_manager, log_list):
        """Test that host cannot leave while others are present"""
        space = spaces_manager.create_space(
            host_wallet="host", title="Test", timestamp=1000000, log_list=log_list
        )

        spaces_manager.join_space(
            space_id=space.space_id,
            participant_wallet="participant_1",
            timestamp=1000100,
            log_list=log_list,
        )

        # Host tries to leave
        with pytest.raises(ValueError, match="Host cannot leave"):
            spaces_manager.leave_space(
                space_id=space.space_id,
                participant_wallet="host",
                timestamp=1000200,
                log_list=log_list,
            )

    def test_end_space(self, spaces_manager, log_list):
        """Test ending a space"""
        space = spaces_manager.create_space(
            host_wallet="host", title="Test", timestamp=1000000, log_list=log_list
        )

        # End space
        ended_space = spaces_manager.end_space(
            space_id=space.space_id,
            host_wallet="host",
            timestamp=1001000,
            log_list=log_list,
        )

        assert ended_space.status == SpaceStatus.ENDED
        assert space.space_id not in spaces_manager.active_spaces

    def test_only_host_can_end_space(self, spaces_manager, log_list):
        """Test that only host can end space"""
        space = spaces_manager.create_space(
            host_wallet="host", title="Test", timestamp=1000000, log_list=log_list
        )

        spaces_manager.join_space(
            space_id=space.space_id,
            participant_wallet="participant_1",
            timestamp=1000100,
            log_list=log_list,
        )

        # Non-host tries to end
        with pytest.raises(ValueError, match="Only host can end"):
            spaces_manager.end_space(
                space_id=space.space_id,
                host_wallet="participant_1",
                timestamp=1001000,
                log_list=log_list,
            )

    def test_record_speak_time(self, spaces_manager, log_list):
        """Test recording speaking time"""
        space = spaces_manager.create_space(
            host_wallet="host", title="Test", timestamp=1000000, log_list=log_list
        )

        spaces_manager.join_space(
            space_id=space.space_id,
            participant_wallet="speaker",
            timestamp=1000100,
            role=ParticipantRole.SPEAKER,
            log_list=log_list,
        )

        # Record speak time
        spaces_manager.record_speak_time(
            space_id=space.space_id,
            participant_wallet="speaker",
            duration_seconds=120,
            log_list=log_list,
        )

        participant = space.get_participant("speaker")
        assert participant.speak_duration == 120

        # Record more time
        spaces_manager.record_speak_time(
            space_id=space.space_id,
            participant_wallet="speaker",
            duration_seconds=60,
            log_list=log_list,
        )

        assert participant.speak_duration == 180

    def test_list_active_spaces_deterministic_order(self, spaces_manager, log_list):
        """Test that active spaces list is deterministically ordered"""
        # Create multiple spaces
        space1 = spaces_manager.create_space(
            host_wallet="host1", title="Space 1", timestamp=1000000, log_list=log_list
        )

        space2 = spaces_manager.create_space(
            host_wallet="host2", title="Space 2", timestamp=1000100, log_list=log_list
        )

        space3 = spaces_manager.create_space(
            host_wallet="host3", title="Space 3", timestamp=1000050, log_list=log_list
        )

        # Get list
        active_spaces = spaces_manager.list_active_spaces()

        # Should be ordered by creation time
        assert len(active_spaces) == 3
        assert active_spaces[0].space_id == space1.space_id
        assert active_spaces[1].space_id == space3.space_id
        assert active_spaces[2].space_id == space2.space_id


class TestSpacesEvents:
    """Test event emission for spaces"""

    def test_emit_space_created(self, cm, log_list):
        """Test space_created event emission"""
        space = Space(
            space_id="test_space_id",
            host_wallet="host_wallet",
            title="Test Space",
            created_at=1000000,
            participants={},
            status=SpaceStatus.ACTIVE,
            metadata={},
        )

        event = emit_space_created(space, cm, log_list, pqc_cid="test_cid")

        assert event.event_type == "space_created"
        assert event.wallet_id == "host_wallet"
        assert event.token_type == "CHR"
        assert event.timestamp == 1000000
        assert "space_id" in event.metadata

    def test_emit_space_joined(self, cm, log_list):
        """Test space_joined event emission"""
        event = emit_space_joined(
            space_id="test_space",
            participant_wallet="participant_wallet",
            timestamp=1000100,
            cm=cm,
            log_list=log_list,
            pqc_cid="test_cid",
        )

        assert event.event_type == "space_joined"
        assert event.wallet_id == "participant_wallet"
        assert event.token_type == "FLX"
        assert event.timestamp == 1000100

    def test_emit_space_spoke_reward_calculation(self, cm, log_list):
        """Test space_spoke event with correct reward calculation"""
        # 5 minutes of speaking
        event = emit_space_spoke(
            space_id="test_space",
            participant_wallet="speaker_wallet",
            speak_duration_seconds=300,
            timestamp=1000200,
            cm=cm,
            log_list=log_list,
            pqc_cid="test_cid",
        )

        assert event.event_type == "space_spoke"
        assert event.wallet_id == "speaker_wallet"
        assert event.token_type == "CHR"

        # Verify reward calculation (5 minutes * 0.05 CHR/min = 0.25 CHR)
        expected_reward = BigNum128.from_string("250000000000000000")
        actual_reward = BigNum128.from_string(event.amount)
        assert actual_reward.value == expected_reward.value

    def test_emit_space_ended_duration_bonus(self, cm, log_list):
        """Test space_ended event with duration bonus"""
        space = Space(
            space_id="test_space_id",
            host_wallet="host_wallet",
            title="Test Space",
            created_at=1000000,
            participants={},
            status=SpaceStatus.ACTIVE,
            metadata={},
        )

        # End after 30 minutes
        end_timestamp = 1000000 + (30 * 60)

        event = emit_space_ended(space, end_timestamp, cm, log_list, pqc_cid="test_cid")

        assert event.event_type == "space_ended"
        assert event.wallet_id == "host_wallet"
        assert event.token_type == "CHR"

        # Verify duration bonus (30 minutes * 0.01 CHR/min = 0.3 CHR)
        expected_bonus = BigNum128.from_string("300000000000000000")
        actual_bonus = BigNum128.from_string(event.amount)
        assert actual_bonus.value == expected_bonus.value


class TestSpacesIntegration:
    """Integration tests for full space lifecycle"""

    def test_full_space_lifecycle_with_events(self, spaces_manager, cm, log_list):
        """Test complete space lifecycle with event emission"""
        # Create space
        # Create space - Manager emits event
        space = spaces_manager.create_space(
            host_wallet="host",
            title="Integration Test Space",
            timestamp=1000000,
            log_list=log_list,
        )

        # Join space - Manager emits event
        spaces_manager.join_space(
            space_id=space.space_id,
            participant_wallet="participant_1",
            timestamp=1000100,
            role=ParticipantRole.SPEAKER,
            log_list=log_list,
        )

        # Record speaking - Manager emits event
        spaces_manager.record_speak_time(
            space_id=space.space_id,
            participant_wallet="participant_1",
            duration_seconds=600,  # 10 minutes
            timestamp=1000700,
            log_list=log_list,
        )

        # End space - Manager emits event
        ended_space = spaces_manager.end_space(
            space_id=space.space_id,
            host_wallet="host",
            timestamp=1002000,
            log_list=log_list,
        )

        # Verify all events logged
        event_logs = [
            log for log in log_list if log.get("operation") == "event_emitted"
        ]
        assert len(event_logs) == 4
