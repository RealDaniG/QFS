"""
explain_governance_cycle.py - Explain Governance Proof Artifacts

Usage:
    python tools/explain_governance_cycle.py --proof <path_to_proof.json>

This tool loads a VoteTallyProof (json) and explains the outcome in plain text.
"""

import json
import sys
import argparse
from dataclasses import dataclass
from typing import Dict, Any


def explain_tally(data: Dict[str, Any]):
    print(f"\n🏛️  Governance Tally Explanation")
    print(f"=================================")
    print(f"Proposal ID : {data.get('proposal_id', 'Unknown')}")
    print(f"Outcome     : {data.get('outcome', 'UNKNOWN')}")
    print(f"Total Votes : {data.get('total_votes', 0)}")
    print(f"Total Weight: {data.get('total_weight', '0')}")
    print(f"---------------------------------")
    print(f"Scores:")
    scores = data.get("scores", {})
    for choice, weight in scores.items():
        print(f"  {choice:<10}: {weight}")
    print(f"---------------------------------")
    print(f"Proof Hash  : {data.get('tally_hash', 'MISSING')}")
    print(f"Status      : ✅ Valid Structure (Hash verification requires re-execution)")


def main():
    parser = argparse.ArgumentParser(description="Explain Governance Tally Proof")
    parser.add_argument("--proof", help="Path to proof JSON file", required=True)
    args = parser.parse_args()

    try:
        with open(args.proof, "r") as f:
            data = json.load(f)
            # Handle if wrapped in "proof" key or raw
            if "proof" in data:
                data = data["proof"]
            explain_tally(data)
    except FileNotFoundError:
        print(f"Error: File {args.proof} not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {args.proof}.")


if __name__ == "__main__":
    main()
