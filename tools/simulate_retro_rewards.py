import sys
import os
import json
import argparse

# Add path to v13
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from v13.atlas.backend.lib.dependencies import evidence_bus
from v13.qfs.f_layer.bounty_github import compute_bounty_rewards
from v13.qfs.events.contributions import CONTRIB_RECORDED


def main():
    parser = argparse.ArgumentParser(description="Simulate Retroactive Rewards")
    parser.add_argument("--round-id", required=True, help="Bounty Round ID")
    parser.add_argument("--output", help="Output JSON file for allocations")
    parser.add_argument(
        "--emit", action="store_true", help="Emit rewards_assigned event to EvidenceBus"
    )

    args = parser.parse_args()

    print(f"Computing rewards for round: {args.round_id}...")

    # 1. Compute
    result = compute_bounty_rewards(args.round_id, evidence_bus)

    # 2. Output
    print(json.dumps(result, indent=2))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Allocations saved to {args.output}")

    # 3. Emit (Optional Phase 4)
    if args.emit:
        event_hash = evidence_bus.log_evidence(
            event_type="rewards_assigned",
            actor_wallet="0x0000000000000000000000000000000000000000",
            payload=result,
        )
        print(f"Emit Success! Evidence Hash: {event_hash}")


if __name__ == "__main__":
    main()
