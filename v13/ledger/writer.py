"""
writer.py - Ledger Event Writer
"""

import json
import hashlib
from typing import List, Dict, Any, Optional
from v13.ledger.genesis_ledger import GenesisLedger, GenesisEntry


class LedgerWriter:
    def __init__(self, ledger_path: str = "genesis_ledger.jsonl"):
        self.ledger = GenesisLedger(ledger_path)

    async def emit_wallet_registered(
        self,
        wallet_id: str,
        role: str,
        scope: str,
        capabilities: List[str],
        reason: str = "DEV_SYSTEM_BOOTSTRAP",
    ) -> GenesisEntry:
        """
        Emit WALLET_REGISTERED event to the ledger.
        """
        ts = "2025-01-01T00:00:00Z"
        entry = GenesisEntry(
            wallet=wallet_id,
            event_type="WALLET_REGISTERED",
            value="0",
            timestamp=ts,
            metadata={
                "wallet_id": wallet_id,
                "role": role,
                "scope": scope,
                "capabilities": capabilities,
                "reason": reason,
            },
        )
        return await self.ledger.append(entry)

    async def emit_session_started(
        self, wallet_id: str, device_id: str, scope: str, ttl: int
    ) -> GenesisEntry:
        """
        Emit SESSION_STARTED event.
        """
        ts = "2025-01-01T00:00:01Z"
        entry = GenesisEntry(
            wallet=wallet_id,
            event_type="SESSION_STARTED",
            value="0",
            timestamp=ts,
            metadata={
                "wallet_id": wallet_id,
                "device_id": device_id,
                "scope": scope,
                "ttl": ttl,
            },
        )
        return await self.ledger.append(entry)
