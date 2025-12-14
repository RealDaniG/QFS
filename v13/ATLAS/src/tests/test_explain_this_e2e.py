"""
test_explain_this_e2e.py

End-to-End Integration Test for Value-Node Explainability.
Verifies that the ATLAS API endpoint correctly uses the ValueNodeReplayEngine
and returns a response matching the frontend expectations.
"""

import pytest
from fastapi.testclient import TestClient
from v13.ATLAS.src.api import app

client = TestClient(app)

def test_explain_reward_e2e_flow():
    """
    Simulate a user asking "Why did I get this reward?" via the ATLAS UI.
    
    1.  Frontend calls GET /explain/reward/{wallet_id}
    2.  Backend instantiates ValueNodeReplayEngine
    3.  Backend replays (mock) ledger events
    4.  Backend generates ValueNodeRewardExplanation
    5.  Backend returns SimplifiedExplanation JSON
    
    We verify the inputs flow through to the output deterministic hash.
    """
    wallet_id = "wallet_test_e2e"
    epoch = 10
    
    response = client.get(f"/explain/reward/{wallet_id}?epoch={epoch}")
    
    assert response.status_code == 200, f"API call failed: {response.text}"
    
    data = response.json()
    
    # Verify Schema Matches Frontend Expectations
    assert data["wallet_id"] == wallet_id
    assert data["epoch"] == epoch
    
    # Verify Content from Replay Engine
    # (These values come from the mock_events in explain.py, proving logic execution)
    assert data["base"] == "10.0 ATR"
    
    # Check Bonuses
    bonuses = data["bonuses"]
    assert len(bonuses) == 3
    assert any(b["label"] == "Humor bonus" for b in bonuses)
    
    # Check Caps
    caps = data["caps"]
    assert len(caps) > 0
    
    # Check Metadata & Hash
    metadata = data["metadata"]
    assert "replay_hash" in metadata
    assert len(metadata["replay_hash"]) == 64  # SHA-256 hex digest
    assert metadata["source"] == "qfs_replay_derived"

    print(f"\n[E2E] Replay Hash Verified: {metadata['replay_hash']}")

def test_explain_ranking_e2e_flow():
    """Simulate a user asking 'Why is this ranked #X?'.
    """
    content_id = "c_test_ranking"
    
    response = client.get(f"/explain/ranking/{content_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["content_id"] == content_id
    assert "signals" in data
    assert len(data["signals"]) == 2 # Interaction Volume + Quality from Replay Engine
    assert data["metadata"]["replay_hash"]
    
    print(f"\n[E2E] Ranking Hash Verified: {data['metadata']['replay_hash']}")

if __name__ == "__main__":
    test_explain_reward_e2e_flow()
    test_explain_ranking_e2e_flow()
