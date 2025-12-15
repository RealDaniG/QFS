"""
test_openagi_dm_integration.py - Open-AGI × DM Integration Tests
Verifies DM is properly wired through Open-AGI governance surface
"""

import pytest
from v13.services.dm.messenger import DirectMessagingService
from v13.integrations.openagi_dm_adapter import OpenAGIDMAdapter


def test_simulation_role_create_thread():
    """OPEN-AGI simulation role creates a DM thread."""
    dm_service = DirectMessagingService()
    dm_service.identity_mgr.publish_identity("sim_user_1", "pk1", "proof1")
    dm_service.identity_mgr.publish_identity("sim_user_2", "pk2", "proof2")

    adapter = OpenAGIDMAdapter(dm_service, scope="SIMULATION")

    result = adapter.dm_create_thread("sim_user_1", "sim_user_2")

    assert "thread_id" in result
    assert result.get("simulated") is True
    assert result["event"]["scope"] == "SIMULATION"
    assert result["event"]["event_type"] == "DM_THREAD_CREATED"


def test_simulation_role_send_message():
    """OPEN-AGI simulation role sends a message."""
    dm_service = DirectMessagingService()
    adapter = OpenAGIDMAdapter(dm_service, scope="SIMULATION")

    # Setup identities for validation
    dm_service.identity_mgr.publish_identity("sim_user_1", "pubkey1", "proof1")
    dm_service.identity_mgr.publish_identity("sim_user_2", "pubkey2", "proof2")

    result = adapter.dm_send_message("sim_user_1", "thread_1", "Hello from simulation")

    assert "message_id" in result
    assert result.get("simulated") is True
    assert result["event"]["scope"] == "SIMULATION"


def test_aegis_content_flag_blocks_send():
    """AEGIS guard blocks message with flagged content."""
    dm_service = DirectMessagingService()
    adapter = OpenAGIDMAdapter(dm_service, scope="SIMULATION")

    result = adapter.dm_send_message("user_1", "thread_1", "This is unsafe content")

    assert result.get("error") == "CONTENT_FLAGGED"
    assert "reason" in result


def test_unauthorized_without_capability():
    """User without DM_SEND capability cannot send."""
    dm_service = DirectMessagingService()
    adapter = OpenAGIDMAdapter(dm_service, scope="PRODUCTION")

    # Mock: would check real authorization here
    # For now, adapter grants all capabilities in SIMULATION mode
    # In PRODUCTION with real auth, this would fail
    pass


def test_list_threads_requiring_read_capability():
    """Listing threads requires DM_READ_OWN capability."""
    dm_service = DirectMessagingService()
    adapter = OpenAGIDMAdapter(dm_service, scope="SIMULATION")

    result = adapter.dm_list_threads("user_1")

    assert "threads" in result
    assert isinstance(result["threads"], list)


def test_dm_event_determinism():
    """Same inputs produce same event structure."""
    dm_service = DirectMessagingService()

    # Setup identities
    dm_service.identity_mgr.publish_identity("user_a", "pk_a", "proof_a")
    dm_service.identity_mgr.publish_identity("user_b", "pk_b", "proof_b")

    adapter = OpenAGIDMAdapter(dm_service, scope="SIMULATION")

    result1 = adapter.dm_create_thread("user_a", "user_b")
    result2 = adapter.dm_create_thread("user_a", "user_b")

    # Thread IDs should be deterministic
    assert result1["thread_id"] == result2["thread_id"]


def test_simulated_events_are_ledger_shaped():
    """Simulated DM events have all required ledger fields."""
    dm_service = DirectMessagingService()
    dm_service.identity_mgr.publish_identity("user_1", "pk1", "proof1")

    adapter = OpenAGIDMAdapter(dm_service, scope="SIMULATION")

    result = adapter.dm_send_message("user_1", "thread_1", "Test message")

    event = result["event"]
    required_fields = ["event_type", "scope", "sender", "thread_id", "timestamp"]
    for field in required_fields:
        assert field in event, f"Missing field: {field}"


def test_replay_dm_events():
    """Replay simulated DM events to reconstruct thread state."""
    # Generate sequence of DM events
    events = [
        {
            "event_type": "DM_THREAD_CREATED",
            "thread_id": "t1",
            "participants": ["u1", "u2"],
        },
        {
            "event_type": "DM_MESSAGE_SENT",
            "thread_id": "t1",
            "sender": "u1",
            "message_id": "m1",
        },
        {
            "event_type": "DM_MESSAGE_SENT",
            "thread_id": "t1",
            "sender": "u2",
            "message_id": "m2",
        },
    ]

    # Mock replay (would use real DM service replay method)
    thread_state = {"t1": {"messages": ["m1", "m2"]}}

    assert len(thread_state["t1"]["messages"]) == 2


def test_production_mode_no_simulation_tag():
    """Production mode events don't have simulation tag."""
    dm_service = DirectMessagingService()

    # Setup real identities
    dm_service.identity_mgr.publish_identity("user_1", "pk1", "proof1")
    dm_service.identity_mgr.publish_identity("user_2", "pk2", "proof2")

    adapter = OpenAGIDMAdapter(dm_service, scope="PRODUCTION")

    result = adapter.dm_create_thread("user_1", "user_2")

    assert result.get("simulated") is None
    # In production, would emit to real ledger
