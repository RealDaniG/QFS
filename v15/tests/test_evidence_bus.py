"""
Tests for EvidenceBus (v16 Baseline)

Ensures deterministic behavior and Zero-Sim compliance.
"""

import os
import tempfile
from v15.evidence.bus import EvidenceBus


def test_evidence_bus_emit():
    """Test basic event emission."""
    # Use temp file for testing
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name

    try:
        # Reset chain
        EvidenceBus._chain_tip = "0" * 64

        # Emit event
        envelope = EvidenceBus.emit("TEST_EVENT", {"data": "test", "timestamp": 0})

        assert envelope["event"]["type"] == "TEST_EVENT"
        assert envelope["event"]["payload"]["data"] == "test"
        assert "hash" in envelope
        assert "signature" in envelope
        assert len(envelope["hash"]) == 64  # SHA3-256 hex

    finally:
        # Cleanup
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


def test_evidence_bus_chain_integrity():
    """Test that events form a valid hash chain."""
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name

    try:
        # Reset chain
        EvidenceBus._chain_tip = "0" * 64

        # Emit multiple events
        env1 = EvidenceBus.emit("EVENT_1", {"timestamp": 0})
        env2 = EvidenceBus.emit("EVENT_2", {"timestamp": 1})
        env3 = EvidenceBus.emit("EVENT_3", {"timestamp": 2})

        # Verify chain linkage
        assert env1["event"]["prev_hash"] == "0" * 64
        assert env2["event"]["prev_hash"] == env1["hash"]
        assert env3["event"]["prev_hash"] == env2["hash"]

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


def test_evidence_bus_determinism():
    """Test that same inputs produce same outputs (deterministic)."""
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name

    try:
        # Reset chain
        EvidenceBus._chain_tip = "0" * 64

        # Emit event with fixed timestamp
        payload = {"data": "deterministic_test", "timestamp": 12345}
        env1 = EvidenceBus.emit("DETERMINISM_TEST", payload)

        # Reset and emit again
        EvidenceBus._chain_tip = "0" * 64
        env2 = EvidenceBus.emit("DETERMINISM_TEST", payload)

        # Hashes should match (deterministic)
        assert env1["hash"] == env2["hash"]

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


if __name__ == "__main__":
    test_evidence_bus_emit()
    test_evidence_bus_chain_integrity()
    test_evidence_bus_determinism()
    print("✅ All EvidenceBus tests passed")
