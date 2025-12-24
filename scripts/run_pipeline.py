import sys
import subprocess
import json
from pathlib import Path
import hashlib


class PipelineRunner:
    def __init__(self):
        self.root = Path(__file__).parent
        self.commit_sha = self.get_commit_sha()
        self.artifacts_dir = self.root / "ci_artifacts" / self.commit_sha
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

        self.stages = {
            "A": {"name": "Static Checks", "status": "pending"},
            "B": {"name": "v15 Audit Suite", "status": "pending"},
            "C": {"name": "Replay & Stress", "status": "pending"},
            "D": {"name": "Ops Verification", "status": "pending"},
            "E": {"name": "Testnet Dry-Run", "status": "pending"},
        }

    def get_commit_sha(self):
        """Get current git commit SHA."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()[:8]
        except:
            return "20240101_000000"

    def run_stage_a(self):
        """Stage A: Static Checks."""
        print("\n" + "=" * 80)
        print("Stage A: Static Checks")
        print("=" * 80)

        try:
            # Linting
            print("\n[1/3] Running linting...")
            subprocess.run(
                ["pylint", "v15/", "--fail-under=8.0"], check=True, cwd=self.root
            )
            print("✓ Linting passed")

            # Type checking
            print("\n[2/3] Running type checking...")
            subprocess.run(["mypy", "v15/", "--strict"], check=True, cwd=self.root)
            print("✓ Type checking passed")

            # Formatting
            print("\n[3/3] Checking formatting...")
            subprocess.run(["black", "--check", "v15/"], check=True, cwd=self.root)
            print("✓ Formatting check passed")

            self.stages["A"]["status"] = "pass"
            return True

        except subprocess.CalledProcessError as e:
            print(f"\n❌ Stage A failed: {e}")
            self.stages["A"]["status"] = "fail"
            return False

    def run_stage_b(self):
        """Stage B: v15 Audit Suite (Quality Gate)."""
        print("\n" + "=" * 80)
        print("Stage B: v15 Audit Suite (Quality Gate)")
        print("=" * 80)

        try:
            # Run full audit suite
            print("\n[1/3] Running v15 full audit suite...")
            result = subprocess.run(
                ["python", "v15/tests/autonomous/test_full_audit_suite.py"],
                capture_output=True,
                text=True,
                cwd=self.root,
            )

            # Save log
            log_file = self.artifacts_dir / "audit_suite.log"
            log_file.write_text(result.stdout + result.stderr)

            if result.returncode != 0:
                print(f"❌ Audit suite failed with exit code {result.returncode}")
                self.stages["B"]["status"] = "fail"
                return False

            print("✓ Audit suite passed")

            # Verify audit results
            print("\n[2/3] Verifying audit results...")
            audit_file = self.root / "AUDIT_RESULTS.json"

            with open(audit_file) as f:
                audit = json.load(f)

            assert audit["total_tests"] == 23, "Expected 23 tests"
            assert audit["passed_tests"] == 23, "All tests must pass"
            assert len(audit["invariants"]) == 13, "Expected 13 invariants"

            for inv in audit["invariants"]:
                assert inv["status"] == "PASS", (
                    f"Invariant {inv['invariant_id']} failed"
                )

            print("✓ Audit results verified")

            # Check for unexecuted tests
            print("\n[3/3] Checking for unexecuted tests...")
            if "unexecuted_tests" in audit and len(audit["unexecuted_tests"]) > 0:
                print(f"❌ {len(audit['unexecuted_tests'])} unexecuted tests found")
                self.stages["B"]["status"] = "fail"
                return False

            print("✓ No unexecuted tests")

            # Copy audit artifacts
            (self.artifacts_dir / "AUDIT_RESULTS.json").write_text(
                json.dumps(audit, indent=2)
            )

            self.stages["B"]["status"] = "pass"
            return True

        except Exception as e:
            print(f"\n❌ Stage B failed: {e}")
            self.stages["B"]["status"] = "fail"
            return False

    def run_stage_c(self):
        """Stage C: Replay & Stress Regression."""
        print("\n" + "=" * 80)
        print("Stage C: Replay & Stress Regression")
        print("=" * 80)

        try:
            # Run replay tests
            print("\n[1/2] Running deterministic replay tests...")
            subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "v15/tests/autonomous/test_governance_replay.py",
                    "-v",
                ],
                check=True,
                cwd=self.root,
            )
            print("✓ Replay tests passed")

            # Run stress campaign
            print("\n[2/2] Running stress campaign (50 proposals)...")
            subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "v15/tests/autonomous/test_stress_campaign.py",
                    "-v",
                ],
                check=True,
                cwd=self.root,
            )
            print("✓ Stress campaign passed")

            # Verify zero drift
            with open(self.root / "AUDIT_RESULTS.json") as f:
                audit = json.load(f)

            replay_inv = [
                i for i in audit["invariants"] if i["invariant_id"] == "REPLAY-I1"
            ][0]
            assert replay_inv["status"] == "PASS", (
                "Replay invariant must pass (zero drift)"
            )
            print("✓ Zero drift verified")

            self.stages["C"]["status"] = "pass"
            return True

        except Exception as e:
            print(f"\n❌ Stage C failed: {e}")
            self.stages["C"]["status"] = "fail"
            return False

    def run_stage_d(self):
        """Stage D: Ops & Health Verification."""
        print("\n" + "=" * 80)
        print("Stage D: Ops & Health Verification")
        print("=" * 80)

        try:
            # Run health check tests
            print("\n[1/2] Running health check tests...")
            subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "v15/tests/test_protocol_health_check.py",
                    "-v",
                ],
                check=True,
                cwd=self.root,
            )
            print("✓ Health check tests passed")

            # Run dashboard tests
            print("\n[2/2] Running dashboard tests...")
            subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "v15/tests/test_governance_dashboard.py",
                    "-v",
                ],
                check=True,
                cwd=self.root,
            )
            print("✓ Dashboard tests passed")

            # Verify operational invariants
            with open(self.root / "AUDIT_RESULTS.json") as f:
                audit = json.load(f)

            ops_invs = [
                "HEALTH-I1",
                "HEALTH-I2",
                "HEALTH-I3",
                "DASH-I1",
                "DASH-I2",
                "DASH-I3",
            ]
            for inv_id in ops_invs:
                inv = [i for i in audit["invariants"] if i["invariant_id"] == inv_id][0]
                assert inv["status"] == "PASS", f"{inv_id} must pass"

            print("✓ All operational invariants verified")

            self.stages["D"]["status"] = "pass"
            return True

        except Exception as e:
            print(f"\n❌ Stage D failed: {e}")
            self.stages["D"]["status"] = "fail"
            return False

    def run_stage_e(self):
        """Stage E: Testnet Dry-Run (Optional)."""
        print("\n" + "=" * 80)
        print("Stage E: Testnet Dry-Run (Optional)")
        print("=" * 80)

        try:
            # Run Scenario 1
            print("\n[1/2] Running Scenario 1 (Change Emission Cap)...")
            subprocess.run(
                ["python", "scenarios/scenario_1_emission_cap.py"],
                check=True,
                cwd=self.root,
            )
            print("✓ Scenario 1 passed")

            # Verify PoE artifacts
            print("\n[2/2] Verifying PoE artifacts...")
            poe_dir = self.root / "logs" / "poe_artifacts"
            if not poe_dir.exists() or not any(poe_dir.iterdir()):
                print("❌ No PoE artifacts generated")
                self.stages["E"]["status"] = "fail"
                return False

            print("✓ PoE artifacts verified")

            self.stages["E"]["status"] = "pass"
            return True

        except Exception as e:
            print(f"\n❌ Stage E failed: {e}")
            self.stages["E"]["status"] = "fail"
            return False

    def generate_status_report(self):
        """Generate pipeline status report."""
        timestamp = "2024-01-01 00:00:00 UTC"

        all_pass = all(
            stage["status"] == "pass"
            for key, stage in self.stages.items()
            if key in ["A", "B", "C", "D"]  # E is optional
        )

        report = f"""# Pipeline Status Report

