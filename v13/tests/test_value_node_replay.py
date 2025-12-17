"""
test_value_node_replay.py - Validation of ValueNodeReplayEngine

Verifies:
1. Graph reconstruction from events.
2. User and content node state tracking.
3. Interaction edge creation.
4. Deterministic snapshotting.
"""
from fractions import Fraction
import pytest
from v13.policy.value_node_replay import ValueNodeReplayEngine
from v13.policy.value_node_explainability import ValueNodeExplainabilityHelper
from v13.policy.humor_policy import HumorSignalPolicy

@pytest.fixture
def replay_engine():
    humor = HumorSignalPolicy()
    helper = ValueNodeExplainabilityHelper(humor)
    return ValueNodeReplayEngine(helper)

@pytest.fixture
def sample_events():
    return [{'type': 'ContentCreated', 'content_id': 'c1', 'user_id': 'u1', 'timestamp': 1000}, {'type': 'InteractionCreated', 'user_id': 'u2', 'content_id': 'c1', 'interaction_type': 'like', 'weight': 1, 'timestamp': 1050}, {'type': 'InteractionCreated', 'user_id': 'u3', 'content_id': 'c1', 'interaction_type': 'share', 'weight': 2, 'timestamp': 1060}, {'type': 'RewardAllocated', 'user_id': 'u1', 'amount_atr': 10, 'timestamp': 1100}]

def test_graph_reconstruction(replay_engine, sample_events):
    replay_engine.replay_events(sample_events)
    snapshot = replay_engine.get_state_snapshot()
    assert 'u1' in snapshot['users']
    assert 'u2' in snapshot['users']
    assert 'u3' in snapshot['users']
    assert 'c1' in snapshot['contents']
    assert snapshot['contents']['c1']['creator_id'] == 'u1'
    assert snapshot['interaction_count'] == 2

def test_state_accumulation(replay_engine):
    events1 = [{'type': 'RewardAllocated', 'user_id': 'u1', 'amount_atr': 10}]
    events2 = [{'type': 'RewardAllocated', 'user_id': 'u1', 'amount_atr': 5}]
    replay_engine.replay_events(events1)
    assert replay_engine.graph.users['u1'].total_rewards_atr == 10
    replay_engine.replay_events(events2)
    assert replay_engine.graph.users['u1'].total_rewards_atr == 15

def test_explain_ranking_from_replay(replay_engine, sample_events):
    replay_engine.replay_events(sample_events)
    explanation = replay_engine.explain_content_ranking('c1', sample_events)
    assert explanation is not None
    assert explanation.content_id == 'c1'
    vol_signal = next((s for s in explanation.signals if s['name'] == 'Interaction Volume'))
    assert vol_signal['score'] == Fraction(1, 5)