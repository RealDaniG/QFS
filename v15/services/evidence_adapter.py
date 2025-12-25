"""
EvidenceBus Adapter
Connects Auth Service to QFS EvidenceBus for immutable audit logging.
"""

from typing import Dict, Any
import json
import logging

# Configure logger
logger = logging.getLogger("EvidenceBus")
logger.setLevel(logging.INFO)


class EvidenceBusAdapter:
    def __init__(self):
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
