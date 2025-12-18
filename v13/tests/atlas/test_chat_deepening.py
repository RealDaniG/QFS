"""
Test Chat Deepening (v14)
Verifies Group Chat Creation, Participant Authorization (Removal), and TTL Schema.
"""

import pytest

try:
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.atlas.chat.chat_session import ChatSessionManager
except ImportError:
    import sys
    import os

    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    )
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.atlas.chat.chat_session import ChatSessionManager


def test_group_chat_creation():
    """Verify group creation with initial members."""
    cm = CertifiedMath()
    manager = ChatSessionManager(cm)
    timestamp = 1000

    owner = "wallet_owner"
    members = [
        "wallet_a",
        "wallet_b",
        "wallet_owner",
    ]  # Owner included to check duplicate handling

    log_list = []
    session = manager.create_session(
        owner, timestamp, log_list, initial_members=members, ttl_seconds=3600
    )

    # Check participants
    assert len(session.participants) == 3  # Owner + A + B
    assert "wallet_a" in session.participants
    assert "wallet_b" in session.participants
    assert session.participants["wallet_a"].role == "member"
    assert session.participants[owner].role == "owner"

    # Check TTL
    assert session.ttl_seconds == 3600

    print(">>> Group Creation Verified")


def test_participant_removal_logic():
    """Verify kick permissions."""
    cm = CertifiedMath()
    manager = ChatSessionManager(cm)
    timestamp = 1000

    owner = "wallet_owner"
    member_a = "wallet_a"
    member_b = "wallet_b"

    log_list = []
    # Create group session properly
    session = manager.create_session(
        owner, timestamp, log_list, initial_members=[member_a, member_b]
    )
    session_id = session.session_id

    # 1. Member tries to kick another member (Fail)
    with pytest.raises(PermissionError):
        manager.remove_participant(
            session_id, target_wallet=member_b, req_wallet=member_a, log_list=log_list
        )

    # 2. Member tries to leave (Success)
    manager.remove_participant(
        session_id, target_wallet=member_a, req_wallet=member_a, log_list=log_list
    )
    assert member_a not in session.participants

    # 3. Owner kicks remaining member B (Success)
    manager.remove_participant(
        session_id, target_wallet=member_b, req_wallet=owner, log_list=log_list
    )
    assert member_b not in session.participants

    # 4. Owner tries to kick invalid member (Fail)
    with pytest.raises(ValueError, match="not in session"):
        manager.remove_participant(
            session_id, target_wallet="ghost", req_wallet=owner, log_list=log_list
        )

    print(">>> Participant Removal Logic Verified")


if __name__ == "__main__":
    test_group_chat_creation()
    test_participant_removal_logic()
