import pytest
from v15.evidence.bus import EvidenceBus
from v17.agents import process_governance_event
from v17.governance.f_proposals import get_proposal_state
from v17.governance.f_execution import compute_outcome
from v17.governance.schemas import GovernanceConfig
from unittest.mock import patch


def test_advisory_resilient_to_spam():
    """
    Ensure advisory processing handles high volume of low-quality/spam inputs gracefully.
    """
    spam_event = {
        "type": "GOV_PROPOSAL_CREATED",
        "payload": {
            "timestamp": 1000,
            "proposal": {
                "proposal_id": "spam_1",
                "requested_amount": 9999999,
                "body": "S" * 10000,  # Large payload
                "title": "S" * 10000,  # Large title
                "creator_wallet": "0xSpam",
            },
        },
    }

    # Process loop
    for i in range(100):
        # Mutate ID slightly to simulate distinct events if needed, or repeated
        spam_event["payload"]["proposal"]["proposal_id"] = f"spam_{i}"
        result = process_governance_event(spam_event)
        assert result is not None
        assert result["type"] == "AGENT_ADVISORY_PROPOSAL"
        assert result["payload"]["timestamp"] == 1000
        # Check logic didn't crash on large strings
        assert (
            "Quality: Description identical to title"
            in result["payload"]["signal"]["reasons"]
        )


def test_advisory_never_changes_outcome():
    """
    Proves that F-layer outcome logic ignores advisory events.
    """
    bus_data = [
        # 1. Proposal Created
        {
            "event": {
                "type": "GOV_PROPOSAL_CREATED",
                "payload": {
                    "timestamp": 100,
                    "proposal": {
                        "proposal_id": "p_safe",
                        "space_id": "s1",
                        "title": "Safe Prop",
                        "body": "Body content",
                        "created_at": 100,
                        "voting_ends_at": 200,
                        "workflow_type": "basic",
                        "creator_wallet": "0xA",
                    },
                },
            }
        },
        # 2. Vote Cast
        {
            "event": {
                "type": "GOV_VOTE_CAST",
                "payload": {
                    "timestamp": 150,
                    "vote": {
                        "proposal_id": "p_safe",
                        "choice": "approve",
                        "weight": 100,
                        "voter_wallet": "0xB",
                        "timestamp": 150,
                    },
                },
            }
        },
        # 3. Advisory Event (Should be ignored by F-layer state reconstruction)
        {
            "event": {
                "type": "AGENT_ADVISORY_PROPOSAL",
                "payload": {
                    "timestamp": 160,
                    "signal": {
                        "target_id": "p_safe",
                        "score": 0.0,
                        "reasons": ["DO NOT APPROVE"],
                    },
                },
            }
        },
    ]

    with patch("v15.evidence.bus.EvidenceBus.get_events", return_value=bus_data):
        # Reconstruct state
        state = get_proposal_state("p_safe")
        assert state is not None

        # Calculate outcome
        config = GovernanceConfig(
            quorum_threshold=0.0, approval_threshold=0.5, voting_period_seconds=100
        )

        # Verify votes counted
        assert state.approve_weight == 100.0

        # Compute outcome at timestamp 250 (after voting_ends_at 200)
        outcome = compute_outcome(state, config, current_timestamp=250)
        assert outcome.final_outcome == "approved"
