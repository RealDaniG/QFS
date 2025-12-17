"""
engine.py - Core Explanation Generation Engine
"""
import hashlib
import json
from typing import Dict, Any, List, Optional

class ExplainerEngine:
    """
    Generates deterministic, ledger-backed explanations for QFS decisions.
    """

    def __init__(self, policy_version: str='v13.8'):
        self.policy_version = policy_version
        self._resolvers = {}
        self._register_default_resolvers()

    def _register_default_resolvers(self):
        """Register type-specific resolvers."""
        from v13.services.explainer.resolvers import RewardResolver, CoherenceResolver, FlagResolver
        self._resolvers['reward'] = RewardResolver()
        self._resolvers['coherence'] = CoherenceResolver()
        self._resolvers['flag'] = FlagResolver()

    def explain(self, entity_type: str, entity_id: str, ledger_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate an explanation for a specific entity.

        Args:
            entity_type: Type of entity to explain
            entity_id: ID of the entity
            ledger_events: Relevant ledger events (pre-fetched)

        Returns:
            Explanation object
        """
        resolver = self._resolvers.get(entity_type)
        if not resolver:
            raise ValueError(f'No resolver for type: {entity_type}')
        explanation_data = resolver.resolve(entity_id, ledger_events, self.policy_version)
        proof_input = json.dumps({'target_type': entity_type, 'target_id': entity_id, 'inputs': explanation_data.get('inputs', []), 'computation': explanation_data.get('computation', {}), 'policy_version': self.policy_version}, sort_keys=True)
        proof_hash = hashlib.sha256(proof_input.encode()).hexdigest()
        explanation = {'id': f'explain_{entity_id}', 'target_type': entity_type.upper(), 'target_id': entity_id, 'inputs': explanation_data.get('inputs', []), 'policy_version': self.policy_version, 'computation': explanation_data.get('computation', {}), 'proof_hash': proof_hash, 'generated_at': '2025-01-01T00:00:00Z'}
        return explanation