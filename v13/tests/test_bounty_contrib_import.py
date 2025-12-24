import pytest
from fastapi.testclient import TestClient
import json
import sys
import os

# Ensure paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from v13.atlas.src.main_minimal import app
from v13.atlas.backend.lib.dependencies import session_manager, evidence_bus

client = TestClient(app)


@pytest.fixture
def mock_session():
    wallet = "0xContribWallet123"
    signature = "0x" + "b" * 130
    token = session_manager.create_session_token(wallet, signature)
    return token, wallet


def test_import_contributions(mock_session):
    token, wallet = mock_session

    # Mock Ledger
    ledger = {
        "round_id": "test-round-01",
        "importer_version": "0.1.0",
        "repo": "RealDaniG/QFS",
        "ledger_hash": "sha256:mock",
        "contributions": [
            {
                "contribution_id": "sha256:commit1",
                "github_username": "octocat",
                "pr_number": 1,
                "lines_added": 100,
                "lines_deleted": 20,
                "files_changed": ["README.md"],
                "component_tag": "core",
                "weight_inputs": {},
            }
        ],
    }

    response = client.post(
        "/api/bounties/import-contrib",
        headers={"Authorization": f"Bearer {token}"},
        json=ledger,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ingested"
    assert data["count"] == 1
    assert len(data["events"]) == 1

    # Verify EvidenceBus
    event_hash = data["events"][0]
    event = evidence_bus.get_evidence_by_hash(event_hash)

    assert event is not None
    assert event["event_type"] == "contrib_recorded"

    payload = json.loads(event["payload"])
    assert payload["github_username"] == "octocat"
    assert payload["contribution_id"] == "sha256:commit1"
    assert payload["round_id"] == "test-round-01"
