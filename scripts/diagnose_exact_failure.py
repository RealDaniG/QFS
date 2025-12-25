"""
Direct GitHub Actions failure diagnosis.
Pinpoints exact error in failed workflow.
"""

import subprocess
import json
import sys
import re


def get_workflow_run_details(run_id):
    """Get detailed job information."""
    try:
        result = subprocess.run(
            ["gh", "api", f"/repos/RealDaniG/QFS/actions/runs/{run_id}/jobs"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error fetching run details: {e}")
        return None


def analyze_job_failure(job):
    """Analyze a failed job and extract actionable error."""
    job_name = job.get("name", "Unknown")
    conclusion = job.get("conclusion", "unknown")

    print(f"\n{'=' * 60}")
    print(f"JOB: {job_name}")
    print(f"Status: {conclusion}")
    print(f"{'=' * 60}")

    steps = job.get("steps", [])
    failed_steps = [s for s in steps if s.get("conclusion") == "failure"]

    if not failed_steps:
        print("⚠️  Job failed but no specific step marked as failure")
        return None

    for step in failed_steps:
        step_name = step.get("name")
        print(f"\n❌ FAILED STEP: {step_name}")
        print(f"   Started: {step.get('started_at')}")
        print(f"   Completed: {step.get('completed_at')}")

        # Try to get step logs
        job_id = job.get("id")
        step_number = step.get("number")

        if job_id:
            logs = get_step_logs(job_id)
            if logs:
                error_analysis = extract_error_from_logs(logs, step_name)
                return error_analysis

    return None


def get_step_logs(job_id):
    """Get logs for a specific job."""
    try:
        result = subprocess.run(
            ["gh", "api", f"/repos/RealDaniG/QFS/actions/jobs/{job_id}/logs"],
            capture_output=True,
            # Handle binary data carefully; API returns raw logs
            check=True,
        )
        # Decode manually
        return result.stdout.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"   Could not fetch logs: {e}")
        return None


def extract_error_from_logs(logs, step_name):
    """Extract actionable error from logs."""

    error_patterns = [
        {
            "pattern": r"ModuleNotFoundError: No module named '([^']+)'",
            "category": "MISSING_MODULE",
            "fix_template": "Add {module} to requirements.txt",
        },
        {
            "pattern": r"FileNotFoundError.*'([^']+)'",
            "category": "MISSING_FILE",
            "fix_template": "Create or verify path: {file}",
        },
        {
            "pattern": r"ImportError: cannot import name '([^']+)' from '([^']+)'",
            "category": "IMPORT_ERROR",
            "fix_template": "Fix import in {module}: {name} not found",
        },
        {
            "pattern": r"AttributeError: module '([^']+)' has no attribute '([^']+)'",
            "category": "ATTRIBUTE_ERROR",
            "fix_template": "Module {module} missing attribute {attr}",
        },
        {
            "pattern": r"FAILED.*AssertionError: (.*)",
            "category": "TEST_FAILURE",
            "fix_template": "Test assertion failed: {message}",
        },
        {
            "pattern": r"pylint.*rated at ([\d.]+)/10",
            "category": "LINT_FAILURE",
            "fix_template": "Pylint score {score}/10 below threshold",
        },
        {
            "pattern": r"mypy.*error:",
            "category": "TYPE_ERROR",
            "fix_template": "Type checking failed - see mypy errors",
        },
    ]

    errors_found = []

    for pattern_def in error_patterns:
        matches = re.finditer(pattern_def["pattern"], logs, re.MULTILINE)
        for match in matches:
            error_info = {
                "category": pattern_def["category"],
                "step": step_name,
                "pattern": pattern_def["pattern"],
                "match": match.group(0),
                "groups": match.groups(),
            }

            # Generate fix suggestion
            if pattern_def["category"] == "MISSING_MODULE":
                error_info["fix"] = f"Add '{match.group(1)}' to v15/requirements.txt"
                error_info["module"] = match.group(1)

            elif pattern_def["category"] == "MISSING_FILE":
                error_info["fix"] = f"Ensure file exists: {match.group(1)}"
                error_info["file"] = match.group(1)

            elif pattern_def["category"] == "IMPORT_ERROR":
                error_info["fix"] = (
                    f"Fix import: cannot import '{match.group(1)}' from '{match.group(2)}'"
                )
                error_info["name"] = match.group(1)
                error_info["module"] = match.group(2)

            elif pattern_def["category"] == "LINT_FAILURE":
                error_info["fix"] = f"Fix pylint issues (score: {match.group(1)}/10)"

            else:
                error_info["fix"] = pattern_def["fix_template"]

            errors_found.append(error_info)

    # Extract relevant log context if no pattern matched but failure happened
    if not errors_found and logs:
        # Print last 20 lines as fallback
        print("\n   [LOG SNIPPET (LAST 20 LINES)]")
        print(logs[-1000:] if len(logs) > 1000 else logs)

    # Extract relevant log context
    if errors_found:
        print(f"\n🔍 ERRORS DETECTED ({len(errors_found)}):")
        for i, err in enumerate(errors_found, 1):
            print(f"\n   Error #{i}:")
            print(f"   Category: {err['category']}")
            print(f"   Match: {err['match'][:100]}...")
            print(f"   Fix: {err['fix']}")

    return errors_found


def generate_fix_script(errors):
    """Generate automated fix script based on errors."""

    if not errors:
        return None

    fixes = []

    for err in errors:
        if err["category"] == "MISSING_MODULE":
            fixes.append(
                {
                    "type": "add_dependency",
                    "module": err.get("module"),
                    "file": "v15/requirements.txt",
                }
            )

        elif err["category"] == "MISSING_FILE":
            fixes.append({"type": "create_file", "path": err.get("file")})

        elif err["category"] == "IMPORT_ERROR":
            fixes.append(
                {
                    "type": "fix_import",
                    "module": err.get("module"),
                    "name": err.get("name"),
                }
            )

    return fixes


def main():
    if len(sys.argv) < 2:
        print("Usage: python diagnose_exact_failure.py <run_id>")
        print("\nTrying latest run...")
        # Try to find latest failed run
        try:
            runs = subprocess.run(
                [
                    "gh",
                    "run",
                    "list",
                    "--workflow=v20_auth_pipeline.yml",
                    "--limit=1",
                    "--json",
                    "databaseId",
                ],
                capture_output=True,
                text=True,
            ).stdout
            run_id = str(json.loads(runs)[0]["databaseId"])
        except:
            run_id = "20505506788"  # Fallback
    else:
        run_id = sys.argv[1]

    print("=" * 60)
    print(f"DIAGNOSING RUN #{run_id}")
    print("=" * 60)

    run_details = get_workflow_run_details(run_id)

    if not run_details:
        print("❌ Could not fetch run details")
        sys.exit(1)

    jobs = run_details.get("jobs", [])
    failed_jobs = [j for j in jobs if j.get("conclusion") == "failure"]

    if not failed_jobs:
        print("✅ No failed jobs found in this run.")
        sys.exit(0)

    print(f"\n📊 Found {len(failed_jobs)} failed job(s)")

    all_errors = []
    for job in failed_jobs:
        errors = analyze_job_failure(job)
        if errors:
            all_errors.extend(errors)

    if all_errors:
        print("\n" + "=" * 60)
        print("REMEDIATION PLAN")
        print("=" * 60)

        fixes = generate_fix_script(all_errors)

        if fixes:
            print("\nAutomated fixes available:")
            for fix in fixes:
                print(f"  - {fix['type']}: {fix}")

        # Save to file for processing
        with open("pipeline_diagnosis.json", "w") as f:
            json.dump(
                {"run_id": run_id, "errors": all_errors, "fixes": fixes}, f, indent=2
            )

        print(f"\n💾 Diagnosis saved to: pipeline_diagnosis.json")
    else:
        print("\n⚠️  No specific errors detected. Manual review required.")


if __name__ == "__main__":
    main()
