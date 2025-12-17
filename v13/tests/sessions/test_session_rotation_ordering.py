import pytest
from typing import List, Dict, Any
from v13.services.sessions.session_manager import SessionManager, SessionToken


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


def test_session_rotation_creates_new_token():
    """Test that session rotation creates a new token with updated block."""
    # Create fake ledger
    ledger = FakeLedger()
    
    # Create session manager
    session_manager = SessionManager(ledger)
    
    # Create initial session
    wallet_id = "wallet_123"
    device_id = "device_456"
    scope = ["read", "write"]
    initial_block = 100
    ttl_blocks = 1000
    
    initial_token = session_manager.create_session(
        wallet_id=wallet_id,
        device_id=device_id,
        scope=scope,
        current_block=initial_block,
        ttl_blocks=ttl_blocks
    )
    
    # Rotate session at a later block
    rotation_block = 150
    rotated_token = session_manager.rotate_session(initial_token, rotation_block)
    
    # Verify new token properties
    assert isinstance(rotated_token, SessionToken)
    assert rotated_token.wallet_id == wallet_id
    assert rotated_token.device_id == device_id
    assert rotated_token.scope == scope
    assert rotated_token.issued_at_block == rotation_block  # Updated block
    assert rotated_token.ttl_blocks == ttl_blocks  # Same TTL
    assert rotated_token.session_id != initial_token.session_id  # New session ID
    
    # Verify the session IDs are deterministically generated
    # Create another token with same parameters to verify deterministic behavior
    another_rotated_token = session_manager.rotate_session(initial_token, rotation_block)
    assert another_rotated_token.session_id == rotated_token.session_id  # Should be same


def test_session_rotation_preserves_metadata():
    """Test that session rotation preserves wallet and device metadata."""
    # Create fake ledger
    ledger = FakeLedger()
    
    # Create session manager
    session_manager = SessionManager(ledger)
    
    # Test data with various metadata
    wallet_id = "wallet_with_long_identifier_123456789"
    device_id = "device_mobile_ios_14_abcdef123456"
    scope = ["read", "write", "delete", "admin"]
    initial_block = 1000
    ttl_blocks = 5000
    
    initial_token = session_manager.create_session(
        wallet_id=wallet_id,
        device_id=device_id,
        scope=scope,
        current_block=initial_block,
        ttl_blocks=ttl_blocks
    )
    
    # Rotate session
    rotation_block = 1050
    rotated_token = session_manager.rotate_session(initial_token, rotation_block)
    
    # Verify all metadata is preserved
    assert rotated_token.wallet_id == wallet_id
    assert rotated_token.device_id == device_id
    assert rotated_token.scope == scope
    assert rotated_token.ttl_blocks == ttl_blocks
    
    # But block number is updated
    assert rotated_token.issued_at_block == rotation_block
    assert rotated_token.issued_at_block != initial_token.issued_at_block


def test_session_rotation_emits_correct_event():
    """Test that session rotation emits the correct ledger event."""
    # Create fake ledger
    ledger = FakeLedger()
    
    # Create session manager
    session_manager = SessionManager(ledger)
    
    # Create initial session
    wallet_id = "wallet_123"
    device_id = "device_456"
    scope = ["basic"]
    initial_block = 100
    ttl_blocks = 1000
    
    initial_token = session_manager.create_session(
        wallet_id=wallet_id,
        device_id=device_id,
        scope=scope,
        current_block=initial_block,
        ttl_blocks=ttl_blocks
    )
    
    # Clear events to focus on rotation event
    ledger.events.clear()
    
    # Rotate session
    rotation_block = 150
    rotated_token = session_manager.rotate_session(initial_token, rotation_block)
    
    # Verify exactly one event was emitted
    assert len(ledger.events) == 1
    
    # Verify event content
    event = ledger.events[0]
    assert event["event_type"] == "SESSION_ROTATED"
    assert event["data"]["old_session_id"] == initial_token.session_id
    assert event["data"]["new_session_id"] == rotated_token.session_id
    assert event["data"]["block"] == rotation_block


def test_multiple_rotations_generate_unique_tokens():
    """Test that multiple rotations generate unique tokens."""
    # Create fake ledger
    ledger = FakeLedger()
    
    # Create session manager
    session_manager = SessionManager(ledger)
    
    # Create initial session
    wallet_id = "wallet_123"
    device_id = "device_456"
    scope = ["read"]
    initial_block = 100
    ttl_blocks = 1000
    
    initial_token = session_manager.create_session(
        wallet_id=wallet_id,
        device_id=device_id,
        scope=scope,
        current_block=initial_block,
        ttl_blocks=ttl_blocks
    )
    
    # Perform multiple rotations
    tokens = [initial_token]
    for i in range(5):
        rotation_block = initial_block + (i + 1) * 10
        new_token = session_manager.rotate_session(tokens[-1], rotation_block)
        tokens.append(new_token)
    
    # Verify all tokens have unique session IDs
    session_ids = [token.session_id for token in tokens]
    assert len(set(session_ids)) == len(session_ids)  # All unique
    
    # Verify block numbers are sequential
    block_numbers = [token.issued_at_block for token in tokens]
    expected_blocks = [100, 110, 120, 130, 140, 150]
    assert block_numbers == expected_blocks


if __name__ == "__main__":
    test_session_rotation_creates_new_token()
    test_session_rotation_preserves_metadata()
    test_session_rotation_emits_correct_event()
    test_multiple_rotations_generate_unique_tokens()
    print("All rotation ordering tests passed!")