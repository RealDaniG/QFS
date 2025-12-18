import sys
import os
import subprocess
import json
import hashlib
from v13.libs.deterministic_helpers import (
    det_time_isoformat,
    det_time_now,
    det_perf_counter,
)

# Configuration
TEST_SUITES = [
    {
        "name": "QFS Core Determinism",
        "command": [
            sys.executable,
            "-m",
            "pytest",
            "v13/tests/deterministic/test_value_node_replay_determinism.py",
            "-v",
        ],
        "critical": True,
    },
    {
        "name": "Humor Slice Zero-Sim",
        "command": [
            sys.executable,
            "-m",
            "pytest",
            "v13/tests/test_humor_deterministic_replay.py",
            "-v",
        ],
        "critical": True,
    },
    {
        "name": "Value-Node Replay & Explainability",
        "command": [
            sys.executable,
            "-m",
            "pytest",
            "v13/tests/unit/test_value_node_replay_explanation.py",
            "-v",
        ],
        "critical": True,
    },
    {
        "name": "ATLAS Explanation E2E",
        "command": [
            sys.executable,
            "-m",
            "pytest",
            "v13/ATLAS/src/tests/test_explain_this_e2e.py",
            "-v",
        ],
        "critical": True,
    },
    {
        "name": "Session Management Tests",
        "command": [sys.executable, "-m", "pytest", "v13/tests/sessions/", "-v"],
        "critical": True,
    },
    {
        "name": "PQC Provider Consistency",
        "command": [
            sys.executable,
            "-m",
            "pytest",
            "v13/tests/unit/test_pqc_provider_consistency_shim.py",
            "-v",
        ],
        "critical": True,
    },
    {
        "name": "HD Derivation",
        "command": [
            sys.executable,
            "-m",
            "pytest",
            "v13/tests/unit/test_hd_derivation.py",
            "-v",
        ],
        "critical": True,
    },
]

EVIDENCE_PATH = "v13/evidence/zero_sim/zero_sim_suite_status.json"


def calculate_file_hash(filepath):
    """Calculates SHA-256 hash of a file."""
    if not os.path.exists(filepath):
        return None
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def run_suite():
    results = {
        "timestamp": det_time_isoformat(),
        "suites": [],
        "overall_status": "PASS",
    }

    print("🚀 Starting Zero-Simulation Verification Suite...")

    for suite in TEST_SUITES:
        print(f"\n▶ Running: {suite['name']}")

        start_time = det_time_now()
        try:
            # Note: We run directly, assuming cwd is repo root
            result = subprocess.run(suite["command"], capture_output=True, text=True)
            duration = det_perf_counter() - start_time

            status = "PASS" if result.returncode == 0 else "FAIL"
            if status == "FAIL" and suite["critical"]:
                results["overall_status"] = "FAIL"

            suite_result = {
                "name": suite["name"],
                "status": status,
                "duration_seconds": duration,
                "output_tail": result.stdout[-500:]
                if result.stdout
                else result.stderr[-500:],
            }
            results["suites"].append(suite_result)

            if status == "PASS":
                print(f"✅ PASS ({duration:.2f}s)")
            else:
                print(f"❌ FAIL ({duration:.2f}s)")
                print(result.stderr)

        except Exception as e:
            print(f"❌ ERROR: {e}")
            results["suites"].append(
                {"name": suite["name"], "status": "ERROR", "error": str(e)}
            )
            results["overall_status"] = "FAIL"

    # Ensure evidence directory exists
    os.makedirs(os.path.dirname(EVIDENCE_PATH), exist_ok=True)

    with open(EVIDENCE_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nExample Verified: {results['overall_status']}")
    print(f"Evidence saved to: {EVIDENCE_PATH}")

    if results["overall_status"] != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    # Check if we are in the right directory
    if not os.path.exists("v13/ATLAS"):
        print("Error: Must run from repository root (where v13/ folder is located).")
        sys.exit(1)

    run_suite()
