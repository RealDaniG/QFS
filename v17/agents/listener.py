from typing import List, Dict, Any
from v15.evidence.bus import EvidenceBus
from v17.agents import (
    process_governance_event,
    process_bounty_event,
    process_social_event,
)


class AdvisoryListener:
    """
    Listens to F-layer events and triggers advisory generation.
    """

    def __init__(self, bus=EvidenceBus):
        self.bus = bus

    def process_event(self, envelope: Dict[str, Any]):
        """
        Process a single event envelope and emit advisory if applicable.
        """
        if not isinstance(envelope, dict):
            return

        event = envelope.get("event", {})

        # Try all processors
        advisory = (
            process_governance_event(event)
            or process_bounty_event(event)
            or process_social_event(event)
        )

        if advisory:
            # Check if this advisory was already emitted (to prevent loops or spam in a naive loop)
            # For simplicity in this phase, we emit.
            # In production, we'd check if we already opined on this target_id with this model_version.
            self.bus.emit(advisory["type"], advisory["payload"])

    def process_history(self, limit: int = 1000):
        """
        Replay history and generate advisories.
        """
        events = self.bus.get_events(limit=limit)
        for envelope in events:
            self.process_event(envelope)
