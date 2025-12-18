import pytest
from typing import List, Dict, Any
from v13.services.sessions.session_manager import SessionManager, SessionToken
from v13.services.sessions.explain_helper import build_session_proof

class FakeLedger:
    """Fake ledger implementation for testing."""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event to the fake ledger."""
        event = {'event_type': event_type, 'data': data}
        self.events.append(event)

def test_session_explainability_pre_device_binding_era():
    """Test session explainability in pre-device-binding era."""
    action_event = {'event_id': 'action_123', 'event_type': 'MESSAGE_SENT', 'block_number': 500, 'creator_id': 'wallet_123', 'data': {'wallet_id': 'wallet_123', 'content': 'Hello world'}}
    session_events = [{'event_type': 'SESSION_STARTED', 'data': {'session_id': 'session_abc', 'wallet_id': 'wallet_123', 'device_id': None, 'issued_at_block': 450, 'ttl_blocks': 1000, 'scope': ['basic']}}]
    proof = build_session_proof(action_event, session_events, era_cutoff_block=1000)
    assert proof['wallet_id'] == 'wallet_123'
    assert proof['device_id'] is None
    assert proof['session_id'] == 'session_abc'
    assert proof['authorized_at_block'] == 450
    assert proof['active'] == True
    assert proof['era'] == 'pre-device-binding'
    assert proof['action_event_id'] == 'action_123'
    assert proof['action_block'] == 500

def test_session_explainability_device_bound_era():
    """Test session explainability in device-bound era."""
    action_event = {'event_id': 'action_456', 'event_type': 'MESSAGE_SENT', 'block_number': 1500, 'creator_id': 'wallet_123', 'data': {'wallet_id': 'wallet_123', 'device_id': 'device_789', 'content': 'Hello world'}}
    session_events = [{'event_type': 'SESSION_STARTED', 'data': {'session_id': 'session_def', 'wallet_id': 'wallet_123', 'device_id': 'device_789', 'issued_at_block': 1450, 'ttl_blocks': 1000, 'scope': ['basic']}}]
    proof = build_session_proof(action_event, session_events, era_cutoff_block=1000)
    assert proof['wallet_id'] == 'wallet_123'
    assert proof['device_id'] == 'device_789'
    assert proof['session_id'] == 'session_def'
    assert proof['authorized_at_block'] == 1450
    assert proof['active'] == True
    assert proof['era'] == 'device-bound'
    assert proof['action_event_id'] == 'action_456'
    assert proof['action_block'] == 1500

def test_session_explainability_with_rotation():
    """Test session explainability with session rotation events."""
    action_event = {'event_id': 'action_789', 'event_type': 'REFERRAL_USED', 'block_number': 2000, 'creator_id': 'wallet_123', 'data': {'wallet_id': 'wallet_123', 'device_id': 'device_789', 'referral_code': 'REF123'}}
    session_events = [{'event_type': 'SESSION_STARTED', 'data': {'session_id': 'session_old', 'wallet_id': 'wallet_123', 'device_id': 'device_789', 'issued_at_block': 1500, 'ttl_blocks': 1000, 'scope': ['basic']}}, {'event_type': 'SESSION_ROTATED', 'data': {'old_session_id': 'session_old', 'new_session_id': 'session_new', 'block': 1800, 'wallet_id': 'wallet_123', 'device_id': 'device_789', 'scope': ['basic'], 'ttl_blocks': 1000}}]
    proof = build_session_proof(action_event, session_events, era_cutoff_block=1000)
    assert proof['wallet_id'] == 'wallet_123'
    assert proof['device_id'] == 'device_789'
    assert proof['session_id'] == 'session_new'
    assert proof['authorized_at_block'] == 1800
    assert proof['era'] == 'device-bound'
    assert proof['action_event_id'] == 'action_789'
    assert proof['action_block'] == 2000

def test_session_explainability_no_session():
    """Test session explainability when no session exists."""
    action_event = {'event_id': 'action_none', 'event_type': 'PROFILE_UPDATE', 'block_number': 3000, 'creator_id': 'wallet_123', 'data': {'wallet_id': 'wallet_123', 'device_id': 'device_789', 'bio': 'Updated bio'}}
    session_events = []
    proof = build_session_proof(action_event, session_events, era_cutoff_block=1000)
    assert proof['wallet_id'] == 'wallet_123'
    assert proof['device_id'] == 'device_789'
    assert proof['session_id'] is None
    assert proof['authorized_at_block'] is None
    assert proof['active'] == False
    assert proof['era'] == 'device-bound'
    assert proof['action_event_id'] == 'action_none'
    assert proof['action_block'] == 3000

def test_session_explainability_canonical_json():
    """Test that canonical JSON is properly generated."""
    action_event = {'event_id': 'action_json', 'event_type': 'MESSAGE_SENT', 'block_number': 1200, 'creator_id': 'wallet_123', 'data': {'wallet_id': 'wallet_123', 'device_id': 'device_789', 'content': 'Test message'}}
    session_events = [{'event_type': 'SESSION_STARTED', 'data': {'session_id': 'session_json', 'wallet_id': 'wallet_123', 'device_id': 'device_789', 'issued_at_block': 1150, 'ttl_blocks': 1000, 'scope': ['basic']}}]
    proof = build_session_proof(action_event, session_events, era_cutoff_block=1000)
    assert 'canonical_json' in proof
    canonical_json = proof['canonical_json']
    assert isinstance(canonical_json, str)
    assert 'wallet_id' in canonical_json
    assert 'device_id' in canonical_json
    assert 'session_id' in canonical_json
    assert 'authorized_at_block' in canonical_json
    assert 'active' in canonical_json
    assert 'era' in canonical_json
if __name__ == '__main__':
    test_session_explainability_pre_device_binding_era()
    test_session_explainability_device_bound_era()
    test_session_explainability_with_rotation()
    test_session_explainability_no_session()
    test_session_explainability_canonical_json()
    print('All explainability tests passed!')
