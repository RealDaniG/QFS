from typing import Optional, Dict, Any
from v17.agents.schemas import AdvisorySignal


def process_social_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Consumer for social events. Generates advisory signals.
    Implements v17.1 heuristics.
    """
    etype = event.get("type")
    payload = event.get("payload", {})

    if etype == "SOCIAL_DISPUTE_OPENED":
        dispute = payload.get("dispute", {})
        dispute_id = dispute.get("dispute_id")
        reason = dispute.get("reason", "").lower()
        timestamp = payload.get("timestamp", 0)

        reasons = []
        score = 0.5  # Baseline Urgency

        # 1. High Urgency Keywords
        critical_terms = ["scam", "fraud", "stolen", "emergency", "exploit"]
        found_critical = [t for t in critical_terms if t in reason]

        if found_critical:
            reasons.append(f"Urgency: Critical keywords ({', '.join(found_critical)})")
            score = 0.9

        # 2. Low Urgency / Noise
        minor_terms = ["typo", "mistake", "rename", "label"]
        found_minor = [t for t in minor_terms if t in reason]

        if found_minor and not found_critical:
            reasons.append("Urgency: Appears to be administrative/minor")
            score = 0.2

        signal = AdvisorySignal(
            target_type="dispute",
            target_id=dispute_id,
            score=max(0.0, min(1.0, score)),
            reasons=reasons,
            model_version="social-heuristic-v1.1",
        )

        event_out = {
            "type": "AGENT_ADVISORY_SOCIAL",
            "payload": {"signal": signal.model_dump(), "timestamp": timestamp},
        }

        # v18.5 Ascon Integration
        from v18.crypto.advisory_wrap import wrap_advisory_event

        return wrap_advisory_event(event_out, seq=int(timestamp % 1000))

    return None
