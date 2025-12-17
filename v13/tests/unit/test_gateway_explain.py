import pytest
from unittest.mock import MagicMock
from v13.atlas_api.gateway import AtlasAPIGateway
from v13.core.CoherenceLedger import LedgerEntry

def test_get_reward_explanation_success():
    gateway = AtlasAPIGateway()
    mock_entry = MagicMock(spec=LedgerEntry)
    mock_entry.entry_id = 'tx123'
    mock_entry.entry_hash = 'hash123'
    mock_entry.previous_hash = 'hash122'
    mock_entry.pqc_cid = 'cid123'
    mock_entry.timestamp = 1000
    mock_entry.entry_type = 'reward_allocation'
    mock_entry.data = {'rewards': {'amount': '10.0', 'reason': 'referral_bonus', 'source_events': ['evt1']}, 'hsmf_metrics': {}, 'guards': {'economics': {'passed': True}}}
    gateway.coherence_ledger.ledger_entries = [mock_entry]
    result = gateway.get_reward_explanation('tx123')
    assert result['success'] is True
    assert result['tx_id'] == 'tx123'
    assert result['explanation']['summary'] == 'You earned 10.0 for referral_bonus.'
    assert result['explanation']['zero_sim_proof']['input_state_hash'] == 'hash122'

def test_get_reward_explanation_not_found():
    gateway = AtlasAPIGateway()
    gateway.coherence_ledger.ledger_entries = []
    result = gateway.get_reward_explanation('tx999')
    assert result['success'] is False
    assert result['error_code'] == 'NOT_FOUND'

def test_get_reward_explanation_blocked():
    gateway = AtlasAPIGateway()
    mock_entry = MagicMock(spec=LedgerEntry)
    mock_entry.entry_id = 'tx_blocked'
    mock_entry.entry_hash = 'hash_blk'
    mock_entry.pqc_cid = 'cid_blk'
    mock_entry.timestamp = 2000
    mock_entry.data = {'rewards': {}, 'guards': {'economics': {'passed': False, 'explanation': 'Cap exceeded'}}}
    gateway.coherence_ledger.ledger_entries = [mock_entry]
    result = gateway.get_reward_explanation('tx_blocked')
    assert result['success'] is True
    assert result['status'] == 'BLOCKED'
    assert 'Cap exceeded' in result['reason']