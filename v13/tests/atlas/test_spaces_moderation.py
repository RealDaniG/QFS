"""
Test Spaces Moderation Logic (v14)
Verifies Roles, Permission Hierarchy, and Moderation Actions (Kick/Ban/Mute).
"""

import pytest

try:
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.atlas.spaces.spaces_manager import (
        SpacesManager,
        ParticipantRole,
        ParticipantStatus,
    )
except ImportError:
    import sys
    import os

    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    )
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.atlas.spaces.spaces_manager import (
        SpacesManager,
        ParticipantRole,
        ParticipantStatus,
    )


def test_role_hierarchy_and_permissions():
    """Verify Host > Moderator > Speaker/Listener hierarchy."""
    cm = CertifiedMath()
    manager = SpacesManager(cm)

    log_list = []
    # Setup: Host A creates space
    host_wallet = "wallet_a_host"
    space = manager.create_space(
        host_wallet, "Moderation Test Space", 1000, log_list=log_list
    )
    space_id = space.space_id

    # Join: B (Mod candidate), C (Speaker candidate), D (Victim)
    b_wallet = "wallet_b_mod"
    c_wallet = "wallet_c_speaker"
    d_wallet = "wallet_d_victim"

    manager.join_space(space_id, b_wallet, 1001, log_list=log_list)
    manager.join_space(space_id, c_wallet, 1002, log_list=log_list)
    manager.join_space(space_id, d_wallet, 1003, log_list=log_list)

    # 1. Host Promotes B to Moderator (Allowed)
    manager.promote_participant(
        space_id, b_wallet, ParticipantRole.MODERATOR, host_wallet, log_list=log_list
    )
    assert space.participants[b_wallet].role == ParticipantRole.MODERATOR

    # 2. Moderator B Promotes C to Speaker (Allowed)
    manager.promote_participant(
        space_id, c_wallet, ParticipantRole.SPEAKER, b_wallet, log_list=log_list
    )
    assert space.participants[c_wallet].role == ParticipantRole.SPEAKER

    # 3. Moderator B tries to Promote D to Moderator (Denied - Mods cannot make Mods)
    with pytest.raises(ValueError, match="Moderators cannot appoint other Moderators"):
        manager.promote_participant(
            space_id, d_wallet, ParticipantRole.MODERATOR, b_wallet, log_list=log_list
        )

    # 4. Moderator B tries to Demote Host A (Denied)
    with pytest.raises(ValueError, match="Moderators cannot modify Host"):
        manager.promote_participant(
            space_id, host_wallet, ParticipantRole.LISTENER, b_wallet, log_list=log_list
        )

    # 5. Moderator B Mutes C (Allowed)
    manager.mute_participant(space_id, c_wallet, b_wallet, log_list=log_list)
    assert space.participants[c_wallet].status == ParticipantStatus.MUTED
    assert (
        space.participants[c_wallet].role == ParticipantRole.LISTENER
    )  # Should be downgraded
    assert c_wallet in space.muted_wallets

    # 6. Moderator B Kicks D (Allowed)
    manager.kick_participant(space_id, d_wallet, b_wallet, log_list=log_list)
    assert d_wallet not in space.participants
    assert d_wallet in space.banned_wallets

    # 7. Kicked User D tries to Join (Denied)
    with pytest.raises(ValueError, match="banned from this space"):
        manager.join_space(space_id, d_wallet, 2000, log_list=log_list)

    # 8. Muted User C Leaves and Re-joins (Should remain Muted)
    manager.leave_space(space_id, c_wallet, 2010, log_list=log_list)
    rejoined_c = manager.join_space(space_id, c_wallet, 2020, log_list=log_list)
    assert rejoined_c.status == ParticipantStatus.MUTED

    print(">>> Moderation Roles & Permissions Verified")


if __name__ == "__main__":
    test_role_hierarchy_and_permissions()
