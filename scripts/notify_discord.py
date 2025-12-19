"""
Discord Notification Helper
Sends pipeline status updates to Discord webhook
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime
import os


class DiscordNotifier:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
        if not self.webhook_url:
            print("⚠️  No Discord webhook URL configured (set DISCORD_WEBHOOK_URL)")
            self.enabled = False
        else:
            self.enabled = True

    def send_pipeline_success(self, commit_sha, branch, tag=None):
        """Send success notification."""
        if not self.enabled:
            return

        title = "✅ Pipeline SUCCESS"
        color = 0x00FF00  # Green

        fields = [
            {"name": "Commit", "value": f"`{commit_sha[:8]}`", "inline": True},
            {"name": "Branch", "value": f"`{branch}`", "inline": True},
        ]

        if tag:
            fields.append({"name": "Tag", "value": f"`{tag}`", "inline": True})

        fields.extend(
            [
                {"name": "Stage A", "value": "✅ Static Checks", "inline": True},
                {"name": "Stage B", "value": "✅ v15 Audit Suite", "inline": True},
                {"name": "Stage C", "value": "✅ Replay & Stress", "inline": True},
                {"name": "Stage D", "value": "✅ Ops Verification", "inline": True},
                {"name": "Stage E", "value": "✅ Testnet Dry-Run", "inline": True},
                {
                    "name": "Status",
                    "value": "**HEAD is deployable to testnet**",
                    "inline": False,
                },
            ]
        )

        self._send_embed(title, color, fields)

    def send_pipeline_failure(self, commit_sha, branch, failed_stages, tag=None):
        """Send failure notification."""
        if not self.enabled:
            return

        title = "❌ Pipeline FAILURE"
        color = 0xFF0000  # Red

        fields = [
            {"name": "Commit", "value": f"`{commit_sha[:8]}`", "inline": True},
            {"name": "Branch", "value": f"`{branch}`", "inline": True},
        ]

        if tag:
            fields.append({"name": "Tag", "value": f"`{tag}`", "inline": True})

        # Add failed stages
        failed_list = "\n".join([f"❌ Stage {s}" for s in failed_stages])
        fields.append({"name": "Failed Stages", "value": failed_list, "inline": False})

        fields.append(
            {
                "name": "Status",
                "value": "**DO NOT DEPLOY - Pipeline failed**",
                "inline": False,
            }
        )

        self._send_embed(title, color, fields)

    def send_testnet_deployment(self, commit_sha, tag, success=True):
        """Send testnet deployment notification."""
        if not self.enabled:
            return

        if success:
            title = "🚀 Testnet Deployment SUCCESS"
            color = 0x0099FF  # Blue
            status = "**Testnet updated successfully**"
        else:
            title = "⚠️ Testnet Deployment FAILED"
            color = 0xFF9900  # Orange
            status = "**Testnet deployment failed - check logs**"

        fields = [
            {"name": "Commit", "value": f"`{commit_sha[:8]}`", "inline": True},
            {"name": "Tag", "value": f"`{tag}`", "inline": True},
            {"name": "Status", "value": status, "inline": False},
        ]

        self._send_embed(title, color, fields)

    def _send_embed(self, title, color, fields):
        """Send Discord embed message."""
        timestamp = datetime.utcnow().isoformat()

        embed = {
            "title": title,
            "color": color,
            "fields": fields,
            "timestamp": timestamp,
            "footer": {"text": "QFS v15 Autonomous Verification"},
        }

        payload = {"embeds": [embed]}

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 204:
                print("✓ Discord notification sent")
            else:
                print(f"⚠️  Discord notification failed: {response.status_code}")
        except Exception as e:
            print(f"⚠️  Discord notification error: {e}")


def main():
    """CLI interface for Discord notifications."""
    import argparse

    parser = argparse.ArgumentParser(description="Send Discord notifications")
    parser.add_argument(
        "--type", choices=["success", "failure", "deployment"], required=True
    )
    parser.add_argument("--commit", required=True)
    parser.add_argument("--branch", default="main")
    parser.add_argument("--tag", default=None)
    parser.add_argument("--failed-stages", nargs="+", default=[])
    parser.add_argument("--deployment-success", action="store_true")

    args = parser.parse_args()

    notifier = DiscordNotifier()

    if args.type == "success":
        notifier.send_pipeline_success(args.commit, args.branch, args.tag)
    elif args.type == "failure":
        notifier.send_pipeline_failure(
            args.commit, args.branch, args.failed_stages, args.tag
        )
    elif args.type == "deployment":
        notifier.send_testnet_deployment(args.commit, args.tag, args.deployment_success)


if __name__ == "__main__":
    main()
