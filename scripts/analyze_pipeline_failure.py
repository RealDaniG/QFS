"""
Direct pipeline failure analysis via GitHub API.
Bypasses artifact download issues.
"""

import subprocess
import json
import sys
import re


def get_failed_jobs(run_id="20505276363"):
    """Get details of failed jobs."""
    try:
        # Get job details for the failed run
        result = subprocess.run(
            ["gh", "run", "view", run_id, "--json", "jobs"],
            capture_output=True,
            text=True,
            check=True,
        )

        data = json.loads(result.stdout)
        failed_jobs = [
            job for job in data.get("jobs", []) if job.get("conclusion") == "failure"
        ]

        return failed_jobs
    except Exception as e:
        print(f"Error: {e}")
        return []


def get_job_logs(job_id):
    """Get logs for a specific job."""
    try:
        # Use simple run + decode manually to handle errors
        result = subprocess.run(
            ["gh", "run", "view", "--job", str(job_id), "--log"],
            capture_output=True,
            check=True,
        )
        return result.stdout.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error getting logs for job {job_id}: {e}")
        return ""


def main():
    print("=" * 60)
    print("PIPELINE FAILURE ANALYSIS")
    print("=" * 60)

    # Optional: fetch latest run ID if default is old
    # But for now hardcoded as per prompt request to analyze specific run
    run_id = "20505276363"

    failed_jobs = get_failed_jobs(run_id)

    if not failed_jobs:
        # Try finding latest run if specific one not found or no failures
        print(f"No failed jobs found for {run_id}. Checking latest run...")
        try:
            latest = subprocess.run(
                ["gh", "run", "list", "--limit", "1", "--json", "databaseId"],
                capture_output=True,
                text=True,
            )
            latest_id = str(json.loads(latest.stdout)[0]["databaseId"])
            print(f"Checking latest run: {latest_id}")
            failed_jobs = get_failed_jobs(latest_id)
        except:
            pass

    if not failed_jobs:
        print("\n✅ No failed jobs found in recent runs.")
        sys.exit(0)

    print(f"\n📋 Found {len(failed_jobs)} failed job(s):\n")

    for job in failed_jobs:
        print(f"Job: {job.get('name')}")
        print(f"Conclusion: {job.get('conclusion')}")
        print(f"ID: {job.get('databaseId')}")
        print("-" * 60)

        # Get logs for this job
        logs = get_job_logs(job.get("databaseId"))

        # Analyze common patterns
        if "ModuleNotFoundError" in logs:
            print("❌ ISSUE: Missing Python module")
            match = re.search(r"ModuleNotFoundError: No module named '(\w+)'", logs)
            if match:
                print(f"   Missing module: {match.group(1)}")
                print(f"   FIX: Add '{match.group(1)}' to requirements.txt")

        elif "FileNotFoundError" in logs:
            print("❌ ISSUE: Missing file")
            match = re.search(r"FileNotFoundError.*'([^']+)'", logs)
            if match:
                print(f"   Missing file: {match.group(1)}")
                print(f"   FIX: Verify file exists in repository")

        elif "ImportError" in logs:
            print("❌ ISSUE: Import error")
            print("   FIX: Check module paths and __init__.py files")

        elif "test" in job.get("name", "").lower() and "FAILED" in logs:
            print("❌ ISSUE: Test failure")
            print("   FIX: Review test logic and fixtures")

        elif "Process completed with exit code 1" in logs:
            # Generic catch, print last lines
            print("❌ ISSUE: Generic Failure")
            print("\nLast 20 lines of log:")
            print(logs[-2000:])

        else:
            print("⚠️  Unknown failure pattern")
            print("\nLast 50 lines of log:")
            print(logs[-2000:])  # Last 2000 chars

        print("\n")


if __name__ == "__main__":
    main()
