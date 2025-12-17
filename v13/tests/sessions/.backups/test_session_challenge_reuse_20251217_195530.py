import pytest
from typing import List, Dict, Any
from v13.services.sessions.session_manager import SessionManager
from v13.services.sessions.session_challenge import compute_challenge, post_session_challenge, post_session_establish

class FakeLedger:
    """Fake ledger implementation for testing."""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event to the fake ledger."""
        event = {'event_type': event_type, 'data': data}
        self.events.append(event)

def test_session_challenge_computation():
    """Test deterministic challenge computation."""
    wallet_id = 'wallet_123'
    device_id = 'device_456'
    block = 100
    nonce = 'abcdef123456'
    challenge = compute_challenge(wallet_id, device_id, block, nonce)
    challenge2 = compute_challenge(wallet_id, device_id, block, nonce)
    assert challenge == challenge2
    challenge3 = compute_challenge('different_wallet', device_id, block, nonce)
    assert challenge != challenge3
    challenge4 = compute_challenge(wallet_id, 'different_device', block, nonce)
    assert challenge != challenge4
    challenge5 = compute_challenge(wallet_id, device_id, 101, nonce)
    assert challenge != challenge5
    challenge6 = compute_challenge(wallet_id, device_id, block, 'different_nonce')
    assert challenge != challenge6

def test_session_challenge_api():
    """Test session challenge API helpers."""
    wallet_id = 'wallet_123'
    device_id = 'device_456'
    current_block = 100
    challenge, nonce, expiry_block = post_session_challenge(wallet_id, device_id, current_block)
    assert isinstance(challenge, str)
    assert isinstance(nonce, str)
    assert isinstance(expiry_block, int)
    assert len(challenge) == 64
    assert len(nonce) == 16
    assert expiry_block == current_block + 100

def test_session_establish_success():
    """Test successful session establishment."""
    ledger = FakeLedger()
    session_manager = SessionManager(ledger)
    wallet_id = 'wallet_123'
    device_id = 'device_456'
    current_block = 100
    challenge, nonce, _ = post_session_challenge(wallet_id, device_id, current_block)
    result = post_session_establish(wallet_id, device_id, challenge, current_block, session_manager)
    assert result['success'] == True
    assert result['session_token'] is not None
    assert result['session_token']['wallet_id'] == wallet_id
    assert result['session_token']['device_id'] == device_id
    assert 'session_id' in result['session_token']
    assert len(ledger.events) == 1
    event = ledger.events[0]
    assert event['event_type'] == 'SESSION_STARTED'

def test_session_establish_failure():
    """Test failed session establishment with wrong challenge."""
    ledger = FakeLedger()
    session_manager = SessionManager(ledger)
    wallet_id = 'wallet_123'
    device_id = 'device_456'
    current_block = 100
    wrong_challenge = 'wrong_challenge_response'
    result = post_session_establish(wallet_id, device_id, wrong_challenge, current_block, session_manager)
    assert result['success'] == False
    assert result['session_token'] is None
    assert 'error' in result
    assert result['error'] == 'Challenge response mismatch'
    assert len(ledger.events) == 0
if __name__ == '__main__':
    test_session_challenge_computation()
    test_session_challenge_api()
    test_session_establish_success()
    test_session_establish_failure()
    print('All challenge tests passed!')