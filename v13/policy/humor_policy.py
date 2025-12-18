"""
HumorPolicy.py - Policy configuration and integration for humor signals

This module provides policy configurations and integration for the humor signal addon,
including reward calculation, observability, and explainability features.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from .policy_engine import PolicyEngine, PolicyConfiguration, PolicyHints

# Standard ZSC Scale for V13 Policies
SCALE = 10**9


@dataclass
class HumorPolicy:
    """Explicit HumorPolicy struct for QFS V13.7 compliance."""

    enabled: bool
    mode: str
    dimension_weights: Dict[str, int]
    max_bonus_ratio: int
    per_user_daily_cap_atr: float
    version: str = "v1.0.0"
    hash: str = ""

    def __post_init__(self):
        """Initialize hash for policy versioning."""
        self.hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculate deterministic hash of policy configuration."""
        policy_data = {
            "enabled": self.enabled,
            "mode": self.mode,
            "dimension_weights": {
                k: v for k, v in sorted(self.dimension_weights.items())
            },
            "max_bonus_ratio": self.max_bonus_ratio,
            "per_user_daily_cap_atr": self.per_user_daily_cap_atr,
            "version": self.version,
        }
        json_str = json.dumps(policy_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()


class HumorPolicyConfig:
    """Configuration for humor policy rules and reward calculations."""

    def __init__(self):
        self.dimension_weights = {
            "chronos": 150000000,  # 0.15
            "lexicon": 100000000,  # 0.10
            "surreal": 100000000,  # 0.10
            "empathy": 200000000,  # 0.20
            "critique": 150000000,  # 0.15
            "slapstick": 100000000,  # 0.10
            "meta": 200000000,  # 0.20
        }
        self.max_humor_bonus = 250000000  # 0.25
        self.daily_user_cap = 1
        self.enabled = True
        self.recognition_only = False
        self.anomaly_spike_threshold = 2
        self.anomaly_duration_minutes = 60


@dataclass
class HumorBonusCalculation:
    """Result of humor bonus calculation."""

    bonus_factor: float
    dimensions_used: Dict[str, int]
    weights_applied: Dict[str, int]
    cap_applied: Optional[float] = None
    policy_version: str = "v1.0.0"


@dataclass
class HumorObservationStats:
    """Statistics for humor signal observability."""

    total_signals_processed: int = 0
    dimension_distributions: Dict[str, List[int]] = field(default_factory=dict)
    average_confidence: int = 0
    bonus_distribution: List[float] = field(default_factory=list)
    anomaly_count: int = 0


class HumorSignalPolicy:
    """
    Policy integration for humor signals that maps 7-dimensional vectors to rewards.

    This class handles:
    1. Mapping humor dimensions to reward bonuses
    2. Applying caps and policy constraints
    3. Handling policy toggles (enabled/disabled, recognition-only)
    4. Anomaly detection for humor-derived rewards
    """

    def __init__(
        self,
        config: Optional[HumorPolicyConfig] = None,
        policy: Optional[HumorPolicy] = None,
    ):
        """
        Initialize the humor signal policy.

        Args:
            config: Humor policy configuration (legacy)
            policy: Explicit HumorPolicy struct (preferred)
        """
        self.config = config or HumorPolicyConfig()
        self.policy = policy or HumorPolicy(
            enabled=True,
            mode="rewarding",
            dimension_weights={
                "chronos": 150000000,
                "lexicon": 100000000,
                "surreal": 100000000,
                "empathy": 200000000,
                "critique": 150000000,
                "slapstick": 100000000,
                "meta": 200000000,
            },
            max_bonus_ratio=250000000,
            per_user_daily_cap_atr=1,
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
        self, dimensions: Dict[str, int], confidence: int
    ) -> HumorBonusCalculation:
        """
        Calculate humor bonus factor from dimensions and confidence.

        Args:
            dimensions: 7-dimensional humor vector (scaled by 10^9)
            confidence: Confidence in the dimension scores (scaled by 10^9)

        Returns:
            HumorBonusCalculation: Calculated bonus and metadata
        """
        if not self.policy.enabled:
            return HumorBonusCalculation(
                bonus_factor=0.0,
                dimensions_used=dimensions,
                weights_applied=self.policy.dimension_weights,
                policy_version=self.policy.version,
            )
        if self.policy.mode == "recognition_only":
            return HumorBonusCalculation(
                bonus_factor=0.0,
                dimensions_used=dimensions,
                weights_applied=self.policy.dimension_weights,
                policy_version=self.policy.version,
            )
        weighted_sum = 0
        for dimension, score in sorted(dimensions.items()):
            weight = self.policy.dimension_weights.get(dimension, 0)
            weighted_sum += (score * weight) // SCALE

        base_bonus_scaled = (weighted_sum * confidence) // SCALE
        final_bonus_scaled = min(base_bonus_scaled, self.policy.max_bonus_ratio)
        final_bonus_float = final_bonus_scaled / SCALE

        self._update_observation_stats(dimensions, confidence, final_bonus_float)

        return HumorBonusCalculation(
            bonus_factor=final_bonus_float,
            dimensions_used=dimensions,
            weights_applied=self.policy.dimension_weights,
            cap_applied=self.policy.max_bonus_ratio / SCALE
            if base_bonus_scaled > self.policy.max_bonus_ratio
            else None,
            policy_version=self.policy.version,
        )

    def _update_observation_stats(
        self, dimensions: Dict[str, int], confidence: int, bonus: float
    ):
        """Update observability statistics."""
        self.observation_stats.total_signals_processed += 1
        for dimension, score in sorted(dimensions.items()):
            self.observation_stats.dimension_distributions[dimension].append(score)

        total_signals = self.observation_stats.total_signals_processed
        current_avg = self.observation_stats.average_confidence
        self.observation_stats.average_confidence = (
            current_avg * (total_signals - 1) + confidence
        ) // total_signals
        self.observation_stats.bonus_distribution.append(bonus)

    def get_observability_stats(self) -> HumorObservationStats:
        """
        Get current observability statistics for humor signals.

        Returns:
            HumorObservationStats: Current statistics
        """
        return self.observation_stats

    def check_for_anomalies(self) -> bool:
        """
        Check if current humor bonus rate indicates an anomaly.

        Returns:
            bool: True if anomaly detected
        """
        if len(self.observation_stats.bonus_distribution) < 10:
            return False
        recent_bonuses = self.observation_stats.bonus_distribution[-10:]
        recent_avg = sum(recent_bonuses) / len(recent_bonuses)
        if len(self.observation_stats.bonus_distribution) >= 100:
            historical_bonuses = self.observation_stats.bonus_distribution[:-10]
            historical_avg = sum(historical_bonuses) / len(historical_bonuses)
            if (
                historical_avg > 0
                and recent_avg / historical_avg > self.config.anomaly_spike_threshold
            ):
                self.observation_stats.anomaly_count += 1
                return True
        return False

    def get_policy_explanation(
        self, dimensions: Dict[str, int], confidence: int
    ) -> Dict[str, Any]:
        """
        Generate explanation for humor bonus calculation.

        Args:
            dimensions: 7-dimensional humor vector (scaled by 10^9)
            confidence: Confidence in the dimension scores (scaled by 10^9)

        Returns:
            Dict: Explanation of the calculation
        """
        calculation = self.calculate_humor_bonus(dimensions, confidence)

        weighted_scores = {}
        weighted_sum = 0
        for dim in sorted(dimensions):
            w = self.policy.dimension_weights.get(dim, 0)
            score = (dimensions[dim] * w) // SCALE
            weighted_scores[dim] = score
            weighted_sum += score

        explanation = {
            "policy_version": calculation.policy_version,
            "policy_hash": self.policy.hash,
            "dimensions": dimensions,
            "confidence": confidence,
            "weights": self.policy.dimension_weights,
            "weighted_scores": weighted_scores,
            "weighted_sum": weighted_sum,
            "confidence_factor": confidence,
            "base_bonus": (weighted_sum * confidence) // SCALE,
            "cap": self.policy.max_bonus_ratio,
            "cap_applied": calculation.cap_applied,
            "final_bonus": calculation.bonus_factor,
            "policy_settings": {
                "enabled": self.policy.enabled,
                "mode": self.policy.mode,
                "max_bonus": self.policy.max_bonus_ratio,
            },
        }
        return explanation
