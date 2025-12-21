from typing import Optional, Dict, Any
from v17.agents.schemas import AdvisorySignal


def process_governance_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Consumer for governance events. Generates advisory signals.
    Implements v17.1 heuristics.
    """
    etype = event.get("type")
    payload = event.get("payload", {})

    if etype == "GOV_PROPOSAL_CREATED":
        proposal = payload.get("proposal", {})
        proposal_id = proposal.get("proposal_id")
        amount = proposal.get("requested_amount", 0)
        # Fallback for description/body mismatch
        description = proposal.get("description") or proposal.get("body", "")
        title = proposal.get("title", "")
        timestamp = payload.get("timestamp", 0)

        reasons = []
        score = 0.8

        # 1. High Amount Heuristic
        # Rationale: Large requests need more scrutiny.
        if amount > 10000:
            reasons.append("Review: High-value request (>10k)")
            score -= 0.1

        # 2. Low Context Heuristic
        # Rationale: Short descriptions often lack necessary detail for voters.
        if len(description) < 50:
            reasons.append("Quality: Description is very short (<50 chars)")
            score -= 0.2

        # 3. Risk Keyword Heuristic
        # Rationale: Self-identified or common risk terms should be highlighted.
        risks = ["risk", "experiment", "audit", "exploit"]
        found_risks = [w for w in risks if w in description.lower()]
        if found_risks:
            reasons.append(
                f"Content: Risk keywords detected ({', '.join(found_risks)})"
            )

        # 4. Spam Heuristic
        if description.strip() == title.strip():
            reasons.append("Quality: Description identical to title")
            score -= 0.1

        signal = AdvisorySignal(
            target_type="proposal",
            target_id=proposal_id,
            score=max(0.0, min(1.0, score)),
            reasons=reasons,
            model_version="gov-heuristic-v1.1",  # Bumped version
        )

        event_out = {
            "type": "AGENT_ADVISORY_PROPOSAL",
            "payload": {"signal": signal.model_dump(), "timestamp": timestamp},
        }

        # v18.5 Ascon Integration
        from v18.crypto.advisory_wrap import wrap_advisory_event

        return wrap_advisory_event(event_out, seq=int(timestamp % 1000))

    return None
