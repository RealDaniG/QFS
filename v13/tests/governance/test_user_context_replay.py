"""
Test UserContext Determinism
============================

Verifies that `UserContext` is strictly derived from ledger events.
"""

import pytest
from v13.services.governance.context import build_user_context


@pytest.fixture
def mock_ledger_identity():
    return [
        {"type": "IdentityCreated", "user_id": "did:qfs:alice", "wallet_id": "0xAlice"},
        {"type": "ReputationUpdated", "user_id": "did:qfs:alice", "score_delta": 50},
        {"type": "RoleAssigned", "user_id": "did:qfs:alice", "role": "VALIDATOR"},
        {
            "type": "FlagSet",
            "user_id": "did:qfs:alice",
            "flag": "is_active",
            "value": True,
        },
    ]


def test_user_context_reconstruction(mock_ledger_identity):
    """Test standard reconstruction from a clean ledger slice."""
    ctx = build_user_context("did:qfs:alice", mock_ledger_identity)

    assert ctx is not None
    assert ctx.user_id == "did:qfs:alice"
    assert ctx.wallet_id == "0xAlice"
    assert ctx.reputation_score == 50
    assert "VALIDATOR" in ctx.roles
    assert ctx.flags["is_active"] is True


def test_user_context_determinism():
    """Test that two runs with identical input produce byte-identical output (via canonical JSON)."""
    slice_a = [
        {"type": "IdentityCreated", "user_id": "did:qfs:bob", "wallet_id": "0xBob"},
        {"type": "RoleAssigned", "user_id": "did:qfs:bob", "role": "AUDITOR"},
        {"type": "ReputationUpdated", "user_id": "did:qfs:bob", "score_delta": 100},
        {"type": "ReputationUpdated", "user_id": "did:qfs:bob", "score_delta": -20},
    ]

    ctx1 = build_user_context("did:qfs:bob", slice_a)
    ctx2 = build_user_context("did:qfs:bob", slice_a)

    # Object equality
    assert ctx1 == ctx2

    # Canonical JSON string equality (Hash preimage)
    assert ctx1.to_canonical_json() == ctx2.to_canonical_json()

    # Value check
    assert ctx1.reputation_score == 80
    assert ctx1.roles == ["AUDITOR"]


def test_user_not_found():
    """Test UserContext returns None for non-existent ID."""
    events = [{"type": "IdentityCreated", "user_id": "did:qfs:charlie"}]
    ctx = build_user_context("did:qfs:dave", events)
    assert ctx is None
