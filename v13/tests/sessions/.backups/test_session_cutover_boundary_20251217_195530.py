import pytest
from typing import List, Dict, Any
from v13.services.sessions.session_manager import SessionManager, SessionToken
from v13.services.sessions.replay_helper import replay_sessions, get_active_sessions_at_block

class FakeLedger:
    """Fake ledger implementation for testing."""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event to the fake ledger."""
        event = {'event_type': event_type, 'data': data}
        self.events.append(event)

def test_session_replay_with_multiple_operations():
    """Test session replay with multiple operations including rotation and revocation."""
    ledger = FakeLedger()
    session_manager = SessionManager(ledger)
    wallet_id = 'wallet_123'
    device_id = 'device_456'
    scope = ['read', 'write']
    token1 = session_manager.create_session(wallet_id=wallet_id, device_id=device_id, scope=scope, current_block=100, ttl_blocks=1000)
    token2 = session_manager.rotate_session(token1, 150)
    token3 = session_manager.rotate_session(token2, 200)
    session_manager.revoke_session(token3, 'timeout', 250)
    assert len(ledger.events) == 4
    session_states = replay_sessions(ledger.events)
    assert len(session_states) == 0
    session_states_1 = replay_sessions(ledger.events[:1])
    assert len(session_states_1) == 1
    assert token1.session_id in session_states_1
    session_states_2 = replay_sessions(ledger.events[:2])
    assert len(session_states_2) == 1
    assert token1.session_id not in session_states_2
    assert token2.session_id in session_states_2
    session_states_3 = replay_sessions(ledger.events[:3])
    assert len(session_states_3) == 1
    assert token2.session_id not in session_states_3
    assert token3.session_id in session_states_3

def test_active_sessions_at_block():
    """Test filtering sessions by block activity."""
    token1 = SessionToken(session_id='session_1', wallet_id='wallet_123', device_id='device_456', issued_at_block=100, ttl_blocks=50, scope=['read'])
    token2 = SessionToken(session_id='session_2', wallet_id='wallet_123', device_id='device_789', issued_at_block=120, ttl_blocks=100, scope=['read', 'write'])
    token3 = SessionToken(session_id='session_3', wallet_id='wallet_456', device_id='device_123', issued_at_block=200, ttl_blocks=50, scope=['admin'])
    sessions = {'session_1': token1, 'session_2': token2, 'session_3': token3}
    active_sessions = get_active_sessions_at_block(sessions, 99)
    assert len(active_sessions) == 0
    active_sessions = get_active_sessions_at_block(sessions, 100)
    assert len(active_sessions) == 1
    assert 'session_1' in active_sessions
    active_sessions = get_active_sessions_at_block(sessions, 120)
    assert len(active_sessions) == 2
    assert 'session_1' in active_sessions
    assert 'session_2' in active_sessions
    active_sessions = get_active_sessions_at_block(sessions, 150)
    assert len(active_sessions) == 1
    assert 'session_1' not in active_sessions
    assert 'session_2' in active_sessions
    active_sessions = get_active_sessions_at_block(sessions, 200)
    assert len(active_sessions) == 2
    assert 'session_2' in active_sessions
    assert 'session_3' in active_sessions
    active_sessions = get_active_sessions_at_block(sessions, 220)
    assert len(active_sessions) == 1
    assert 'session_2' not in active_sessions
    assert 'session_3' in active_sessions
    active_sessions = get_active_sessions_at_block(sessions, 250)
    assert len(active_sessions) == 0
if __name__ == '__main__':
    test_session_replay_with_multiple_operations()
    test_active_sessions_at_block()
    print('All cutover boundary tests passed!')