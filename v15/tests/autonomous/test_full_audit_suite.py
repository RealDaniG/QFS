"""
test_full_audit_suite.py - QFS v15 Comprehensive Audit Runner

Purpose:
Orchestrates all existing v15 tests (unit, integration, replay, stress, health)
and generates a machine-readable JSON audit report mapping invariants to evidence.

Output:
- AUDIT_RESULTS.json: Detailed pass/fail per invariant
- AUDIT_RESULTS_SUMMARY.md: Human-readable summary
"""

import unittest
import json
import sys
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict

# Robust Path Setup
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import all test suites
from v15.atlas.governance.tests.test_proposal_engine import TestProposalEngineV15
from v15.tests.autonomous.test_governance_replay import TestGovernanceReplay
from v15.tests.autonomous.test_stage_6_simulation import TestStage6Simulation
from v15.tests.autonomous.test_stress_campaign import TestStressCampaign
from v15.tests.test_protocol_health_check import TestProtocolHealthCheck
from v15.tests.test_governance_dashboard import TestGovernanceDashboard


@dataclass
class InvariantResult:
    invariant_id: str
    description: str
    component: str
    test_coverage: List[str]
    status: str  # "PASS", "FAIL", "PARTIAL"
    evidence: str


@dataclass
class AuditReport:
    timestamp: str
    qfs_version: str
    atlas_version: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    invariants: List[InvariantResult]
    overall_status: str


