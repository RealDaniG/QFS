import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import json
import sys
import datetime

# Import components
from v13.atlas.src.api.routes.explain import router
from v13.core.observability.logger import TraceContext


# Fixture to setup app and client
@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)

    # Mock dependencies
    # We need to override get_current_user and get_replay_source
    from v13.atlas.src.api.dependencies import get_current_user, get_replay_source

    async def mock_get_current_user():
        return {"wallet_id": "test_wallet", "permissions": ["audit_all_explanations"]}

    class MockReplaySource:
        def get_reward_events(self, wallet_id, epoch):
            return [
                {
                    "id": "reward_evt_1",
                    "type": "RewardAllocated",
                    "wallet_id": wallet_id,
                    "epoch": epoch,
                    "timestamp": 1234567890,
                    # Provide data that will trigger math in ValueNodeExplainabilityHelper
                    "log_details": {
                        "base_reward": {"ATR": "100.00 ATR"},
                        "bonuses": [{"name": "Funny", "value": "10.00 ATR"}],
                        "caps": [],
                    },
                }
            ]

    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_replay_source] = MockReplaySource

    return TestClient(app)


def test_trace_propagation_end_to_end(client, capsys):
    """
    Verify that X-Trace-Id header propagates to CertifiedMath logs.
    """
    trace_id = "test-trace-12345"

    # Make request
    response = client.get(
        "/explain/reward/test_wallet?epoch=1", headers={"x-trace-id": trace_id}
    )

    assert response.status_code == 200

    # Capture stdout
    captured = capsys.readouterr()
    stdout_lines = captured.out.splitlines()

    # Filter for CertifiedMath logs
    math_logs = []
    for line in sorted(stdout_lines):
        try:
            log_entry = json.loads(line)
            if log_entry.get("message", "").startswith("CertifiedMath."):
                math_logs.append(log_entry)
        except json.JSONDecodeError:
            continue

    # Verify we found math logs
    assert len(math_logs) > 0, "No CertifiedMath logs found in stdout"

    # Verify trace_id is present
    found_trace = False
    for log in sorted(math_logs):
        if log.get("trace_id") == trace_id:
            found_trace = True
            # Verify it was a math op
            assert "inputs" in log.get("data", {})
            break

    assert found_trace, (
        f"Trace ID {trace_id} not found in CertifiedMath logs. Found: {[l.get('trace_id') for l in math_logs]}"
    )


def test_trace_propagation_no_header(client, capsys):
    """
    Verify that a new trace ID is generated if header is missing.
    """
    response = client.get("/explain/reward/test_wallet?epoch=1")
    assert response.status_code == 200

    captured = capsys.readouterr()
    stdout_lines = captured.out.splitlines()

    math_logs = [json.loads(line) for line in stdout_lines if "CertifiedMath" in line]
    assert len(math_logs) > 0

    # Just verify they HAVE a trace_id
    assert "trace_id" in math_logs[0]
    assert math_logs[0]["trace_id"]  # Not empty
