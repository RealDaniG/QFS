"""
ArtisticPolicy.py - Policy configuration and integration for AES signals

This module provides policy configurations and integration for the Artistic Evaluation Signal (AES),
including reward calculation, observability, and explainability features.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from v13.libs.BigNum128 import BigNum128
from v13.policy.artistic_constants import SCALE, PHI
from v13.policy.artistic_vector import ArtisticVector
from v13.policy.artistic_features.composition import analyze_composition
from v13.policy.artistic_features.color import analyze_color_harmony
from v13.policy.artistic_features.symmetry import analyze_symmetry
from v13.policy.artistic_features.complexity import analyze_complexity
from v13.policy.artistic_features.narrative import analyze_narrative


@dataclass
class ArtisticPolicy:
    """Explicit ArtisticPolicy struct for QFS V13.8 compliance."""

    enabled: bool
    mode: str
    dimension_weights: Dict[str, BigNum128]
    max_bonus_ratio: BigNum128
    per_user_daily_cap_atr: BigNum128
    version: str = "v13.8.0-GUT"
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
                k: str(v) for k, v in sorted(self.dimension_weights.items())
            },
            "max_bonus_ratio": str(self.max_bonus_ratio),
            "per_user_daily_cap_atr": str(self.per_user_daily_cap_atr),
            "version": self.version,
        }
        json_str = json.dumps(policy_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()


@dataclass
class ArtisticBonusCalculation:
    """Result of artistic bonus calculation."""

    bonus_factor: BigNum128
    dimensions_used: Dict[str, BigNum128]
    weights_applied: Dict[str, BigNum128]
    cap_applied: Optional[BigNum128] = None
    policy_version: str = "v13.8.0-GUT"
    reputation_adjustments: List[str] = field(default_factory=list)


@dataclass
class ArtisticObservationStats:
    """Statistics for artistic signal observability."""

    total_signals_processed: int = 0
    dimension_distributions: Dict[str, List[BigNum128]] = field(default_factory=dict)
    average_confidence: BigNum128 = field(default_factory=lambda: BigNum128.zero())
    bonus_distribution: List[BigNum128] = field(default_factory=list)
    anomaly_count: int = 0
    ROLLING_WINDOW_SIZE = 100


class ArtisticSignalPolicy:
    """
    Policy integration for AES signals that maps 7-dimensional vectors to rewards.
    Handles AEGIS Reputation tier weighting adjustments.
    """

    def __init__(self, policy: Optional[ArtisticPolicy] = None):
        """
        Initialize the artistic signal policy.
        """
        self.policy = policy or ArtisticPolicy(
            enabled=True,
            mode="rewarding",
            dimension_weights={
                "composition": BigNum128.from_string("0.2"),  # 20%
                "color_harmony": BigNum128.from_string("0.15"),
                "symmetry": BigNum128.from_string("0.1"),
                "complexity": BigNum128.from_string("0.1"),
                "narrative": BigNum128.from_string("0.15"),
                "originality": BigNum128.from_string("0.2"),
                "resonance": BigNum128.from_string("0.1"),
            },
            max_bonus_ratio=BigNum128.from_string("0.3"),
            per_user_daily_cap_atr=BigNum128.from_int(2),
        )
        self.observation_stats = ArtisticObservationStats()
        for dimension in [
            "composition",
            "color_harmony",
            "symmetry",
            "complexity",
            "narrative",
            "originality",
            "resonance",
        ]:
            self.observation_stats.dimension_distributions[dimension] = []

    def compute_vector(
        self, content_id: str, content_metadata: Dict[str, Any], event_ids: List[str]
    ) -> ArtisticVector:
        """
        Compute deterministic artistic vector using feature extractors.
        """
        composition = analyze_composition(content_metadata)
        color_harmony = analyze_color_harmony(content_metadata)
        symmetry = analyze_symmetry(content_metadata)
        complexity = analyze_complexity(content_metadata)
        narrative = analyze_narrative(content_metadata)

        len_events = len(event_ids)
        originality = max(0, SCALE - len_events * SCALE // 100)
        resonance = max(0, SCALE - len_events * SCALE // 50)

        return ArtisticVector(
            composition=composition,
            color_harmony=color_harmony,
            symmetry=symmetry,
            complexity=complexity,
            narrative=narrative,
            originality=originality,
            resonance=resonance,
            content_id=content_id,
            event_ids=sorted(event_ids),
            phi_weights=self.policy.dimension_weights,
            reason_codes=["generated_via_gut_extractors"],
        )

    def calculate_artistic_bonus(
        self,
        vector_input: Any,
        confidence: int = SCALE,
        aegis_context: Optional[Dict[str, Any]] = None,
    ) -> ArtisticBonusCalculation:
        """
        Calculate artistic bonus factor from vector and AEGIS context.
        """
        if not self.policy.enabled:
            return ArtisticBonusCalculation(
                BigNum128.zero(),
                {},
                self.policy.dimension_weights,
                policy_version=self.policy.version,
            )

        factor = BigNum128.SCALE // SCALE

        def to_bn(val: int) -> BigNum128:
            return BigNum128(val * factor)

        dimensions: Dict[str, BigNum128] = {}

        if hasattr(vector_input, "to_dict"):
            dimensions = {
                "composition": to_bn(vector_input.composition),
                "color_harmony": to_bn(vector_input.color_harmony),
                "symmetry": to_bn(vector_input.symmetry),
                "complexity": to_bn(vector_input.complexity),
                "narrative": to_bn(vector_input.narrative),
                "originality": to_bn(vector_input.originality),
                "resonance": to_bn(vector_input.resonance),
            }
        elif isinstance(vector_input, dict):
            dimensions = {k: to_bn(v) for k, v in vector_input.items()}
        else:
            raise ValueError("Invalid vector input")

        weights = self.policy.dimension_weights.copy()
        adjustments = []

        if aegis_context:
            tier = aegis_context.get("reputation_tier", "new")
            if tier == "veteran":
                boost = BigNum128.from_string("0.15")
                weights["originality"] = (
                    weights.get("originality", BigNum128.from_string("0.2")) + boost
                )
                adjustments.append("veteran_originality_boost")
            elif tier == "established":
                boost = BigNum128.from_string("0.10")
                weights["resonance"] = (
                    weights.get("resonance", BigNum128.from_string("0.1")) + boost
                )
                adjustments.append("established_resonance_boost")

        weighted_sum = BigNum128.zero()
        for dim, score_bn in sorted(dimensions.items()):
            w = weights.get(dim, BigNum128.zero())
            weighted_sum += score_bn * w

        conf_bn = to_bn(confidence)
        base_bonus = weighted_sum * conf_bn

        if base_bonus > self.policy.max_bonus_ratio:
            final_bonus = self.policy.max_bonus_ratio
        else:
            final_bonus = base_bonus

        self._update_observation_stats(dimensions, conf_bn, final_bonus)

        return ArtisticBonusCalculation(
            bonus_factor=final_bonus,
            dimensions_used=dimensions,
            weights_applied=weights,
            cap_applied=self.policy.max_bonus_ratio
            if base_bonus > self.policy.max_bonus_ratio
            else None,
            policy_version=self.policy.version,
            reputation_adjustments=adjustments,
        )

    def _update_observation_stats(
        self, dimensions: Dict[str, BigNum128], confidence: BigNum128, bonus: BigNum128
    ):
        self.observation_stats.total_signals_processed += 1
        for dim, score in sorted(dimensions.items()):
            if dim not in self.observation_stats.dimension_distributions:
                self.observation_stats.dimension_distributions[dim] = []
            dist = self.observation_stats.dimension_distributions[dim]
            dist.append(score)
            if len(dist) > self.observation_stats.ROLLING_WINDOW_SIZE:
                dist.pop(0)

        self.observation_stats.bonus_distribution.append(bonus)
        if (
            len(self.observation_stats.bonus_distribution)
            > self.observation_stats.ROLLING_WINDOW_SIZE
        ):
            self.observation_stats.bonus_distribution.pop(0)

        n = self.observation_stats.total_signals_processed
        prev_avg = self.observation_stats.average_confidence

        num = (prev_avg * BigNum128.from_int(n - 1)) + confidence
        if n > 0:
            self.observation_stats.average_confidence = num / BigNum128.from_int(n)
