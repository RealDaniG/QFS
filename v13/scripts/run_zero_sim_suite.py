"""
Zero-Sim Test Suite Runner - QFS V13.8

Executes the subset of tests that must strictly adhere to Zero-Simulation invariants:
- No wall-clock time
- No random floats
- No external I/O
- Deterministic behavior

Targets: v13/tests
"""

import pytest
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class ZeroSimAbort(Exception):
    def __init__(self, code):
        self.code = code
        sys.exit(code)


def main():
    logger.info(">> Running Zero-Sim Test Suite...")
    target_tests = [
        "v13/tests/test_audit_integrity.py",
        "v13/tests/test_artistic_signal.py",
        "v13/tests/test_explain_this_performance.py",
        "v13/ATLAS/src/tests/test_explain_this_e2e.py",
    ]
    valid_targets = []
    for t in sorted(target_tests):
        if os.path.exists(t):
            valid_targets.append(t)
        else:
            logger.warning(f"Warning: Test file {t} not found, skipping.")
    if not valid_targets:
        logger.error("No valid Zero-Sim tests found!")
        sys.exit(1)
    exit_code = pytest.main(["-v"] + valid_targets)
    if exit_code == 0:
        logger.info("[OK] Zero-Sim Suite PASSED")
        sys.exit(0)
    else:
        logger.error("[FAIL] Zero-Sim Suite FAILED")
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
