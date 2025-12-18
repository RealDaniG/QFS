"""
Test Contracts (v14)
Verifies that internal logic objects convert correctly to Canonical Contracts.
"""

import pytest
import sys
import os

# Adapt path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# Internal Logic Modules
try:
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.atlas.spaces.spaces_manager import SpacesManager, ParticipantRole
    from v13.atlas.spaces.wall_posts import WallPostManager
    from v13.atlas.chat.chat_session import ChatSessionManager

    # Contracts
    from v13.atlas.contracts import (
        space_to_contract,
        post_to_contract,
        message_to_contract,
        AtlasSpace,
        AtlasWallPost,
        AtlasChatMessage,
    )
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)


def test_space_contract():
    """Verify Space -> AtlasSpace conversion."""
    cm = CertifiedMath()
    mgr = SpacesManager(cm)
    log_list = []

    # Create Internal
    space = mgr.create_space(
        "host_0x1", "Contract Test Space", 1000, {"category": "test"}, log_list
    )
    mgr.join_space(space.space_id, "user_0x2", 1001, log_list=log_list)

    # Convert
    contract = space_to_contract(space)

    # Assert
    assert isinstance(contract, AtlasSpace)
    assert contract.space_id == space.space_id
    assert contract.title == "Contract Test Space"
    assert contract.participant_count == 2
    assert contract.status.value == "active"

    # Check JSON serialization (Pydantic feature)
    json_data = (
        contract.model_dump_json()
        if hasattr(contract, "model_dump_json")
        else contract.json()
    )
    assert "Contract Test Space" in json_data

    print(">>> Space Contract Verified")


def test_post_contract():
    """Verify WallPost -> AtlasWallPost conversion."""
    cm = CertifiedMath()
    mgr = WallPostManager(cm)
    log_list = []

    # Create Internal (Recap)
    post = mgr.create_post(
        "space_123", "host_0x1", "Recap Content", 2000, is_recap=True, log_list=log_list
    )
    # Like it
    mgr.like_post(post.post_id, "liker_0x2", 2005, log_list)
    # Pin it
    mgr.pin_post(post.post_id, "mod_0x3", 2010, is_authorized=True, log_list=log_list)

    # Convert
    contract = post_to_contract(post)

    # Assert
    assert isinstance(contract, AtlasWallPost)
    assert contract.is_recap is True
    assert contract.is_pinned is True
    assert contract.like_count == 1
    assert contract.content == "Recap Content"
    assert contract.linked_space_id == "space_123"

    print(">>> WallPost Contract Verified")


def test_chat_contract():
    """Verify ChatMessage -> AtlasChatMessage conversion."""
    cm = CertifiedMath()
    mgr = ChatSessionManager(cm)
    log_list = []

    session = mgr.create_session("alice", 3000, log_list)
    msg = mgr.send_message(
        session.session_id,
        "alice",
        "Hello",
        3001,
        "sig",
        log_list,
        references=["ref_1", "ref_2"],
    )

    # Convert
    contract = message_to_contract(msg)

    # Assert
    assert isinstance(contract, AtlasChatMessage)
    assert contract.content == "Hello"
    assert contract.references == ["ref_1", "ref_2"]
    assert contract.sequence_number == 1

    print(">>> Chat Contract Verified")


if __name__ == "__main__":
    test_space_contract()
    test_post_contract()
    test_chat_contract()
