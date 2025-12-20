import pytest
from fastapi.testclient import TestClient
from src.main_minimal import app

client = TestClient(app)


def test_openapi_spec_contains_v18_routes():
    """
    Regression test to ensure v18 and v1 routes are correctly loaded
    and exposed in the OpenAPI specification.
    """
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    paths = schema.get("paths", {})

    # Check for V18 Governance
    assert "/api/v18/governance/proposals" in paths, "Governance V18 routes missing"

    # Check for V18 Content
    assert "/api/v18/content/feed" in paths, "Content V18 routes missing"

    # Check for V1 Wallets (Legacy/Hybrid)
    assert "/api/v1/wallets/" in paths or "/api/v1/wallets" in paths, (
        "Wallet V1 routes missing"
    )

    # Check for V1 Auth
    assert "/api/v1/auth/nonce" in paths, "Auth V1 routes missing"


def test_health_check_returns_v18_status():
    """
    Ensure health check confirms v18 readiness.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "v18_clusters" in data.get("services", {}), (
        "Health check should report v18 cluster status"
    )