**Commit:** {self.commit_sha}
**Timestamp:** {timestamp}
**Overall Status:** {"✅ PASS - Ready for testnet deployment" if all_pass else "❌ FAIL - Do not deploy"}

## Stage Results

"""

        for key, stage in self.stages.items():
            status_icon = {
                "pass": "✅",
                "fail": "❌",
                "pending": "⏳",
                "disabled": "⏭️",
            }.get(stage["status"], "❓")

            report += f"- **Stage {key} ({stage['name']}):** {status_icon} {stage['status'].upper()}\n"

        report += f"""

## Artifacts

Artifacts saved to: `{self.artifacts_dir.relative_to(self.root)}/`

## Next Actions

"""

        if not all_pass:
            failed_stages = [
                f"Stage {key} ({stage['name']})"
                for key, stage in self.stages.items()
                if stage["status"] == "fail"
            ]
            report += "**Fix the following failed stages:**\n"
            for failed in failed_stages:
                report += f"- {failed}\n"
        else:
            report += "✅ All required stages passed. System is ready for testnet deployment.\n"

        # Save report
        report_file = self.artifacts_dir / "PIPELINE_STATUS.md"
        report_file.write_text(report)

        # Also save to root for easy access
        (self.root / "PIPELINE_STATUS.md").write_text(report)

        return report

    def run(self):
        """Run full pipeline."""
        print("=" * 80)
        print("QFS v15 - Stage 12.1 Pipeline Self-Verification")
        print("=" * 80)
        print(f"\nCommit: {self.commit_sha}")
        print(f"Artifacts: {self.artifacts_dir.relative_to(self.root)}/")

        # Run stages in order
        stages_to_run = [
            ("A", self.run_stage_a),
            ("B", self.run_stage_b),
            ("C", self.run_stage_c),
            ("D", self.run_stage_d),
            ("E", self.run_stage_e),  # Optional
        ]

        for stage_key, stage_func in stages_to_run:
            if not stage_func():
                # Stop on first failure (except E which is optional)
                if stage_key != "E":
                    print(f"\n❌ Pipeline stopped at Stage {stage_key}")
                    break

        # Generate status report
        print("\n" + "=" * 80)
        print("Generating Pipeline Status Report")
        print("=" * 80)

        report = self.generate_status_report()
        print(report)

        # Return exit code
        all_pass = all(
            stage["status"] == "pass"
            for key, stage in self.stages.items()
            if key in ["A", "B", "C", "D"]
        )

        return 0 if all_pass else 1


if __name__ == "__main__":
    runner = PipelineRunner()
    sys.exit(runner.run())
