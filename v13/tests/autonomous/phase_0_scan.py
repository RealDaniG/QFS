"""
Autonomous Phase 0: Environment Scan & Baseline
Location: v13/tests/autonomous/phase_0_scan.py

Creates system state checkpoint and verifies all critical modules exist.
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class EnvironmentScanner:
    """Autonomous environment scanner with self-healing"""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.checkpoint_dir = root_dir / "checkpoints"
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.scan_results = {}

    def scan_imports(self) -> Dict[str, List[str]]:
        """Scan all Python files for import statements"""
        import_map = {}

        for py_file in self.root_dir.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                imports = []

                for line in content.split("\n"):
                    line = line.strip()
                    if line.startswith("from ") or line.startswith("import "):
                        imports.append(line)

                if imports:
                    import_map[str(py_file.relative_to(self.root_dir))] = imports

            except Exception as e:
                print(f"[SCAN ERROR] {py_file}: {e}")

        return import_map

    def verify_module_paths(self) -> Dict[str, bool]:
        """Verify all imported modules exist"""
        module_status = {}

        critical_modules = [
            ("v13.libs.BigNum128", "v13/libs/BigNum128.py"),
            ("v13.libs.CertifiedMath", "v13/libs/CertifiedMath.py"),
            (
                "v13.libs.economics.EconomicsGuard",
                "v13/libs/economics/EconomicsGuard.py",
            ),
            (
                "v13.libs.economics.economic_constants",
                "v13/libs/economics/economic_constants.py",
            ),
            (
                "v13.libs.integration.StateTransitionEngine",
                "v13/libs/integration/StateTransitionEngine.py",
            ),
            (
                "v13.libs.governance.NODInvariantChecker",
                "v13/libs/governance/NODInvariantChecker.py",
            ),
            (
                "v13.policy.bounties.bounty_state_machine",
                "v13/policy/bounties/bounty_state_machine.py",
            ),
            (
                "v13.policy.bounties.bounty_schema",
                "v13/policy/bounties/bounty_schema.py",
            ),
            (
                "v13.policy.bounties.bounty_events",
                "v13/policy/bounties/bounty_events.py",
            ),
            (
                "v13.policy.treasury.dev_rewards_treasury",
                "v13/policy/treasury/dev_rewards_treasury.py",
            ),
            ("v13.handlers.CIR302_Handler", "v13/handlers/CIR302_Handler.py"),
        ]

        for module, file_path in critical_modules:
            full_path = self.root_dir / file_path
            module_status[module] = full_path.exists()

            if not full_path.exists():
                print(f"[MISSING] {module} -> {full_path}")

        return module_status

    def create_checkpoint(self) -> Path:
        """Create system state checkpoint"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint = {
            "timestamp": timestamp,
            "imports": self.scan_imports(),
            "modules": self.verify_module_paths(),
            "git_hash": self.get_git_hash(),
        }

        checkpoint_file = self.checkpoint_dir / f"checkpoint_{timestamp}.json"
        checkpoint_file.write_text(json.dumps(checkpoint, indent=2))

        print(f"[CHECKPOINT] Created: {checkpoint_file}")
        return checkpoint_file

    def get_git_hash(self) -> str:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.root_dir,
            )
            return result.stdout.strip() if result.returncode == 0 else "NO_GIT"
        except:
            return "NO_GIT"

    def execute(self) -> bool:
        """Execute Phase 0 scan"""
        print("\n" + "=" * 80)
        print("PHASE 0: ENVIRONMENT SCAN & BASELINE")
        print("=" * 80)

        # Scan imports
        print("\n[STEP 1] Scanning imports...")
        imports = self.scan_imports()
        print(f"  ✓ Found {len(imports)} Python files with imports")

        # Verify modules
        print("\n[STEP 2] Verifying module paths...")
        modules = self.verify_module_paths()
        missing = [m for m, exists in modules.items() if not exists]

        if missing:
            print(f"  ✗ MISSING MODULES: {len(missing)}")
            for m in missing:
                print(f"    - {m}")
            return False
        else:
            print(f"  ✓ All {len(modules)} critical modules found")

        # Create checkpoint
        print("\n[STEP 3] Creating checkpoint...")
        self.create_checkpoint()

        print("\n[PHASE 0] COMPLETE ✓")
        return True


if __name__ == "__main__":
    root = Path(__file__).parent.parent.parent
    scanner = EnvironmentScanner(root)
    success = scanner.execute()
    sys.exit(0 if success else 1)
