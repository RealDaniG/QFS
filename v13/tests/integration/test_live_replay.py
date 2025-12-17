"""
test_live_replay.py - Integration test for LiveLedgerReplaySource

Verifies that the Explain-This engine can correctly hydrate from a persisted
ledger artifact and provide deterministic explanations.
"""
import pytest
import json
from typing import Dict, Any
from v13.core.QFSReplaySource import LiveLedgerReplaySource
from v13.core.StorageEngine import StorageEngine
from v13.libs.CertifiedMath import CertifiedMath
TEST_LEDGER_PATH = 'v13/tests/integration/fixtures/test_ledger.jsonl'

@pytest.fixture
def mock_ledger_artifact(tmp_path):
    """Create a temporary JSONL ledger artifact."""
    artifact_path = tmp_path / 'test_ledger.jsonl'
    entries = [{'entry_id': 'hash_1', 'timestamp': 1000, 'entry_type': 'token_state', 'data': {'token_bundle': {'id': 'bundle_1'}}, 'previous_hash': 'genesis', 'entry_hash': 'hash_1', 'pqc_cid': 'cid_1', 'quantum_metadata': {}}, {'entry_id': 'hash_2', 'timestamp': 1001, 'entry_type': 'reward_allocation', 'data': {'rewards': {'wallet_123': {'amount': '100.0'}}}, 'previous_hash': 'hash_1', 'entry_hash': 'hash_2', 'pqc_cid': 'cid_2', 'quantum_metadata': {}}]
    with open(artifact_path, 'w') as f:
        for entry in sorted(entries):
            f.write(json.dumps(entry) + '\n')
    return str(artifact_path)

def test_live_replay_hydration(mock_ledger_artifact):
    """Test that LiveLedgerReplaySource hydrates correctly from disk."""
    cm = CertifiedMath()
    storage = StorageEngine(cm)
    replay_source = LiveLedgerReplaySource(mock_ledger_artifact, storage)
    assert len(replay_source.ledger.ledger_entries) == 2
    assert replay_source.ledger.ledger_entries[0].entry_id == 'hash_1'
    assert replay_source.ledger.ledger_entries[1].entry_type == 'reward_allocation'

def test_get_reward_events(mock_ledger_artifact):
    """Test retrieval of reward events from hydrated source."""
    cm = CertifiedMath()
    storage = StorageEngine(cm)
    replay_source = LiveLedgerReplaySource(mock_ledger_artifact, storage)
    events = replay_source.get_reward_events('wallet_123', epoch=1)
    assert len(events) >= 1
    assert events[-1]['type'] == 'RewardAllocated'
    assert events[-1]['id'] == 'hash_2'

def test_missing_artifact():
    """Test error handling for missing artifact."""
    cm = CertifiedMath()
    storage = StorageEngine(cm)
    with pytest.raises(FileNotFoundError):
        LiveLedgerReplaySource('non_existent_file.jsonl', storage)