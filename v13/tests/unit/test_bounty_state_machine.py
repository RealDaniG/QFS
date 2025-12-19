import pytest
from unittest.mock import Mock, MagicMock
from v13.policy.bounties.bounty_state_machine import BountyStateMachine
from v13.policy.bounties.bounty_schema import (
    Bounty,
    BountyStatus,
    BountySubmission,
    ImpactTier,
)
from v13.policy.bounties.bounty_events import EconomicEvent
from v13.policy.treasury.dev_rewards_treasury import DevRewardsTreasury


@pytest.fixture
def mock_treasury():
    treasury = Mock(spec=DevRewardsTreasury)
    # mock payout to return an event
    treasury.pay_bounty.return_value = EconomicEvent(
        event_type="dev_bounty_paid",
        actor="dev1",
        timestamp=123,
        metadata={},
        flx_delta=100,
    )
    return treasury


@pytest.fixture
def machine(mock_treasury):
    return BountyStateMachine(mock_treasury)


@pytest.fixture
def open_bounty():
    return Bounty(
        bounty_id="B-1",
        title="Fix Bug",
        scope="Fix things",
        acceptance_criteria=[],
        reward_flx=100,
        reward_chr=50,
        res_stake_required=10,
        impact_tier=ImpactTier.MINOR,
        status=BountyStatus.OPEN,
        created_at=1000,
        created_by="owner",
    )


def test_claim_bounty_success(machine, open_bounty):
    events = machine.claim_bounty(open_bounty, "dev1", 10)
    assert open_bounty.status == BountyStatus.CLAIMED
    assert open_bounty.current_claimant == "dev1"
    assert len(events) == 1
    assert events[0].event_type == "bounty_claimed"


def test_claim_bounty_insufficient_res(machine, open_bounty):
    with pytest.raises(ValueError, match="Insufficient RES"):
        machine.claim_bounty(open_bounty, "dev1", 5)


def test_submit_bounty(machine, open_bounty):
    machine.claim_bounty(open_bounty, "dev1", 10)

    submission = BountySubmission(
        submission_id="S-1",
        bounty_id="B-1",
        contributor_wallet="dev1",
        pr_number=1,
        commit_hash="abc",
        res_staked=10,
        submitted_at=1001,
        status="SUBMITTED",
    )

    machine.submit_bounty(open_bounty, submission)
    assert open_bounty.status == BountyStatus.SUBMITTED
    assert open_bounty.submission == submission


def test_verify_bounty_valid(machine, open_bounty):
    machine.claim_bounty(open_bounty, "dev1", 10)
    submission = BountySubmission("S-1", "B-1", "dev1", 1, "abc", 10, 1001, "SUBMITTED")
    machine.submit_bounty(open_bounty, submission)

    events = machine.verify_bounty(open_bounty, "verifier1", True)
    assert open_bounty.status == BountyStatus.VERIFIED

    # Verification itself emits no events until payment/rejection
    assert len(events) == 0


def test_verify_bounty_reject(machine, open_bounty):
    machine.claim_bounty(open_bounty, "dev1", 10)
    submission = BountySubmission("S-1", "B-1", "dev1", 1, "abc", 10, 1001, "SUBMITTED")
    machine.submit_bounty(open_bounty, submission)

    events = machine.verify_bounty(open_bounty, "verifier1", False, reason="Bad code")
    assert open_bounty.status == BountyStatus.REJECTED

    # Should have refund (good faith) and rejection event
    assert len(events) == 2
    assert events[0].event_type == "res_stake_returned"
    assert events[1].event_type == "bounty_rejected"


def test_process_payment(machine, open_bounty, mock_treasury):
    machine.claim_bounty(open_bounty, "dev1", 10)
    submission = BountySubmission("S-1", "B-1", "dev1", 1, "abc", 10, 1001, "SUBMITTED")
    machine.submit_bounty(open_bounty, submission)
    machine.verify_bounty(open_bounty, "verifier1", True)

    events = machine.process_payment(open_bounty, "verifier1")

    assert open_bounty.status == BountyStatus.PAID

    # Expect: dev_bounty_paid, res_stake_returned, atr_boost_applied
    assert len(events) == 3
    assert events[0].event_type == "dev_bounty_paid"
    assert events[1].event_type == "res_stake_returned"
    assert events[2].event_type == "atr_boost_applied"

    # Verify ATR boost logic
    assert events[2].atr_delta == 10

    mock_treasury.pay_bounty.assert_called_once()
