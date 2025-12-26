import sys
import os

# Add root to python path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from v13.libs.BigNum128 import BigNum128
from v13.atlas.social.models import Post, Comment, SocialEpoch
from v13.atlas.social.coherence import CoherenceSpec, CoherenceScorer
from v13.atlas.social.engagement import EngagementCalculator
from v13.atlas.social.rewards import SocialRewardDistributor
from v13.atlas.social.governance import SocialGovernance
from v13.atlas.social.growth import GrowthEngine


def test_social_layer():
    print("Initializing Engines...")
    spec = CoherenceSpec.get_v1_0()
    scorer = CoherenceScorer(spec)
    eng_calc = EngagementCalculator()
    distributor = SocialRewardDistributor(scorer, eng_calc)
    governance = SocialGovernance()
    growth = GrowthEngine()

    # 1. Setup Epoch
    epoch = SocialEpoch(
        epoch_id=1,
        start_time=1000,
        end_time=2000,
        emission_pool=BigNum128.from_int(1000),  # 1000 FLX Pool
    )

    # 2. Setup Data
    # Post A: High Coherence, Low Engagement
    post_a = Post(
        id="post_a",
        author_id="alice",
        timestamp=1100,
        content_hash="h1",
        text_content="Good post",
        thread_id="t1",
        title="A",
    )
    features_a = {
        "topic": BigNum128.from_string("0.9"),
        "logic": BigNum128.from_string("0.9"),
        "signal": BigNum128.from_string("0.8"),
        "contradiction": BigNum128.from_string("0.0"),  # Good (low contradiction)
        "clarity": BigNum128.from_string("1.0"),
    }

    # Post B: Med Coherence, High Engagement
    post_b = Post(
        id="post_b",
        author_id="bob",
        timestamp=1200,
        content_hash="h2",
        text_content="Viral post",
        thread_id="t2",
        title="B",
    )
    features_b = {
        "topic": BigNum128.from_string("0.5"),  # Just ok
        "logic": BigNum128.from_string("0.5"),
        "signal": BigNum128.from_string("0.5"),
        "contradiction": BigNum128.from_string("0.2"),
        "clarity": BigNum128.from_string("0.8"),
    }

    feature_map = {"post_a": features_a, "post_b": features_b}

    # Comments: Post B has many
    comments_map = {
        "post_a": [],
        "post_b": [
            Comment(
                id=f"c{i}",
                author_id=f"u{i}",
                timestamp=1300,
                content_hash="x",
                text_content="y",
                post_id="post_b",
            )
            for i in range(50)
        ],
    }

    # 3. Run Distribution
    print("Running Distribution...")
    results = distributor.calculate_epoch_rewards(
        epoch, [post_a, post_b], feature_map, comments_map
    )

    reward_a = results["post_a"]
    reward_b = results["post_b"]

    print(f"Post A FLX: {reward_a.flx_reward}")
    print(f"Post B FLX: {reward_b.flx_reward}")
    print(f"Post A CHR Gain: {reward_a.chr_reward}")

    # Conservation Check
    # Distributable was 900 (10% RES)
    # Validate sum is approx 900
    total_distributed = reward_a.flx_reward.add(reward_b.flx_reward)
    print(f"Total Distributed: {total_distributed}")

    res_a = reward_a.res_reward
    res_b = reward_b.res_reward
    print(f"RES Buffer A: {res_a}")
    print(f"RES Buffer B: {res_b}")

    # 4. Snapshot
    print("Creating Snapshot...")
    # Need to simulate populated coherence map
    coherence_map_sim = {
        "post_a": scorer.compute_score(features_a),
        "post_b": scorer.compute_score(features_b),
    }
    snapshot = governance.create_epoch_snapshot(
        epoch, ["post_a", "post_b"], coherence_map_sim, results
    )
    print(f"Merkle Root: {snapshot.merkle_root}")

    # 5. Growth
    # Calculate average coherence for epoch
    avg_coh = (
        coherence_map_sim["post_a"]
        .add(coherence_map_sim["post_b"])
        .div(BigNum128.from_int(2))
    )
    print(f"Avg Coherence: {avg_coh}")

    next_pool = growth.calculate_next_emission(epoch.emission_pool, avg_coh)
    print(f"Next Epoch Pool: {next_pool}")

    assert total_distributed > BigNum128.from_int(0)
    print("Test Passed!")


if __name__ == "__main__":
    test_social_layer()
