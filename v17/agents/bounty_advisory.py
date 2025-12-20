from typing import Optional, Dict, Any
from v17.agents.schemas import AdvisorySignal


def process_bounty_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Consumer for bounty events. Generates advisory signals.
    Implements v17.1 heuristics.
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

        # 1. Reference Check
        # Rationale: Contributions usually require external proofs (links, hashes).
        if "http" in reference or "ipfs" in reference or "0x" in reference:
            reasons.append("Quality: Valid reference format detected")
            score += 0.3
        else:
            reasons.append("Review: Reference format unclear")

        # 2. Detail Check
        # Rationale: Substantive textual explanations help verification.
        if len(content) > 100:
            reasons.append("Quality: Detailed explanation provided")
            score += 0.2
        elif len(content) < 10:
            reasons.append("Quality: Explanation very brief")
            score -= 0.1

        signal = AdvisorySignal(
            target_type="bounty_contribution",
            target_id=f"{bounty_id}:{contrib.get('contributor_wallet')}",
            score=max(0.0, min(1.0, score)),
            reasons=reasons,
            model_version="bounty-heuristic-v1.1",
        )

        return {
            "type": "AGENT_ADVISORY_BOUNTY",
            "payload": {"signal": signal.model_dump(), "timestamp": timestamp},
        }

    return None
