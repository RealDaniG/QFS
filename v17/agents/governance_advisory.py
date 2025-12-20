from typing import Optional, Dict, Any
from v17.agents.schemas import AdvisorySignal


def process_governance_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Consumer for governance events. Generates advisory signals.
    """
    etype = event.get("type")
    payload = event.get("payload", {})

    if etype == "GOV_PROPOSAL_CREATED":
        proposal = payload.get("proposal", {})
        proposal_id = proposal.get("proposal_id")
        amount = proposal.get("requested_amount", 0)
        description = proposal.get("description", "")
        timestamp = payload.get("timestamp", 0)

        reasons = []
        score = 0.8

        # Deterministic Heuristics
        if amount > 10000:
            reasons.append("High requested amount")
            score -= 0.1

        if len(description) < 50:
            reasons.append("Description too short")
            score -= 0.2

        if "risk" in description.lower():
            reasons.append("Self-identified risk")

        signal = AdvisorySignal(
            target_type="proposal",
            target_id=proposal_id,
            score=max(0.0, min(1.0, score)),
            reasons=reasons,
            model_version="gov-heuristic-v1",
        )

        return {
            "type": "AGENT_ADVISORY_PROPOSAL",
            "payload": {"signal": signal.model_dump(), "timestamp": timestamp},
        }

    return None
