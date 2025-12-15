"""
resolvers.py - Type-specific explanation resolvers
"""

from typing import Dict, Any, List


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
        for event in ledger_events:
            if event.get("id") == entity_id and event.get("type") == "REWARD":
                reward_event = event
                break

        if not reward_event:
            return {"inputs": [], "computation": {}}

        # Mock computation
        base_reward = reward_event.get("amount", 100)
        coherence_multiplier = 1.2  # Mock from user coherence

        return {
            "inputs": [
                {
                    "event_id": "content_posted",
                    "weight": 0.6,
                    "description": "Content contribution",
                },
                {
                    "event_id": "coherence_score",
                    "weight": 0.4,
                    "description": "User reputation",
                },
            ],
            "computation": {
                "base_reward": base_reward,
                "coherence_multiplier": coherence_multiplier,
                "final_reward": base_reward * coherence_multiplier,
            },
        }


class CoherenceResolver(BaseResolver):
    """Resolves coherence score change explanations."""

    def resolve(
        self, entity_id: str, ledger_events: List[Dict[str, Any]], policy_version: str
    ) -> Dict[str, Any]:
        return {
            "inputs": [
                {"event_id": "interaction_positive", "weight": 0.7},
                {"event_id": "content_quality_score", "weight": 0.3},
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
            "inputs": [{"event_id": "content_analysis", "weight": 1.0}],
            "computation": {
                "flag_type": "ADVISORY",
                "confidence": 0.85,
                "matched_patterns": ["safety_keywords"],
                "human_review_required": False,
            },
        }
