"""
Unit tests for ATLAS Secure Chat Module
"""

import pytest
from typing import Dict, Any, List
from v13.atlas.chat.chat_session import ChatSessionManager
from v13.libs.CertifiedMath import CertifiedMath
from v13.libs.BigNum128 import BigNum128


@pytest.fixture
def cm():
    """Real CertifiedMath instance for strict testing"""
    return CertifiedMath()


@pytest.fixture
def chat_manager(cm):
    return ChatSessionManager(cm)


def test_chat_creation_determinism(chat_manager):
    """Verify strictly deterministic session IDs."""
    log_list = []

    # Run 1
    session1 = chat_manager.create_session("owner_1", 1000, log_list)

    # Run 2 (New manager)
    cm2 = CertifiedMath()
    mgr2 = ChatSessionManager(cm2)
    session2 = mgr2.create_session("owner_1", 1000, [])

    assert session1.session_id == session2.session_id
    assert session1.owner_wallet == session2.owner_wallet
    assert "active" == session1.status


def test_join_logic(chat_manager):
    """Verify join mechanics and idempotency."""
    log_list = []
    session = chat_manager.create_session("owner", 1000, log_list)

    # Owner is implicit participant
    assert "owner" in session.participants

    # Join new user
    user = chat_manager.join_session(session.session_id, "user_2", 1010, log_list)
    assert "user_2" in session.participants
    assert user.role == "member"

    # Re-join (Idempotent)
    user_again = chat_manager.join_session(session.session_id, "user_2", 1020, log_list)
    assert user_again == user

    # Check logs
    ops = [l["operation"] for l in log_list]
    assert "chat_session_created" in ops
    assert "chat_participant_joined" in ops


def test_message_flow(chat_manager):
    """Verify sending messages and ensuring non-participants cannot send."""
    log_list = []
    session = chat_manager.create_session("owner", 1000, log_list)

    # Non-participant send attempt
    with pytest.raises(ValueError, match="not a participant"):
        chat_manager.send_message(
            session.session_id, "intruder", "hex_cipher", 1010, "sig", log_list
        )

    # Valid send
    msg = chat_manager.send_message(
        session.session_id, "owner", "hex_cipher", 1010, "sig", log_list
    )

    assert msg.session_id == session.session_id
    assert msg.author_wallet == "owner"
    assert len(session.messages) == 1
    assert log_list[-1]["operation"] == "chat_message_dist"


def test_economic_events(cm):
    """Verify chat events produce correct cost amounts."""
    log_list = []
    mgr = ChatSessionManager(cm)

    # Create Session (1.0 FLX)
    session = mgr.create_session("owner", 1000, log_list)

    # Find event
    evt_create = None
    for item in log_list:
        if (
            item.get("operation") == "event_emitted"
            and item.get("event_type") == "chat_created"
        ):
            # In a real system, the event object might be captured differently,
            # but here we rely on the fact that emit_ returns the object.
            # We can't access the return value of emit_ inside create_session easily
            # without mocking, so let's call emit function directly to verify math.
            pass

    # Direct verify of emitter logic
    from v13.atlas.chat.chat_events import emit_chat_created

    evt = emit_chat_created("sid", "owner", 1000, cm, [])
    expected_flx = BigNum128.from_string("1.0").to_decimal_string()
    assert BigNum128.from_string(evt.amount).to_decimal_string() == expected_flx


def test_end_session(chat_manager):
    """Verify ending session constraints."""
    log = []
    session = chat_manager.create_session("owner", 1000, log)

    # Non-owner try
    with pytest.raises(PermissionError):
        chat_manager.end_session(session.session_id, "other", 1010, log)

    chat_manager.end_session(session.session_id, "owner", 1020, log)
    assert session.status == "ended"

    # Try sending to ended session
    with pytest.raises(ValueError, match="not active"):
        chat_manager.send_message(
            session.session_id, "owner", "cipher", 1030, "sig", log
        )
