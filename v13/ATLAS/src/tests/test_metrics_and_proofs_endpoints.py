import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure the repository's ATLAS root directory (parent of 'src') is on sys.path
_THIS_FILE = Path(__file__).resolve()
_ATLAS_ROOT = None
for parent in _THIS_FILE.parents:
    if parent.name == "ATLAS":
        _ATLAS_ROOT = parent
        break
if _ATLAS_ROOT is not None:
    if str(_ATLAS_ROOT) not in sys.path:
        sys.path.insert(0, str(_ATLAS_ROOT))

from src.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def _auth_headers(token: str = "test-token") -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_metrics_endpoint_ok(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    # Avoid depending on QFS core availability: monkeypatch storage engine construction.
    from src.api.routes import metrics as metrics_route

    class DummyStorageEngine:
        def __init__(self):
            self.nodes = {}
            self.objects = {}
            self.shards = {}
            self.current_epoch = 0
            self.storage_event_log = []

        def get_eligible_nodes(self):
            return []

    monkeypatch.setattr(metrics_route, "get_storage_engine", lambda: DummyStorageEngine())

    response = client.get("/api/v1/metrics/storage", headers=_auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert "nodes_registered" in body
    assert "objects_stored" in body
    assert "current_epoch" in body


def test_metrics_endpoint_degraded(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from src.api.routes import metrics as metrics_route

    def _boom():
        raise RuntimeError("StorageEngine not available")

    monkeypatch.setattr(metrics_route, "get_storage_engine", _boom)

    response = client.get("/api/v1/metrics/storage", headers=_auth_headers())
    assert response.status_code == 500
    body = response.json()
    assert body.get("detail") == "Failed to retrieve storage metrics"


def test_proofs_endpoint_bad_request(client: TestClient) -> None:
    response = client.post("/api/v1/proofs/verify-storage", json={}, headers=_auth_headers())
    assert response.status_code == 400


def test_proofs_endpoint_minimal_success(client: TestClient) -> None:
    payload = {
        "object_id": "obj_1",
        "version": 1,
        "shard_id": "shard_a",
        "merkle_root": "abc",
        "proof": "proofdata",
        "assigned_nodes": ["n3", "n1", "n2"],
        "expected_content_hash": "deadbeef",
    }

    response = client.post("/api/v1/proofs/verify-storage", json=payload, headers=_auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["object_id"] == "obj_1"
    assert body["version"] == 1
    assert body["shard_id"] == "shard_a"
    assert "verification_hash" in body
    assert "is_valid" in body
    assert "verification_details" in body
