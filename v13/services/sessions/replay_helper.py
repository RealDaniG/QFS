import json
from typing import Dict, List, Any, Optional
from .session_manager import SessionToken

def replay_sessions(events: List[Dict[str, Any]]) -> Dict[str, SessionToken]:
    """Reconstruct all session state from SESSION_* events deterministically.
    
    Args:
        events: List of ledger events, filtered to SESSION_* types
        
    Returns:
        Dict mapping session_id to current SessionToken
    """
    sessions = {}
    for i in range(len(events)):
        event = events[i]
        event_type = event.get('event_type')
        data = event.get('data', {})
        if event_type == 'SESSION_STARTED':
            token = SessionToken(session_id=data['session_id'], wallet_id=data['wallet_id'], device_id=data['device_id'], issued_at_block=data['issued_at_block'], ttl_blocks=data['ttl_blocks'], scope=data['scope'])
            sessions[token.session_id] = token
        elif event_type == 'SESSION_ROTATED':
            old_session_id = data['old_session_id']
            new_session_id = data['new_session_id']
            if old_session_id in sessions:
                old_token = sessions[old_session_id]
                new_token = SessionToken(session_id=new_session_id, wallet_id=data['wallet_id'], device_id=data['device_id'], issued_at_block=data['block'], ttl_blocks=data['ttl_blocks'], scope=data['scope'])
                del sessions[old_session_id]
                sessions[new_session_id] = new_token
        elif event_type == 'SESSION_REVOKED':
            session_id = data['session_id']
            if session_id in sessions:
                del sessions[session_id]
    return sessions

def get_active_sessions_at_block(sessions: Dict[str, SessionToken], block_number: int) -> Dict[str, SessionToken]:
    """Filter sessions to only those active at a specific block number.
    
    Args:
        sessions: Dict of session_id to SessionToken
        block_number: Block number to check activity at
        
    Returns:
        Dict of active sessions at the specified block
    """
    active_sessions = {}
    for session_id, token in sessions.items():
        if block_number >= token.issued_at_block and block_number < token.issued_at_block + token.ttl_blocks:
            active_sessions[session_id] = token
    return active_sessions
