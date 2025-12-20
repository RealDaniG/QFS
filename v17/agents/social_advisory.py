from typing import Optional, Dict, Any
from v17.agents.schemas import AdvisorySignal


def process_social_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Consumer for social events. Generates advisory signals.
    """
    etype = event.get("type")
    payload = event.get("payload", {})

    if etype == "SOCIAL_DISPUTE_OPENED":
        dispute = payload.get("dispute", {})
        dispute_id = dispute.get("dispute_id")
        reason = dispute.get("reason", "").lower()
        timestamp = payload.get("timestamp", 0)

        reasons = []
        score = 0.5  # Urgency

        # Deterministic Heuristics
        if "scam" in reason or "fraud" in reason:
            reasons.append("High urgency keyword detected")
            score = 0.9

        if "typo" in reason:
            reasons.append("Low urgency: likely minor")
            score = 0.2

        signal = AdvisorySignal(
            target_type="dispute",
            target_id=dispute_id,
            score=max(0.0, min(1.0, score)),
            reasons=reasons,
            model_version="social-heuristic-v1",
        )

        return {
            "type": "AGENT_ADVISORY_SOCIAL",
            "payload": {"signal": signal.model_dump(), "timestamp": timestamp},
        }

    return None
