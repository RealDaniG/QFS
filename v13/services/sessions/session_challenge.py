import hashlib
import json
from typing import Tuple, Dict, Any
from .session_manager import sha256, compute_device_id

def compute_challenge(wallet_id: str, device_id: str, block: int, nonce: str) -> str:
    """Deterministically compute a challenge using SHA-256.
    
    The inputs are concatenated with double pipe separators to avoid ambiguity.
    """
    challenge_input = f'{wallet_id}||{device_id}||{block}||{nonce}'
    return sha256(challenge_input)

def post_session_challenge(wallet_id: str, device_id: str, current_block: int) -> Tuple[str, str, int]:
    """Generate a challenge for session establishment.
    
    Returns:
        Tuple of (challenge, nonce, expiry_block)
    """
    nonce_input = f'{wallet_id}||{device_id}||{current_block}'
    nonce = sha256(nonce_input)[:16]
    challenge = compute_challenge(wallet_id, device_id, current_block, nonce)
    expiry_block = current_block + 100
    return (challenge, nonce, expiry_block)

def post_session_establish(wallet_id: str, device_id: str, challenge_response: str, current_block: int, session_manager: Any, ttl_blocks: int=1000) -> Dict[str, Any]:
    """Establish a session by verifying challenge and creating session token.
    
    Args:
        wallet_id: Wallet identifier
        device_id: Device identifier
        challenge_response: Client's response to the challenge
        current_block: Current ledger block
        session_manager: SessionManager instance
        ttl_blocks: Session time-to-live in blocks
        
    Returns:
        Dict containing session token and success status
    """
    nonce_input = f'{wallet_id}||{device_id}||{current_block}'
    nonce = sha256(nonce_input)[:16]
    expected_challenge = compute_challenge(wallet_id, device_id, current_block, nonce)
    if challenge_response != expected_challenge:
        return {'success': False, 'error': 'Challenge response mismatch', 'session_token': None}
    scope = ['basic']
    token = session_manager.create_session(wallet_id=wallet_id, device_id=device_id, scope=scope, current_block=current_block, ttl_blocks=ttl_blocks)
    return {'success': True, 'session_token': {'session_id': token.session_id, 'wallet_id': token.wallet_id, 'device_id': token.device_id, 'issued_at_block': token.issued_at_block, 'ttl_blocks': token.ttl_blocks, 'scope': token.scope}}
