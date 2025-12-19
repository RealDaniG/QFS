"""
Autonomous Phase 0: Environment Scan & Baseline
Location: v13/tests/autonomous/phase_0_scan.py

Creates system state checkpoint and verifies all critical modules exist.
"""

import sys
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List

# Setup logger
logger = logging.getLogger(__name__)
# Setup logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


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
                try:
                    content = py_file.read_text(encoding="utf-8")
                except (PermissionError, OSError) as e:
                    logger.warning(
                        f"  ! Skipped {str(py_file.name)} due to permission/OS error: {e}"
                    )
                    continue

                imports = []

                for line in content.split("\n"):
                    line = line.strip()
                    if line.startswith("from ") or line.startswith("import "):
                        imports.append(line)

                if imports:
                    try:
                        import_map[str(py_file.relative_to(self.root_dir))] = imports
                    except ValueError:
                        # Fallback if relative path fails
                        import_map[str(py_file)] = imports

            except Exception as e:
                # Use ascii safe error message
                logger.error(
                    f"[SCAN ERROR] {str(py_file).encode('ascii', 'replace').decode()}: {str(e)}"
                )

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
            (
                "v13.policy.governance.ProposalEngine",
                "v13/policy/governance/ProposalEngine.py",
            ),
            ("v13.atlas.scoring.ViralEngine", "v13/atlas/scoring/ViralEngine.py"),
            ("v13.atlas.social.SocialBridge", "v13/atlas/social/SocialBridge.py"),
            (
                "v13.atlas.economics.ViralRewardBinder",
                "v13/atlas/economics/ViralRewardBinder.py",
            ),
            (
                "v13.policy.governance.GovernanceParameterRegistry",
                "v13/policy/governance/GovernanceParameterRegistry.py",
            ),
        ]

        for module, file_path in critical_modules:
            full_path = self.root_dir / file_path
            module_status[module] = full_path.exists()

            if not full_path.exists():
                logger.warning(f"[MISSING] {module} -> {full_path}")

        return module_status

    def create_checkpoint(self) -> Path:
        """Create system state checkpoint"""
        # Use git hash as deterministic timestamp base
        git_hash = self.get_git_hash()
        timestamp = git_hash[:12] if git_hash != "NO_GIT" else "no_git_000000"

        checkpoint = {
            "git_hash": git_hash,
            "checkpoint_id": timestamp,
            "imports": self.scan_imports(),
            "modules": self.verify_module_paths(),
        }

        checkpoint_file = self.checkpoint_dir / f"checkpoint_{timestamp}.json"
        checkpoint_file.write_text(json.dumps(checkpoint, indent=2))

        logger.info(f"[CHECKPOINT] Created: {checkpoint_file}")
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
        except Exception:
            return "NO_GIT"

    def execute(self) -> bool:
        """Execute Phase 0 scan"""
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 0: ENVIRONMENT SCAN & BASELINE")
        logger.info("=" * 80)

        # Scan imports
        logger.info("\n[STEP 1] Scanning imports...")
        imports = self.scan_imports()
        logger.info(f"  ✓ Found {len(imports)} Python files with imports")

        # Verify modules
        logger.info("\n[STEP 2] Verifying module paths...")
        modules = self.verify_module_paths()
        missing = [m for m, exists in modules.items() if not exists]

        if missing:
            logger.error(f"  ✗ MISSING MODULES: {len(missing)}")
            with open("missing_modules.txt", "w", encoding="utf-8") as f:
                for m in missing:
                    f.write(f"{m}\n")
                    logger.error(f"    - {m}")
            return False

        else:
            logger.info(f"  ✓ All {len(modules)} critical modules found")

        # Create checkpoint
        logger.info("\n[STEP 3] Creating checkpoint...")
        self.create_checkpoint()

        logger.info("\n[PHASE 0] COMPLETE ✓")
        return True


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent.parent.parent
    scanner = EnvironmentScanner(root)
    success = scanner.execute()
    sys.exit(0 if success else 1)
