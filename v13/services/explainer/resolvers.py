"""
resolvers.py - Type-specific explanation resolvers
"""

from typing import Dict, Any, List
from ...libs.CertifiedMath import CertifiedMath
from ...libs.BigNum128 import BigNum128


class BaseResolver:
    """Base class for explanation resolvers."""

    def resolve(
        self, entity_id: str, ledger_events: List[Dict[str, Any]], policy_version: str
    ) -> Dict[str, Any]:
        raise NotImplementedError


class RewardResolver(BaseResolver):
    """Resolves reward explanations."""

    def resolve(
        self, entity_id: str, ledger_events: List[Dict[str, Any]], policy_version: str
    ) -> Dict[str, Any]:
        # Find the reward event
        reward_event = None
        for event in sorted(ledger_events, key=lambda x: str(x.get('id', '')) + str(x.get('type', ''))):
            if event.get("id") == entity_id and event.get("type") == "REWARD":
                reward_event = event
                break

        if not reward_event:
            return {"inputs": [], "computation": {}}

        # Mock computation - use integers for Zero-Sim compliance
        base_reward = reward_event.get("amount", 100)
        coherence_multiplier_scaled = 120  # 1.2 * 100 (scaled by 100)

        # Ensure base_reward is a BigNum128
        if not isinstance(base_reward, BigNum128):
            base_reward = BigNum128.from_int(base_reward)
        
        # Ensure coherence_multiplier_scaled is a BigNum128
        if not isinstance(coherence_multiplier_scaled, BigNum128):
            coherence_multiplier_scaled = BigNum128.from_int(coherence_multiplier_scaled)

        # Create CertifiedMath instance for calculations
        cm = CertifiedMath()
        
        # Perform calculations
        multiplied_reward = cm.mul(base_reward, coherence_multiplier_scaled)
        final_reward = cm.idiv(multiplied_reward, 100)

        return {
            "inputs": [
                {
                    "event_id": "content_posted",
                    "weight": 60,  # 0.6 * 100 (percentage as integer)
                    "description": "Content contribution",
                },
                {
                    "event_id": "coherence_score",
                    "weight": 40,  # 0.4 * 100 (percentage as integer)
                    "description": "User reputation",
                },
            ],
            "computation": {
                "base_reward": base_reward.to_decimal_string(),  # Convert to string for JSON serialization
                "coherence_multiplier_scaled": coherence_multiplier_scaled.to_decimal_string(),  # Convert to string for JSON serialization
                "final_reward": final_reward.to_decimal_string(),  # Convert to string for JSON serialization
            },
        }


class CoherenceResolver(BaseResolver):
    """Resolves coherence score change explanations."""

    def resolve(
        self, entity_id: str, ledger_events: List[Dict[str, Any]], policy_version: str
    ) -> Dict[str, Any]:
        return {
            "inputs": [
                {"event_id": "interaction_positive", "weight": 70},  # 0.7 * 100
                {"event_id": "content_quality_score", "weight": 30},  # 0.3 * 100
            ],
            "computation": {
                "previous_score": 400,
                "delta": 50,
                "new_score": 450,
                "reason": "Positive community interactions",
            },
        }


class FlagResolver(BaseResolver):
    """Resolves AEGIS flag explanations."""

    def resolve(
        self, entity_id: str, ledger_events: List[Dict[str, Any]], policy_version: str
    ) -> Dict[str, Any]:
        return {
            "inputs": [{"event_id": "content_analysis", "weight": 100}],  # 1.0 * 100
            "computation": {
                "flag_type": "ADVISORY",
                "confidence": 85,  # 0.85 * 100 (percentage as integer)
                "matched_patterns": ["safety_keywords"],
                "human_review_required": False,
            },
        }