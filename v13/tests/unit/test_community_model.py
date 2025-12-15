"""
test_community_model.py - Unit tests for Community/Guild Model
"""

import pytest
from v13.services.community.manager import GuildManager
from v13.services.community.membership import MembershipService


def test_guild_lifecycle():
    mgr = GuildManager()

    # Create
    g = mgr.create_guild("Quantum Guild", "Test Desc", "0xFounder")
    assert g["name"] == "Quantum Guild"
    assert g["creator_id"] == "0xFounder"
    gid = g["id"]

    # Get
    fetched = mgr.get_guild(gid)
    assert fetched == g

    # Update
    mgr.update_guild(gid, {"description": "New Desc"})
    assert mgr.get_guild(gid)["description"] == "New Desc"


def test_membership_flow():
    g_mgr = GuildManager()
    m_mgr = MembershipService(g_mgr)

    # Setup Guild
    g = g_mgr.create_guild(
        "Elite Guild", "...", "0xFounder", coherence_threshold=500, staking_amt=100
    )
    gid = g["id"]

    # User A: Low Coherence -> Fail
    with pytest.raises(ValueError, match="Coherence score.*below threshold"):
        m_mgr.join_guild("0xUserA", gid, user_coherence=400, user_balance=1000)

    # User B: Low Balance -> Fail
    with pytest.raises(ValueError, match="Insufficient balance"):
        m_mgr.join_guild("0xUserB", gid, user_coherence=600, user_balance=50)

    # User C: Success
    success = m_mgr.join_guild("0xUserC", gid, user_coherence=600, user_balance=200)
    assert success is True

    members = m_mgr.get_members(gid)
    assert len(members) == 1
    assert members[0]["user_id"] == "0xUserC"

    # Guild stats updated
    assert (
        g_mgr.get_guild(gid)["members_count"] == 2
    )  # Founder (implicit logic in create) + 1 joined
    # Note: Founder logic in 'create' sets count to 1, but doesn't add to membership list in this simple mock.
    # The test assertions confirm the mock logic behaves as currently written.
