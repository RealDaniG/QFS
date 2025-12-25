"""
Automated CI failure triage.
Monitors GitHub Actions and suggests fixes.
"""

import os
import sys
import json
import subprocess
from typing import List, Dict


def get_latest_workflow_run():
    """Get status of latest workflow run."""
    try:
        result = subprocess.run(
            [
                "gh",
                "run",
                "list",
                "--workflow=v20_auth_pipeline.yml",
                "--limit=1",
                "--json=status,conclusion,databaseId",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        runs = json.loads(result.stdout)
        if runs:
            return runs[0]
        return None
    except Exception as e:
        print(f"Error fetching workflow run: {e}")
        return None


def download_logs(run_id: int):
    """Download logs for a workflow run."""
    try:
        subprocess.run(["gh", "run", "download", str(run_id)], check=True)
        print(f"✅ Downloaded logs for run {run_id}")
    except Exception as e:
        print(f"❌ Failed to download logs: {e}")


def analyze_failure_patterns(logs_dir: str) -> List[Dict]:
    """Analyze log files for common failure patterns."""

    patterns = [
        {
            "pattern": "ModuleNotFoundError",
            "category": "MISSING_DEPENDENCY",
            "fix": "Add missing module to requirements.txt",
        },
        {
            "pattern": "FileNotFoundError",
            "category": "MISSING_FILE",
            "fix": "Verify file exists in repository",
        },
        {
            "pattern": "MUTATION_STATE",
            "category": "ZERO_SIM_VIOLATION",
            "fix": "Apply whitelisted pattern or refactor",
        },
        {
            "pattern": "AssertionError",
            "category": "TEST_FAILURE",
            "fix": "Review test logic and data fixtures",
        },
        {
            "pattern": "ImportError",
            "category": "IMPORT_ERROR",
            "fix": "Check import paths and __init__.py files",
        },
        {
            "pattern": "UnicodeEncodeError",
            "category": "ENCODING_ERROR",
            "fix": "Set PYTHONIOENCODING=utf-8 or fix character output",
        },
    ]

    findings = []

    # Scan log files
    for root, dirs, files in os.walk(logs_dir):
        for file in files:
            if file.endswith(".txt"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                        for pattern_def in patterns:
                            if pattern_def["pattern"] in content:
                                findings.append(
                                    {
                                        "file": file,
                                        "category": pattern_def["category"],
                                        "pattern": pattern_def["pattern"],
                                        "fix": pattern_def["fix"],
                                    }
                                )
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

    return findings


def generate_triage_report(findings: List[Dict]):
    """Generate human-readable triage report."""

    print("\n" + "=" * 60)
    print("CI FAILURE TRIAGE REPORT")
    print("=" * 60)

    if not findings:
        print("\n✅ No common failure patterns detected")
        print("\nManual review required. Check logs for specific errors.")
        return

    # Group by category
    by_category = {}
    for finding in findings:
        cat = finding["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(finding)

    for category, items in by_category.items():
        print(f"\n{category} ({len(items)} occurrences)")
        print("-" * 60)

        for item in items:
            print(f"  File: {item['file']}")
            print(f"  Pattern: {item['pattern']}")
            print(f"  Fix: {item['fix']}")
            print()


def main():
    print("Checking latest workflow run...")

    run = get_latest_workflow_run()

    if not run:
        print("❌ No workflow runs found or 'gh' CLI not authenticated/installed.")
        print(
            "Please ensure you have GitHub CLI installed and authenticated (gh auth login)."
        )
        sys.exit(1)

    print(f"\nRun ID: {run['databaseId']}")
    print(f"Status: {run['status']}")
    print(f"Conclusion: {run.get('conclusion', 'N/A')}")

    if run["conclusion"] == "success":
        print("\n✅ Latest workflow run succeeded!")
        sys.exit(0)

    if run["status"] != "completed":
        print("\n⏳ Workflow still running. Wait for completion.")
        sys.exit(0)

    # Download and analyze logs
    print("\nDownloading logs for analysis...")
    download_logs(run["databaseId"])

    print("\nAnalyzing failure patterns...")
    findings = analyze_failure_patterns(f".")

    generate_triage_report(findings)


if __name__ == "__main__":
    main()
