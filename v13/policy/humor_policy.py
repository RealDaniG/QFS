"""
HumorPolicy.py - Policy configuration and integration for humor signals

This module provides policy configurations and integration for the humor signal addon,
including reward calculation, observability, and explainability features.
"""

from fractions import Fraction
import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from v13.libs.BigNum128 import BigNum128
from .policy_engine import PolicyEngine, PolicyConfiguration, PolicyHints


@dataclass
class HumorPolicy:
    """Explicit HumorPolicy struct for QFS V13.7 compliance."""

    enabled: bool
    mode: str
    dimension_weights: Dict[str, BigNum128]
    max_bonus_ratio: BigNum128
    per_user_daily_cap_atr: BigNum128
    version: str = "v1.0.0"
    hash: str = ""

    def __post_init__(self) -> None:
        """Initialize hash for policy versioning."""
        self.hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculate deterministic hash of policy configuration."""
        policy_data = {
            "enabled": self.enabled,
            "mode": self.mode,
            "dimension_weights": {k: str(v) for k, v in self.dimension_weights.items()},
            "max_bonus_ratio": str(self.max_bonus_ratio),
            "per_user_daily_cap_atr": str(self.per_user_daily_cap_atr),
            "version": self.version,
        }
        json_str = json.dumps(policy_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()


class HumorPolicyConfig:
    """Configuration for humor policy rules and reward calculations."""

    def __init__(self) -> None:
        self.dimension_weights = {
            "chronos": BigNum128.from_string("0.15"),  # 3/20
            "lexicon": BigNum128.from_string("0.10"),  # 1/10
            "surreal": BigNum128.from_string("0.10"),  # 1/10
            "empathy": BigNum128.from_string("0.20"),  # 1/5
            "critique": BigNum128.from_string("0.15"),  # 3/20
            "slapstick": BigNum128.from_string("0.10"),  # 1/10
            "meta": BigNum128.from_string("0.20"),  # 1/5
        }
        self.max_humor_bonus = BigNum128.from_string("0.25")  # 1/4
        self.daily_user_cap = 1
        self.enabled = True
        self.recognition_only = False
        self.anomaly_spike_threshold = 2
        self.anomaly_duration_minutes = 60


@dataclass
class HumorBonusCalculation:
    """Result of humor bonus calculation."""

    bonus_factor: BigNum128
    dimensions_used: Dict[str, BigNum128]
    weights_applied: Dict[str, BigNum128]
    cap_applied: Optional[BigNum128] = None
    policy_version: str = "v1.0.0"


@dataclass
class HumorObservationStats:
    """Statistics for humor signal observability."""

    total_signals_processed: int = 0
    dimension_distributions: Dict[str, List[BigNum128]] = field(default_factory=dict)
    average_confidence: BigNum128 = field(default_factory=lambda: BigNum128.zero())
    bonus_distribution: List[BigNum128] = field(default_factory=list)
    anomaly_count: int = 0


class HumorSignalPolicy:
    """
    Policy integration for humor signals that maps 7-dimensional vectors to rewards.
    """

    def __init__(
        self,
        config: Optional[HumorPolicyConfig] = None,
        policy: Optional[HumorPolicy] = None,
    ):
        """
        Initialize the humor signal policy.
        """
        self.config = config or HumorPolicyConfig()
        self.policy = policy or HumorPolicy(
            enabled=True,
            mode="rewarding",
            dimension_weights={
                "chronos": BigNum128.from_string("0.15"),
                "lexicon": BigNum128.from_string("0.10"),
                "surreal": BigNum128.from_string("0.10"),
                "empathy": BigNum128.from_string("0.20"),
                "critique": BigNum128.from_string("0.15"),
                "slapstick": BigNum128.from_string("0.10"),
                "meta": BigNum128.from_string("0.20"),
            },
            max_bonus_ratio=BigNum128.from_string("0.25"),
            per_user_daily_cap_atr=BigNum128.from_int(1),
        )
        self.observation_stats = HumorObservationStats()
        for dimension in [
            "chronos",
            "lexicon",
            "surreal",
            "empathy",
            "critique",
            "slapstick",
            "meta",
        ]:
            self.observation_stats.dimension_distributions[dimension] = []

    def calculate_humor_bonus(
        self, dimensions: Dict[str, float], confidence: float
    ) -> HumorBonusCalculation:
        """
        Calculate humor bonus factor from dimensions and confidence.
        Note: inputs are accepted as float for compat, but converted immediately.
        """
        # Convert inputs to BigNum128
        dims_bn = {k: BigNum128.from_string(str(v)) for k, v in dimensions.items()}
        conf_bn = BigNum128.from_string(str(confidence))

        if not self.policy.enabled:
            return HumorBonusCalculation(
                bonus_factor=BigNum128.zero(),
                dimensions_used=dims_bn,
                weights_applied=self.policy.dimension_weights,
                policy_version=self.policy.version,
            )
        if self.policy.mode == "recognition_only":
            return HumorBonusCalculation(
                bonus_factor=BigNum128.zero(),
                dimensions_used=dims_bn,
                weights_applied=self.policy.dimension_weights,
                policy_version=self.policy.version,
            )

        weighted_sum = BigNum128.zero()
        for dimension, score_bn in sorted(dims_bn.items()):
            weight = self.policy.dimension_weights.get(dimension, BigNum128.zero())
            weighted_sum += score_bn * weight

        base_bonus = weighted_sum * conf_bn

        # Min(base_bonus, max_bonus)
        if base_bonus > self.policy.max_bonus_ratio:
            final_bonus = self.policy.max_bonus_ratio
        else:
            final_bonus = base_bonus

        self._update_observation_stats(dims_bn, conf_bn, final_bonus)
        return HumorBonusCalculation(
            bonus_factor=final_bonus,
            dimensions_used=dims_bn,
            weights_applied=self.policy.dimension_weights,
            cap_applied=self.policy.max_bonus_ratio
            if base_bonus > self.policy.max_bonus_ratio
            else None,
            policy_version=self.policy.version,
        )

    def _update_observation_stats(
        self, dimensions: Dict[str, BigNum128], confidence: BigNum128, bonus: BigNum128
    ) -> None:
        """Update observability statistics."""
        self.observation_stats.total_signals_processed += 1
        for dimension, score in sorted(dimensions.items()):
            self.observation_stats.dimension_distributions[dimension].append(score)

        # Moving average calculation using BigNum
        total_signals = self.observation_stats.total_signals_processed
        current_avg = self.observation_stats.average_confidence

        # (avg * (n-1)) + new
        numerator = (current_avg * (total_signals - 1)) + confidence
        # / n
        if total_signals > 0:
            self.observation_stats.average_confidence = numerator / BigNum128.from_int(
                total_signals
            )

        self.observation_stats.bonus_distribution.append(bonus)

    def get_observability_stats(self) -> HumorObservationStats:
        """
        Get current observability statistics for humor signals.
        """
        return self.observation_stats

    def check_for_anomalies(self) -> bool:
        """
        Check if current humor bonus rate indicates an anomaly.
        """
        if len(self.observation_stats.bonus_distribution) < 10:
            return False

        # Recent average
        recent_bonuses = self.observation_stats.bonus_distribution[-10:]
        recent_sum = sum(recent_bonuses, BigNum128.zero())
        recent_avg = recent_sum / BigNum128.from_int(len(recent_bonuses))

        if len(self.observation_stats.bonus_distribution) >= 100:
            historical_bonuses = self.observation_stats.bonus_distribution[:-10]
            hist_sum = sum(historical_bonuses, BigNum128.zero())
            historical_avg = hist_sum / BigNum128.from_int(len(historical_bonuses))

            # Divide check
            if historical_avg > BigNum128.zero():
                ratio = recent_avg / historical_avg
                if ratio > BigNum128.from_int(self.config.anomaly_spike_threshold):
                    self.observation_stats.anomaly_count += 1
                    return True
        return False

    def get_policy_explanation(
        self, dimensions: Dict[str, float], confidence: float
    ) -> Dict[str, Any]:
        """
        Generate explanation for humor bonus calculation.
        """
        calculation = self.calculate_humor_bonus(dimensions, confidence)

        # For explanation dict, we convert BigNum to decimal strings
        dims_str = {
            k: str(BigNum128.from_string(str(v))) for k, v in dimensions.items()
        }
        weights_str = {k: str(v) for k, v in self.policy.dimension_weights.items()}

        explanation = {
            "policy_version": calculation.policy_version,
            "policy_hash": self.policy.hash,
            "dimensions": dims_str,
            "confidence": str(confidence),
            "weights": weights_str,
            "weighted_scores": {
                dim: str(
                    BigNum128.from_string(str(dimensions[dim]))
                    * self.policy.dimension_weights[dim]
                )
                for dim in dimensions
            },
            "final_bonus": str(calculation.bonus_factor),
            "policy_settings": {
                "enabled": self.policy.enabled,
                "mode": self.policy.mode,
                "max_bonus": str(self.policy.max_bonus_ratio),
            },
        }
        return explanation
