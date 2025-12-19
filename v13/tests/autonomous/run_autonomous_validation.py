"""
Autonomous Validation Master Controller
Location: v13/tests/autonomous/run_autonomous_validation.py

Orchestrates all validation phases with self-healing and comprehensive logging.
"""

import sys
import subprocess
from pathlib import Path
import json
import os

# Add root to path and change to root directory
root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root))
os.chdir(root)

# Import phases
sys.path.insert(0, str(Path(__file__).parent))
from phase_0_scan import EnvironmentScanner
from phase_2_guards import GuardValidator


class AutonomousValidator:
    """Master controller for autonomous validation"""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.git_hash = self._get_git_hash()
        self.results = {
            "git_hash": self.git_hash,
            "phases": {},
            "overall_status": "PENDING",
        }
        self.logs_dir = root_dir / "logs" / "autonomous"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _get_git_hash(self) -> str:
        """Get current git commit hash for deterministic timestamp"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.root_dir,
            )
            return result.stdout.strip() if result.returncode == 0 else "NO_GIT"
        except Exception:
            return "NO_GIT"

    def run_phase_0(self) -> bool:
        """Run Phase 0: Environment Scan"""
        print("\n" + "█" * 80)
        print("STARTING PHASE 0: ENVIRONMENT SCAN")
        print("█" * 80)

        scanner = EnvironmentScanner(self.root_dir)
        success = scanner.execute()

        self.results["phases"]["phase_0"] = {
            "name": "Environment Scan",
            "status": "PASS" if success else "FAIL",
            "git_hash": self.git_hash,
        }

        return success

    def run_phase_2(self) -> bool:
        """Run Phase 2: Guard Validation"""
        print("\n" + "█" * 80)
        print("STARTING PHASE 2: CONSTITUTIONAL GUARD VALIDATION")
        print("█" * 80)

        validator = GuardValidator()
        success = validator.execute()

        self.results["phases"]["phase_2"] = {
            "name": "Guard Validation",
            "status": "PASS" if success else "FAIL",
            "git_hash": self.git_hash,
        }

        return success

    def save_results(self):
        """Save validation results to JSON"""
        # Determine overall status
        all_passed = all(
            phase["status"] == "PASS" for phase in self.results["phases"].values()
        )
        self.results["overall_status"] = "PASS" if all_passed else "FAIL"

        # Save to file with git hash as filename
        timestamp = self.git_hash[:12] if self.git_hash != "NO_GIT" else "no_git_000000"
        results_file = self.logs_dir / f"validation_results_{timestamp}.json"
        results_file.write_text(json.dumps(self.results, indent=2))

        print(f"\n[RESULTS] Saved to: {results_file}")

    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 80)
        print("AUTONOMOUS VALIDATION SUMMARY")
        print("=" * 80)

        for phase_id, phase_data in self.results["phases"].items():
            status_symbol = "✓" if phase_data["status"] == "PASS" else "✗"
            print(f"{status_symbol} {phase_data['name']}: {phase_data['status']}")

        print("\n" + "=" * 80)
        overall_symbol = "✓" if self.results["overall_status"] == "PASS" else "✗"
        print(f"{overall_symbol} OVERALL STATUS: {self.results['overall_status']}")
        print("=" * 80)

    def execute(self) -> bool:
        """Execute all validation phases"""
        print("\n" + "█" * 80)
        print("AUTONOMOUS CONSTITUTIONAL GOVERNANCE VALIDATION")
        print(f"Git Hash: {self.git_hash}")
        print("█" * 80)

        # Phase 0: Environment Scan
        if not self.run_phase_0():
            print("\n[ABORT] Phase 0 failed - cannot continue")
            self.save_results()
            self.print_summary()
            return False

        # Phase 2: Guard Validation
        if not self.run_phase_2():
            print("\n[WARNING] Phase 2 failed - guards not operational")
            self.save_results()
            self.print_summary()
            return False

        # Save and summarize
        self.save_results()
        self.print_summary()

        return self.results["overall_status"] == "PASS"


if __name__ == "__main__":
    root = Path(__file__).parent.parent.parent
    validator = AutonomousValidator(root)
    success = validator.execute()
    sys.exit(0 if success else 1)
