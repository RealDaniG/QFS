"""
coherence.py - Deterministic Coherence Scoring Engine for ATLAS

Implements the logic to map content features (from off-chain agents)
to a canonical Coherence Score using versioned, immutable specs.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from v13.libs.BigNum128 import BigNum128
from v13.atlas.social.models import Post


@dataclass
class CoherenceSpec:
    """
    Defines the weights and parameters for computing Coherence Score.
    This object should be treated as immutable for a given version.
    """

    version: str

    # Weights (Must sum to 1.0 ideally, but logic handles normalization)
    # Stored as BigNum128
    w_topic_consistency: BigNum128
    w_logical_flow: BigNum128
    w_signal_noise: BigNum128
    w_non_contradiction: BigNum128
    w_language_clarity: BigNum128

    # Thresholds
    tau_min: BigNum128  # Minimum score to be eligible for rewards
    tau_max: BigNum128  # Score above which we cap/plateau

    # v1.1: HSMF Integration
    w_hsmf: BigNum128 = field(default_factory=lambda: BigNum128.from_int(0))

    @classmethod
    def get_v1_0(cls) -> "CoherenceSpec":
        """Returns the frozen V1.0 spec"""
        return cls(
            version="1.0",
            w_topic_consistency=BigNum128.from_string("0.30"),
            w_logical_flow=BigNum128.from_string("0.25"),
            w_signal_noise=BigNum128.from_string("0.20"),
            w_non_contradiction=BigNum128.from_string("0.15"),
            w_language_clarity=BigNum128.from_string("0.10"),
            w_hsmf=BigNum128.from_int(0),
            tau_min=BigNum128.from_string("0.40"),
            tau_max=BigNum128.from_string("0.95"),
        )

    @classmethod
    def get_v1_1(cls) -> "CoherenceSpec":
        """Returns V1.1 spec with HSMF Integration (80/20 split implied by weights)"""
        # We re-normalize existing weights to sum to 0.8, assign 0.2 to HSMF
        # 0.3 * 0.8 = 0.24
        # 0.25 * 0.8 = 0.20
        # 0.20 * 0.8 = 0.16
        # 0.15 * 0.8 = 0.12
        # 0.10 * 0.8 = 0.08
        # Sum = 0.80
        return cls(
            version="1.1",
            w_topic_consistency=BigNum128.from_string("0.24"),
            w_logical_flow=BigNum128.from_string("0.20"),
            w_signal_noise=BigNum128.from_string("0.16"),
            w_non_contradiction=BigNum128.from_string("0.12"),
            w_language_clarity=BigNum128.from_string("0.08"),
            w_hsmf=BigNum128.from_string("0.20"),
            tau_min=BigNum128.from_string("0.40"),
            tau_max=BigNum128.from_string("0.95"),
        )


class CoherenceScorer:
    """
    Stateless engine to compute Coherence Score from features.
    """

    def __init__(self, spec: CoherenceSpec):
        self.spec = spec
        self.ZERO = BigNum128.from_int(0)
        self.ONE = BigNum128.from_int(1)

    def compute_score(self, features: Dict[str, BigNum128]) -> BigNum128:
        """
        Compute deterministic score = DotProduct(Features, Weights)

        Args:
            features: Dictionary mapping feature names to BigNum128 values [0.0, 1.0]
                      Keys must match: 'topic', 'logic', 'signal', 'contradiction', 'clarity'
        """

        # 1. Extract values (default to 0 if missing)
        f_topic = features.get("topic", self.ZERO)
        f_logic = features.get("logic", self.ZERO)
        f_signal = features.get("signal", self.ZERO)
        f_contra = features.get("contradiction", self.ZERO)
        f_clarity = features.get("clarity", self.ZERO)

        # 2. Weighted Sum
        score = self.ZERO
        score = score.add(f_topic.mul(self.spec.w_topic_consistency))
        score = score.add(f_logic.mul(self.spec.w_logical_flow))
        score = score.add(f_signal.mul(self.spec.w_signal_noise))
        score = score.add(f_contra.mul(self.spec.w_non_contradiction))
        score = score.add(f_clarity.mul(self.spec.w_language_clarity))

        # HSMF (v1.1)
        if hasattr(self.spec, "w_hsmf") and self.spec.w_hsmf > self.ZERO:
            f_hsmf = features.get("hsmf", self.ZERO)
            score = score.add(f_hsmf.mul(self.spec.w_hsmf))

        # 3. Clamp [0, 1] (though inputs should be bounded, safety first)
        if score > self.ONE:
            score = self.ONE
        if score < self.ZERO:
            score = self.ZERO

        return score

    def get_reward_eligibility(self, score: BigNum128) -> BigNum128:
        """
        Determine eligibility ramp based on tau_min and tau_max.
        Returns a multiplier [0.0, 1.0].
        This is matching the 'Linear ramp of coherence weight' requirement.
        """
        if score < self.spec.tau_min:
            return self.ZERO

        # If > tau_max, return 1.0 (flat region)
        if score > self.spec.tau_max:
            return self.ONE

        # Linear Ramp: (score - min) / (max - min)
        numerator = score.sub(self.spec.tau_min)
        denominator = self.spec.tau_max.sub(self.spec.tau_min)

        if denominator == self.ZERO:
            return self.ONE  # Should not happen with valid spec

        return numerator.div(denominator)
