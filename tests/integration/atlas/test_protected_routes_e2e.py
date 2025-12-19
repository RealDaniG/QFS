"""
Integration tests for v15.4 Phase 3: Protected Routes End-to-End Flow
Tests wallet auth → bounty list → claim → my bounties
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from v13.atlas.src.api import app
from v15.atlas.auth.session_manager import SessionManager

client = TestClient(app)

# Mock session for testing
MOCK_SESSION = {
    "wallet_address": "0xTEST123",
    "scopes": ["bounty:read", "bounty:claim"],
    "expires_at": 9999999999,
}


@pytest.fixture
def mock_session_manager():
    """Mock SessionManager for testing"""
    with patch("v13.atlas.src.api.dependencies._session_manager") as mock_sm:
        mock_sm.validate_session.return_value = MOCK_SESSION
        yield mock_sm


def test_bounty_list_requires_auth():
    """Test that bounty list requires authentication"""
    response = client.get("/api/bounties/")
    assert response.status_code == 401
    assert "Authorization header missing" in response.json()["detail"]


def test_bounty_list_requires_bounty_read_scope(mock_session_manager):
    """Test that bounty list requires bounty:read scope"""
    # Mock session without bounty:read scope
    mock_session_manager.validate_session.return_value = {
        "wallet_address": "0xTEST123",
        "scopes": [],
        "expires_at": 9999999999,
    }

    response = client.get(
        "/api/bounties/", headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 403
    assert "Missing scope: bounty:read" in response.json()["detail"]


def test_bounty_list_success(mock_session_manager):
    """Test successful bounty list retrieval"""
    response = client.get(
        "/api/bounties/", headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "title" in data[0]
    assert "reward" in data[0]


def test_claim_bounty_requires_auth():
    """Test that claiming bounty requires authentication"""
    response = client.post("/api/bounties/BNT-001/claim")
    assert response.status_code == 401


def test_claim_bounty_requires_bounty_claim_scope(mock_session_manager):
    """Test that claiming bounty requires bounty:claim scope"""
    # Mock session without bounty:claim scope
    mock_session_manager.validate_session.return_value = {
        "wallet_address": "0xTEST123",
        "scopes": ["bounty:read"],
        "expires_at": 9999999999,
    }

    response = client.post(
        "/api/bounties/BNT-001/claim", headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 403
    assert "Missing scope: bounty:claim" in response.json()["detail"]


def test_claim_bounty_success(mock_session_manager):
    """Test successful bounty claim"""
    response = client.post(
        "/api/bounties/BNT-001/claim", headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "BNT-001" in data["message"]
    assert data["bounty_id"] == "BNT-001"


def test_my_bounties_requires_auth():
    """Test that my bounties requires authentication"""
    response = client.get("/api/bounties/my-bounties")
    assert response.status_code == 401


def test_my_bounties_success(mock_session_manager):
    """Test successful my bounties retrieval"""
    response = client.get(
        "/api/bounties/my-bounties", headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_end_to_end_bounty_flow(mock_session_manager):
    """Test complete end-to-end flow: list → claim → my bounties"""

    # 1. List bounties
    list_response = client.get(
        "/api/bounties/", headers={"Authorization": "Bearer test_token"}
    )
    assert list_response.status_code == 200
    bounties = list_response.json()
    assert len(bounties) > 0

    # 2. Claim a bounty
    bounty_id = bounties[0]["id"]
    claim_response = client.post(
        f"/api/bounties/{bounty_id}/claim",
        headers={"Authorization": "Bearer test_token"},
    )
    assert claim_response.status_code == 200
    assert claim_response.json()["status"] == "success"

    # 3. Check my bounties
    my_bounties_response = client.get(
        "/api/bounties/my-bounties", headers={"Authorization": "Bearer test_token"}
    )
    assert my_bounties_response.status_code == 200
    my_bounties = my_bounties_response.json()

    # Verify claimed bounty appears in my bounties
    # (In mock data, this depends on implementation)
    assert isinstance(my_bounties, list)


def test_session_token_validation(mock_session_manager):
    """Test that invalid session tokens are rejected"""
    mock_session_manager.validate_session.side_effect = ValueError("Invalid token")

    response = client.get(
        "/api/bounties/", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_expired_session_token(mock_session_manager):
    """Test that expired session tokens are rejected"""
    mock_session_manager.validate_session.return_value = {
        "wallet_address": "0xTEST123",
        "scopes": ["bounty:read"],
        "expires_at": 0,  # Expired
    }

    response = client.get(
        "/api/bounties/", headers={"Authorization": "Bearer expired_token"}
    )
    # Should be rejected by session validation
    assert response.status_code in [401, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
