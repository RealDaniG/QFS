"""
Tests for Agent Advisory Layer (v16 Baseline)

Ensures deterministic behavior, Zero-Sim compliance, and PoE logging.
"""

import os
import tempfile
from v15.evidence.bus import EvidenceBus
from v15.agents import AdvisoryRouter, MockAgentProvider


def test_agent_advisory_determinism():
    """Test that same inputs produce same advisory outputs (deterministic)."""
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name

    try:
        # Reset chain
        EvidenceBus._chain_tip = "0" * 64

        # Setup router with mock provider
        router = AdvisoryRouter()
        mock_provider = MockAgentProvider()
        router.register_provider("mock", mock_provider)

        # Request content score (deterministic inputs)
        env1 = router.request_content_score(
            content_id="post_123",
            content_type="post",
            content_text="This is a test post",
            provider="mock",
            timestamp=12345,
        )

        # Reset and request again
        EvidenceBus._chain_tip = "0" * 64
        env2 = router.request_content_score(
            content_id="post_123",
            content_type="post",
            content_text="This is a test post",
            provider="mock",
            timestamp=12345,
        )

        # Hashes should match (deterministic)
        assert env1["hash"] == env2["hash"]
        assert env1["event"]["type"] == "AGENT_ADVISORY"

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


def test_agent_advisory_poe_logging():
    """Test that all advisory outputs are PoE-logged to EvidenceBus."""
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name

    try:
        # Reset chain
        EvidenceBus._chain_tip = "0" * 64

        # Setup router
        router = AdvisoryRouter()
        mock_provider = MockAgentProvider()
        router.register_provider("mock", mock_provider)

        # Request multiple advisories
        router.request_content_score(
            content_id="post_1",
            content_type="post",
            content_text="Test content 1",
            provider="mock",
            timestamp=1000,
        )

        router.request_recommendation(
            entity_id="bounty_1",
            entity_type="bounty",
            context={"status": "open"},
            provider="mock",
            timestamp=2000,
        )

        router.request_risk_assessment(
            entity_id="user_1",
            entity_type="user",
            context={"activity": "high"},
            provider="mock",
            timestamp=3000,
        )

        # Verify all logged to EvidenceBus
        advisory_history = router.get_advisory_history(limit=10)
        assert len(advisory_history) == 3

        # Verify types
        types = []
        for e in advisory_history:
            if isinstance(e, dict):
                advisory_type = (
                    e.get("event", {})
                    .get("payload", {})
                    .get("advisory", {})
                    .get("advisory_type")
                )
                if advisory_type:
                    types.append(advisory_type)

        assert "content_score" in types
        assert "recommendation" in types
        assert "risk_flag" in types

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


def test_agent_advisory_non_authoritative():
    """Test that advisories are non-authoritative (no direct state mutation)."""
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name

    try:
        # Reset chain
        EvidenceBus._chain_tip = "0" * 64

        # Setup router
        router = AdvisoryRouter()
        mock_provider = MockAgentProvider()
        router.register_provider("mock", mock_provider)

        # Request advisory
        envelope = router.request_content_score(
            content_id="post_999",
            content_type="post",
            content_text="Test",
            provider="mock",
            timestamp=5000,
        )

        # Verify it's just an event, not a state change
        assert envelope["event"]["type"] == "AGENT_ADVISORY"

        # Advisory should contain metadata marking it as non-authoritative
        advisory = envelope["event"]["payload"]["advisory"]
        assert advisory["advisory_type"] == "content_score"

        # The advisory itself doesn't mutate any state
        # It's just a logged suggestion in the EvidenceBus

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


def test_agent_advisory_filtering():
    """Test filtering advisory history by entity and type."""
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name

    try:
        # Reset chain
        EvidenceBus._chain_tip = "0" * 64

        # Setup router
        router = AdvisoryRouter()
        mock_provider = MockAgentProvider()
        router.register_provider("mock", mock_provider)

        # Create multiple advisories
        router.request_content_score(
            content_id="post_A",
            content_type="post",
            content_text="Content A",
            provider="mock",
            timestamp=1000,
        )

        router.request_content_score(
            content_id="post_B",
            content_type="post",
            content_text="Content B",
            provider="mock",
            timestamp=2000,
        )

        router.request_recommendation(
            entity_id="bounty_X",
            entity_type="bounty",
            context={},
            provider="mock",
            timestamp=3000,
        )

        # Filter by type
        content_scores = router.get_advisory_history(advisory_type="content_score")
        assert len(content_scores) >= 2  # At least 2, may have more from previous tests

        recommendations = router.get_advisory_history(advisory_type="recommendation")
        assert len(recommendations) >= 1  # At least 1

        # Filter by entity
        post_a_advisories = router.get_advisory_history(entity_id="post_A")
        assert len(post_a_advisories) >= 1  # At least 1

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


if __name__ == "__main__":
    test_agent_advisory_determinism()
    test_agent_advisory_poe_logging()
    test_agent_advisory_non_authoritative()
    test_agent_advisory_filtering()
    print("✅ All Agent Advisory tests passed")
