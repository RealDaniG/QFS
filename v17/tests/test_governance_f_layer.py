"""
Tests for Governance F-Layer (v17 Beta)

Ensures deterministic behavior, Zero-Sim compliance, and PoE logging.
"""

import os
import tempfile
from v15.evidence.bus import EvidenceBus
from v17.governance import (
    GovernanceConfig,
    create_proposal,
    get_proposal_state,
    cast_vote,
    compute_outcome,
    finalize_proposal,
)


def test_governance_determinism():
    """Test that same inputs produce same governance outcomes (deterministic)."""
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name

    try:
        # Reset chain
        EvidenceBus._chain_tip = "0" * 64

        # Create config
        config = GovernanceConfig(
            quorum_threshold="0.500000000000000000",
            approval_threshold="0.600000000000000000",
            voting_period_seconds=86400,
        )

        # Create proposal (deterministic inputs)
        prop1 = create_proposal(
            space_id="space_test",
            creator_wallet="0xabc",
            title="Test Proposal",
            body="This is a test",
            timestamp=1000000,
            config=config,
        )

        # Reset and create again
        EvidenceBus._chain_tip = "0" * 64
        prop2 = create_proposal(
            space_id="space_test",
            creator_wallet="0xabc",
            title="Test Proposal",
            body="This is a test",
            timestamp=1000000,
            config=config,
        )

        # IDs should match (deterministic)
        assert prop1.proposal_id == prop2.proposal_id
        assert prop1.voting_ends_at == prop2.voting_ends_at

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


def test_governance_poe_logging():
    """Test that all governance actions are PoE-logged to EvidenceBus."""
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name

    try:
        # Reset chain
        EvidenceBus._chain_tip = "0" * 64

        # Create config
        config = GovernanceConfig(
            quorum_threshold="0.300000000000000000",
            approval_threshold="0.500000000000000000",
            voting_period_seconds=1000,
        )

        # Create proposal
        proposal = create_proposal(
            space_id="space_test",
            creator_wallet="0xabc",
            title="Test Proposal",
            body="This is a test",
            timestamp=1000000,
            config=config,
        )

        # Cast votes
        cast_vote(
            proposal_id=proposal.proposal_id,
            voter_wallet="0xvoter1",
            choice="approve",
            timestamp=1000100,
            config=config,
        )

        cast_vote(
            proposal_id=proposal.proposal_id,
            voter_wallet="0xvoter2",
            choice="approve",
            timestamp=1000200,
            config=config,
        )

        cast_vote(
            proposal_id=proposal.proposal_id,
            voter_wallet="0xvoter3",
            choice="reject",
            timestamp=1000300,
            config=config,
        )

        # Get state from EvidenceBus
        state = get_proposal_state(proposal.proposal_id)
        assert state is not None
        assert len(state.votes) == 3
        assert state.total_votes == 3

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


def test_governance_outcome_computation():
    """Test deterministic outcome computation."""
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name

    try:
        # Reset chain
        EvidenceBus._chain_tip = "0" * 64

        # Create config
        config = GovernanceConfig(
            quorum_threshold="0.300000000000000000",  # 30% participation required
            approval_threshold="0.600000000000000000",  # 60% approval required
            voting_period_seconds=1000,
        )

        # Create proposal
        proposal = create_proposal(
            space_id="space_test",
            creator_wallet="0xabc",
            title="Test Proposal",
            body="This is a test",
            timestamp=1000000,
            config=config,
        )

        # Cast votes (65% approval)
        for i in range(65):
            cast_vote(
                proposal_id=proposal.proposal_id,
                voter_wallet=f"0xvoter{i}",
                choice="approve",
                timestamp=1000100 + i,
                config=config,
            )

        for i in range(35):
            cast_vote(
                proposal_id=proposal.proposal_id,
                voter_wallet=f"0xreject{i}",
                choice="reject",
                timestamp=1000200 + i,
                config=config,
            )

        # Get state
        state = get_proposal_state(proposal.proposal_id)
        assert state is not None

        # Compute outcome
        outcome = compute_outcome(
            proposal_state=state,
            config=config,
            current_timestamp=1001001,  # After voting period
        )

        # Should be approved (quorum met, approval > 60%)
        assert outcome.final_outcome == "approved"
        assert outcome.total_votes == 100
        assert float(outcome.approve_weight) == 65.0
        assert float(outcome.reject_weight) == 35.0

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


def test_governance_tie_breaking():
    """Test deterministic tie-breaking."""
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name

    try:
        # Reset chain
        EvidenceBus._chain_tip = "0" * 64

        # Create config with tie-break rule
        config = GovernanceConfig(
            quorum_threshold="0.300000000000000000",
            approval_threshold="0.500000000000000000",
            voting_period_seconds=1000,
            tie_break_rule="reject",  # Ties default to reject
        )

        # Create proposal
        proposal = create_proposal(
            space_id="space_test",
            creator_wallet="0xabc",
            title="Tie Test",
            body="This will tie",
            timestamp=1000000,
            config=config,
        )

        # Cast equal votes
        for i in range(50):
            cast_vote(
                proposal_id=proposal.proposal_id,
                voter_wallet=f"0xapprove{i}",
                choice="approve",
                timestamp=1000100 + i,
                config=config,
            )

        for i in range(50):
            cast_vote(
                proposal_id=proposal.proposal_id,
                voter_wallet=f"0xreject{i}",
                choice="reject",
                timestamp=1000200 + i,
                config=config,
            )

        # Get state
        state = get_proposal_state(proposal.proposal_id)
        assert state is not None

        # Compute outcome
        outcome = compute_outcome(
            proposal_state=state,
            config=config,
            current_timestamp=1001001,
        )

        # Should be rejected (tie-break rule)
        assert outcome.final_outcome == "rejected"
        assert "tie" in outcome.reason.lower()

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


if __name__ == "__main__":
    test_governance_determinism()
    test_governance_poe_logging()
    test_governance_outcome_computation()
    test_governance_tie_breaking()
    print("✅ All Governance F-Layer tests passed")
