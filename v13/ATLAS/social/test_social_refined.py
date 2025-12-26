"""
test_social_refined.py - Comprehensive Test Suite for Refined Social Layer
"""

import unittest
from v13.libs.BigNum128 import BigNum128
from v13.atlas.social.models import Post, Comment, SocialEpoch
from v13.atlas.social.coherence import CoherenceSpec, CoherenceScorer
from v13.atlas.social.engagement import EngagementCalculator
from v13.atlas.social.rewards import SocialRewardDistributor
from v13.atlas.social.growth import GrowthEngine


class TestSocialRefined(unittest.TestCase):
    def setUp(self):
        self.spec = CoherenceSpec.get_v1_0()
        self.scorer = CoherenceScorer(self.spec)
        self.eng_calc = EngagementCalculator()
        self.distributor = SocialRewardDistributor(self.scorer, self.eng_calc)
        self.growth = GrowthEngine()

    def test_coherence_determinism_and_hsmf(self):
        """Test Step 1 & 4: No floats, HSMF integration"""

        # Test Case 1: Pure Coherence
        features = {
            "topic": BigNum128.from_string("1.0"),
            "logic": BigNum128.from_string("1.0"),
            "signal": BigNum128.from_string("1.0"),
            "contradiction": BigNum128.from_string("1.0"),  # 1.0 means High Consistency
            "clarity": BigNum128.from_string("1.0"),
        }
        score = self.scorer.compute_score(features)

        # Coherence 1.0 = 1.0
        self.assertEqual(score.to_decimal_string(), "1.000000000000000000")

        # Eligibility
        eligibility = self.scorer.get_reward_eligibility(score)
        self.assertTrue(eligibility.to_decimal_string() == "1.000000000000000000")

        # Below Threshold
        low_features = {"topic": BigNum128.from_string("0.1")}
        low_score = self.scorer.compute_score(low_features)
        # 0.1 * 0.3 = 0.03 < 0.40 (tau_min)
        eligibility_low = self.scorer.get_reward_eligibility(low_score)
        self.assertEqual(eligibility_low.to_decimal_string(), "0.000000000000000000")

        # HSMF Integration (use v1.1)
        spec_v1_1 = CoherenceSpec.get_v1_1()
        scorer_v1_1 = CoherenceScorer(spec_v1_1)

        # If HSMF is 0.5, and Coherence 1.0 (other features 1.0)
        # Weights: 5 features sum to 0.8. HSMF 0.2.
        # Score = (1.0 * 0.8) + (0.5 * 0.2) = 0.8 + 0.1 = 0.9

        features_hsmf = features.copy()
        features_hsmf["hsmf"] = BigNum128.from_string("0.5")

        combined = scorer_v1_1.compute_score(features_hsmf)
        self.assertEqual(combined.to_decimal_string(), "0.900000000000000000")

    def test_engagement_sybil(self):
        """Test Step 2: Engagement Saturation & Sybil"""

        # Saturation
        val_0 = self.eng_calc.compute_engagement_weight(BigNum128.from_int(0))
        self.assertEqual(val_0.to_decimal_string(), "0.500000000000000000")  # Min

        val_high = self.eng_calc.compute_engagement_weight(BigNum128.from_int(10000))
        # Should be close to 2.0
        self.assertTrue(val_high > BigNum128.from_string("1.9"))

        # Sybil
        # Age 0 vs Ramp 10 -> 0.0
        sybil_0 = self.eng_calc.compute_sybil_multiplier(0, 10)
        self.assertEqual(sybil_0.to_decimal_string(), "0.000000000000000000")

        # Age 5 vs Ramp 10 -> 0.5
        sybil_5 = self.eng_calc.compute_sybil_multiplier(5, 10)
        self.assertEqual(sybil_5.to_decimal_string(), "0.500000000000000000")

        # Age 20 vs Ramp 10 -> 1.0
        sybil_20 = self.eng_calc.compute_sybil_multiplier(20, 10)
        self.assertEqual(sybil_20.to_decimal_string(), "1.000000000000000000")

    def test_brigading_scenario(self):
        """Test Step 3: Brigading / Spam Scenario"""

        epoch = SocialEpoch(
            epoch_id=1,
            start_time=1000,
            end_time=2000,
            emission_pool=BigNum128.from_int(1000),
        )

        # Post A: High Quality (0.9), Low Engagement (5 comments)
        post_a = Post("A", "alice", 1100, "h1", "", "")
        # Actually logic is strictly weighted names.
        feat_a = {
            k: BigNum128.from_string("1.0")
            for k in ["topic", "logic", "signal", "contradiction", "clarity"]
        }
        comments_a = [Comment("c1", "u1", 1105, "hash_c1", "content")] * 5

        # Post B: Low Quality (0.3), High Engagement (100 comments) - BRIGADING
        post_b = Post("B", "bad_actor", 1200, "h2", "", "")
        feat_b = {
            k: BigNum128.from_string("0.3")
            for k in ["topic", "logic", "signal", "contradiction", "clarity"]
        }
        comments_b = [Comment("c2", "sybil", 1205, "hash_c2", "spam")] * 100

        user_ages = {"alice": 100, "bad_actor": 10}  # Mature vs Ramp Complete

        rewards = self.distributor.calculate_epoch_rewards(
            epoch,
            [post_a, post_b],
            {"A": feat_a, "B": feat_b},
            {"A": comments_a, "B": comments_b},
            user_ages,
        )

        # Verify Post B gets ZERO FLX because Coherence 0.3 < 0.4 (tau_min)
        # Even with high engagement.
        res_b = rewards["B"]
        self.assertEqual(
            res_b.bundle.flx_reward.to_decimal_string(), "0.000000000000000000"
        )

        # Post A should get all distributable FLX (900 FLX, 100 to RES)
        res_a = rewards["A"]
        # Allow tiny epsilon due to integer division (floor) in 2-pass normalization
        val_a = float(res_a.bundle.flx_reward.to_decimal_string())
        self.assertTrue(abs(val_a - 900.0) < 0.000000000000001)

    def test_growth_engine(self):
        """Test Step 3: Growth Logic"""
        # Target 0.70
        base = BigNum128.from_int(1000)

        # Case 1: Exact Target -> No change
        next_pool = self.growth.calculate_next_emission(
            base, BigNum128.from_string("0.70")
        )
        self.assertEqual(next_pool.to_decimal_string(), "1000.000000000000000000")

        # Case 2: Max Growth (e.g. 1.0 Coherence -> +0.3 delta -> 1.3x)
        next_pool_high = self.growth.calculate_next_emission(
            base, BigNum128.from_string("1.00")
        )
        # 1000 * 1.3 = 1300
        self.assertEqual(next_pool_high.to_decimal_string(), "1300.000000000000000000")

        # Case 3: Decay (e.g. 0.4 Coherence -> -0.3 delta -> 0.7x)
        next_pool_low = self.growth.calculate_next_emission(
            base, BigNum128.from_string("0.40")
        )
        self.assertEqual(next_pool_low.to_decimal_string(), "700.000000000000000000")


if __name__ == "__main__":
    unittest.main()
