"""
Nightly E2E Runner for QFS V13.8

Executes the full suite of operational verification tests:
1. Zero-Mock Compliance Scan
2. Zero-Sim Test Suite
3. Explain-This Integrity Checks
4. AES Signal Verification
5. Performance Benchmarks

Usage: python nightly_e2e.py
"""

import subprocess
import json
import datetime
import sys
import os

# Zero-Sim: Import deterministic time helper
from v13.libs.deterministic_helpers import (
    det_time_isoformat,
    det_time_now,
    ZeroSimAbort,
)


def run_step(name, command):
    print(f"[{det_time_isoformat()}] Running {name}...")
    start = det_time_now()
    try:
        if command[0] == "python":
            cmd = [sys.executable] + command[1:]
        else:
            cmd = command

        result = subprocess.run(cmd, capture_output=True, text=True)
        # Deterministic duration will be 0
        duration = float(det_time_now() - start)

        if result.returncode == 0:
            print(f"✅ {name} PASSED ({duration:.2f}s)")
            return {
                "step": name,
                "status": "PASS",
                "duration": duration,
                "output": result.stdout[:500] + "..."
                if len(result.stdout) > 500
                else result.stdout,
            }
        else:
            print(f"❌ {name} FAILED ({duration:.2f}s)")
            print(result.stderr)
            return {
                "step": name,
                "status": "FAIL",
                "duration": duration,
                "error": result.stderr,
            }
    except Exception as e:
        print(f"❌ {name} CRASHED: {e}")
        return {"step": name, "status": "CRASH", "error": str(e)}


def main():
    print("=== QFS V13.8 NIGHTLY E2E START ===")

    results = []

    # 0. Zero-Sim Suite (Strict Logic Verification)
    results.append(
        run_step("Zero-Sim Logic Suite", ["python", "scripts/run_zero_sim_suite.py"])
    )

    # 1. Zero-Mock Compliance (Static Scan)
    results.append(
        run_step("Zero-Mock Scan", ["python", "scripts/scan_zero_mock_compliance.py"])
    )

    # 2. Audit Integrity Tests
    results.append(
        run_step(
            "Audit Integrity",
            ["python", "-m", "pytest", "tests/test_audit_integrity.py"],
        )
    )

    # 3. Artistic Signal Tests
    results.append(
        run_step(
            "AES Signal Tests",
            ["python", "-m", "pytest", "tests/test_artistic_signal.py"],
        )
    )

    # 4. Performance Tests
    results.append(
        run_step(
            "Performance Benchmarks",
            ["python", "-m", "pytest", "tests/test_explain_this_performance.py"],
        )
    )

    # Generate Evidence
    evidence = {
        "timestamp": det_time_isoformat(),
        "suite": "Nightly E2E V13.8",
        "results": results,
        "overall_status": "PASS"
        if all(r["status"] == "PASS" for r in results)
        else "FAIL",
    }

    # Save evidence
    os.makedirs("evidence/nightly", exist_ok=True)
    filename = "evidence/nightly/nightly_e2e_run.json"

    with open(filename, "w") as f:
        json.dump(evidence, f, indent=2)

    print(f"=== FINISHED. Evidence saved to {filename} ===")

    if evidence["overall_status"] == "FAIL":
        raise ZeroSimAbort(1)


if __name__ == "__main__":
    main()
