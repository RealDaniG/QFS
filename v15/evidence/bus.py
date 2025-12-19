"""
EvidenceBus - Central Event Spine (v16 Baseline)

Zero-Sim Compliant:
- Deterministic sequencing (no threading)
- Hash-chained logging
- MOCKQPC-backed signatures
"""

import hashlib
import json
import time
from typing import Any, Dict, Optional

# V15 Crypto
from v15.crypto.adapter import sign_poe, verify_poe


class EvidenceBus:
    """
    Singleton-like event bus for the QFS v16 Baseline.
    In dev/beta (`MOCKQPC_ENABLED=true`), this mocks the consensus layer.
    """

    _chain_tip: str = "0" * 64
    _log_file: str = "evidence_chain.jsonl"

    @classmethod
    def emit(cls, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Emit an event to the Evidence Chain.
        """
        ts = payload.get("timestamp", int(time.time()))

        # 2. Construct Canonical Event
        event = {
            "type": event_type,
            "payload": payload,
            "prev_hash": cls._chain_tip,
            "timestamp": ts,
        }

        # 3. Serialize Deterministically
        event_json = json.dumps(event, sort_keys=True, separators=(",", ":"))
        event_bytes = event_json.encode("utf-8")

        # 4. Hash
        algo = hashlib.sha3_256()
        algo.update(event_bytes)
        event_hash = algo.hexdigest()

        # 5. MOCKQPC Sign (PoE)
        signature = sign_poe(bytes.fromhex(event_hash))

        # 6. Update Chain Tip
        cls._chain_tip = event_hash

        # 7. Construct Final Envelope
        envelope = {
            "event": event,
            "hash": event_hash,
            "signature": signature.hex(),
        }

        # 8. Persist (Dev/MOCKQPC Mode)
        with open(cls._log_file, "a") as f:
            f.write(json.dumps(envelope) + "\n")

        return envelope

    @classmethod
    def get_tip(cls) -> str:
        return cls._chain_tip

    @classmethod
    def get_events(cls, limit: int = 100) -> list[Dict]:
        """Read events from the local chain log."""
        events = []
        try:
            with open(cls._log_file, "r") as f:
                for line in f:
                    if line.strip():
                        events.append(json.loads(line))
        except FileNotFoundError:
            return []
        return events[-limit:]
