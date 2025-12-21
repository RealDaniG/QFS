import pytest
from fastapi.testclient import TestClient
from src.main_minimal import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_public_routes():
    # Content/Recommendations
    res = client.get("/api/v18/content/recommendations")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # Spaces (Public?)
    res = client.get("/api/v18/spaces")
    assert res.status_code == 200
    assert len(res.json()) > 0

    # Trending
    res = client.get("/api/v18/trending")
    assert res.status_code == 200


def test_wallet_routes_structure():
    # If mocking auth, we can test success, or test 401 if strict.
    # Currently assumes public or we skip auth in test configuration?
    # Ideally should use an override or get a token.
    pass
