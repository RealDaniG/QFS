from typing import Optional, Dict, Any
from v17.agents.schemas import AdvisorySignal


def process_bounty_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Consumer for bounty events. Generates advisory signals.
    """
    etype = event.get("type")
    payload = event.get("payload", {})

    if etype == "BOUNTY_CONTRIBUTION_SUBMITTED":
        contrib = payload.get("contribution", {})
        bounty_id = contrib.get("bounty_id")
        content = contrib.get("content", "")
        reference = contrib.get("reference", "")
        timestamp = payload.get("timestamp", 0)

        reasons = []
        score = 0.5

        # Deterministic Heuristics
        if "http" in reference:
            reasons.append("Contains valid reference link")
            score += 0.3

        if len(content) > 100:
            reasons.append("Detailed description")
            score += 0.2

        signal = AdvisorySignal(
            target_type="bounty_contribution",
            target_id=f"{bounty_id}:{contrib.get('contributor_wallet')}",
            score=max(0.0, min(1.0, score)),
            reasons=reasons,
            model_version="bounty-heuristic-v1",
        )

        return {
            "type": "AGENT_ADVISORY_BOUNTY",
            "payload": {"signal": signal.model_dump(), "timestamp": timestamp},
        }

    return None
