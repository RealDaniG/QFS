import hashlib
import json
from dataclasses import dataclass
from typing import List, Dict, Any

def sha256(data: str) -> str:
    """Return the hex SHA‑256 digest of the UTF‑8 encoded string."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def compute_device_id(os_type: str, hardware_id: str, label: str='') -> str:
    """Deterministically compute a device identifier using SHA‑256.
    The inputs are concatenated with double pipe separators to avoid ambiguity.
    """
    return sha256(f'{os_type}||{hardware_id}||{label}')

@dataclass
class SessionToken:
    session_id: str
    wallet_id: str
    device_id: str
    issued_at_block: int
    ttl_blocks: int
    scope: List[str]

class SessionManager:
    """Pure session manager that emits deterministic ledger events.
    The `ledger` object must provide an `emit_event(event_type: str, data: dict)`
    method. No global mutable state is kept; all information is derived from
    inputs and emitted events.
    """

    def __init__(self, ledger: Any):
        self.ledger = ledger

    def _session_id(self, wallet_id: str, device_id: str, issued_at_block: int, scope: List[str]) -> str:
        """Compute deterministic session_id using SHA‑256 over a canonical JSON payload."""
        payload = {'wallet_id': wallet_id, 'device_id': device_id, 'issued_at_block': issued_at_block, 'scope': sorted(scope)}
        canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return sha256(canonical)

    def create_session(self, wallet_id: str, device_id: str, scope: List[str], current_block: int, ttl_blocks: int) -> SessionToken:
        """Create a new session and emit a SESSION_STARTED event."""
        session_id = self._session_id(wallet_id, device_id, current_block, scope)
        token = SessionToken(session_id=session_id, wallet_id=wallet_id, device_id=device_id, issued_at_block=current_block, ttl_blocks=ttl_blocks, scope=scope)
        event_data = {'session_id': session_id, 'wallet_id': wallet_id, 'device_id': device_id, 'issued_at_block': current_block, 'ttl_blocks': ttl_blocks, 'scope': scope}
        self.ledger.emit_event('SESSION_STARTED', event_data)
        return token

    def rotate_session(self, old_token: SessionToken, current_block: int) -> SessionToken:
        """Rotate an existing session, emitting SESSION_ROTATED."""
        session_id = self._session_id(old_token.wallet_id, old_token.device_id, current_block, old_token.scope)
        new_token = SessionToken(session_id=session_id, wallet_id=old_token.wallet_id, device_id=old_token.device_id, issued_at_block=current_block, ttl_blocks=old_token.ttl_blocks, scope=old_token.scope)
        rotate_data = {'old_session_id': old_token.session_id, 'new_session_id': new_token.session_id, 'block': current_block, 'wallet_id': old_token.wallet_id, 'device_id': old_token.device_id, 'scope': old_token.scope, 'ttl_blocks': old_token.ttl_blocks}
        self.ledger.emit_event('SESSION_ROTATED', rotate_data)
        return new_token

    def revoke_session(self, token: SessionToken, reason: str, current_block: int) -> None:
        """Revoke a session, emitting SESSION_REVOKED."""
        revoke_data = {'session_id': token.session_id, 'reason': reason, 'block': current_block}
        self.ledger.emit_event('SESSION_REVOKED', revoke_data)

    def is_session_active(self, token: SessionToken, current_block: int) -> bool:
        """Return True if the session is within its TTL at `current_block`."""
        if current_block < token.issued_at_block:
            return False
        if current_block >= token.issued_at_block + token.ttl_blocks:
            return False
        return True