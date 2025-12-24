#!/usr/bin/env python3
"""
Discord Notification Script (Stub)

Deterministic, side-effect-free stub for CI notifications.
In production, this would send webhook notifications to Discord.
For now, it logs to stdout for CI visibility.
"""

import argparse
import json
import sys
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description="Send Discord notification")
    parser.add_argument(
        "--type",
        required=True,
        choices=["success", "failure"],
        help="Notification type",
    )
    parser.add_argument("--commit", required=True, help="Commit SHA")
    parser.add_argument("--branch", required=True, help="Branch name")
    parser.add_argument("--tag", default="", help="Tag name (if applicable)")
    parser.add_argument(
        "--failed-stages", default="", help="Failed stages (for failure notifications)"
    )

    args = parser.parse_args()

    # Construct notification payload
    payload = {
        "type": args.type,
        "commit": args.commit[:8],  # Short SHA
        "branch": args.branch,
        "tag": args.tag,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    if args.type == "failure" and args.failed_stages:
        payload["failed_stages"] = args.failed_stages.strip()

    # Log to stdout (deterministic, no external I/O)
    print(f"[DISCORD NOTIFICATION STUB]")
    print(json.dumps(payload, indent=2))

    # In production, this would send to Discord webhook:
    # import os
    # import requests
    # webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    # if webhook_url:
    #     requests.post(webhook_url, json={"content": format_message(payload)})

    print(f"✅ Discord notification logged (type={args.type})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
