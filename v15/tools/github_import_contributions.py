import logging
import os
import requests
import json
import time
from datetime import datetime

# Adjust import based on where this script runs, assuming from root with -m
from v15.services.evidence_adapter import EvidenceBusAdapter, EvidenceEvent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GitHubImporter")

GITHUB_API_URL = "https://api.github.com"
# For higher rate limits
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def create_contrib_recorded_event(
    repo_owner: str,
    repo_name: str,
    item_type: str,  # "pr" or "issue"
    item_id: int,
    user_handle: str,
    created_at_iso: str,
    url: str,
) -> EvidenceEvent:
    """
    Creates a deterministic CONTRIB_RECORDED event.
    """
    return EvidenceEvent(
        event_type="CONTRIB_RECORDED",
        version=1,
        payload={
            "platform": "github",
            "repo": f"{repo_owner}/{repo_name}",
            "type": item_type,
            "id": item_id,
            "user": user_handle,
            "created_at": created_at_iso,
            "url": url,
            "imported_at": int(time.time()),
            "round_id": "v20-retro-epoch-1",  # Hardcoded for this phase
        },
    )


def fetch_repo_activity(owner: str, repo: str):
    """
    Fetches Pull Requests and Issues from a GitHub repository.
    """
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    adapter = EvidenceBusAdapter()

    # 1. Fetch Pull Requests
    logger.info(f"Fetching PRs for {owner}/{repo}...")
    page = 1
    while True:
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls?state=all&per_page=100&page={page}"
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            logger.error(f"Error fetching PRs: {resp.status_code} {resp.text}")
            break

        items = resp.json()
        if not items:
            break

        for pr in items:
            event = create_contrib_recorded_event(
                repo_owner=owner,
                repo_name=repo,
                item_type="pr",
                item_id=pr["number"],
                user_handle=pr["user"]["login"],
                created_at_iso=pr["created_at"],
                url=pr["html_url"],
            )
            adapter.emit(event)
            logger.info(f"Recorded PR #{pr['number']} by {pr['user']['login']}")

        page += 1

    # 2. Fetch Issues (excluding PRs)
    # Note: GitHub API /issues returns both issues and PRs. We must filter.
    logger.info(f"Fetching Issues for {owner}/{repo}...")
    page = 1
    while True:
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/issues?state=all&per_page=100&page={page}"
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            logger.error(f"Error fetching Issues: {resp.status_code} {resp.text}")
            break

        items = resp.json()
        if not items:
            break

        for issue in items:
            # Skip if it is a PR
            if "pull_request" in issue:
                continue

            event = create_contrib_recorded_event(
                repo_owner=owner,
                repo_name=repo,
                item_type="issue",
                item_id=issue["number"],
                user_handle=issue["user"]["login"],
                created_at_iso=issue["created_at"],
                url=issue["html_url"],
            )
            adapter.emit(event)
            logger.info(
                f"Recorded Issue #{issue['number']} by {issue['user']['login']}"
            )

        page += 1


if __name__ == "__main__":
    # Example usage: python -m v15.tools.github_import_contributions REPO_OWNER REPO_NAME
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m v15.tools.github_import_contributions <owner> <repo>")
        sys.exit(1)

    owner = sys.argv[1]
    repo = sys.argv[2]
    fetch_repo_activity(owner, repo)
