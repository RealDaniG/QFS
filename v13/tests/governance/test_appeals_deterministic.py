"""
Test Appeals Determinism
========================

Verifies boolean determinism of the scoring engine.
"""

import pytest
from v13.services.governance.appeals import score_appeal, Vote


def test_scoring_determinism():
    """Same votes + same evidence must yield same score."""
    evidence = {"id": "ev_001", "content": "spam"}
    votes = [
        Vote(voter_id="alice", reputation=1000, approve=True),  # +1000
        Vote(voter_id="bob", reputation=500, approve=False),  # -500
    ]

    # Net = 500. Threshold = 400. -> Approved.
    res1 = score_appeal(evidence, votes, threshold=400)
    res2 = score_appeal(evidence, votes, threshold=400)

    assert res1["score_net"] == 500
    assert res1["approved"] is True
    assert res1 == res2


def test_scoring_threshold_failure():
    """Net score below threshold -> Rejected."""
    evidence = {"id": "ev_002"}
    votes = [
        Vote(voter_id="alice", reputation=200, approve=True)  # +200
    ]

    res = score_appeal(evidence, votes, threshold=500)
    assert res["score_net"] == 200
    assert res["approved"] is False


def test_rounding_safety():
    """Verify integer division behavior via CertifiedMath."""
    # Weight 100 * Rep 55 // 100 = 55
    votes = [Vote(voter_id="v", reputation=55, approve=True)]
    res = score_appeal({}, votes, threshold=0)
    assert res["score_net"] == 55
