"""
test_anchoring_stub.py - Tests for PQCAnchorService Stub

Verifies that the anchor service correctly batches events and emits
proofs when the batch size is reached.
"""

import pytest
from v13.core.pqc.PQCAnchorService import PQCAnchorService


def test_anchor_batching():
    # Setup service with small batch size
    service = PQCAnchorService(batch_size=5)

    # Submit 4 events (should not trigger)
    for i in range(4):
        h = f"hash_{i}"
        proof = service.submit_event_hash(h)
        assert proof is None

    # Submit 5th event (should trigger)
    h5 = "hash_4"
    proof = service.submit_event_hash(h5)

    assert proof is not None
    assert proof.batch_start_index == 0
    assert proof.batch_end_index == 5
    assert "MOCK_DILITHIUM_SIG" in proof.pqc_signature

    # Check that pending is cleared
    assert len(service.pending_hashes) == 0

    # Submit next 1 (should wait)
    proof2 = service.submit_event_hash("next_hash")
    assert proof2 is None


def test_anchor_chaining():
    service = PQCAnchorService(batch_size=2)
    proof1 = service.submit_event_hash("h1")
    proof1 = service.submit_event_hash("h2")  # Triggers

    assert proof1.batch_start_index == 0

    proof2 = service.submit_event_hash("h3")
    proof2 = service.submit_event_hash("h4")  # Triggers

    assert proof2.batch_start_index == 2
    assert proof2.batch_end_index == 4


if __name__ == "__main__":
    test_anchor_batching()
    test_anchor_chaining()
    print("PQC Anchoring Test PASSED")
