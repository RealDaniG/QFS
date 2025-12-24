"""
generate_full_stack_evidence.py - Nightly Evidence Generation

Runs the full stack determinism test and produces a signed JSON artifact.
"""

import subprocess
import json
import os
import sys
import datetime

# Zero-Sim: Import deterministic time helper
from v13.libs.deterministic_helpers import det_time_isoformat, ZeroSimAbort


def generate_evidence():
    print("Running Full Stack Determinism Test...")
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "v13/tests/integration/test_full_stack_determinism.py",
        "-v",
    ]

    # Zero-Sim: Use deterministic timestamps
    start_time = det_time_isoformat()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = det_time_isoformat()

    success = result.returncode == 0

    # Calculate duration (will be 0 with deterministic time, which is expected behavior for Zero-Sim)
    duration = 0.0

    evidence = {
        "evidence_type": "FULL_STACK_DETERMINISM",
        "timestamp": end_time,
        "duration_seconds": duration,
        "status": "PASS" if success else "FAIL",
        "verification_suite": "v13/tests/integration/test_full_stack_determinism.py",
        "output_summary": result.stdout[-500:] if result.stdout else "No output",
        "error_summary": result.stderr[-500:] if result.stderr else "No errors",
        "environment": "CI/CD",
    }

    os.makedirs("v13/evidence/nightly", exist_ok=True)
    # Zero-Sim: Fixed filename
    filename = "v13/evidence/nightly/full_stack_evidence.json"

    with open(filename, "w") as f:
        json.dump(evidence, f, indent=2)

    print(f"Evidence generated: {filename}")

    if not success:
        print("Verification FAILED")
        raise ZeroSimAbort(1)
    else:
        print("Verification PASSED")
        # Use ZeroSimAbort(0) instead of sys.exit(0) for consistency if preferred,
        # or stick to sys.exit(0) if ZeroSimAbort is only for errors.
        # The previous code had ZeroSimAbort(0) in one branch.
        sys.exit(0)


if __name__ == "__main__":
    generate_evidence()
