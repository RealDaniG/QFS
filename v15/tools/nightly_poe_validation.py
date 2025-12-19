"""
Nightly PoE Validation Script
Runs autonomous validation of all PoE artifacts in the evidence directory.
"""

import sys
import glob
import json
import subprocess
from pathlib import Path
from datetime import datetime


class NightlyValidator:
    def __init__(self):
        self.evidence_dir = Path("evidence/poe_artifacts")
        self.report_dir = Path("evidence/nightly_reports")
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def validate_all(self):
        print(f"🌙 Starting Nightly PoE Validation: {datetime.utcnow().isoformat()}")

        artifacts = list(self.evidence_dir.glob("*.json"))
        results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_artifacts": len(artifacts),
            "passed": 0,
            "failed": 0,
            "failures": [],
        }

        print(f"Found {len(artifacts)} artifacts to validate.")

        for art_path in artifacts:
            art_id = art_path.stem
            print(f"Validating {art_id}...", end=" ")

            # Run verify_poe.py
            cmd = [sys.executable, "v15/tools/verify_poe.py", "--artifact_id", art_id]
            res = subprocess.run(cmd, capture_output=True, text=True)

            if res.returncode == 0:
                print("✅ PASS")
                results["passed"] += 1
            else:
                print("❌ FAIL")
                results["failed"] += 1
                results["failures"].append(
                    {"artifact_id": art_id, "error": res.stdout + res.stderr}
                )

        # Save Report
        report_path = (
            self.report_dir
            / f"poe_validation_{datetime.utcnow().strftime('%Y%m%d')}.json"
        )
        with open(report_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n📊 Validation Complete.")
        print(f"   Passed: {results['passed']}")
        print(f"   Failed: {results['failed']}")
        print(f"   Report: {report_path}")

        if results["failed"] > 0:
            sys.exit(1)


if __name__ == "__main__":
    validator = NightlyValidator()
    validator.validate_all()