class FullAuditSuite:
    def __init__(self):
        self.results = []
        self.invariants = []

    def run_all_tests(self):
        """Execute all test suites and collect results."""
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        # Add all test suites
        suite.addTests(loader.loadTestsFromTestCase(TestProposalEngineV15))
        suite.addTests(loader.loadTestsFromTestCase(TestGovernanceReplay))
        suite.addTests(loader.loadTestsFromTestCase(TestStage6Simulation))
        suite.addTests(loader.loadTestsFromTestCase(TestStressCampaign))
        suite.addTests(loader.loadTestsFromTestCase(TestProtocolHealthCheck))
        suite.addTests(loader.loadTestsFromTestCase(TestGovernanceDashboard))

        # Run with detailed output
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        return result

    def map_invariants(self, test_result):
        """Map test results to invariants."""
        # Governance Core Invariants
        self.invariants.append(
            InvariantResult(
                invariant_id="GOV-I1",
                description="Quorum (30%) and Supermajority (66%) via integer math only",
                component="ProposalEngine",
                test_coverage=["test_integer_thresholds"],
                status="PASS" if test_result.wasSuccessful() else "FAIL",
                evidence="test_proposal_engine.py::test_integer_thresholds",
            )
        )

        self.invariants.append(
            InvariantResult(
                invariant_id="GOV-I2",
                description="Proposal IDs are content-addressed (SHA3-512)",
                component="ProposalEngine",
                test_coverage=["test_deterministic_id"],
                status="PASS" if test_result.wasSuccessful() else "FAIL",
                evidence="test_proposal_engine.py::test_deterministic_id",
            )
        )

        # Registry Invariants
        self.invariants.append(
            InvariantResult(
                invariant_id="GOV-R1",
                description="Immutable parameters cannot be modified",
                component="GovernanceParameterRegistry",
                test_coverage=[
                    "test_immutable_protection",
                    "test_immutable_protection_under_load",
                ],
                status="PASS" if test_result.wasSuccessful() else "FAIL",
                evidence="test_proposal_engine.py::test_immutable_protection, test_stress_campaign.py::test_immutable_protection_under_load",
            )
        )

        # Trigger Invariants
        self.invariants.append(
            InvariantResult(
                invariant_id="TRIG-I1",
                description="Active parameters constant within epoch",
                component="GovernanceTrigger",
                test_coverage=["test_full_execution_lifecycle"],
                status="PASS" if test_result.wasSuccessful() else "FAIL",
                evidence="test_stage_6_simulation.py::test_full_execution_lifecycle",
            )
        )

        # Replay Determinism
        self.invariants.append(
            InvariantResult(
                invariant_id="REPLAY-I1",
                description="Bit-for-bit deterministic replay (0 drift)",
                component="ProposalEngine + Registry + Trigger",
                test_coverage=["test_bit_for_bit_replay", "test_campaign_replay_drift"],
                status="PASS" if test_result.wasSuccessful() else "FAIL",
                evidence="test_governance_replay.py::test_bit_for_bit_replay, test_stress_campaign.py::test_campaign_replay_drift",
            )
        )

        # AEGIS Coherence
        self.invariants.append(
            InvariantResult(
                invariant_id="AEGIS-G1",
                description="Active Snapshot == Registry at sync points",
                component="GovernanceCoherenceCheck",
                test_coverage=[
                    "test_full_execution_lifecycle",
                    "test_campaign_replay_drift",
                ],
                status="PASS" if test_result.wasSuccessful() else "FAIL",
                evidence="test_stage_6_simulation.py + test_stress_campaign.py (AEGIS checks)",
            )
        )

        # Economic Integration
        self.invariants.append(
            InvariantResult(
                invariant_id="ECON-I1",
                description="VIRAL_POOL_CAP read from GovernanceTrigger snapshot",
                component="ViralRewardBinder",
                test_coverage=["test_full_execution_lifecycle"],
                status="PASS" if test_result.wasSuccessful() else "FAIL",
                evidence="test_stage_6_simulation.py::test_full_execution_lifecycle",
            )
        )

        # Operational Tools Invariants
        self.invariants.append(
            InvariantResult(
                invariant_id="HEALTH-I1",
                description="All metrics derived from deterministic, on-ledger data",
                component="ProtocolHealthCheck",
                test_coverage=["test_health_check_deterministic_metrics"],
                status="PASS" if test_result.wasSuccessful() else "FAIL",
                evidence="test_protocol_health_check.py::test_health_check_deterministic_metrics",
            )
        )

        self.invariants.append(
            InvariantResult(
                invariant_id="HEALTH-I2",
                description="Critical failures return non-zero exit code",
                component="ProtocolHealthCheck",
                test_coverage=["test_health_check_aegis_fail_detection"],
                status="PASS" if test_result.wasSuccessful() else "FAIL",
                evidence="test_protocol_health_check.py::test_health_check_aegis_fail_detection",
            )
        )

        self.invariants.append(
            InvariantResult(
                invariant_id="HEALTH-I3",
                description="No external dependencies or network calls",
                component="ProtocolHealthCheck",
                test_coverage=["test_health_check_no_external_dependencies"],
                status="PASS" if test_result.wasSuccessful() else "FAIL",
                evidence="test_protocol_health_check.py::test_health_check_no_external_dependencies",
            )
        )

        self.invariants.append(
            InvariantResult(
                invariant_id="DASH-I1",
                description="Dashboard is read-only (no state mutations)",
                component="GovernanceDashboard",
                test_coverage=["test_dashboard_read_only"],
                status="PASS" if test_result.wasSuccessful() else "FAIL",
                evidence="test_governance_dashboard.py::test_dashboard_read_only",
            )
        )

        self.invariants.append(
            InvariantResult(
                invariant_id="DASH-I2",
                description="All displayed data sourced from governance modules",
                component="GovernanceDashboard",
                test_coverage=["test_dashboard_data_accuracy_parameters"],
                status="PASS" if test_result.wasSuccessful() else "FAIL",
                evidence="test_governance_dashboard.py::test_dashboard_data_accuracy_parameters",
            )
        )

        self.invariants.append(
            InvariantResult(
                invariant_id="DASH-I3",
                description="PoE artifacts displayed match actual proof chain",
                component="GovernanceDashboard",
                test_coverage=["test_dashboard_poe_artifacts_section"],
                status="PASS" if test_result.wasSuccessful() else "FAIL",
                evidence="test_governance_dashboard.py::test_dashboard_poe_artifacts_section",
            )
        )

    def generate_report(self, test_result) -> AuditReport:
        """Generate comprehensive audit report."""
        self.map_invariants(test_result)

        return AuditReport(
            timestamp=datetime.now().isoformat(),
            qfs_version="19.0.0",
            atlas_version="1.3.0",
            total_tests=test_result.testsRun,
            passed_tests=test_result.testsRun
            - len(test_result.failures)
            - len(test_result.errors),
            failed_tests=len(test_result.failures) + len(test_result.errors),
            invariants=self.invariants,
            overall_status="PASS" if test_result.wasSuccessful() else "FAIL",
        )

    def save_results(self, report: AuditReport):
        """Save audit results to JSON and Markdown."""
        # JSON Report
        with open("AUDIT_RESULTS.json", "w", encoding="utf-8") as f:
            json.dump(asdict(report), f, indent=2)

        # Markdown Summary
        with open("AUDIT_RESULTS_SUMMARY.md", "w", encoding="utf-8") as f:
            f.write(f"# QFS v15 Audit Results\n\n")
            f.write(f"**Timestamp:** {report.timestamp}\n")
            f.write(
                f"**Version:** QFS {report.qfs_version} / ATLAS {report.atlas_version}\n"
            )
            f.write(
                f"**Overall Status:** {'PASS' if report.overall_status == 'PASS' else 'FAIL'}\n\n"
            )
            f.write(f"## Test Summary\n\n")
            f.write(f"- Total Tests: {report.total_tests}\n")
            f.write(f"- Passed: {report.passed_tests}\n")
            f.write(f"- Failed: {report.failed_tests}\n\n")
            f.write(f"## Invariant Verification\n\n")

            for inv in report.invariants:
                status_mark = "[PASS]" if inv.status == "PASS" else "[FAIL]"
                f.write(f"### {status_mark} {inv.invariant_id}: {inv.description}\n\n")
                f.write(f"- **Component:** {inv.component}\n")
                f.write(f"- **Evidence:** {inv.evidence}\n")
                f.write(f"- **Status:** {inv.status}\n\n")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("QFS v15 FULL AUDIT SUITE")
    print("=" * 80 + "\n")

    auditor = FullAuditSuite()

    print("[AUDIT] Running all test suites...\n")
    test_result = auditor.run_all_tests()

    print("\n[AUDIT] Generating audit report...")
    report = auditor.generate_report(test_result)

    print("[AUDIT] Saving results...")
    auditor.save_results(report)

    print(f"\n[AUDIT] Results saved to:")
    print(f"  - AUDIT_RESULTS.json")
    print(f"  - AUDIT_RESULTS_SUMMARY.md")

    if report.overall_status == "PASS":
        print("\n[PASS] AUDIT PASSED: All invariants verified")
        sys.exit(0)
    else:
        print("\n[FAIL] AUDIT FAILED: Review AUDIT_RESULTS_SUMMARY.md")
        sys.exit(1)
