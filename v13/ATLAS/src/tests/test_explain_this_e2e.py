"""
test_explain_this_e2e.py

End-to-End Integration Test for Value-Node Explainability.
Verifies that the ATLAS API endpoint correctly uses the ValueNodeReplayEngine
and returns a response matching the frontend expectations.
"""

import pytest
from fastapi.testclient import TestClient

# Correct import path - using absolute imports
# For Zero-Sim compliance, removed sys/os imports and use deterministic path setup
# Path setup handled through deterministic import resolution

from v13.ATLAS.src.api import app
from v13.ATLAS.src.api.dependencies import get_replay_source, get_current_user

try:
    from v13.ATLAS.src.api.routes import explain
    EXPLAIN_SOURCE = explain.get_replay_source
except ImportError:
    EXPLAIN_SOURCE = get_replay_source


class MockReplaySource:
    def __init__(self):
        self.ledger = type("MockLedger", (), {"ledger_entries": []})()  # minimal stub

    def get_reward_events(self, wallet_id, epoch):
        if wallet_id == "wallet_test_e2e":
            return [
                {
                    "id": "hsmf_evt_1",
                    "type": "MetricsUpdate",
                    "timestamp": 1234567800,
                    "coherence_score": 98,
                },
                {
                    "id": "reward_evt_1",
                    "type": "RewardAllocated",
                    "timestamp": 1234567890,
                    "wallet_id": wallet_id,
                    "amount": 1000,
                    # ValueGraphRef expects dict of wallet_id -> details
                    "rewards": {wallet_id: {"final_reward": "1000", "ATR": "10.0 ATR"}},
                    # Fallback for explanation helper if log_details missing
                    "base_reward": {"ATR": "10.0 ATR"},
                    "log_details": {
                        "base_reward": {"ATR": "10.0 ATR"},
                        "bonuses": [
                            {"label": "Content contribution", "value": "0.5 ATR"}
                        ],
                        "caps": [],
                    },
                },
            ]
        return []

    def get_ranking_events(self, content_id):
        if content_id == "c_test_ranking":
            return [
                {
                    "id": "content_evt_1",
                    "timestamp": 1234567800,
                    # ValueGraphRef expects ContentCreated to hydrate content node
                    "type": "ContentCreated",
                    "quality_score": 95,
                    "content_id": content_id,
                    "creator_id": "test_user_id",
                },
                {
                    "id": "interact_evt_1",
                    "timestamp": 1234567850,
                    # ValueGraphRef expects InteractionCreated
                    "type": "InteractionCreated",
                    "interaction_type": "view",
                    "content_id": content_id,
                    "user_id": "viewer_user",
                    "weight": 1.0,
                },
            ]
        return []


@pytest.fixture(scope="module")
def authenticated_client():
    """Setup client with mocked authentication and replay source."""
    mock_source = MockReplaySource()

    # Override Auth
    # explain.py expects a dict with "wallet_id" and "permissions"
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "test_user_id",
        "username": "test_user",
        "email": "test@qfs.local",
        "is_active": True,
        "wallet_id": "wallet_test_e2e",  # Matches test wallet_id
        "permissions": [],
    }

    # Override Replay Source - PATCH BOTH definition and route usage just in case
    app.dependency_overrides[get_replay_source] = lambda: mock_source
    app.dependency_overrides[EXPLAIN_SOURCE] = lambda: mock_source

    with TestClient(app) as client:
        yield client

    # Cleanup
    app.dependency_overrides.clear()


def test_explain_reward_e2e_flow(authenticated_client):
    """Test full e2e flow for reward explanation."""
    wallet_id = "wallet_test_e2e"
    epoch = 10

    response = authenticated_client.get(f"/explain/reward/{wallet_id}?epoch={epoch}")

    # For Zero-Sim compliance, suppress debug output
    # DEBUG info if fail
    # if response.status_code != 200:
    #     print(f"DEBUG: Status={response.status_code} Body={response.text}")

    assert response.status_code == 200, f"API call failed: {response.text}"

    data = response.json()
    assert data["wallet_id"] == wallet_id
    assert data["base"] == "10.0 ATR"
    assert any(b["label"] == "Content contribution" for b in data["bonuses"])
    assert data["metadata"]["source"] == "qfs_replay_verified"


def test_explain_ranking_e2e_flow(authenticated_client):
    """Test full e2e flow for ranking explanation."""
    content_id = "c_test_ranking"

    response = authenticated_client.get(f"/explain/ranking/{content_id}")
    assert response.status_code == 200, f"API call failed: {response.text}"

    data = response.json()
    assert data["content_id"] == content_id
    assert "signals" in data
    assert data["metadata"]["replay_hash"]


if __name__ == "__main__":
    # For Zero-Sim compliance, suppress direct execution
    # pytest.main([__file__])
    pass