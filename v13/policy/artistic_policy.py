"""
ArtisticPolicy.py - Policy configuration and integration for AES signals

This module provides policy configurations and integration for the Artistic Evaluation Signal (AES),
including reward calculation, observability, and explainability features.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
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
    dimension_weights: Dict[str, int]
    max_bonus_ratio: int
    per_user_daily_cap_atr: float
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
                k: v for k, v in sorted(self.dimension_weights.items())
            },
            "max_bonus_ratio": self.max_bonus_ratio,
            "per_user_daily_cap_atr": self.per_user_daily_cap_atr,
            "version": self.version,
        }
        json_str = json.dumps(policy_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()


@dataclass
class ArtisticBonusCalculation:
    """Result of artistic bonus calculation."""

    bonus_factor: float
    dimensions_used: Dict[str, int]
    weights_applied: Dict[str, int]
    cap_applied: Optional[float] = None
    policy_version: str = "v13.8.0-GUT"
    reputation_adjustments: List[str] = field(default_factory=list)


@dataclass
class ArtisticObservationStats:
    """Statistics for artistic signal observability."""

    total_signals_processed: int = 0
    dimension_distributions: Dict[str, List[int]] = field(default_factory=dict)
    average_confidence: int = 0
    bonus_distribution: List[float] = field(default_factory=list)
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
                "composition": 200000000,
                "color_harmony": 150000000,
                "symmetry": 100000000,
                "complexity": 100000000,
                "narrative": 150000000,
                "originality": 200000000,
                "resonance": 100000000,
            },
            max_bonus_ratio=300000000,
            per_user_daily_cap_atr=2,
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
        originality = max(0, SCALE - len(event_ids) * SCALE // 100)
        resonance = max(0, SCALE - len(event_ids) * SCALE // 50)
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
                0, {}, self.policy.dimension_weights, policy_version=self.policy.version
            )
        if hasattr(vector_input, "to_dict"):
            dimensions = {
                "composition": vector_input.composition,
                "color_harmony": vector_input.color_harmony,
                "symmetry": vector_input.symmetry,
                "complexity": vector_input.complexity,
                "narrative": vector_input.narrative,
                "originality": vector_input.originality,
                "resonance": vector_input.resonance,
            }
        elif isinstance(vector_input, dict):
            dimensions = vector_input
        else:
            raise ValueError("Invalid vector input")
        weights = self.policy.dimension_weights.copy()
        adjustments = []
        if aegis_context:
            tier = aegis_context.get("reputation_tier", "new")
            if tier == "veteran":
                boost = 150000000
                weights["originality"] = weights.get("originality", 200000000) + boost
                adjustments.append("veteran_originality_boost")
            elif tier == "established":
                boost = 100000000
                weights["resonance"] = weights.get("resonance", 100000000) + boost
                adjustments.append("established_resonance_boost")
        weighted_sum = 0
        for dim, score in sorted(dimensions.items()):
            w = weights.get(dim, 0)
            weighted_sum += score * w // SCALE
        base_bonus_scaled = weighted_sum * confidence // SCALE
        final_bonus_scaled = min(base_bonus_scaled, self.policy.max_bonus_ratio)
        final_bonus_float = final_bonus_scaled / SCALE
        cap_float = self.policy.max_bonus_ratio / SCALE
        self._update_observation_stats(dimensions, confidence, final_bonus_float)
        return ArtisticBonusCalculation(
            bonus_factor=final_bonus_float,
            dimensions_used=dimensions,
            weights_applied=weights,
            cap_applied=cap_float
            if base_bonus_scaled > self.policy.max_bonus_ratio
            else None,
            policy_version=self.policy.version,
            reputation_adjustments=adjustments,
        )

    def _update_observation_stats(
        self, dimensions: Dict[str, int], confidence: int, bonus: float
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
        self.observation_stats.average_confidence = (
            prev_avg + (confidence - prev_avg) // n
        )
