"""
ViralEngine.py - Deterministic Viral Scoring & Engagement Tracking for ATLAS

This module implements the placeholder logic for deterministic viral scoring,
enforcing "Viral Determinism" (v15 invariant). It ensures that given a set of
engagement inputs (likes, shares, views), the resulting "Viral Score" is
bit-for-bit reproducible, preventing algorithm manipulation.

Invariants Enforced:
- VIRAL-I1: Deterministic Scoring (Input Set -> Single Output Score)
- VIRAL-I2: Engagement Capping (Max Score per Time Window)
"""

import hashlib
import json
from dataclasses import dataclass


@dataclass
class EngagementMetrics:
    likes: int
    shares: int
    views: int
    comments: int
    timestamp: int


class ConstraintChecker:
    """Enforces constitutional caps on viral scoring."""

    MAX_SCORE_PER_CONTENT = 1000
    MAX_VELOCITY_PER_HOUR = 500  # Max score gain per hour

    @staticmethod
    def check_caps(raw_score: int) -> int:
        return min(raw_score, ConstraintChecker.MAX_SCORE_PER_CONTENT)


class ViralEngine:
    """
    Calculates viral scores deterministically with constitutional constraints.
    """

    def __init__(self):
        self.constraint_checker = ConstraintChecker()

    def calculate_viral_score(self, content_id: str, metrics: EngagementMetrics) -> int:
        """
        Calculate a deterministic viral score based on engagement metrics.
        FORMULA: Score = (Likes * 10) + (Shares * 50) + (Comments * 20) + (Views * 1)
        """
        # 1. Deterministic Input Serialization
        data = {
            "content_id": content_id,
            "likes": metrics.likes,
            "shares": metrics.shares,
            "views": metrics.views,
            "comments": metrics.comments,
        }

        # 2. Score Calculation (Deterministic Function)
        raw_score = (
            (metrics.likes * 10)
            + (metrics.shares * 50)
            + (metrics.comments * 20)
            + (metrics.views * 1)
        )

        # 3. Apply Constitutional Caps
        final_score = self.constraint_checker.check_caps(raw_score)

        return final_score

    def generate_score_proof(
        self, content_id: str, metrics: EngagementMetrics, score: int
    ) -> str:
        """
        Generate a cryptographic proof that a score was derived from specific metrics.
        """
        proof_data = {
            "content_id": content_id,
            "metrics": {
                "likes": metrics.likes,
                "shares": metrics.shares,
                "views": metrics.views,
                "comments": metrics.comments,
            },
            "score": score,
            "formula": "10*L + 50*S + 20*C + 1*V",
            "cap": ConstraintChecker.MAX_SCORE_PER_CONTENT,
        }
        proof_json = json.dumps(proof_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(proof_json.encode("utf-8")).hexdigest()


def test_viral_engine():
    """Self-test for ViralEngine invariants."""
    engine = ViralEngine()
    metrics = EngagementMetrics(
        likes=10, shares=2, views=100, comments=5, timestamp=123456789
    )

    # 10*10 + 2*50 + 5*20 + 100*1 = 100 + 100 + 100 + 100 = 400
    score = engine.calculate_viral_score("content-123", metrics)
    assert score == 400, f"Expected 400, got {score}"

    # Verify Proof
    proof = engine.generate_score_proof("content-123", metrics, score)
    assert proof is not None
    assert len(proof) == 64  # SHA-256 hex digest length

    # Cap check
    high_metrics = EngagementMetrics(
        likes=1000, shares=1000, views=10000, comments=1000, timestamp=123
    )
    capped_score = engine.calculate_viral_score("content-high", high_metrics)
    assert capped_score == 1000, f"Expected 1000, got {capped_score}"

    print("ViralEngine self-test passed.")


if __name__ == "__main__":
    test_viral_engine()
