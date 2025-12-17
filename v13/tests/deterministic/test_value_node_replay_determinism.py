"""
test_value_node_replay_determinism.py

Tests the deterministic behavior of the ValueNodeReplayEngine.
Ensures that replaying the same sequence of events always results in:
1. The exact same state graph.
2. The exact same explanation hashes.
"""
import pytest
import copy
from typing import List, Dict, Any
from v13.policy.value_node_replay import ValueNodeReplayEngine
from v13.policy.value_node_explainability import ValueNodeExplainabilityHelper
from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicy

@pytest.fixture
def mock_humor_policy():
    return HumorSignalPolicy(policy=HumorPolicy(enabled=True, mode='rewarding', dimension_weights={}, max_bonus_ratio=0.25, per_user_daily_cap_atr=1))

@pytest.fixture
def replay_engine(mock_humor_policy):
    helper = ValueNodeExplainabilityHelper(mock_humor_policy)
    return ValueNodeReplayEngine(helper)

@pytest.fixture
def sample_events_sequence() -> List[Dict[str, Any]]:
    return [{'type': 'ContentCreated', 'content_id': 'c1', 'user_id': 'u1', 'timestamp': 1000}, {'type': 'InteractionCreated', 'user_id': 'u2', 'content_id': 'c1', 'interaction_type': 'like', 'timestamp': 1010}, {'type': 'RewardAllocated', 'event_id': 'r1', 'user_id': 'u1', 'amount_atr': 10, 'timestamp': 1020, 'log_details': {'base_reward': {'ATR': '5.0 ATR'}, 'bonuses': [{'label': 'Creator Bonus', 'value': '+5.0 ATR', 'reason': 'Good content'}], 'caps': [], 'guards': [{'name': 'EconGuard', 'result': 'pass'}]}}]

def test_replay_state_determinism(mock_humor_policy, sample_events_sequence):
    """
    Verify that multiple replays of the same event sequence produce identical state snapshots.
    """
    results = []
    for _ in range(5):
        helper = ValueNodeExplainabilityHelper(mock_humor_policy)
        engine = ValueNodeReplayEngine(helper)
        engine.replay_events(copy.deepcopy(sample_events_sequence))
        results.append(engine.get_state_snapshot())
    first_result = results[0]
    for i, res in enumerate(results[1:]):
        assert res == first_result, f'Run {i + 1} drifted from Run 0'

def test_explanation_determinism(replay_engine, sample_events_sequence):
    """
    Verify that generating an explanation for the same event always produces the same hash.
    """
    reward_id = 'r1'
    replay_engine.replay_events(copy.deepcopy(sample_events_sequence))
    explanation1 = replay_engine.explain_specific_reward(reward_id, sample_events_sequence)
    assert explanation1 is not None
    hash1 = explanation1.explanation_hash
    helper2 = ValueNodeExplainabilityHelper(replay_engine.explainability_helper.humor_policy)
    engine2 = ValueNodeReplayEngine(helper2)
    engine2.replay_events(copy.deepcopy(sample_events_sequence))
    explanation2 = engine2.explain_specific_reward(reward_id, sample_events_sequence)
    assert explanation2 is not None
    hash2 = explanation2.explanation_hash
    assert hash1 == hash2

def test_missing_event_explanation(replay_engine, sample_events_sequence):
    """
    Verify behavior when trying to explain a non-existent event.
    """
    replay_engine.replay_events(sample_events_sequence)
    explanation = replay_engine.explain_specific_reward('non_existent_id', sample_events_sequence)
    assert explanation is None