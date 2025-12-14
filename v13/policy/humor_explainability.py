"""
HumorExplainability.py - Explainability layer for humor rewards

This module provides explainability features for humor-derived rewards,
allowing users and operators to understand why specific humor bonuses were awarded.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from .humor_policy import HumorSignalPolicy


@dataclass
class HumorRewardExplanation:
    """Detailed explanation of a humor reward calculation."""
    content_id: str
    user_id: str
    reward_event_id: str
    timestamp: int
    
    # Input data
    dimensions: Dict[str, float]
    confidence: float
    ledger_context: Dict[str, Any]
    
    # Policy information
    policy_version: str
    dimension_weights: Dict[str, float]
    
    # Calculation breakdown
    weighted_scores: Dict[str, float]
    weighted_sum: float
    confidence_factor: float
    base_bonus: float
    cap_applied: Optional[float]
    final_bonus: float
    
    # Policy settings at time of calculation
    policy_settings: Dict[str, Any]
    
    # Deterministic hash for verification
    explanation_hash: str = ""


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
        timestamp: int
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
        # Get policy explanation
        policy_explanation = self.humor_policy.get_policy_explanation(dimensions, confidence)
        
        # Create explanation object
        explanation = HumorRewardExplanation(
            content_id=content_id,
            user_id=user_id,
            reward_event_id=reward_event_id,
            timestamp=timestamp,
            
            # Input data
            dimensions=dimensions,
            confidence=confidence,
            ledger_context=ledger_context,
            
            # Policy information
            policy_version=policy_explanation["policy_version"],
            dimension_weights=policy_explanation["weights"],
            
            # Calculation breakdown
            weighted_scores=policy_explanation["weighted_scores"],
            weighted_sum=policy_explanation["weighted_sum"],
            confidence_factor=policy_explanation["confidence_factor"],
            base_bonus=policy_explanation["base_bonus"],
            cap_applied=policy_explanation.get("cap_applied"),
            final_bonus=policy_explanation["final_bonus"],
            
            # Policy settings
            policy_settings=policy_explanation["policy_settings"]
        )
        
        # Generate deterministic hash
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
        # Create hashable representation
        hash_data = {
            "content_id": explanation.content_id,
            "user_id": explanation.user_id,
            "reward_event_id": explanation.reward_event_id,
            "timestamp": explanation.timestamp,
            "dimensions": explanation.dimensions,
            "confidence": explanation.confidence,
            "policy_version": explanation.policy_version,
            "weighted_sum": explanation.weighted_sum,
            "confidence_factor": explanation.confidence_factor,
            "base_bonus": explanation.base_bonus,
            "final_bonus": explanation.final_bonus
        }
        
        # Serialize to JSON with sorted keys for deterministic representation
        json_str = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
        
        # Generate SHA256 hash
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def verify_explanation_consistency(
        self,
        explanation: HumorRewardExplanation
    ) -> bool:
        """
        Verify that an explanation is consistent with current policy.
        
        Args:
            explanation: Explanation to verify
            
        Returns:
            bool: True if explanation is consistent
        """
        # Recalculate using same inputs
        recalculated = self.humor_policy.get_policy_explanation(
            explanation.dimensions,
            explanation.confidence
        )
        
        # Compare key values
        return (
            abs(recalculated["final_bonus"] - explanation.final_bonus) < 1e-10 and
            recalculated["policy_version"] == explanation.policy_version and
            recalculated["weights"] == explanation.dimension_weights
        )
    
    def get_simplified_explanation(
        self,
        explanation: HumorRewardExplanation
    ) -> Dict[str, Any]:
        """
        Generate simplified explanation for end users.
        
        Args:
            explanation: Detailed explanation
            
        Returns:
            Dict: Simplified explanation
        """
        # Determine strongest dimension
        strongest_dimension = max(
            explanation.dimensions.items(),
            key=lambda x: x[1]
        )
        
        # Determine if bonus was capped
        was_capped = explanation.cap_applied is not None
        
        simplified = {
            "summary": f"Received humor bonus of {explanation.final_bonus:.2%}",
            "reason": f"Strong {strongest_dimension[0]} score ({strongest_dimension[1]:.2f})",
            "breakdown": {
                "dimensions": explanation.dimensions,
                "confidence": explanation.confidence,
                "final_bonus": explanation.final_bonus
            },
            "policy_info": {
                "version": explanation.policy_version,
                "was_capped": was_capped,
                "max_bonus": explanation.cap_applied or "N/A"
            },
            "verification": {
                "hash": explanation.explanation_hash[:16] + "...",
                "consistent": self.verify_explanation_consistency(explanation)
            }
        }
        
        return simplified
    
    def batch_explain_rewards(
        self,
        reward_data_list: List[Dict[str, Any]]
    ) -> List[HumorRewardExplanation]:
        """
        Generate explanations for multiple rewards in batch.
        
        Args:
            reward_data_list: List of reward data dictionaries
            
        Returns:
            List[HumorRewardExplanation]: List of explanations
        """
        explanations = []
        
        for reward_data in reward_data_list:
            explanation = self.explain_humor_reward(**reward_data)
            explanations.append(explanation)
        
        return explanations


# Test function
def test_humor_explainability():
    """Test the humor explainability helper implementation."""
    print("Testing HumorExplainabilityHelper...")
    
    # Create humor policy and helper
    from v13.policy.humor_policy import HumorSignalPolicy
    humor_policy = HumorSignalPolicy()
    explain_helper = HumorExplainabilityHelper(humor_policy)
    
    # Test case
    dimensions = {
        "chronos": 0.8,
        "lexicon": 0.6,
        "surreal": 0.4,
        "empathy": 0.9,
        "critique": 0.7,
        "slapstick": 0.3,
        "meta": 0.5
    }
    
    ledger_context = {
        "views": 1000,
        "laughs": 800,
        "saves": 200,
        "replays": 150,
        "author_reputation": 0.9
    }
    
    # Generate explanation
    explanation = explain_helper.explain_humor_reward(
        content_id="content_123",
        user_id="user_456",
        reward_event_id="reward_789",
        dimensions=dimensions,
        confidence=0.85,
        ledger_context=ledger_context,
        timestamp=1234567890
    )
    
    print(f"Explanation generated for content {explanation.content_id}")
    print(f"Final bonus: {explanation.final_bonus:.3f}")
    print(f"Hash: {explanation.explanation_hash[:16]}...")
    
    # Verify consistency
    is_consistent = explain_helper.verify_explanation_consistency(explanation)
    print(f"Explanation consistent: {is_consistent}")
    
    # Get simplified explanation
    simplified = explain_helper.get_simplified_explanation(explanation)
    print(f"Simplified summary: {simplified['summary']}")
    
    # Test batch explanation
    batch_data = [
        {
            "content_id": f"content_{i}",
            "user_id": f"user_{i}",
            "reward_event_id": f"reward_{i}",
            "dimensions": dimensions,
            "confidence": 0.85 - i * 0.05,
            "ledger_context": ledger_context,
            "timestamp": 1234567890 + i
        }
        for i in range(3)
    ]
    
    batch_explanations = explain_helper.batch_explain_rewards(batch_data)
    print(f"Batch processed {len(batch_explanations)} explanations")
    
    print("✓ HumorExplainabilityHelper test passed!")


if __name__ == "__main__":
    test_humor_explainability()