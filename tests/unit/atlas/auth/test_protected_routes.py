"""
test_protected_routes.py - Tests for Phase 3 Protected API Routes.
"""

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from v13.atlas.src.api.dependencies import get_current_session
from v13.atlas.src.api.routes import bounties
from v15.atlas.auth.session_manager import SessionManager

# Setup Test App
app = FastAPI()
app.include_router(bounties.router)

# Mock Session Manager
mock_session_mgr = SessionManager()
session_token = mock_session_mgr.create_session(
    wallet_address="0xTestWallet", scopes=["bounty:read", "bounty:claim"]
)
ro_session_token = mock_session_mgr.create_session(
    wallet_address="0xReadOnly", scopes=["bounty:read"]
)


# Patch the global singleton used by the actual dependency
from v13.atlas.src.api import dependencies

dependencies._session_manager = mock_session_mgr

client = TestClient(app)


def test_list_bounties_authorized():
    """Test listing bounties with valid scope."""
    response = client.get(
        "/bounties/", headers={"Authorization": f"Bearer {session_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert data[0]["id"] == "BNT-001"


def test_list_bounties_unauthorized():
    """Test accessing without token."""
    response = client.get("/bounties/")
    assert response.status_code == 401  # Missing Header


def test_list_bounties_invalid_token():
    """Test accessing with fake token."""
    response = client.get("/bounties/", headers={"Authorization": "Bearer fake_token"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired session"


def test_claim_bounty_authorized():
    """Test claiming with authorized scope."""
    response = client.post(
        "/bounties/BNT-001/claim", headers={"Authorization": f"Bearer {session_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_claim_bounty_forbidden():
    """Test claiming with read-only scope."""
    response = client.post(
        "/bounties/BNT-001/claim",
        headers={"Authorization": f"Bearer {ro_session_token}"},
    )
    assert response.status_code == 403
    assert "Missing scope" in response.json()["detail"]


if __name__ == "__main__":
    try:
        test_list_bounties_authorized()
        print("test_list_bounties_authorized OK")
        test_list_bounties_unauthorized()
        print("test_list_bounties_unauthorized OK")
        test_list_bounties_invalid_token()
        print("test_list_bounties_invalid_token OK")
        test_claim_bounty_authorized()
        print("test_claim_bounty_authorized OK")
        test_claim_bounty_forbidden()
        print("test_claim_bounty_forbidden OK")
        print("✅ ALL TESTS PASSED")
    except Exception as e:
        import traceback

        traceback.print_exc()
        exit(1)
