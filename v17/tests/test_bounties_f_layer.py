"""
Tests for Bounty F-Layer (v17 Beta)

Ensures deterministic behavior, Zero-Sim compliance, and PoE logging.
"""

import os
import tempfile
from v15.evidence.bus import EvidenceBus
from v17.bounties import (
    create_bounty,
    submit_contribution,
    get_bounty_state,
    compute_rewards,
    finalize_bounty,
)


def test_bounty_determinism():
    """Test that same inputs produce same bounty outcomes (deterministic)."""
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name

    try:
        # Reset chain
        EvidenceBus._chain_tip = "0" * 64

        # Create bounty (deterministic inputs)
        bounty1 = create_bounty(
            space_id="space_test",
            title="Test Bounty",
            description="This is a test bounty",
            reward_amount=1000.0,
            created_by="0xabc",
            timestamp=1000000,
        )

        # Reset and create again
        EvidenceBus._chain_tip = "0" * 64
        bounty2 = create_bounty(
            space_id="space_test",
            title="Test Bounty",
            description="This is a test bounty",
            reward_amount=1000.0,
            created_by="0xabc",
            timestamp=1000000,
        )

        # IDs should match (deterministic)
        assert bounty1.bounty_id == bounty2.bounty_id
        assert bounty1.reward_amount == bounty2.reward_amount

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


def test_bounty_poe_logging():
    """Test that all bounty actions are PoE-logged to EvidenceBus."""
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name

    try:
        # Reset chain
        EvidenceBus._chain_tip = "0" * 64

        # Create bounty
        bounty = create_bounty(
            space_id="space_test",
            title="Test Bounty",
            description="This is a test bounty",
            reward_amount=1000.0,
            created_by="0xabc",
            timestamp=1000000,
        )

        # Submit contributions
        submit_contribution(
            bounty_id=bounty.bounty_id,
            contributor_wallet="0xcontrib1",
            reference="https://github.com/org/repo/pull/1",
            timestamp=1000100,
        )

        submit_contribution(
            bounty_id=bounty.bounty_id,
            contributor_wallet="0xcontrib2",
            reference="https://github.com/org/repo/pull/2",
            timestamp=1000200,
        )

        # Get state from EvidenceBus
        state = get_bounty_state(bounty.bounty_id)
        assert state is not None
        assert len(state.contributions) == 2
        assert state.total_contributions == 2

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


def test_bounty_reward_computation():
    """Test deterministic reward computation."""
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name

    try:
        # Reset chain
        EvidenceBus._chain_tip = "0" * 64

        # Create bounty
        bounty = create_bounty(
            space_id="space_test",
            title="Test Bounty",
            description="This is a test bounty",
            reward_amount=1000.0,
            created_by="0xabc",
            timestamp=1000000,
        )

        # Submit contributions
        for i in range(3):
            submit_contribution(
                bounty_id=bounty.bounty_id,
                contributor_wallet=f"0xcontrib{i}",
                reference=f"https://github.com/org/repo/pull/{i}",
                timestamp=1000100 + i * 100,
            )

        # Get state
        state = get_bounty_state(bounty.bounty_id)
        assert state is not None

        # Compute rewards
        rewards = compute_rewards(
            bounty_state=state,
            timestamp=1001000,
            use_advisory=False,  # No advisory signals for this test
        )

        # Should have 3 reward decisions
        assert len(rewards) == 3

        # Total rewards should equal bounty amount
        total_allocated = sum(r.amount for r in rewards)
        assert abs(total_allocated - 1000.0) < 0.01  # Allow small floating point error

        # All percentages should sum to 1.0
        total_percentage = sum(r.percentage for r in rewards)
        assert abs(total_percentage - 1.0) < 0.01

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


def test_bounty_reward_determinism():
    """Test that reward computation is deterministic."""
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name

    try:
        # Reset chain
        EvidenceBus._chain_tip = "0" * 64

        # Create bounty
        bounty = create_bounty(
            space_id="space_test",
            title="Test Bounty",
            description="This is a test bounty",
            reward_amount=1000.0,
            created_by="0xabc",
            timestamp=1000000,
        )

        # Submit contributions
        submit_contribution(
            bounty_id=bounty.bounty_id,
            contributor_wallet="0xcontrib1",
            reference="https://github.com/org/repo/pull/1",
            timestamp=1000100,
        )

        submit_contribution(
            bounty_id=bounty.bounty_id,
            contributor_wallet="0xcontrib2",
            reference="https://github.com/org/repo/pull/2",
            timestamp=1000200,
        )

        # Get state
        state = get_bounty_state(bounty.bounty_id)

        # Compute rewards twice
        rewards1 = compute_rewards(state, 1001000, use_advisory=False)
        rewards2 = compute_rewards(state, 1001000, use_advisory=False)

        # Should be identical
        assert len(rewards1) == len(rewards2)
        for r1, r2 in zip(rewards1, rewards2):
            assert r1.recipient_wallet == r2.recipient_wallet
            assert r1.amount == r2.amount
            assert r1.percentage == r2.percentage

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


if __name__ == "__main__":
    test_bounty_determinism()
    test_bounty_poe_logging()
    test_bounty_reward_computation()
    test_bounty_reward_determinism()
    print("✅ All Bounty F-Layer tests passed")
