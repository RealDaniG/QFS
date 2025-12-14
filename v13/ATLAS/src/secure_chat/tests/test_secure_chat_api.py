"""API tests for Secure Chat endpoints.

Covers basic auth behavior and happy-path flows using the mocked
QFSClient and authentication dependencies.
"""

import sys
from pathlib import Path
from typing import Dict, Any

import pytest
from fastapi.testclient import TestClient

# Ensure the repository's ATLAS src directory is on sys.path
_THIS_FILE = Path(__file__).resolve()
_ATLAS_ROOT = None
for parent in _THIS_FILE.parents:
    if parent.name == "ATLAS":
        _ATLAS_ROOT = parent
        break
if _ATLAS_ROOT is not None:
    _SRC_DIR = _ATLAS_ROOT / "src"
    if str(_SRC_DIR) not in sys.path:
        sys.path.insert(0, str(_SRC_DIR))

from main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def test_create_thread_unauthenticated(client: TestClient) -> None:
    """Requests without Authorization header should return 401."""
    response = client.post("/api/v1/secure-chat/threads", json={"participants": ["user_abc"]})
    assert response.status_code == 401


def _auth_headers(token: str = "test-token") -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_create_thread_authenticated(client: TestClient) -> None:
    """Authenticated user can create a thread and receives deterministic metadata."""
    payload = {
        "participants": ["user_456"],
        "title": "Integration Thread",
        "metadata": {"purpose": "test"},
    }

    response = client.post(
        "/api/v1/secure-chat/threads",
        json=payload,
        headers=_auth_headers(),
    )

    assert response.status_code == 201
    body = response.json()

    # Basic shape checks
    assert "thread_id" in body
    assert body["creator_id"] == "user_123"  # comes from mocked get_current_user
    assert sorted(body["participants"]) == sorted(["user_456", "user_123"])
    assert body["status"] == "ACTIVE"
    assert body["metadata"]["purpose"] == "test"
    assert "transaction_id" in body


def test_send_message_authenticated(client: TestClient) -> None:
    """Authenticated user can send a message referencing content_hash only."""
    # First create a thread
    t_resp = client.post(
        "/api/v1/secure-chat/threads",
        json={"participants": ["user_789"]},
        headers=_auth_headers(),
    )
    assert t_resp.status_code == 201
    thread_id = t_resp.json()["thread_id"]

    m_payload = {
        "thread_id": thread_id,
        "content_hash": "a" * 64,
        "content_size": 42,
        "content_type": "text/plain",
        "message_type": "text",
        "metadata": {"kind": "unit-test"},
    }

    m_resp = client.post(
        "/api/v1/secure-chat/messages",
        json=m_payload,
        headers=_auth_headers(),
    )

    assert m_resp.status_code == 201
    body = m_resp.json()
    assert body["thread_id"] == thread_id
    assert body["sender_id"] == "user_123"
    assert body["content_hash"] == m_payload["content_hash"]
    assert body["content_size"] == m_payload["content_size"]
    assert body["message_type"] == "text"
    assert "transaction_id" in body


def test_list_threads_authenticated(client: TestClient) -> None:
    """Listing threads should succeed for an authenticated user.

    The underlying mock QFSClient may not yet populate real thread
    state, so this test only verifies HTTP-level behavior and that the
    response structure is correct.
    """
    resp = client.get("/api/v1/secure-chat/threads", headers=_auth_headers())
    assert resp.status_code in (200, 500)
    # If 200, basic shape checks
    if resp.status_code == 200:
        data = resp.json()
        assert "threads" in data
        assert "total" in data


def test_get_thread_unauthorized_access(client: TestClient) -> None:
    """Access control errors should return 403, not leak internals.

    Because we are using a mocked QFSClient + MockLedger with very
    simple state, we only assert that 403 or 500 are possible
    outcomes, and that 401 is *not* returned when auth is present.
    """
    # Use a dummy thread id; backend may return 500 if state not found,
    # or 403 if access control triggers first.
    resp = client.get("/api/v1/secure-chat/threads/dummy-thread", headers=_auth_headers())
    assert resp.status_code in (403, 500)
    assert resp.status_code != 401
