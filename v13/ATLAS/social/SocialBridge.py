"""
SocialBridge.py - Integration Layer for ATLAS Social Components & ViralEngine

This module acts as the bridge between ATLAS social contexts (Spaces, Wall, Chat)
and the deterministic ViralEngine. It normalizes engagement data from different
sources into the strictly typed EngagementMetrics required by the protocol.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

try:
    from v13.atlas.scoring.ViralEngine import ViralEngine, EngagementMetrics
except ImportError:
    import sys
    import os

    # Fallback to local import if run directly
    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    )
    from v13.atlas.scoring.ViralEngine import ViralEngine, EngagementMetrics


@dataclass
class SocialContent:
    """Standardized content wrapper for all ATLAS objects."""

    content_id: str
    content_type: str  # 'post', 'comment', 'message', 'space_event'
    author_id: str
    timestamp: int
    metadata: Dict[str, Any]


class SocialBridge:
    """
    Bridge adapter connecting ATLAS Social Layer to ViralEngine.
    """

    def __init__(self):
        self.viral_engine = ViralEngine()

    def process_engagement(
        self, content: SocialContent, raw_metrics: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Process raw engagement data from any ATLAS component and return
        the deterministic viral score and cryptographic proof.

        Args:
            content: SocialContent object identifying the item
            raw_metrics: Dictionary of raw counts (likes, shares, views, etc.)

        Returns:
            Dict containing 'score', 'proof', and 'metrics_used'
        """
        # 1. Normalize Metrics
        metrics = EngagementMetrics(
            likes=raw_metrics.get("likes", 0),
            shares=raw_metrics.get("shares", 0),
            views=raw_metrics.get("views", 0),
            comments=raw_metrics.get("comments", 0),
            timestamp=content.timestamp,  # Bind metric snapshot to content time? Or current?
            # For Stage 3, we use content timestamp for now to ensure
            # deterministic replay if metrics are cumulative snapshot.
        )

        # 2. Calculate Score
        score = self.viral_engine.calculate_viral_score(content.content_id, metrics)

        # 3. Generate Proof
        proof = self.viral_engine.generate_score_proof(
            content.content_id, metrics, score
        )

        return {
            "content_id": content.content_id,
            "score": score,
            "proof": proof,
            "metrics_snapshot": {
                "likes": metrics.likes,
                "shares": metrics.shares,
                "views": metrics.views,
                "comments": metrics.comments,
            },
        }


def test_social_bridge():
    """Self-test for SocialBridge."""
    bridge = SocialBridge()

    # Simulate a Wall Post
    post = SocialContent(
        content_id="post_888",
        content_type="post",
        author_id="user_alice",
        timestamp=1700000000,
        metadata={"tags": ["crypto", "qfs"]},
    )

    raw_metrics = {"likes": 50, "shares": 5, "views": 200, "comments": 10}

    # Expected Score:
    # (50 * 10) + (5 * 50) + (10 * 20) + (200 * 1)
    # 500 + 250 + 200 + 200 = 1150
    # Capped at 1000

    result = bridge.process_engagement(post, raw_metrics)

    print(f"Bridge Result: {result}")

    assert result["score"] == 1000
    assert result["content_id"] == "post_888"
    assert "proof" in result

    print("SocialBridge self-test passed.")


if __name__ == "__main__":
    test_social_bridge()
