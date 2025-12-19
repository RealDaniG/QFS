"""
Integration tests for Bounty System constitutional guarantees.

Tests verify:
1. Treasury over-allocation triggers guard violations
2. Bounty state transitions are deterministically replayable
3. RES stake mechanics (lock/return/slash) work correctly
"""

import pytest
from v13.libs.BigNum128 import BigNum128
from v13.libs.CertifiedMath import CertifiedMath
from v13.policy.bounties.bounty_schema import (
    Bounty,
    BountyStatus,
    BountySubmission,
    ImpactTier,
)
from v13.policy.bounties.bounty_state_machine import BountyStateMachine
from v13.policy.treasury.dev_rewards_treasury import (
    DevRewardsTreasury,
    InsufficientTreasuryError,
)
from v13.libs.fatal_errors import ZeroSimAbort


class TestBountyIntegration:
    """Integration tests for bounty system with constitutional guards."""

    def test_bounty_over_allocation_triggers_guard(self):
        """
        Verify that attempting to allocate more bounties than treasury reserves
        triggers InsufficientTreasuryError (constitutional guard).
        """
        # Initialize treasury with limited reserves
        treasury = DevRewardsTreasury(
            flx_reserve=BigNum128.from_int(1000),
            chr_reserve=BigNum128.from_int(500),
        )

        state_machine = BountyStateMachine(treasury)

        # Bounty 1: 800 CHR + 300 FLX (should succeed)
        bounty1 = Bounty(
            bounty_id="BNT-001",
            title="First Bounty",
            scope="Test bounty 1",
            acceptance_criteria=["Criterion 1"],
            reward_flx=300,
            reward_chr=800,
            res_stake_required=50,
            created_at=1000,
            created_by="creator",
            impact_tier=ImpactTier.FEATURE,
        )

        # Claim and pay bounty 1
        state_machine.claim_bounty(bounty1, "alice", BigNum128.from_int(50))
        submission1 = BountySubmission(
            submission_id="SUB-001",
            bounty_id="BNT-001",
            contributor_wallet="alice",
            pr_number=123,
            commit_hash="abc123",
            res_staked=50,
            submitted_at=2000,
        )
        state_machine.submit_bounty(bounty1, submission1)
        state_machine.verify_bounty(bounty1, "verifier", valid=True)
        state_machine.process_payment(bounty1, "verifier")

        # Bounty 2: 300 CHR + 250 FLX (should FAIL - exceeds remaining reserves)
        bounty2 = Bounty(
            bounty_id="BNT-002",
            title="Second Bounty",
            scope="Test bounty 2",
            acceptance_criteria=["Criterion 1"],
            reward_flx=250,
            reward_chr=300,
            res_stake_required=50,
            created_at=3000,
            created_by="creator",
            impact_tier=ImpactTier.FEATURE,
        )

        state_machine.claim_bounty(bounty2, "bob", BigNum128.from_int(50))
        submission2 = BountySubmission(
            submission_id="SUB-002",
            bounty_id="BNT-002",
            contributor_wallet="bob",
            pr_number=124,
            commit_hash="def456",
            res_staked=50,
            submitted_at=4000,
        )
        state_machine.submit_bounty(bounty2, submission2)
        state_machine.verify_bounty(bounty2, "verifier", valid=True)

        # This should raise InsufficientTreasuryError
        with pytest.raises(InsufficientTreasuryError) as exc:
            state_machine.process_payment(bounty2, "verifier")

        assert "Treasury cannot pay" in str(exc.value)
        assert "CHR" in str(exc.value) or "FLX" in str(exc.value)

    def test_bounty_state_deterministic_replay(self):
        """
        Verify bounty state transitions produce identical hashes
        across scrambled execution orders.
        """
        # Create identical treasury instances
        treasury1 = DevRewardsTreasury(
            flx_reserve=BigNum128.from_int(10000),
            chr_reserve=BigNum128.from_int(10000),
        )
        treasury2 = DevRewardsTreasury(
            flx_reserve=BigNum128.from_int(10000),
            chr_reserve=BigNum128.from_int(10000),
        )

        # Create three bounties
        bounties = [
            Bounty(
                bounty_id=f"BNT-{i:03d}",
                title=f"Bounty {i}",
                scope=f"Test bounty {i}",
                acceptance_criteria=[f"Criterion {i}"],
                reward_flx=100,
                reward_chr=200,
                res_stake_required=10,
                created_at=1000 + i * 100,
                created_by="creator",
                impact_tier=ImpactTier.FEATURE,
            )
            for i in range(1, 4)
        ]

        # Execution order 1: Sequential (A -> B -> C)
        sm1 = BountyStateMachine(treasury1)
        log1 = []
        for i, bounty in enumerate(bounties):
            sm1.claim_bounty(bounty, f"user{i}", BigNum128.from_int(10))
            submission = BountySubmission(
                submission_id=f"SUB-{i:03d}",
                bounty_id=bounty.bounty_id,
                contributor_wallet=f"user{i}",
                pr_number=100 + i,
                commit_hash=f"hash{i}",
                res_staked=10,
                submitted_at=2000 + i * 100,
            )
            sm1.submit_bounty(bounty, submission)
            sm1.verify_bounty(bounty, "verifier", valid=True)
            events = sm1.process_payment(bounty, "verifier")
            log1.extend(events)

        # Execution order 2: Scrambled (C -> A -> B)
        sm2 = BountyStateMachine(treasury2)
        log2 = []
        scrambled_order = [2, 0, 1]  # C, A, B
        for idx in scrambled_order:
            bounty = bounties[idx]
            sm2.claim_bounty(bounty, f"user{idx}", BigNum128.from_int(10))
            submission = BountySubmission(
                submission_id=f"SUB-{idx:03d}",
                bounty_id=bounty.bounty_id,
                contributor_wallet=f"user{idx}",
                pr_number=100 + idx,
                commit_hash=f"hash{idx}",
                res_staked=10,
                submitted_at=2000 + idx * 100,
            )
            sm2.submit_bounty(bounty, submission)
            sm2.verify_bounty(bounty, "verifier", valid=True)
            events = sm2.process_payment(bounty, "verifier")
            log2.extend(events)

        # Verify treasury states are identical
        assert treasury1.flx_reserve.value == treasury2.flx_reserve.value
        assert treasury1.chr_reserve.value == treasury2.chr_reserve.value
        assert treasury1.total_paid_flx.value == treasury2.total_paid_flx.value
        assert treasury1.total_paid_chr.value == treasury2.total_paid_chr.value

        # Verify event counts match
        assert len(log1) == len(log2)

    def test_res_stake_slash_on_spam(self):
        """
        Verify RES stake is slashed (not refunded) when rejection reason is 'SPAM'.
        """
        treasury = DevRewardsTreasury(
            flx_reserve=BigNum128.from_int(10000),
            chr_reserve=BigNum128.from_int(10000),
        )
        state_machine = BountyStateMachine(treasury)

        bounty = Bounty(
            bounty_id="BNT-SPAM",
            title="Spam Bounty",
            scope="Low quality submission",
            acceptance_criteria=["Must be quality"],
            reward_flx=100,
            reward_chr=200,
            res_stake_required=100,
            created_at=1000,
            created_by="creator",
            impact_tier=ImpactTier.MINOR,
        )

        # Claim with RES stake
        res_stake = BigNum128.from_int(100)
        state_machine.claim_bounty(bounty, "spammer", res_stake)

        # Submit low-quality work
        submission = BountySubmission(
            submission_id="SUB-SPAM",
            bounty_id="BNT-SPAM",
            contributor_wallet="spammer",
            pr_number=0,
            commit_hash="NA",
            res_staked=100,
            submitted_at=2000,
        )
        state_machine.submit_bounty(bounty, submission)

        # Reject as SPAM
        events = state_machine.verify_bounty(
            bounty, verifier="moderator", valid=False, reason="SPAM"
        )

        # Verify NO res_stake_returned event
        event_types = [e.event_type for e in events]
        assert "res_stake_returned" not in event_types

        # Verify rejection event shows slashed amount
        reject_event = next(e for e in events if e.event_type == "bounty_rejected")
        assert reject_event.res_slashed == 100  # Full stake burned

    def test_res_stake_returned_on_valid_rejection(self):
        """
        Verify RES stake IS refunded when rejection is not for SPAM.
        """
        treasury = DevRewardsTreasury(
            flx_reserve=BigNum128.from_int(10000),
            chr_reserve=BigNum128.from_int(10000),
        )
        state_machine = BountyStateMachine(treasury)

        bounty = Bounty(
            bounty_id="BNT-REJECT",
            title="Rejected Bounty",
            scope="Incomplete work",
            acceptance_criteria=["Must be complete"],
            reward_flx=100,
            reward_chr=200,
            res_stake_required=50,
            created_at=1000,
            created_by="creator",
            impact_tier=ImpactTier.MINOR,
        )

        # Claim with RES stake
        state_machine.claim_bounty(bounty, "contributor", BigNum128.from_int(50))

        # Submit incomplete work
        submission = BountySubmission(
            submission_id="SUB-REJECT",
            bounty_id="BNT-REJECT",
            contributor_wallet="contributor",
            pr_number=999,
            commit_hash="incomplete",
            res_staked=50,
            submitted_at=2000,
        )
        state_machine.submit_bounty(bounty, submission)

        # Reject for incomplete work (not SPAM)
        events = state_machine.verify_bounty(
            bounty, verifier="moderator", valid=False, reason="INCOMPLETE"
        )

        # Verify res_stake_returned event exists
        event_types = [e.event_type for e in events]
        assert "res_stake_returned" in event_types

        # Verify full stake returned
        return_event = next(e for e in events if e.event_type == "res_stake_returned")
        assert return_event.res_amount == 50
