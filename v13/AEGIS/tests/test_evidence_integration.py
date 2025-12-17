"""
Integration tests for AEGIS Evidence Service.
"""

import pytest
from unittest.mock import MagicMock
from v13.AEGIS.services.evidence_service import get_proof_vectors_by_ids
from v13.core.QFSReplaySource import QFSReplaySource
from v13.libs.deterministic_helpers import det_time_isoformat


def test_get_proof_vectors_by_ids_integration():
    """
    Verify that get_proof_vectors_by_ids correctly fetches events from QFSReplaySource
    and constructs ProofVectorRef objects.
    """
    # Mock QFSReplaySource
    mock_source = MagicMock(spec=QFSReplaySource)

    # Setup mock data
    tx_id = "tx_12345"
    mock_events = [
        {
            "id": tx_id,
            "type": "RewardAllocated",
            "timestamp": det_time_isoformat(),
            "integrity_hash": "log_hash_abc",
            "state_hash": "state_hash_xyz",
            "data": {"amount": "100"},
        },
        {
            "id": "evt_2",
            "type": "GuardCheck",
            "timestamp": det_time_isoformat(),
            "integrity_hash": "log_hash_def",
        },
    ]

    mock_source.get_events_for_transaction.return_value = mock_events

    # Call service
    results = get_proof_vectors_by_ids([tx_id], mock_source)

    # Assertions
    assert len(results) == 1
    ref = results[0]
    assert ref.id == tx_id
    assert ref.scenario_type == "economic_reward"
    assert ref.log_hash == "log_hash_def"  # Should get the last log hash
    assert ref.state_hash == "state_hash_xyz"

    # Verify interaction
    mock_source.get_events_for_transaction.assert_called_with(tx_id)


def test_get_proof_vectors_empty():
    """Verify behavior with invalid IDs."""
    mock_source = MagicMock(spec=QFSReplaySource)
    mock_source.get_events_for_transaction.side_effect = ValueError("Not found")

    results = get_proof_vectors_by_ids(["invalid_id"], mock_source)
    assert len(results) == 0
