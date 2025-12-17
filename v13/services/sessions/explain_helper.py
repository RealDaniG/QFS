import json
from typing import Dict, List, Any, Optional
from .session_manager import SessionToken


def build_session_proof(action_event: Dict[str, Any], session_events: List[Dict[str, Any]], 
                       era_cutoff_block: int = 1000) -> Dict[str, Any]:
    """Build a session proof for Explain-This system.
    
    Args:
        action_event: The action event being explained
        session_events: All SESSION_* events related to the wallet/device
        era_cutoff_block: Block number that determines pre-device-binding vs device-bound era
        
    Returns:
        Dict containing proof information for Explain-This
    """
    # Extract wallet_id and device_id from action event
    wallet_id = action_event.get("data", {}).get("wallet_id") or action_event.get("creator_id")
    device_id = action_event.get("data", {}).get("device_id")
    
    # Find the most relevant session event
    relevant_session_event = None
    session_token = None
    
    # Look for SESSION_STARTED or SESSION_ROTATED events
    for event in reversed(session_events):  # Check most recent first
        event_type = event.get("event_type")
        event_data = event.get("data", {})
        
        # Match by wallet_id and device_id if available
        event_wallet_id = event_data.get("wallet_id")
        event_device_id = event_data.get("device_id")
        
        # For SESSION_ROTATED events, also check if this is the new session we're looking for
        if event_type == "SESSION_ROTATED":
            # Check if the new session ID matches what we might be looking for
            # Or if the wallet and device match
            if event_wallet_id == wallet_id:
                if device_id is None or event_device_id == device_id:
                    relevant_session_event = event
                    break
        elif event_type == "SESSION_STARTED":
            if event_wallet_id == wallet_id:
                if device_id is None or event_device_id == device_id:
                    relevant_session_event = event
                    break
    
    # If we found a session event, extract session information
    session_id = None
    authorized_at_block = None
    active = False
    
    if relevant_session_event:
        event_type = relevant_session_event.get("event_type")
        event_data = relevant_session_event.get("data", {})
        
        if event_type == "SESSION_STARTED":
            session_id = event_data.get("session_id")
            authorized_at_block = event_data.get("issued_at_block")
            # Create temporary token to check if active
            temp_token = SessionToken(
                session_id=event_data.get("session_id"),
                wallet_id=event_data.get("wallet_id"),
                device_id=event_data.get("device_id"),
                issued_at_block=event_data.get("issued_at_block"),
                ttl_blocks=event_data.get("ttl_blocks"),
                scope=event_data.get("scope")
            )
            # We need the current block to determine if active
            current_block = action_event.get("block_number", 0)
            active = (current_block >= temp_token.issued_at_block and 
                     current_block < temp_token.issued_at_block + temp_token.ttl_blocks)
            
        elif event_type == "SESSION_ROTATED":
            session_id = event_data.get("new_session_id")
            authorized_at_block = event_data.get("block")
            # For simplicity, assume active (in a real implementation we'd check)
            active = True
            
        elif event_type == "SESSION_REVOKED":
            session_id = event_data.get("session_id")
            authorized_at_block = event_data.get("block")
            active = False
    
    # Determine era based on cutoff block
    era = "pre-device-binding" if (authorized_at_block and authorized_at_block < era_cutoff_block) else "device-bound"
    
    # Build the proof
    proof = {
        "wallet_id": wallet_id,
        "device_id": device_id,
        "session_id": session_id,
        "authorized_at_block": authorized_at_block,
        "active": active,
        "era": era,
        "action_event_id": action_event.get("event_id"),
        "action_block": action_event.get("block_number"),
        "explanation": f"Action authorized through session {session_id} created at block {authorized_at_block}",
        "canonical_json": json.dumps({
            "wallet_id": wallet_id,
            "device_id": device_id,
            "session_id": session_id,
            "authorized_at_block": authorized_at_block,
            "active": active,
            "era": era
        }, sort_keys=True, separators=(',', ':'))
    }
    
    return proof