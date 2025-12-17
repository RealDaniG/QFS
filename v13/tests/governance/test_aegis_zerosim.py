"""
Test AEGIS Zero-Sim Determinism
===============================

Verifies that AEGIS policies are pure functions of UserContext.
"""

import pytest
from v13.services.governance.context import UserContext
from v13.services.aegis.policies import evaluate_policy


@pytest.fixture
def ctx_banned():
    return UserContext(
        user_id="did:qfs:bad",
        wallet_id="0x00",
        reputation_score=500,
        roles=[],
        flags={"is_banned": True},
    )


@pytest.fixture
def ctx_validator():
    return UserContext(
        user_id="did:qfs:val",
        wallet_id="0x01",
        reputation_score=2000,  # > 1000
        roles=["VALIDATOR"],
        flags={"is_active": True},
    )


def test_policy_can_appeal_determinism(ctx_banned, ctx_validator):
    # Rule 1: Banned user cannot appeal
    assert evaluate_policy("can_appeal", ctx_banned, evidence_hash="abc") is False

    # Rule 2: Validator with high rep can appeal
    assert evaluate_policy("can_appeal", ctx_validator, evidence_hash="abc") is True

    # Determinism check
    # Running multiple times yields same result
    for _ in range(10):
        assert evaluate_policy("can_appeal", ctx_validator, evidence_hash="abc") is True


def test_policy_can_vote_determinism(ctx_banned, ctx_validator):
    # Banned user has no roles -> False
    assert evaluate_policy("can_vote", ctx_banned, appeal_id="1") is False

    # Validator -> True
    assert evaluate_policy("can_vote", ctx_validator, appeal_id="1") is True
