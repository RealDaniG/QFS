"""
Bounty Projection Service (v17 UI Layer)

Projects pure EvidenceBus events into human-legible timeline DTOs for the Admin Dashboard.
Read-only, deterministic projection over the event sourcing log.
"""

from typing import Dict, List, Optional
from v15.evidence.bus import EvidenceBus
from v17.bounties.f_bounties import get_bounty_state


class BountyProjection:
    """
    Project bounty events into view models for the dashboard.
    """

    def __init__(self, bus=EvidenceBus):
        self.bus = bus

    def list_bounties(self, limit: int = 50) -> List[Dict]:
        """
        Get a summary list of recent bounties.

        DTO Schema:
        {
            "id": str,
            "title": str,
            "status": "open" | "completed",
            "reward": str,
            "contribution_count": int,
            "created_at": int
        }
        """
        all_events = self.bus.get_events(limit=limit * 10)
        bounties = {}

        for envelope in all_events:
            event = envelope.get("event", {})
            event_type = event.get("type", "")
            payload = event.get("payload", {})

            if event_type == "BOUNTY_CREATED":
                b = payload.get("bounty", {})
                bid = b.get("bounty_id")
                if bid:
                    bounties[bid] = {
                        "id": bid,
                        "title": b.get("title"),
                        "status": "open",
                        "reward": f"{b.get('reward_amount')} {b.get('currency')}",
                        "contribution_count": 0,
                        "created_at": b.get("created_at"),
                    }

            elif event_type == "BOUNTY_CONTRIBUTION_SUBMITTED":
                contribution = payload.get("contribution", {})
                bid = contribution.get("bounty_id")
                if bid in bounties:
                    bounties[bid]["contribution_count"] += 1

            elif event_type == "BOUNTY_REWARD_DECIDED":
                decision = payload.get("decision", {})
                bid = decision.get("bounty_id")
                if bid in bounties:
                    bounties[bid]["status"] = "completed"

        # Sort by creation time desc
        result = list(bounties.values())
        result.sort(key=lambda x: x["created_at"], reverse=True)
        return result[:limit]

    def get_bounty_timeline(self, bounty_id: str) -> Optional[Dict]:
        """
        Get detailed timeline for a bounty.
        """
        state = get_bounty_state(bounty_id)
        if not state:
            return None

        # Build timeline
        timeline = []

        # 1. Created
        timeline.append(
            {
                "stage": "Created",
                "timestamp": state.bounty.created_at,
                "actor": state.bounty.created_by,
                "description": f"Bounty created: {state.bounty.title} ({state.bounty.reward_amount} {state.bounty.currency})",
            }
        )

        # 2. Contributions
        for c in state.contributions:
            timeline.append(
                {
                    "stage": "Contribution",
                    "timestamp": c.submitted_at,
                    "actor": c.contributor_wallet,
                    "description": f"Contribution submitted: {c.reference}",
                }
            )

        # 3. Advisory Signals
        for adv in state.advisory_signals:
            if isinstance(adv, dict):
                content_score = adv.get("content_score", {})
                if content_score:
                    timeline.append(
                        {
                            "stage": "Advisory Signal",
                            "timestamp": adv.get("timestamp"),
                            "actor": f"Agent:{adv.get('provider')}",
                            "description": f"Quality Score: {content_score.get('quality'):.2f}",
                            "is_advisory": True,
                        }
                    )

        # 4. Rewards
        if state.reward_decisions:
            total = sum(d.amount for d in state.reward_decisions)
            timeline.append(
                {
                    "stage": "Rewards Allocated",
                    "timestamp": state.reward_decisions[
                        0
                    ].decided_at,  # Approximate group time
                    "actor": "Protocol",
                    "description": f"Protocol allocated {total:.2f} {state.bounty.currency} to {len(state.reward_decisions)} contributors.",
                    "is_final": True,
                }
            )

        timeline.sort(key=lambda x: x.get("timestamp", 0))

        return {
            "info": {
                "id": state.bounty.bounty_id,
                "title": state.bounty.title,
                "status": "completed" if state.reward_decisions else "open",
                "total_contributions": state.total_contributions,
            },
            "timeline": timeline,
            "reward_summary": self._generate_reward_summary(state),
            "evidence_link": f"/evidence?filter=bounty_id:{bounty_id}",
        }

    def _generate_reward_summary(self, state) -> Optional[Dict]:
        if not state.reward_decisions:
            return None

        return {
            "total_payout": sum(d.amount for d in state.reward_decisions),
            "recipients": [
                {
                    "wallet": d.recipient_wallet,
                    "amount": d.amount,
                    "percent": d.percentage,
                }
                for d in state.reward_decisions
            ],
            "method": "Normalized Score Distribution",
        }
