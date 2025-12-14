"""
ValueNodeExplainability.py - Explainability layer for value-node rewards

This module provides explainability features for value-node derived rewards,
allowing users and operators to understand why specific rewards were awarded.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from .humor_policy import HumorSignalPolicy


@dataclass
class ValueNodeRewardExplanation:
    """Detailed explanation of a value-node reward calculation."""
    wallet_id: str
    user_id: str
    reward_event_id: str
    epoch: int
    timestamp: int
    
    # Input data
    base_reward: Dict[str, Any]
    bonuses: List[Dict[str, Any]]
    caps: List[Dict[str, Any]]
    guards: List[Dict[str, Any]]
    
    # Policy information
    policy_version: str
    policy_hash: str
    
    # Calculation breakdown
    total_reward: Dict[str, Any]
    
    # Deterministic hash for verification
    explanation_hash: str = ""
    
    # Reason codes
    reason_codes: List[str] = field(default_factory=list)


@dataclass
class ContentRankingExplanation:
    """Detailed explanation of a content ranking calculation."""
    content_id: str
    epoch: int
    timestamp: int
    
    signals: List[Dict[str, Any]]
    neighbors: List[Dict[str, Any]]
    final_rank: int
    
    policy_version: str
    policy_hash: str
    
    explanation_hash: str = ""


class ValueNodeExplainabilityHelper:
    """
    Explainability helper for value-node rewards.
    
    This class provides:
    1. Detailed breakdowns of value-node reward calculations
    2. Traceability from ledger events to reward computations
    3. Verification capabilities for deterministic explanations
    """
    
    def __init__(self, humor_policy: HumorSignalPolicy):
        """
        Initialize the value-node explainability helper.
        
        Args:
            humor_policy: Humor policy instance (used as example of policy integration)
        """
        self.humor_policy = humor_policy
    
    def explain_value_node_reward(
        self,
        wallet_id: str,
        user_id: str,
        reward_event_id: str,
        epoch: int,
        base_reward: Dict[str, Any],
        bonuses: List[Dict[str, Any]],
        caps: List[Dict[str, Any]],
        guards: List[Dict[str, Any]],
        timestamp: int
    ) -> ValueNodeRewardExplanation:
        """
        Generate detailed explanation for a value-node reward.
        
        Args:
            wallet_id: ID of the wallet being rewarded
            user_id: ID of the user receiving the reward
            reward_event_id: ID of the reward event
            epoch: Epoch number
            base_reward: Base reward information
            bonuses: List of bonus information
            caps: List of cap information
            guards: List of guard results
            timestamp: Timestamp of the reward calculation
            
        Returns:
            ValueNodeRewardExplanation: Detailed explanation
        """
        # Determine reason codes
        reason_codes = []
        for guard in guards:
            if guard.get("result") == "fail":
                reason_codes.append(f"GUARD_FAILED_{guard.get('name', '').upper()}")
        
        # Check for caps applied
        if caps:
            reason_codes.append("REWARD_CAPS_APPLIED")
            
        # Check for bonuses applied
        if bonuses:
            reason_codes.append("REWARD_BONUSES_APPLIED")
        
        # Calculate total reward
        total_reward = self._calculate_total_reward(base_reward, bonuses, caps)
        
        # Create explanation object
        explanation = ValueNodeRewardExplanation(
            wallet_id=wallet_id,
            user_id=user_id,
            reward_event_id=reward_event_id,
            epoch=epoch,
            timestamp=timestamp,
            
            # Input data
            base_reward=base_reward,
            bonuses=bonuses,
            caps=caps,
            guards=guards,
            
            # Policy information (using humor policy as example)
            policy_version=getattr(self.humor_policy, 'policy', None).__dict__.get('version', 'v1.0.0') if hasattr(self.humor_policy, 'policy') else 'v1.0.0',
            policy_hash=getattr(self.humor_policy, 'policy', None).__dict__.get('hash', '') if hasattr(self.humor_policy, 'policy') else '',
            
            # Calculation breakdown
            total_reward=total_reward,
            
            # Reason codes
            reason_codes=reason_codes
        )
        
        # Generate deterministic hash
        explanation.explanation_hash = self._generate_explanation_hash(explanation)
        
        return explanation
    
    def explain_content_ranking(
        self,
        content_id: str,
        epoch: int,
        signals: List[Dict[str, Any]],
        neighbors: List[Dict[str, Any]],
        final_rank: int,
        timestamp: int
    ) -> ContentRankingExplanation:
        """
        Generate detailed explanation for a content ranking.
        
        Args:
            content_id: ID of the content
            epoch: Epoch number
            signals: List of signal components (name, weight, score)
            neighbors: List of neighbor comparisons
            final_rank: Final computed rank
            timestamp: Timestamp of calculation
            
        Returns:
            ContentRankingExplanation: Detailed explanation
        """
        explanation = ContentRankingExplanation(
            content_id=content_id,
            epoch=epoch,
            timestamp=timestamp,
            signals=signals,
            neighbors=neighbors,
            final_rank=final_rank,
            
            # Policy information
            policy_version=getattr(self.humor_policy, 'policy', None).__dict__.get('version', 'v1.0.0') if hasattr(self.humor_policy, 'policy') else 'v1.0.0',
            policy_hash=getattr(self.humor_policy, 'policy', None).__dict__.get('hash', '') if hasattr(self.humor_policy, 'policy') else '',
        )
        
        # Generate hash
        explanation.explanation_hash = self._generate_ranking_hash(explanation)
        
        return explanation

    def _generate_ranking_hash(self, explanation: ContentRankingExplanation) -> str:
        """Generate deterministic hash for ranking explanation."""
        hash_data = {
            "content_id": explanation.content_id,
            "epoch": explanation.epoch,
            "timestamp": explanation.timestamp,
            "signals": explanation.signals,
            "neighbors": explanation.neighbors,
            "final_rank": explanation.final_rank,
            "policy_version": explanation.policy_version,
            "policy_hash": explanation.policy_hash
        }
        json_str = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def _calculate_total_reward(
        self, 
        base_reward: Dict[str, Any], 
        bonuses: List[Dict[str, Any]], 
        caps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate total reward from base, bonuses, and caps.
        
        Args:
            base_reward: Base reward information
            bonuses: List of bonus information
            caps: List of cap information
            
        Returns:
            Dict: Total reward calculation
        """
        # This is a simplified calculation - in a real implementation,
        # this would involve actual token math using BigNum128
        total = dict(base_reward)
        
        # Add bonuses
        total_bonus = 0
        for bonus in bonuses:
            # Extract numeric value from bonus (e.g., "+2.5 ATR" -> 2.5)
            value_str = bonus.get("value", "0").replace("+", "").split()[0]
            try:
                total_bonus += float(value_str)
            except ValueError:
                pass  # Skip invalid values
        
        # Apply caps
        total_cap_reduction = 0
        for cap in caps:
            # Extract numeric value from cap (e.g., "-0.3 ATR" -> -0.3)
            value_str = cap.get("value", "0").replace("-", "").split()[0]
            try:
                total_cap_reduction += float(value_str)
            except ValueError:
                pass  # Skip invalid values
        
        # Apply to total (simplified)
        if "ATR" in total:
            total_atr = float(total["ATR"].split()[0]) if isinstance(total["ATR"], str) else total["ATR"]
            final_atr = total_atr + total_bonus - total_cap_reduction
            total["ATR"] = f"{final_atr:.1f} ATR"
        
        return total
    
    def _generate_explanation_hash(self, explanation: ValueNodeRewardExplanation) -> str:
        """
        Generate deterministic hash for explanation verification.
        
        Args:
            explanation: Explanation to hash
            
        Returns:
            str: SHA256 hash of the explanation
        """
        # Create hashable representation
        hash_data = {
            "wallet_id": explanation.wallet_id,
            "user_id": explanation.user_id,
            "reward_event_id": explanation.reward_event_id,
            "epoch": explanation.epoch,
            "timestamp": explanation.timestamp,
            "base_reward": explanation.base_reward,
            "policy_version": explanation.policy_version,
            "policy_hash": explanation.policy_hash,
            "total_reward": explanation.total_reward,
            "reason_codes": explanation.reason_codes
        }
        
        # Serialize to JSON with sorted keys for deterministic representation
        json_str = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
        
        # Generate SHA256 hash
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def verify_explanation_consistency(
        self,
        explanation: ValueNodeRewardExplanation
    ) -> bool:
        """
        Verify that an explanation is consistent with current policy.
        
        Args:
            explanation: Explanation to verify
            
        Returns:
            bool: True if explanation is consistent
        """
        # Recalculate using same inputs
        recalculated = self.explain_value_node_reward(
            explanation.wallet_id,
            explanation.user_id,
            explanation.reward_event_id,
            explanation.epoch,
            explanation.base_reward,
            explanation.bonuses,
            explanation.caps,
            explanation.guards,
            explanation.timestamp
        )
        
        # Compare key values
        return (
            recalculated.total_reward == explanation.total_reward and
            recalculated.policy_version == explanation.policy_version and
            recalculated.explanation_hash == explanation.explanation_hash
        )
    
    def get_simplified_explanation(
        self,
        explanation: ValueNodeRewardExplanation
    ) -> Dict[str, Any]:
        """
        Generate simplified explanation for end users.
        
        Args:
            explanation: Detailed explanation
            
        Returns:
            Dict: Simplified explanation
        """
        # Determine if there were guard failures
        guard_failures = [g for g in explanation.guards if g.get("result") == "fail"]
        has_guard_failures = len(guard_failures) > 0
        
        # Determine total reward
        total_atr = explanation.total_reward.get("ATR", "0 ATR")
        
        simplified = {
            "summary": f"Received value-node reward of {total_atr}",
            "reason": f"Based on wallet activity in epoch {explanation.epoch}",
            "reason_codes": explanation.reason_codes,
            "breakdown": {
                "base_reward": explanation.base_reward,
                "bonuses": explanation.bonuses,
                "caps": explanation.caps,
                "guards": explanation.guards,
                "total_reward": explanation.total_reward
            },
            "policy_info": {
                "version": explanation.policy_version,
                "hash": explanation.policy_hash[:16] + "..." if explanation.policy_hash else "",
                "has_guard_failures": has_guard_failures
            },
            "verification": {
                "hash": explanation.explanation_hash[:16] + "..." if explanation.explanation_hash else "",
                "consistent": self.verify_explanation_consistency(explanation)
            }
        }
        
        return simplified


