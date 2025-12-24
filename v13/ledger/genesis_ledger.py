import json
import hashlib
import os
import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class GenesisEntry(BaseModel):
    wallet: str
    event_type: str
    value: str = "0"  # BigNum128 string
    metadata: Dict[str, Any] = {}
    timestamp: str = ""
    hash: str = ""
    previous_hash: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        if not self.timestamp:
            # Zero-Sim: Use fixed epoch if not provided
            self.timestamp = "1970-01-01T00:00:00Z"


class GenesisLedger:
    def __init__(self, filepath: str = "genesis_ledger.jsonl"):
        self.filepath = filepath
        self.lock = asyncio.Lock()

    async def append(self, entry: GenesisEntry) -> GenesisEntry:
        last_hash = "0" * 64
        if os.path.exists(self.filepath) and os.path.getsize(self.filepath) > 0:
            with open(self.filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                if lines:
                    try:
                        last_line = lines[-1]
                        last_entry = json.loads(last_line)
                        last_hash = last_entry.get("hash", last_hash)
                    except Exception:
                        pass
        entry.previous_hash = last_hash
        payload = f"{entry.previous_hash}|{entry.timestamp}|{entry.wallet}|{entry.event_type}|{entry.value}|{json.dumps(entry.metadata, sort_keys=True)}"
        entry.hash = hashlib.sha256(payload.encode()).hexdigest()
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(entry.json() + "\n")
        return entry

    def read_all(self) -> List[GenesisEntry]:
        if not os.path.exists(self.filepath):
            return []
        entries = []
        with open(self.filepath, "r", encoding="utf-8") as f:
            for line in sorted(f):
                if line.strip():
                    entries.append(GenesisEntry(**json.loads(line)))
        return entries
