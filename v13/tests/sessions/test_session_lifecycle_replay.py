import pytest
from typing import List, Dict, Any
from v13.services.sessions.session_manager import SessionManager, SessionToken
from v13.services.sessions.replay_helper import replay_sessions


class FakeLedger:
    """Fake ledger implementation for testing."""
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        
    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event to the fake ledger."""
        event = {
            "event_type": event_type,
            "data": data
        }
        self.events.append(event)


def test_session_lifecycle_replay():
    """Test session lifecycle with replay functionality."""
    # Create fake ledger
    ledger = FakeLedger()
    
    # Create session manager
    session_manager = SessionManager(ledger)
    
    # Test data
    wallet_id = "wallet_123"
    device_id = "device_456"
    scope = ["read", "write"]
    current_block = 100
    ttl_blocks = 1000
    
    # Create session
    token = session_manager.create_session(
        wallet_id=wallet_id,
        device_id=device_id,
        scope=scope,
        current_block=current_block,
        ttl_blocks=ttl_blocks
    )
    
    # Verify session token
    assert token.wallet_id == wallet_id
    assert token.device_id == device_id
    assert token.scope == scope
    assert token.issued_at_block == current_block
    assert token.ttl_blocks == ttl_blocks
    
    # Verify event was emitted
    assert len(ledger.events) == 1
    event = ledger.events[0]
    assert event["event_type"] == "SESSION_STARTED"
    assert event["data"]["session_id"] == token.session_id
    assert event["data"]["wallet_id"] == wallet_id
    assert event["data"]["device_id"] == device_id
    
    # Rotate session
    current_block = 150
    new_token = session_manager.rotate_session(token, current_block)
    
    # Verify new token
    assert new_token.wallet_id == wallet_id
    assert new_token.device_id == device_id
    assert new_token.session_id != token.session_id  # Should be different
    assert new_token.issued_at_block == current_block
    
    # Verify events were emitted
    assert len(ledger.events) == 2
    rotate_event = ledger.events[1]
    assert rotate_event["event_type"] == "SESSION_ROTATED"
    assert rotate_event["data"]["old_session_id"] == token.session_id
    assert rotate_event["data"]["new_session_id"] == new_token.session_id
    
    # Revoke session
    current_block = 200
    reason = "user_logout"
    session_manager.revoke_session(new_token, reason, current_block)
    
    # Verify revoke event
    assert len(ledger.events) == 3
    revoke_event = ledger.events[2]
    assert revoke_event["event_type"] == "SESSION_REVOKED"
    assert revoke_event["data"]["session_id"] == new_token.session_id
    assert revoke_event["data"]["reason"] == reason
    
    # Test replay functionality
    session_states = replay_sessions(ledger.events)
    
    # After revoke, session should not exist
    assert len(session_states) == 0
    assert new_token.session_id not in session_states


def test_session_active_check():
    """Test session active checking."""
    # Create fake ledger
    ledger = FakeLedger()
    
    # Create session manager
    session_manager = SessionManager(ledger)
    
    # Create session
    wallet_id = "wallet_123"
    device_id = "device_456"
    scope = ["read"]
    current_block = 100
    ttl_blocks = 100  # Session valid for 100 blocks
    
    token = session_manager.create_session(
        wallet_id=wallet_id,
        device_id=device_id,
        scope=scope,
        current_block=current_block,
        ttl_blocks=ttl_blocks
    )
    
    # Test active at issuance
    assert session_manager.is_session_active(token, current_block) == True
    
    # Test active within TTL
    assert session_manager.is_session_active(token, current_block + 50) == True
    
    # Test inactive after TTL
    assert session_manager.is_session_active(token, current_block + 100) == False
    assert session_manager.is_session_active(token, current_block + 150) == False
    
    # Test inactive before issuance (should not happen in practice but let's check)
    assert session_manager.is_session_active(token, current_block - 1) == False


if __name__ == "__main__":
    test_session_lifecycle_replay()
    test_session_active_check()
    print("All tests passed!")