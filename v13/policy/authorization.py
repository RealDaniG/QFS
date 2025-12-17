"""
authorization.py - Role and Capability Resolution Engine
"""
from typing import List, Dict, Any

class AuthorizationEngine:

    def __init__(self, ledger_entries: List[Any]):
        self.roles: Dict[str, Dict[str, Any]] = {}
        self.capabilities: Dict[str, List[str]] = {}
        self._replay(ledger_entries)

    def _replay(self, entries: List[Any]):
        for entry in sorted(entries):
            event_type = getattr(entry, 'event_type', None)
            metadata = getattr(entry, 'metadata', {})
            if event_type == 'WALLET_REGISTERED':
                w_id = metadata.get('wallet_id')
                if w_id:
                    self.roles[w_id] = {'role': metadata.get('role'), 'scope': metadata.get('scope')}
                    self.capabilities[w_id] = metadata.get('capabilities', [])

    def resolve_role(self, wallet_id: str) -> str:
        return self.roles.get(wallet_id, {}).get('role', 'NONE')

    def authorize(self, wallet_id: str, capability: str, scope: str) -> bool:
        """
        Authorize an action based on wallet role and capabilities.
        """
        user_data = self.roles.get(wallet_id)
        if not user_data:
            return False
        if user_data.get('scope') != scope:
            return False
        user_caps = self.capabilities.get(wallet_id, [])
        if 'LEDGER_READ_ALL' in user_caps and capability == 'READ':
            return True
        return capability in user_caps