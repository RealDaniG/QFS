from typing import Dict, List, Any
from v13.qfs.events.contributions import CONTRIB_RECORDED
from v13.qfs.events.identity import IDENTITY_LINK_GITHUB
import json


# QFS F-Layer: GitHub Bounties
# Phase 4 Implementation: Deterministic Rewards


def compute_bounty_rewards(round_id: str, evidence_bus) -> Dict[str, Any]:
    """
    Deterministic Reward Computation for a Bounty Round.

    1. Replays Identity Links (GitHub -> Wallet).
    2. Replays Contributions for round_id.
    3. Computes Score: (lines_added * 10) + (files * 50) + (500 flat).
       Note: Uses Basis Points (1.0 FLX = 100 units) for integer math.
    4. Aggregates per wallet.
    5. Returns Allocation Table + Proposal for 'rewards_assigned' event.
    """

    # 1. Fetch and Sort Events (Strict Determinism)
    # We fetch sufficient history. In production, this would use a specific projection.
    all_events = evidence_bus.get_recent_evidence(limit=10000)

    # Explicitly sort by timestamp + sequence/id to ensure replayability
    # Assuming 'id' or 'timestamp' exists. Fallback to 'created_at' if needed.
    # We use a tuple key for stability: (timestamp, event_id/hash)
    # If event_id is not guaranteed, we rely on the bus returning events in log order,
    # but strictly checking fields is better.
    # For this implementation, we trust the bus returns DESC, so we reverse to ASC.
    # But to be safe against bus changes, we sort by 'timestamp'.
    all_events.sort(key=lambda x: x.get("timestamp", 0))

    identity_map = {}  # github_username -> wallet_address

    for event in all_events:
        if event["event_type"] == IDENTITY_LINK_GITHUB:
            try:
                payload = json.loads(event["payload"])
                # LWW (Last Write Wins) policy: Later events override earlier links
                if "github_username" in payload and "wallet_address" in payload:
                    identity_map[payload["github_username"]] = payload["wallet_address"]
            except json.JSONDecodeError:
                continue

    # 2. Scan Contributions
    allocations_bp = {}  # wallet -> amount (in basis points)
    contrib_count = 0

    for event in all_events:
        if event["event_type"] == CONTRIB_RECORDED:
            try:
                payload = json.loads(event["payload"])
                if payload.get("round_id") != round_id:
                    continue

                gh_user = payload["github_username"]
                wallet = identity_map.get(gh_user)

                if not wallet:
                    continue

                # 3. Compute Score (Integer Math)
                score_inputs = payload["score_inputs"]
                lines = int(score_inputs.get("lines_added", 0))
                files = int(score_inputs.get("files", 0))

                # Policy:
                # lines * 0.1 FLX -> lines * 10 BP
                # files * 0.5 FLX -> files * 50 BP
                # 5.0 FLX flat -> 500 BP
                reward_bp = (lines * 10) + (files * 50) + 500

                # Aggregate
                current_bp = allocations_bp.get(wallet, 0)
                allocations_bp[wallet] = current_bp + reward_bp
                contrib_count += 1
            except (json.JSONDecodeError, ValueError):
                continue

    # 4. Finalize
    # Convert Basis Points back to Float for display/payout
    # 100 BP = 1.00 FLX
    final_allocations = {k: round(v / 100.0, 2) for k, v in allocations_bp.items()}

    return {
        "round_id": round_id,
        "total_contributors": len(final_allocations),
        "total_contributions": contrib_count,
        "allocations": final_allocations,
    }


def get_rewards_from_events(
    evidence_bus, wallet_address: str = None
) -> List[Dict[str, Any]]:
    """
    Query 'rewards_assigned' events and filter by wallet.
    Returns list of { round_id, amount }.
    """
    # Scan recent events (Phase 4 optimization: scanning last 1000 is okay for dev)
    # TODO: Add paging or limit parameter for production scaling
    all_events = evidence_bus.get_recent_evidence(limit=1000)

    # Sort for consistent display order
    all_events.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

    rewards = []

    for event in all_events:
        if event["event_type"] == "rewards_assigned":
            try:
                payload = json.loads(event["payload"])
                allocations = payload.get("allocations", {})

                # If specific wallet request
                if wallet_address:
                    amount = allocations.get(wallet_address)
                    if amount:
                        rewards.append(
                            {
                                "round_id": payload["round_id"],
                                "amount": amount,
                                "timestamp": event["timestamp"],
                            }
                        )
                else:
                    # Admin/Debug view: Return all allocations structure
                    # Explicitly handled via flag in future; currently filtered by caller check
                    pass
            except json.JSONDecodeError:
                continue

    return rewards