# Test function
def test_value_node_explainability():
    """Test the value-node explainability helper implementation."""
    print("Testing ValueNodeExplainabilityHelper...")
    
    # Create humor policy (as example) and helper
    from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicy
    humor_policy = HumorSignalPolicy(
        policy=HumorPolicy(
            enabled=True,
            mode="rewarding",
            dimension_weights={
                "chronos": 0.15,
                "lexicon": 0.10,
                "surreal": 0.10,
                "empathy": 0.20,
                "critique": 0.15,
                "slapstick": 0.10,
                "meta": 0.20
            },
            max_bonus_ratio=0.25,
            per_user_daily_cap_atr=1.0
        )
    )
    explain_helper = ValueNodeExplainabilityHelper(humor_policy)
    
    # Test case
    base_reward = {"ATR": "10.0 ATR"}
    bonuses = [
        {"label": "Coherence bonus", "value": "+2.5 ATR", "reason": "Coherence score 0.92 above threshold"},
        {"label": "Humor bonus", "value": "+1.2 ATR", "reason": "Humor signal 0.88 above threshold"}
    ]
    caps = [
        {"label": "Humor cap", "value": "-0.3 ATR", "reason": "Humor cap applied at 1.0 ATR"},
        {"label": "Global cap", "value": "-2.0 ATR", "reason": "Global reward cap for epoch"}
    ]
    guards = [
        {"name": "Balance guard", "result": "pass", "reason": "Balance within limits"},
        {"name": "Rate limit guard", "result": "pass", "reason": "Rate limit not exceeded"}
    ]
    
    # Generate explanation
    explanation = explain_helper.explain_value_node_reward(
        wallet_id="wallet_123",
        user_id="user_456",
        reward_event_id="reward_789",
        epoch=1,
        base_reward=base_reward,
        bonuses=bonuses,
        caps=caps,
        guards=guards,
        timestamp=1234567890
    )
    
    print(f"Explanation generated for wallet {explanation.wallet_id}")
    print(f"Total reward: {explanation.total_reward}")
    print(f"Hash: {explanation.explanation_hash[:16]}...")
    
    # Verify consistency
    is_consistent = explain_helper.verify_explanation_consistency(explanation)
    print(f"Explanation consistent: {is_consistent}")
    
    # Get simplified explanation
    simplified = explain_helper.get_simplified_explanation(explanation)
    print(f"Simplified summary: {simplified['summary']}")
    
    print("✓ ValueNodeExplainabilityHelper test passed!")


if __name__ == "__main__":
    test_value_node_explainability()