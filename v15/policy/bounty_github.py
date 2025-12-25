from typing import List, Dict, Any, Optional
from v15.services.evidence_adapter import EvidenceBusAdapter, EvidenceEvent
from dataclasses import dataclass


@dataclass
class BountyRound:
    round_id: str
    start_time: int
    end_time: int
    flx_pool: float
    status: str  # "active", "finalized"


# Hardcoded rounds for v20 Alpha
ROUNDS = {
    "v20-retro-epoch-1": BountyRound(
        round_id="v20-retro-epoch-1",
        start_time=0,
        end_time=9999999999,
        flx_pool=10000.0,
        status="active",
    )
}


def compute_rewards_for_round(
    round_id: str, adapter: EvidenceBusAdapter
) -> List[Dict[str, Any]]:
    """
    Deterministic F-Layer logic:
    1. Replay events to build contribution ledger.
    2. Apply scoring rules (currently equal weight per item).
    3. Distribute FLX pool pro-rata.
    4. Emit REWARDS_ASSIGNED events.
    """
    round_config = ROUNDS.get(round_id)
    if not round_config:
        raise ValueError(f"Unknown round: {round_id}")

    # In a real replay, we would read from the event log.
    # For now, we assume we are fed a list of relevant events or we query a store.
    # Since we don't have a full event store query API yet, we'll define the LOGIC here
    # and expect the caller to provide the events or we mock it.

    # Placeholder: Caller passes events.
    # But wait, the function signature only takes adapter.
    # We need a source of truth.
    pass


class RewardComputer:
    def __init__(self, adapter: EvidenceBusAdapter):
        self.adapter = adapter

    def process_ledger(self, events: List[EvidenceEvent], round_id: str):
        round_config = ROUNDS.get(round_id)
        if not round_config:
            return

        # 1. Filter events for this round
        contribs = []
        for e in events:
            if (
                e.event_type == "CONTRIB_RECORDED"
                and e.payload.get("round_id") == round_id
            ):
                contribs.append(e)

        if not contribs:
            return

        # 2. Compute Scores (Deterministic)
        # Rule: 1 PR = 5 points, 1 Issue = 1 point
        scores: Dict[str, float] = {}  # user_handle -> score
        total_score = 0.0

        for c in contribs:
            user = c.payload["user"]
            ctype = c.payload["type"]

            points = 0.0
            if ctype == "pr":
                points = 5.0
            elif ctype == "issue":
                points = 1.0

            scores[user] = scores.get(user, 0.0) + points
            total_score += points

        # 3. Allocation
        rewards = []
        if total_score > 0:
            for user, score in scores.items():
                flx_amount = (score / total_score) * round_config.flx_pool
                rewards.append({"user": user, "score": score, "flx": flx_amount})

                # Emit Event
                self.adapter.emit(
                    {
                        "event_type": "REWARDS_ASSIGNED",
                        "auth_event_version": 1,
                        "round_id": round_id,
                        "user": user,
                        "flx_amount": flx_amount,
                        "basis_score": score,
                        "timestamp": 0,  # Deterministic? Or derived from processing time?
                    }
                )

        return rewards
