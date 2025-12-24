import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import pytest
from fastapi.testclient import TestClient
from v13.atlas.backend.lib.dependencies import session_manager, evidence_bus
from v13.atlas.src.main_minimal import app

client = TestClient(app)


@pytest.fixture
def mock_session():
    # Create a deterministic session for testing
    wallet = "0x1234567890123456789012345678901234567890"
    signature = "0x" + "a" * 130
    token = session_manager.create_session_token(wallet, signature)
    return token, wallet


def test_bind_github_identity(mock_session):
    token, wallet = mock_session
    username = "octocat"

    # 1. Call bind endpoint
    response = client.post(
        "/api/auth/bind-github",
        headers={"Authorization": f"Bearer {token}"},
        json={"github_username": username, "link_proof": "signed_intent_proof"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "linked"
    assert data["wallet_address"] == wallet
    assert data["github_username"] == username
    assert "evidence_hash" in data

    # 2. Verify EvidenceBus
    evidence_hash = data["evidence_hash"]
    evidence = evidence_bus.get_evidence_by_hash(evidence_hash)

    assert evidence is not None
    assert evidence["event_type"] == "identity_link.github"
    assert evidence["actor_wallet"] == wallet

    # Check payload determinism
    import json

    payload = json.loads(evidence["payload"])
    assert payload["github_username"] == username
    assert payload["link_proof"] == "signed_intent_proof"
    assert payload["linked_at_sequence"] == 0


def test_bind_github_unauthorized():
    response = client.post(
        "/api/auth/bind-github",
        json={"github_username": "hacker", "link_proof": "fake"},
    )
    assert response.status_code == 401
