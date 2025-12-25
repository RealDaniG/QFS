"""
EvidenceBus Adapter
Connects Auth Service to QFS EvidenceBus for immutable audit logging.
"""

from typing import Dict, Any
import json
import logging
import time

# Configure logger
logger = logging.getLogger("EvidenceBus")
logger.setLevel(logging.INFO)


from dataclasses import dataclass, field


@dataclass
class EvidenceEvent:
    event_type: str
    version: int
    payload: Dict[str, Any]
    timestamp: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "version": self.version,
            **self.payload,
            **self.payload,
            "timestamp": self.timestamp or int(time.time()),
        }


class EvidenceBusAdapter:
    def __init__(self) -> None:
        self.enabled = True

    def emit(self, event: Dict[str, Any]) -> None:
        """
        Emit structured event to EvidenceBus.
        For Alpha: Logs to stdout/file.
        For Beta: Will push to P2P network/ledger.
        """
        if not self.enabled:
            return

        # Ensure event is serializable
        try:
            payload = json.dumps(event)
            logger.info(f"EVIDENCE_EVENT: {payload}")
            # In production, this would go to the real EvidenceBus
        except Exception as e:
            logger.error(f"Failed to emit evidence: {e}")
