"""
Social & Profile Projection (v17 UI Layer)

Aggregates threads, comments, and per-user activity history.
"""

from typing import Dict, List, Any
from v15.evidence.bus import EvidenceBus


class SocialProjection:
    def __init__(self, bus=EvidenceBus):
        self.bus = bus

    def get_threads_for_entity(self, entity_id: str) -> List[Dict]:
        """Find threads bound to a specific entity (Proposal/Bounty)."""
        limit = 1_000_000  # Full scan
        events = self.bus.get_events(limit=limit)
        threads = []

        for envelope in events:
            if not isinstance(envelope, dict):
                continue
            event = envelope.get("event", {})
            if event.get("type") == "SOCIAL_THREAD_CREATED":
                payload = event.get("payload", {})
                t = payload.get("thread", {})
                if t.get("reference_id") == entity_id:
                    threads.append(t)

        return threads

    def get_user_history(self, wallet_address: str) -> Dict[str, Any]:
        """
        Construct a comprehensive contribution timeline for a user.
        Includes: Votes, Comments, Proposals, Bounties, Contributions, Disputes.
        """
        limit = 1_000_000
        events = self.bus.get_events(limit=limit)

        timeline = []
        stats = {
            "votes": 0,
            "proposals": 0,
            "bounties_created": 0,
            "contributions": 0,
            "threads": 0,
            "comments": 0,
            "disputes_raised": 0,
        }

        for envelope in events:
            if not isinstance(envelope, dict):
                continue
            event = envelope.get("event", {})
            etype = event.get("type")
            payload = event.get("payload", {})
            ts = payload.get("timestamp", 0)

            item = None

            # Governance
            if etype == "GOV_VOTE_CAST":
                vote = payload.get("vote", {})
                if vote.get("voter_wallet") == wallet_address:
                    stats["votes"] += 1
                    item = {
                        "type": "vote",
                        "summary": f"Voted '{vote.get('choice')}' on {vote.get('proposal_id')}",
                        "timestamp": ts,
                        "weight": vote.get("weight"),
                    }
            elif etype == "GOV_PROPOSAL_CREATED":
                prop = payload.get("proposal", {})
                if prop.get("creator_wallet") == wallet_address:
                    stats["proposals"] += 1
                    item = {
                        "type": "proposal_created",
                        "summary": f"Created proposal: {prop.get('title')}",
                        "timestamp": ts,
                        "id": prop.get("proposal_id"),
                    }

            # Bounties
            elif etype == "BOUNTY_CREATED":
                b = payload.get("bounty", {})
                if b.get("created_by") == wallet_address:
                    stats["bounties_created"] += 1
                    item = {
                        "type": "bounty_created",
                        "summary": f"Created bounty: {b.get('title')}",
                        "timestamp": ts,
                        "amount": b.get("reward_amount"),
                    }
            elif etype == "BOUNTY_CONTRIBUTION_SUBMITTED":
                c = payload.get("contribution", {})
                if c.get("contributor_wallet") == wallet_address:
                    stats["contributions"] += 1
                    item = {
                        "type": "contribution",
                        "summary": f"Contributed to {c.get('bounty_id')}",
                        "timestamp": ts,
                        "ref": c.get("reference"),
                    }

            # Social
            elif etype == "SOCIAL_THREAD_CREATED":
                t = payload.get("thread", {})
                if t.get("created_by") == wallet_address:
                    stats["threads"] += 1
                    item = {
                        "type": "thread_created",
                        "summary": f"Started thread: {t.get('title')}",
                        "timestamp": ts,
                        "id": t.get("thread_id"),
                    }
            elif etype == "SOCIAL_COMMENT_POSTED":
                c = payload.get("comment", {})
                if c.get("author_wallet") == wallet_address:
                    stats["comments"] += 1
                    item = {
                        "type": "comment",
                        "summary": f"Commented on {c.get('thread_id')}",
                        "timestamp": ts,
                        "snippet": c.get("content", "")[:50],
                    }
            elif etype == "SOCIAL_DISPUTE_OPENED":
                d = payload.get("dispute", {})
                if d.get("raised_by") == wallet_address:
                    stats["disputes_raised"] += 1
                    item = {
                        "type": "dispute",
                        "summary": f"Raised dispute on {d.get('target_type')} {d.get('target_id')}",
                        "timestamp": ts,
                        "status": d.get("status"),
                    }

            if item:
                timeline.append(item)

        # Sort desc
        timeline.sort(key=lambda x: x["timestamp"], reverse=True)

        return {"wallet": wallet_address, "stats": stats, "timeline": timeline}
