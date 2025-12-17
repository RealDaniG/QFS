"""
Deterministic Appeal Scoring
============================

Calculates appeal outcomes based strictly on EvidenceHash and Vote Weights.
Zero-Sim requirement: 100% Deterministic Math (CertifiedMath).

Scoring Algorithm (V1):
1. Base score derived from Evidence Hash (deterministically seeded).
2. Validator votes add weight (scaled int).
3. Reputation score modifies weight.
4. Final Score > Threshold -> Approved.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from v13.libs.CertifiedMath import CertifiedMath
from v13.services.governance.context import UserContext
from v13.services.governance.evidence import hash_evidence


@dataclass
class Vote:
    voter_id: str
    reputation: int
    approve: bool
    weight: int = 100  # Standard weight factor (1.00)


def score_appeal(
    evidence_payload: Dict[str, Any],
    votes: List[Vote],
    threshold: int = 5000,  # 50.00 ATR
) -> Dict[str, Any]:
    """
    Calculate the final score for an appeal.

    Args:
        evidence_payload: The raw evidence dictionary.
        votes: List of cast votes.
        threshold: Score required for approval (Scale 100).

    Returns:
        Dict with 'approved' (bool), 'score' (int), 'hash' (str).
    """
    # 1. Canonical Hash (The 'Seed')
    ev_hash = hash_evidence(evidence_payload)

    # 2. Calculate Tally using CertifiedMath
    # We use basic integer math here as CertifiedMath wrappers are mainly for
    # complex funcs (log, exp) or safe division. For additions, standard int matches
    # Zero-Sim if inputs are integers.

    score_approve = 0
    score_reject = 0

    for v in votes:
        # Weight = VoteWeight * (Reputation / 100)
        # Scale: weight(100) * rep(1000) / 100 = 1000.
        # Use CertifiedMath for division to be safe and consistent.

        # effective_weight = (v.weight * v.reputation) // 100
        effective_weight = CertifiedMath.idiv(v.weight * v.reputation, 100)

        if v.approve:
            score_approve += effective_weight
        else:
            score_reject += effective_weight

    final_score = score_approve - score_reject

    # 3. Decision
    approved = final_score > threshold

    return {
        "approved": approved,
        "score_net": final_score,
        "score_approve": score_approve,
        "score_reject": score_reject,
        "evidence_hash": ev_hash,
        "threshold": threshold,
    }
