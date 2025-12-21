from fastapi.testclient import TestClient
from src.main_minimal import app

client = TestClient(app)


def test_v18_routes_are_registered():
    """
    Ensure v18 routes are registered in the FastAPI app.
    We check app.routes directly to avoid Pydantic JSON Schema generation errors
    caused by complex mock types in v15 components.
    """
    # Flatten all routes (including mounted/included routers)
    # in FastAPI, app.routes contains everything if included properly.
    registered_paths = {route.path for route in app.routes}

    # Check for V18 Governance
    assert "/api/v18/governance/proposals" in registered_paths, (
        "Governance V18 routes missing"
    )

    # Check for V18 Content
    assert "/api/v18/content/feed" in registered_paths, "Content V18 routes missing"

    # Check for V1 Auth (compatibility layer)
    # V1 auth routes are registered with full paths like /api/v1/auth/nonce
    v1_auth_routes = [p for p in registered_paths if p.startswith("/api/v1/auth")]
    assert len(v1_auth_routes) > 0, (
        f"Auth V1 routes missing. Found routes: {sorted(registered_paths)}"
    )

    # Check for V1 Wallets (Legacy/Hybrid)
    # Check if any route starts with /api/v1/wallets
    wallet_present = any(p.startswith("/api/v1/wallets") for p in registered_paths)
    assert wallet_present, "Wallet V1 routes missing"


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
