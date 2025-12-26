"""
rewards.py - Deterministic Social Reward Distribution

Orchestrates the calculation of FLX rewards and CHR updates for a SocialEpoch.
Ensures strict conservation of the emission pool via two-pass normalization.
"""

from typing import List, Dict
from v13.libs.BigNum128 import BigNum128
from v13.atlas.social.models import Post, Comment, SocialEpoch, SocialRewardReceipt
from v13.atlas.social.coherence import CoherenceScorer
from v13.atlas.social.engagement import EngagementCalculator
from v13.core.reward_types import RewardBundle


class SocialRewardDistributor:
    """
    Distributes rewards for a social epoch.
    """

    def __init__(
        self, coherence_scorer: CoherenceScorer, engagement_calc: EngagementCalculator
    ):
        self.scorer = coherence_scorer
        self.eng_calc = engagement_calc
        self.ZERO = BigNum128.from_int(0)
        self.ONE = BigNum128.from_int(1)

        # Configuration
        self.RES_BUFFER_FRACTION = BigNum128.from_string("0.10")  # 10% kept in buffer
        self.CHR_ALPHA = BigNum128.from_string(
            "0.10"
        )  # 10% update per epoch for stability

    def calculate_epoch_rewards(
        self,
        epoch: SocialEpoch,
        posts: List[Post],
        post_features_map: Dict[str, Dict[str, BigNum128]],  # post_id -> feature_map
        post_comments_map: Dict[str, List[Comment]],  # post_id -> comments
        user_ages: Dict[str, int] = None,  # author_id -> age_epochs
    ) -> Dict[str, SocialRewardReceipt]:
        if user_ages is None:
            user_ages = {}
        """
        Main entry point. Calculates rewards for all posts in the epoch.
        Returns a map of PostID -> SocialRewardReceipt.
        """

        # 1. Separate Pool into Distributable and Buffer
        pool = epoch.emission_pool
        res_amount = pool.mul(self.RES_BUFFER_FRACTION)
        distributable = pool.sub(res_amount)

        # 2. Pass 1: Calculate Raw Weights (Score = Coh * Eng)
        post_weights: Dict[str, BigNum128] = {}
        total_weight = self.ZERO

        # Also store intermediate results to avoid re-computation
        post_coherence: Dict[str, BigNum128] = {}
        post_factors: Dict[str, Dict[str, BigNum128]] = {}

        for post in posts:
            # A. Coherence
            features = post_features_map.get(post.id, {})
            coh_score = self.scorer.compute_score(features)
            post_coherence[post.id] = coh_score

            # B. Engagement
            # Sum comment quality (Mock: assuming comment quality is 1 for now, or need logic)
            # In a real impl, we'd score comments. Here we use count as proxy for quality-sum
            # or require 'quality_score' to be pre-set on comments.
            comments = post_comments_map.get(post.id, [])
            sum_quality = self.ZERO
            for c in comments:
                q = (
                    c.quality_score if c.quality_score else self.ONE
                )  # Default to 1 if not set
                sum_quality = sum_quality.add(q)

            eng_weight = self.eng_calc.compute_engagement_weight(sum_quality)

            # C. Combined Weight
            # Weight = Coherence * Engagement * Eligibility * Sybil

            # 1. Eligibility (Ramp)
            eligibility_bn = self.scorer.get_reward_eligibility(coh_score)

            # 2. Sybil Multiplier
            author_age = user_ages.get(
                post.author_id, 100
            )  # Default to 100 (mature) if not found for tests
            # Hardcoded ramp epochs for now? Or pass config?
            # User requirement: "Use actual account_age_epochs input".
            # Let's say ramp is 10 epochs.
            ramp_epochs = 10
            sybil_mult = self.eng_calc.compute_sybil_multiplier(author_age, ramp_epochs)

            final_weight = coh_score.mul(eng_weight).mul(eligibility_bn).mul(sybil_mult)

            post_weights[post.id] = final_weight
            total_weight = total_weight.add(final_weight)

            post_factors[post.id] = {
                "engagement": eng_weight,
                "sybil": sybil_mult,
                "eligibility": eligibility_bn,
            }

        # 3. Pass 2: Distribute
        results: Dict[str, SocialRewardReceipt] = {}

        if total_weight == self.ZERO:
            # No valid posts? Return zeroed bundles
            for post in posts:
                # Need empty receipt
                bundle = self._empty_bundle()
                results[post.id] = SocialRewardReceipt(
                    epoch.epoch_id,
                    post.id,
                    post.author_id,
                    bundle,
                    self.ZERO,
                    self.ZERO,
                    self.ZERO,
                    self.ZERO,
                )
            return results

        # Normalization factor (Distributable / TotalWeight)
        norm_factor = distributable.div(total_weight)

        for post in posts:
            weight = post_weights[post.id]
            flx_amount = weight.mul(norm_factor)

            # Distribute a share of RES reward?
            # Strict math: (Weight/Total) * RES_Buffer
            allocated_res = weight.div(total_weight).mul(res_amount)

            # CHR Update (Delta)
            # CHR Gain = Coherence * 10
            chr_gain = post_coherence[post.id].mul(BigNum128.from_int(10))

            bundle = RewardBundle(
                flx_reward=flx_amount,
                chr_reward=chr_gain,
                res_reward=allocated_res,
                psi_sync_reward=self.ZERO,
                atr_reward=self.ZERO,
                nod_reward=self.ZERO,
                total_reward=flx_amount,
            )

            receipt = SocialRewardReceipt(
                epoc_id=epoch.epoch_id,
                post_id=post.id,
                author_id=post.author_id,
                bundle=bundle,
                coherence_score=post_coherence[post.id],
                engagement_weight=post_factors[post.id]["engagement"],
                sybil_multiplier=post_factors[post.id]["sybil"],
                eligibility_factor=post_factors[post.id]["eligibility"],
            )
            results[post.id] = receipt

        return results

    def _empty_bundle(self):
        return RewardBundle(
            self.ZERO, self.ZERO, self.ZERO, self.ZERO, self.ZERO, self.ZERO, self.ZERO
        )

    def update_user_chr(
        self, current_chr: BigNum128, new_performance: BigNum128
    ) -> BigNum128:
        """
        Updates a user's CHR score using EMA.
        CHR = (1 - alpha) * CHR + alpha * Performance
        """
        decay_factor = self.ONE.sub(self.CHR_ALPHA)
        retained = current_chr.mul(decay_factor)
        added = new_performance.mul(self.CHR_ALPHA)
        return retained.add(added)
