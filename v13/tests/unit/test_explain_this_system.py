"""
test_explain_this_system.py - Unit tests for Explain-This System
"""
import pytest
import hashlib
import json
from v13.services.explainer.engine import ExplainerEngine

def test_reward_explanation():
    engine = ExplainerEngine(policy_version='v13.8')
    ledger_events = [{'id': 'reward_123', 'type': 'REWARD', 'amount': 100, 'user_id': '0xUser'}]
    explanation = engine.explain('reward', 'reward_123', ledger_events)
    assert explanation['target_type'] == 'REWARD'
    assert explanation['target_id'] == 'reward_123'
    assert explanation['policy_version'] == 'v13.8'
    assert 'proof_hash' in explanation
    assert len(explanation['inputs']) > 0
    assert 'computation' in explanation

def test_coherence_explanation():
    engine = ExplainerEngine()
    explanation = engine.explain('coherence', 'coherence_456', [])
    assert explanation['target_type'] == 'COHERENCE'
    assert 'delta' in explanation['computation']
    assert 'new_score' in explanation['computation']

def test_flag_explanation():
    engine = ExplainerEngine()
    explanation = engine.explain('flag', 'flag_789', [])
    assert explanation['target_type'] == 'FLAG'
    assert 'flag_type' in explanation['computation']
    assert 'confidence' in explanation['computation']

def test_proof_hash_determinism():
    """Verify that proof hash is deterministic."""
    engine = ExplainerEngine(policy_version='v13.8')
    ledger_events = [{'id': 'e1', 'type': 'REWARD', 'amount': 50}]
    exp1 = engine.explain('reward', 'e1', ledger_events)
    exp2 = engine.explain('reward', 'e1', ledger_events)
    assert exp1['proof_hash'] == exp2['proof_hash']

def test_unknown_entity_type():
    engine = ExplainerEngine()
    with pytest.raises(ValueError, match='No resolver'):
        engine.explain('unknown_type', 'id', [])

def test_explanation_structure():
    """Verify all required fields are present."""
    engine = ExplainerEngine()
    explanation = engine.explain('reward', 'r1', [{'id': 'r1', 'type': 'REWARD', 'amount': 100}])
    required_fields = ['id', 'target_type', 'target_id', 'inputs', 'policy_version', 'computation', 'proof_hash', 'generated_at']
    for field in sorted(required_fields):
        assert field in explanation, f'Missing field: {field}'
