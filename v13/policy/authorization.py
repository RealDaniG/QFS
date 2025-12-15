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
        for entry in entries:
            # Handle standard dictionary or object with attributes
            event_type = getattr(entry, 'event_type', None)
            metadata = getattr(entry, 'metadata', {})
            
            if event_type == "WALLET_REGISTERED":
                w_id = metadata.get("wallet_id")
                if w_id:
                    self.roles[w_id] = {
                        "role": metadata.get("role"),
                        "scope": metadata.get("scope")
                    }
                    self.capabilities[w_id] = metadata.get("capabilities", [])

    def resolve_role(self, wallet_id: str) -> str:
        return self.roles.get(wallet_id, {}).get("role", "NONE")

    def authorize(self, wallet_id: str, capability: str, scope: str) -> bool:
        """
        Authorize an action based on wallet role and capabilities.
        """
        user_data = self.roles.get(wallet_id)
        if not user_data:
            return False
            
        # Scope check
        if user_data.get("scope") != scope:
            # If scope is DEV, they might be allowed in DEV, but not TESTNET?
            # Enforce strict equality for now.
            return False
            
        # Capability check
        user_caps = self.capabilities.get(wallet_id, [])
        if "LEDGER_READ_ALL" in user_caps and capability == "READ":
            return True # Simplified hierarchy
            
        return capability in user_caps
