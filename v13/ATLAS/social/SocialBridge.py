"""
SocialBridge.py - Integration Layer for ATLAS Social Components & ViralEngine

This module acts as the bridge between ATLAS social contexts (Spaces, Wall, Chat)
and the deterministic ViralEngine. It normalizes engagement data from different
sources into the strictly typed EngagementMetrics required by the protocol.
"""

from dataclasses import dataclass
from typing import Dict, Any

try:
    from v13.atlas.scoring.ViralEngine import ViralEngine, EngagementMetrics
    from v13.atlas.src import build_info
except ImportError:
    import sys
    import os

    # Fallback to local import if run directly
    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    )
    from v13.atlas.scoring.ViralEngine import ViralEngine, EngagementMetrics

    try:
        from v13.atlas.src import build_info
    except ImportError:
        # Fallback if build_info missing in some test envs
        class build_info:
            BUILD_MANIFEST_SHA256 = "unknown-test-build"


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
        try:
            from v13.atlas.backend.lib.evidence_bus import EvidenceBus

            self.evidence_bus = EvidenceBus()
        except ImportError:
            print("Warning: EvidenceBus not available in SocialBridge context")
            self.evidence_bus = None

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

    def normalize_metrics_for_rewards(
        self, raw_metrics: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Adapts raw metrics for use in Social Rewards.
        Returns a simplified dict of {metric_name: count}.
        """
        # This could interface with ViralEngine to get weighted "quality" metrics
        # For now, pass through standard keys
        return {
            "shares": raw_metrics.get("shares", 0),
        }

    def emit_reward_events(self, epoch_id: int, rewards: Dict[str, Any]):
        """
        Emits SOCIAL_REWARD_APPLIED events for the EvidenceBus.
        Expects rewards dict to contain SocialRewardReceipt objects.
        """
        events = []
        for post_id, receipt in rewards.items():
            # Receipt has .bundle and .coherence_score etc.
            bundle = receipt.bundle
            event = {
                "type": "SOCIAL_REWARD_APPLIED",
                "epoch_id": receipt.epoch_id,  # Use receipt's epoch which should match
                "post_id": receipt.post_id,
                "author_id": receipt.author_id,
                # Factors
                "coherence_score": receipt.coherence_score.to_decimal_string(),
                "engagement_weight": receipt.engagement_weight.to_decimal_string(),
                "sybil_multiplier": receipt.sybil_multiplier.to_decimal_string(),
                "eligibility_factor": receipt.eligibility_factor.to_decimal_string(),
                # Rewards
                "flx_reward": bundle.flx_reward.to_decimal_string(),
                "chr_reward": bundle.chr_reward.to_decimal_string(),
                "res_reward": bundle.res_reward.to_decimal_string(),
                # Versioning
                "v13_version": "v13.5.0-social-v2",
                "build_manifest_sha256": build_info.BUILD_MANIFEST_SHA256,
            }
            events.append(event)

            # Publish to EvidenceBus
            # Using 'social_node' as actor for now, or could use the author_id if self-identifying?
            # Better: 'social_distributor' service identity.
            self.evidence_bus.log_evidence(
                event_type="SOCIAL_REWARD_APPLIED",
                actor_wallet="social_distributor_v2",
                payload=event,
            )

        return events


def test_social_bridge():
    """Self-test for SocialBridge."""
    bridge = SocialBridge()
    from v13.libs.BigNum128 import BigNum128
    from v13.core.reward_types import RewardBundle
    from v13.atlas.social.models import SocialRewardReceipt

    # Simulate a Wall Post
    post = SocialContent(
        content_id="post_888",
        content_type="post",
        author_id="user_alice",
        timestamp=1700000000,
        metadata={"tags": ["crypto", "qfs"]},
    )

    raw_metrics = {"likes": 50, "shares": 5, "views": 200, "comments": 10}

    result = bridge.process_engagement(post, raw_metrics)
    rewards_input = bridge.normalize_metrics_for_rewards(raw_metrics)

    print(f"Bridge Result: {result}")
    print(f"Rewards Input: {rewards_input}")

    assert result["score"] == 1000
    assert result["content_id"] == "post_888"
    assert "proof" in result

    # Test Events
    mock_bundle = RewardBundle(
        flx_reward=BigNum128.from_int(100),
        chr_reward=BigNum128.from_int(10),
        res_reward=BigNum128.from_int(5),
        psi_sync_reward=BigNum128.zero(),
        atr_reward=BigNum128.zero(),
        nod_reward=BigNum128.zero(),
        total_reward=BigNum128.from_int(100),
    )
    mock_receipt = SocialRewardReceipt(
        epoc_id=1,
        post_id="post_888",
        author_id="alice",
        bundle=mock_bundle,
        coherence_score=BigNum128.from_string("0.9"),
        engagement_weight=BigNum128.from_string("1.5"),
        sybil_multiplier=BigNum128.from_string("1.0"),
        eligibility_factor=BigNum128.from_string("1.0"),
    )

    events = bridge.emit_reward_events(1, {"post_888": mock_receipt})
    assert len(events) == 1
    assert events[0]["type"] == "SOCIAL_REWARD_APPLIED"
    assert events[0]["coherence_score"] == "0.900000000000000000"
    assert "build_manifest_sha256" in events[0]

    print("SocialBridge self-test passed.")


if __name__ == "__main__":
    test_social_bridge()
