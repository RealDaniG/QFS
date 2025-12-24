import argparse
import json
import hashlib
import sys
import os
from typing import List, Dict, Any

# Ensure we can import from v13 if needed, though this is a standalone tool
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))


def deterministic_hash(data: Any) -> str:
    """Produces a deterministic hash of the JSON-dumped data."""
    serialized = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def fetch_contributions(
    repo: str, username: str, token: str = None
) -> List[Dict[str, Any]]:
    """
    Fetches contributions for a user in a repo.
    MOCKED FOR NOW.
    In a real implementation, this would call GitHub API.
    """
    # TODO: Implement actual GitHub API calls using requests
    # url = f"https://api.github.com/repos/{repo}/commits?author={username}"
    # ...

    print(f"Fetching contributions for {username} in {repo}...")

    # Returning mock data for structural verification
    return [
        {
            "contribution_id": "mock_sha:1",
            "github_username": username,
            "pr_number": 123,
            "lines_added": 10,
            "lines_deleted": 2,
            "files_changed": ["README.md"],
            "component_tag": "v13/docs",
            "weight_inputs": {"bounty_eligible": True},
        }
    ]


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic GitHub Contribution Importer"
    )
    parser.add_argument(
        "--repo", default="RealDaniG/QFS", help="GitHub repository (owner/name)"
    )
    parser.add_argument(
        "--username", required=True, help="GitHub username to filter by"
    )
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--token", help="GitHub Personal Access Token (optional)")

    args = parser.parse_args()

    contributions = fetch_contributions(args.repo, args.username, args.token)

    # Deterministic Sort
    contributions.sort(key=lambda x: x["contribution_id"])

    # Create Ledger
    ledger = {
        "repo": args.repo,
        "username": args.username,
        "generated_at_sequence": 0,  # Placeholder for logical time
        "importer_version": "0.1.0",
        "contributions": contributions,
    }

    # Calculate hash of the content
    ledger["ledger_hash"] = deterministic_hash(ledger)

    output_json = json.dumps(ledger, indent=2, sort_keys=True)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_json)
        print(f"Ledger written to {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
