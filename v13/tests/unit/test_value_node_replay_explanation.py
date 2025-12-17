"""
test_value_node_replay_explanation.py

Unit tests for the explanation generation logic within the replay context.
Focuses on correctness of data extraction and formatting.
"""
import pytest
from typing import Dict, Any
from v13.policy.value_node_replay import ValueNodeReplayEngine
from v13.policy.value_node_explainability import ValueNodeExplainabilityHelper
from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicy

@pytest.fixture
def engine():
    policy = HumorSignalPolicy(HumorPolicy(enabled=True, mode='rewarding', dimension_weights={}, max_bonus_ratio=0.25, per_user_daily_cap_atr=1.0))
    helper = ValueNodeExplainabilityHelper(policy)
    return ValueNodeReplayEngine(helper)

def test_explain_full_fidelity_event(engine):
    """
    Test explanation generation when event has full log details.
    """
    event = {'type': 'RewardAllocated', 'event_id': 'full_fid_1', 'user_id': 'u_test', 'amount_atr': 100, 'epoch': 5, 'timestamp': 12345, 'log_details': {'base_reward': {'ATR': '80.0 ATR'}, 'bonuses': [{'label': 'Loyalty', 'value': '+20.0 ATR', 'reason': 'Old account'}], 'caps': [], 'guards': [{'name': 'MaxReward', 'result': 'pass'}]}}
    explanation = engine.explain_specific_reward('full_fid_1', [event])
    assert explanation is not None
    assert explanation.user_id == 'u_test'
    assert explanation.epoch == 5
    assert len(explanation.bonuses) == 1
    assert explanation.bonuses[0]['label'] == 'Loyalty'
    assert 'REWARD_BONUSES_APPLIED' in explanation.reason_codes

def test_explain_low_fidelity_event_fallback(engine):
    """
    Test explanation generation when event lacks refined log details.
    Should fallback to available data.
    """
    event = {'type': 'RewardAllocated', 'event_id': 'low_fid_1', 'user_id': 'u_fallback', 'amount_atr': 50, 'epoch': 2, 'timestamp': 67890}
    explanation = engine.explain_specific_reward('low_fid_1', [event])
    assert explanation is not None
    assert explanation.user_id == 'u_fallback'
    assert explanation.base_reward == {'ATR': '50 ATR'}
    assert explanation.bonuses == []
    assert explanation.caps == []

def test_replay_integration_with_explanation(engine):
    """
    Test that replaying events correctly enables state lookup if needed (future proofing),
    though currently explanation is mostly stateless from the event context.
    """
    events = [{'type': 'ContentCreated', 'content_id': 'c1', 'user_id': 'u1'}, {'type': 'RewardAllocated', 'event_id': 'r1', 'user_id': 'u1', 'amount_atr': 10}]
    engine.replay_events(events)
    assert 'u1' in engine.graph.users
    expl = engine.explain_specific_reward('r1', events)
    assert expl is not None
    assert expl.user_id == 'u1'