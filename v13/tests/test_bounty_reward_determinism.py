import pytest
from typing import List, Dict
from v13.qfs.f_layer.bounty_github import compute_bounty_rewards
from v13.qfs.events.contributions import CONTRIB_RECORDED
from v13.qfs.events.identity import IDENTITY_LINK_GITHUB
import json


class MockEvidenceBus:
    def __init__(self, events: List[Dict]):
        self.events = events

    def get_recent_evidence(self, limit: int = 100) -> List[Dict]:
        # Return strictly strictly newest first? Real impl does DESC scan
        # Our logic reverses it. So we simulate fetching DESC.
        return list(reversed(self.events[-limit:]))


def test_reward_determinism():
    # Setup Events
    # 1. Identity Link
    identity_payload = {"wallet_address": "0xWalletA", "github_username": "octocat"}

    # 2. Contribution
    contrib_payload = {
        "round_id": "test-round",
        "contribution_id": "c1",
        "github_username": "octocat",
        "score_inputs": {"lines_added": 100, "files": 2},
    }

    events = [
        {
            "event_type": IDENTITY_LINK_GITHUB,
            "payload": json.dumps(identity_payload),
            "timestamp": 100,
        },
        {
            "event_type": CONTRIB_RECORDED,
            "payload": json.dumps(contrib_payload),
            "timestamp": 200,
        },
    ]

    bus = MockEvidenceBus(events)

    # Run 1
    result1 = compute_bounty_rewards("test-round", bus)

    # Run 2
    result2 = compute_bounty_rewards("test-round", bus)

    assert result1 == result2
    assert result1["total_contributors"] == 1
    assert result1["allocations"]["0xWalletA"] == 10.0 + 1.0 + 5.0  # 16.0
