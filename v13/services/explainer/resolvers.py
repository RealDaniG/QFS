"""
resolvers.py - Type-specific explanation resolvers
"""
from typing import Dict, Any, List
from ...libs.CertifiedMath import CertifiedMath
from ...libs.BigNum128 import BigNum128

class BaseResolver:
    """Base class for explanation resolvers."""

    def resolve(self, entity_id: str, ledger_events: List[Dict[str, Any]], policy_version: str) -> Dict[str, Any]:
        raise NotImplementedError

class RewardResolver(BaseResolver):
    """Resolves reward explanations."""

    def resolve(self, entity_id: str, ledger_events: List[Dict[str, Any]], policy_version: str) -> Dict[str, Any]:
        reward_event = None
        for event in sorted(ledger_events, key=lambda x: str(x.get('id', '')) + str(x.get('type', ''))):
            if event.get('id') == entity_id and event.get('type') == 'REWARD':
                reward_event = event
                break
        if not reward_event:
            return {'inputs': [], 'computation': {}}
        base_reward = reward_event.get('amount', 100)
        coherence_multiplier_scaled = 120
        if not isinstance(base_reward, BigNum128):
            base_reward = BigNum128.from_int(base_reward)
        if not isinstance(coherence_multiplier_scaled, BigNum128):
            coherence_multiplier_scaled = BigNum128.from_int(coherence_multiplier_scaled)
        cm = CertifiedMath()
        multiplied_reward = cm.mul(base_reward, coherence_multiplier_scaled)
        final_reward = cm.idiv(multiplied_reward, 100)
        return {'inputs': [{'event_id': 'content_posted', 'weight': 60, 'description': 'Content contribution'}, {'event_id': 'coherence_score', 'weight': 40, 'description': 'User reputation'}], 'computation': {'base_reward': base_reward.to_decimal_string(), 'coherence_multiplier_scaled': coherence_multiplier_scaled.to_decimal_string(), 'final_reward': final_reward.to_decimal_string()}}

class CoherenceResolver(BaseResolver):
    """Resolves coherence score change explanations."""

    def resolve(self, entity_id: str, ledger_events: List[Dict[str, Any]], policy_version: str) -> Dict[str, Any]:
        return {'inputs': [{'event_id': 'interaction_positive', 'weight': 70}, {'event_id': 'content_quality_score', 'weight': 30}], 'computation': {'previous_score': 400, 'delta': 50, 'new_score': 450, 'reason': 'Positive community interactions'}}

class FlagResolver(BaseResolver):
    """Resolves AEGIS flag explanations."""

    def resolve(self, entity_id: str, ledger_events: List[Dict[str, Any]], policy_version: str) -> Dict[str, Any]:
        return {'inputs': [{'event_id': 'content_analysis', 'weight': 100}], 'computation': {'flag_type': 'ADVISORY', 'confidence': 85, 'matched_patterns': ['safety_keywords'], 'human_review_required': False}}
