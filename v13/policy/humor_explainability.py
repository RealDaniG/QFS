"""
HumorExplainability.py - Explainability layer for humor rewards

This module provides explainability features for humor-derived rewards,
allowing users and operators to understand why specific humor bonuses were awarded.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from decimal import Decimal
from .humor_policy import HumorSignalPolicy


@dataclass
class HumorRewardExplanation:
    """Detailed explanation of a humor reward calculation."""

    content_id: str
    user_id: str
    reward_event_id: str
    timestamp: int
    dimensions: Dict[str, float]
    confidence: float
    ledger_context: Dict[str, Any]
    policy_version: str
    policy_hash: str
    dimension_weights: Dict[str, float]
    weighted_scores: Dict[str, float]
    weighted_sum: float
    confidence_factor: float
    base_bonus: float
    cap_applied: Optional[float]
    final_bonus: float
    policy_settings: Dict[str, Any]
    explanation_hash: str = ""
    reason_codes: List[str] = field(default_factory=list)


class HumorExplainabilityHelper:
    """
    Explainability helper for humor rewards.

    This class provides:
    1. Detailed breakdowns of humor bonus calculations
    2. Traceability from ledger events to reward computations
    3. Verification capabilities for deterministic explanations
    """

    def __init__(self, humor_policy: HumorSignalPolicy):
        """
        Initialize the humor explainability helper.

        Args:
            humor_policy: Humor policy instance to use for explanations
        """
        self.humor_policy = humor_policy

    def explain_humor_reward(
        self,
        content_id: str,
        user_id: str,
        reward_event_id: str,
        dimensions: Dict[str, float],
        confidence: float,
        ledger_context: Dict[str, Any],
        timestamp: int,
    ) -> HumorRewardExplanation:
        """
        Generate detailed explanation for a humor reward.

        Args:
            content_id: ID of the content being rewarded
            user_id: ID of the user receiving the reward
            reward_event_id: ID of the reward event
            dimensions: 7-dimensional humor vector
            confidence: Confidence in the dimension scores
            ledger_context: Ledger-derived context metrics
            timestamp: Timestamp of the reward calculation

        Returns:
            HumorRewardExplanation: Detailed explanation
        """
        policy_explanation = self.humor_policy.get_policy_explanation(
            dimensions, confidence
        )
        reason_codes = []
        if not self.humor_policy.policy.enabled:
            reason_codes.append("HUMOR_DISABLED")
        elif self.humor_policy.policy.mode == "recognition_only":
            reason_codes.append("RECOGNITION_ONLY")
        elif policy_explanation.get("cap_applied"):
            reason_codes.append("HUMOR_CAP_APPLIED")
        explanation = HumorRewardExplanation(
            content_id=content_id,
            user_id=user_id,
            reward_event_id=reward_event_id,
            timestamp=timestamp,
            dimensions=dimensions,
            confidence=confidence,
            ledger_context=ledger_context,
            policy_version=policy_explanation["policy_version"],
            policy_hash=policy_explanation.get("policy_hash", ""),
            dimension_weights=policy_explanation["weights"],
            weighted_scores=policy_explanation["weighted_scores"],
            weighted_sum=policy_explanation["weighted_sum"],
            confidence_factor=policy_explanation["confidence_factor"],
            base_bonus=policy_explanation["base_bonus"],
            cap_applied=policy_explanation.get("cap_applied"),
            final_bonus=policy_explanation["final_bonus"],
            policy_settings=policy_explanation["policy_settings"],
            reason_codes=reason_codes,
        )
        explanation.explanation_hash = self._generate_explanation_hash(explanation)
        return explanation

    def _generate_explanation_hash(self, explanation: HumorRewardExplanation) -> str:
        """
        Generate deterministic hash for explanation verification.

        Args:
            explanation: Explanation to hash

        Returns:
            str: SHA256 hash of the explanation
        """
        hash_data = {
            "content_id": explanation.content_id,
            "user_id": explanation.user_id,
            "reward_event_id": explanation.reward_event_id,
            "timestamp": explanation.timestamp,
            "dimensions": explanation.dimensions,
            "confidence": explanation.confidence,
            "policy_version": explanation.policy_version,
            "policy_hash": explanation.policy_hash,
            "weighted_sum": explanation.weighted_sum,
            "confidence_factor": explanation.confidence_factor,
            "base_bonus": explanation.base_bonus,
            "final_bonus": explanation.final_bonus,
            "reason_codes": explanation.reason_codes,
        }
        json_str = json.dumps(hash_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()

    def verify_explanation_consistency(
        self, explanation: HumorRewardExplanation
    ) -> bool:
        """
        Verify that an explanation is consistent with current policy.

        Args:
            explanation: Explanation to verify

        Returns:
            bool: True if explanation is consistent
        """
        recalculated = self.humor_policy.get_policy_explanation(
            explanation.dimensions, explanation.confidence
        )
        # Fix: Use Decimal for deterministic float comparison tolerance
        return (
            abs(recalculated["final_bonus"] - explanation.final_bonus)
            < Decimal("1e-10")
            and recalculated["policy_version"] == explanation.policy_version
            and (recalculated["weights"] == explanation.dimension_weights)
            and (recalculated.get("policy_hash", "") == explanation.policy_hash)
        )

    def get_simplified_explanation(
        self, explanation: HumorRewardExplanation
    ) -> Dict[str, Any]:
        """
        Generate simplified explanation for end users.

        Args:
            explanation: Detailed explanation

        Returns:
            Dict: Simplified explanation
        """
        strongest_dimension = max(explanation.dimensions.items(), key=lambda x: x[1])
        was_capped = explanation.cap_applied is not None
        simplified = {
            "summary": f"Received humor bonus of {explanation.final_bonus:.2%}",
            "reason": f"Strong {strongest_dimension[0]} score ({strongest_dimension[1]:.2f})",
            "reason_codes": explanation.reason_codes,
            "breakdown": {
                "dimensions": explanation.dimensions,
                "confidence": explanation.confidence,
                "final_bonus": explanation.final_bonus,
            },
            "policy_info": {
                "version": explanation.policy_version,
                "hash": explanation.policy_hash + "...",
                "was_capped": was_capped,
                "max_bonus": explanation.cap_applied or "N/A",
            },
            "verification": {
                "hash": explanation.explanation_hash + "...",
                "consistent": self.verify_explanation_consistency(explanation),
            },
        }
        return simplified

    def batch_explain_rewards(
        self, reward_data_list: List[Dict[str, Any]]
    ) -> List[HumorRewardExplanation]:
        """
        Generate explanations for multiple rewards in batch.

        Args:
            reward_data_list: List of reward data dictionaries

        Returns:
            List[HumorRewardExplanation]: List of explanations
        """
        explanations = []
        for reward_data in sorted(reward_data_list):
            explanation = self.explain_humor_reward(**reward_data)
            explanations.append(explanation)
        return explanations
