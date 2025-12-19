"""
test_release_candidate.py - v15 Release Candidate Validation Suite

Purpose:
Aggregates all critical autonomous verification tests for the v15 Release.
Must pass 100% for the release to be considered "Green".

Includes:
1. Governance Replay (Bit-for-Bit Determinism)
2. Stage 6 Simulation (Triggers, Execution Wiring, Coherence)
"""

import unittest
import sys
import os

# Robust Path Setup
import os
import sys

# Get the absolute path to the project root (4 levels up from this file)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import Test Suites (Safe now that path is fixed)
try:
    from v15.tests.autonomous.test_governance_replay import TestGovernanceReplay
    from v15.tests.autonomous.test_stage_6_simulation import TestStage6Simulation
    from v15.atlas.governance.tests.test_proposal_engine import TestProposalEngineV15
except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    print(f"sys.path: {sys.path}")
    sys.exit(1)


def suite():
    """Aggregates release tests."""
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()

    # 1. Core Logic Tests
    test_suite.addTest(loader.loadTestsFromTestCase(TestProposalEngineV15))

    # 2. Replay Tests (Determinism)
    test_suite.addTest(loader.loadTestsFromTestCase(TestGovernanceReplay))

    # 3. Integration Simulations (Wiring)
    test_suite.addTest(loader.loadTestsFromTestCase(TestStage6Simulation))

    return test_suite


if __name__ == "__main__":
    import io

    # Capture output to buffer
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)

    print("\n[v15 RELEASE CANDIDATE VALIDATION]\n" + "=" * 40)
    result = runner.run(suite())

    # Write full output to log file for agent debugging
    output = stream.getvalue()
    print(output)  # Still print to stdout

    with open("rc_failure_log.txt", "w") as f:
        f.write(output)
        if not result.wasSuccessful():
            f.write("\n\nFAILURES/ERRORS:\n")
            for failure in result.failures:
                f.write(str(failure) + "\n")
            for error in result.errors:
                f.write(str(error) + "\n")

    if result.wasSuccessful():
        print("\n\n✅ v15 RELEASE CANDIDATE: APPROVED")
        sys.exit(0)
    else:
        print("\n\n❌ v15 RELEASE CANDIDATE: FAILED")
        sys.exit(1)
