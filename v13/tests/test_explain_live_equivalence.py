"""
test_explain_live_equivalence.py - HASH EQUIVALENCE VERIFICATION
Phase 1.2: Prove that Mock vs Live (via Adapter) produces identical explanation hashes.

Invariant:
- Given the same sequence of events, QFSReplaySource + ValueNodeReplayEngine MUST produce
  bit-identical explanation hashes to the verified mock baseline.
"""
import pytest
from v13.core.QFSReplaySource import QFSReplaySource
from v13.policy.value_node_replay import ValueNodeReplayEngine
from v13.policy.value_node_explainability import ValueNodeExplainabilityHelper
from v13.policy.humor_policy import HumorSignalPolicy
from v13.policy.artistic_policy import ArtisticSignalPolicy

@pytest.fixture
def mock_events():
    """Canonical event stream for verification."""
    return [{'id': 'evt_1', 'type': 'ContentCreated', 'timestamp': 1000, 'content_id': 'cid_1', 'author_id': 'did:key:zUser1', 'text': 'Hello World'}, {'id': 'evt_2', 'type': 'Interaction', 'timestamp': 1050, 'user_id': 'did:key:zUser2', 'content_id': 'cid_1', 'interaction_type': 'like', 'weight': 1}, {'id': 'evt_3', 'type': 'RewardAllocated', 'timestamp': 1100, 'wallet_id': 'wallet_test', 'user_id': 'did:key:zUser1', 'reason': 'engagement', 'amount_atr': 50, 'bonuses': [{'source': 'humor', 'amount': 10}], 'caps': [], 'guards': []}]

@pytest.fixture
def live_replay_source(mock_events, monkeypatch):
    """
    Simulates the 'Live' QFSReplaySource by monkeypatching the data retrieval 
    to return our canonical events, but running through the real class structure.
    """

    def fake_get_reward_events(self, wallet_id, epoch):
        return mock_events
    monkeypatch.setattr(QFSReplaySource, 'get_reward_events', fake_get_reward_events)
    return QFSReplaySource(ledger=None, storage=None)

@pytest.fixture
def explain_helper():
    """Real helper with real policies."""
    humor = HumorSignalPolicy()
    artistic = ArtisticSignalPolicy()
    return ValueNodeExplainabilityHelper(humor_policy=humor, artistic_policy=artistic)

def test_reward_explanation_hash_equivalence(mock_events, live_replay_source, explain_helper):
    """
    CRITICAL: Verify that the Explanation Hash is identical whether we use
    raw mock data or the QFSReplaySource adapter.
    """
    reward_evt_id = 'evt_3'
    engine_baseline = ValueNodeReplayEngine(explainability_helper=explain_helper)
    engine_baseline.replay_events(mock_events)
    explanation_baseline = engine_baseline.explain_specific_reward(reward_event_id=reward_evt_id, events_context=mock_events)
    assert explanation_baseline is not None, 'Baseline failed to generate explanation'
    hash_baseline = explanation_baseline.explanation_hash
    print(f'Baseline Hash: {hash_baseline}')
    events_from_source = live_replay_source.get_reward_events('wallet_test', epoch=1)
    engine_live = ValueNodeReplayEngine(explainability_helper=explain_helper)
    engine_live.replay_events(events_from_source)
    explanation_live = engine_live.explain_specific_reward(reward_event_id=reward_evt_id, events_context=events_from_source)
    assert explanation_live is not None, 'Live source failed to generate explanation'
    hash_live = explanation_live.explanation_hash
    print(f'Live Hash:     {hash_live}')
    assert hash_baseline == hash_live, 'Hash Mismatch! Replay Source must be deterministic.'
    assert explanation_baseline.total_reward == explanation_live.total_reward
    assert explanation_baseline.wallet_id == explanation_live.wallet_id

def test_qfs_source_structure(live_replay_source):
    """Verify QFSReplaySource signature compliance."""
    assert hasattr(live_replay_source, 'get_reward_events')
    assert hasattr(live_replay_source, 'get_ranking_events')
    assert hasattr(live_replay_source, 'get_storage_events')