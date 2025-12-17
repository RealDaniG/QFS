"""
test_artistic_explainability.py - Verification of AES Metadata in Explanations

Tests:
1. Explain helper includes Artistic policy version/hash.
2. Aggregation works correctly with/without Humor policy.
"""
import pytest
from v13.policy.value_node_explainability import ValueNodeExplainabilityHelper
from v13.policy.artistic_policy import ArtisticSignalPolicy
from v13.policy.humor_policy import HumorSignalPolicy

def test_metadata_inclusion():
    """Verify Artistic metadata appears in explanation."""
    artistic = ArtisticSignalPolicy()
    humor = HumorSignalPolicy()
    helper = ValueNodeExplainabilityHelper(humor_policy=humor, artistic_policy=artistic)
    explanation = helper.explain_value_node_reward('w1', 'u1', 'evt1', 1, {}, [], [], [], 1000)
    assert 'Artistic:' in explanation.policy_version
    assert 'Humor:' in explanation.policy_version
    assert 'Artistic:' in explanation.policy_hash
    assert 'v13.8.0' in explanation.policy_version

def test_explanation_hash_determinism():
    """Hash should change if Artistic policy hash changes."""
    artistic = ArtisticSignalPolicy()
    humor = HumorSignalPolicy()
    helper = ValueNodeExplainabilityHelper(humor_policy=humor, artistic_policy=artistic)
    exp1 = helper.explain_value_node_reward('w1', 'u1', 'evt1', 1, {}, [], [], [], 1000)
    artistic.policy.dimension_weights['composition'] = 0.99
    artistic.policy.__post_init__()
    exp2 = helper.explain_value_node_reward('w1', 'u1', 'evt1', 1, {}, [], [], [], 1000)
    assert exp1.explanation_hash != exp2.explanation_hash
    assert exp1.policy_hash != exp2.policy_hash