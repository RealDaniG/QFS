"""
QFS × ATLAS Static Analysis Tool
Enforces Type Safety Hardening (Track B)
"""

import sys
import subprocess
from pathlib import Path

ROOTDIR = Path(__file__).resolve().parents[2]
MYPY_CONFIG = ROOTDIR / "mypy.ini"


def run_type_check() -> int:
    """Execute MyPy with strict configuration"""
    print("=" * 60)
    print("[SEARCH] QFS STATIC ANALYSIS: TYPE SAFETY CHECK")
    print("=" * 60)

    # Target directories for hardening (Track B scope)
    targets = ["v13/libs", "v13/atlas", "v13/policy/bounties"]

    cmd = [sys.executable, "-m", "mypy", "--config-file", str(MYPY_CONFIG), *targets]

    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=str(ROOTDIR),
        capture_output=False,  # Stream to stdout/stderr
    )

    print("=" * 60)
    if result.returncode == 0:
        print("[PASS] TYPE SAFETY CHECK: PASSED")
    else:
        print(f"[FAIL] TYPE SAFETY CHECK: FAILED (Exit Code {result.returncode})")
    print("=" * 60)

    return result.returncode


if __name__ == "__main__":
    sys.exit(run_type_check())
