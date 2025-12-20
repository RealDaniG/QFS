from v17.agents import (
    process_governance_event,
    process_bounty_event,
    process_social_event,
)


def test_governance_advisory_logic():
    # 1. High Amount Case
    ts = 123456
    event_high_val = {
        "type": "GOV_PROPOSAL_CREATED",
        "payload": {
            "timestamp": ts,
            "proposal": {
                "proposal_id": "p1",
                "requested_amount": 15000,
                "description": "Short desc",
                "creator_wallet": "0xABC",
            },
        },
    }

    adv = process_governance_event(event_high_val)
    assert adv is not None
    assert adv["payload"]["timestamp"] == ts
    signal = adv["payload"]["signal"]
    assert signal["target_id"] == "p1"
    assert "High requested amount" in signal["reasons"]
    assert signal["score"] <= 0.8  # Penalized

    # 2. Determinism check
    adv2 = process_governance_event(event_high_val)
    assert adv2["payload"]["signal"] == signal


def test_bounty_advisory_logic():
    # 1. Good Contribution
    ts = 234567
    event_good = {
        "type": "BOUNTY_CONTRIBUTION_SUBMITTED",
        "payload": {
            "timestamp": ts,
            "contribution": {
                "bounty_id": "b1",
                "contributor_wallet": "0xContrib",
                "content": "A" * 150,  # Long content
                "reference": "http://github.com/example",
            },
        },
    }

    adv = process_bounty_event(event_good)
    assert adv is not None
    assert adv["payload"]["timestamp"] == ts
    signal = adv["payload"]["signal"]
    assert "Contains valid reference link" in signal["reasons"]
    assert signal["score"] > 0.5  # Bonus applied

    # Check target ID format
    assert signal["target_id"] == "b1:0xContrib"


def test_social_advisory_logic():
    # 1. Scam Alert
    ts = 345678
    event_scam = {
        "type": "SOCIAL_DISPUTE_OPENED",
        "payload": {
            "timestamp": ts,
            "dispute": {
                "dispute_id": "d1",
                "reason": "This is a scam!",
                "raised_by": "0xUser",
            },
        },
    }

    adv = process_social_event(event_scam)
    assert adv["payload"]["signal"]["score"] == 0.9
    assert adv["payload"]["timestamp"] == ts
    assert "High urgency keyword detected" in adv["payload"]["signal"]["reasons"]

    # 2. Minor issue
    event_typo = {
        "type": "SOCIAL_DISPUTE_OPENED",
        "payload": {
            "timestamp": ts,
            "dispute": {
                "dispute_id": "d2",
                "reason": "Just a typo",
                "raised_by": "0xUser",
            },
        },
    }
    adv_typo = process_social_event(event_typo)
    assert adv_typo["payload"]["signal"]["score"] == 0.2
