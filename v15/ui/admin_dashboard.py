"""
Admin Dashboard (v16 Baseline)

Read-only EvidenceBus viewer for governance, moderation, bounties, and agent events.
Zero-Sim compliant: no direct DB writes, deterministic filtering.
"""

from typing import Dict, List, Optional
from datetime import datetime

from v15.evidence.bus import EvidenceBus


class AdminDashboard:
    """
    Admin Panel for viewing EvidenceBus events.
    All operations are read-only and deterministic.
    """

    def __init__(self):
        self.bus = EvidenceBus

    def get_recent_events(self, limit: int = 100) -> List[Dict]:
        """Get recent events from the Evidence Chain."""
        return self.bus.get_events(limit=limit)

    def filter_by_type(self, event_type: str, limit: int = 100) -> List[Dict]:
        """Filter events by type (e.g., 'AUTH_LOGIN', 'GOVERNANCE_VOTE')."""
        all_events = self.bus.get_events(limit=limit * 2)  # Over-fetch for filtering
        filtered = [
            e for e in all_events if e.get("event", {}).get("type") == event_type
        ]
        return filtered[:limit]

    def filter_by_wallet(self, wallet_address: str, limit: int = 100) -> List[Dict]:
        """Filter events by wallet address."""
        all_events = self.bus.get_events(limit=limit * 2)
        filtered = []
        for e in all_events:
            payload = e.get("event", {}).get("payload", {})
            if (
                payload.get("wallet") == wallet_address
                or payload.get("wallet_address") == wallet_address
            ):
                filtered.append(e)
        return filtered[:limit]

    def get_chain_summary(self) -> Dict:
        """Get summary statistics of the Evidence Chain."""
        events = self.bus.get_events(limit=1000)

        event_types = {}
        for e in events:
            event_type = e.get("event", {}).get("type", "UNKNOWN")
            event_types[event_type] = event_types.get(event_type, 0) + 1

        return {
            "total_events": len(events),
            "chain_tip": self.bus.get_tip(),
            "event_types": event_types,
            "latest_event": events[-1] if events else None,
        }

    def verify_chain_integrity(self, limit: int = 100) -> Dict:
        """
        Verify the hash chain integrity.
        Returns verification status and any broken links.
        """
        events = self.bus.get_events(limit=limit)

        broken_links = []
        prev_hash = "0" * 64  # Genesis

        for idx, envelope in enumerate(events):
            event = envelope.get("event", {})
            claimed_prev = event.get("prev_hash")

            if claimed_prev != prev_hash:
                broken_links.append(
                    {
                        "index": idx,
                        "expected": prev_hash,
                        "found": claimed_prev,
                    }
                )

            prev_hash = envelope.get("hash")

        return {
            "verified": len(broken_links) == 0,
            "events_checked": len(events),
            "broken_links": broken_links,
        }


class EvidenceChainViewer:
    """
    Evidence Chain Viewer for tracing decisions and actions.
    Provides deterministic, replayable audit trails.
    """

    def __init__(self):
        self.bus = EvidenceBus

    def trace_entity(self, entity_id: str, entity_type: str = "wallet") -> List[Dict]:
        """
        Trace all events related to an entity (wallet, bounty, proposal, etc.).

        Args:
            entity_id: The identifier (wallet address, bounty ID, etc.)
            entity_type: Type of entity ('wallet', 'bounty', 'proposal')

        Returns:
            Chronological list of events involving this entity
        """
        all_events = self.bus.get_events(limit=1000)

        related_events = []
        for envelope in all_events:
            event = envelope.get("event", {})
            payload = event.get("payload", {})

            # Check various payload fields for entity_id
            if (
                payload.get("wallet") == entity_id
                or payload.get("wallet_address") == entity_id
                or payload.get("bounty_id") == entity_id
                or payload.get("proposal_id") == entity_id
                or payload.get("user_id") == entity_id
            ):
                related_events.append(envelope)

        return related_events

    def explain_decision(self, decision_hash: str) -> Dict:
        """
        Explain a decision by showing the PoE chain that led to it.

        Args:
            decision_hash: Hash of the decision event

        Returns:
            Decision context with preceding events
        """
        all_events = self.bus.get_events(limit=1000)

        # Find the decision event
        decision_event = None
        decision_index = -1

        for idx, envelope in enumerate(all_events):
            if envelope.get("hash") == decision_hash:
                decision_event = envelope
                decision_index = idx
                break

        if not decision_event:
            return {"error": "Decision not found", "hash": decision_hash}

        # Get preceding events (context window)
        context_start = max(0, decision_index - 10)
        context_events = all_events[context_start : decision_index + 1]

        return {
            "decision": decision_event,
            "context": context_events,
            "chain_position": decision_index,
            "total_events": len(all_events),
        }

    def get_governance_timeline(self, limit: int = 50) -> List[Dict]:
        """Get chronological governance events."""
        all_events = self.bus.get_events(limit=limit * 2)

        governance_types = [
            "GOVERNANCE_PROPOSAL",
            "GOVERNANCE_VOTE",
            "GOVERNANCE_EXECUTION",
            "GOVERNANCE_VETO",
        ]

        timeline = [
            e for e in all_events if e.get("event", {}).get("type") in governance_types
        ]

        return timeline[:limit]

    def get_agent_advisory_log(self, limit: int = 50) -> List[Dict]:
        """Get agent advisory events (read-only recommendations)."""
        all_events = self.bus.get_events(limit=limit * 2)

        agent_events = [
            e
            for e in all_events
            if e.get("event", {}).get("type", "").startswith("AGENT_")
        ]

        return agent_events[:limit]
