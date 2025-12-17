#!/usr/bin/env python3
"""
Rollback Batch 1 Changes
Restores all files from .backups/ directories
"""

import shutil
from pathlib import Path
import subprocess
import sys


def rollback_from_backups(root_dir: str = "."):
    """Restore all files from backup directories"""
    v13_tests = Path(root_dir) / "v13" / "tests"

    if not v13_tests.exists():
        print(f"❌ Test directory not found: {v13_tests}")
        return False

    print("🔄 Rolling back Batch 1 changes...")
    print("=" * 60)

    restored_count = 0
    backup_dirs = list(v13_tests.rglob(".backups"))

    for backup_dir in sorted(backup_dirs):
        if not backup_dir.is_dir():
            continue

        parent_dir = backup_dir.parent

        for backup_file in backup_dir.glob("*.py"):
            # Extract original filename (remove timestamp)
            # Format: filename_YYYYMMDD_HHMMSS.py
            parts = backup_file.stem.rsplit("_", 2)
            if len(parts) >= 3:
                original_name = parts[0] + backup_file.suffix
            else:
                original_name = backup_file.name

            original_path = parent_dir / original_name

            try:
                shutil.copy2(backup_file, original_path)
                print(f"  ✅ Restored: {original_path.relative_to(Path(root_dir))}")
                restored_count += 1
            except Exception as e:
                print(f"  ❌ Failed to restore {original_name}: {e}")

    print("=" * 60)
    print(f"Restored {restored_count} files from backups")

    return restored_count > 0


def verify_baseline(root_dir: str = "."):
    """Verify violations are back to baseline"""
    print("\n🔍 Verifying baseline restoration...")

    try:
        result = subprocess.run(
            ["python", "v13/libs/AST_ZeroSimChecker.py", "v13/", "--fail"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Parse violation count
        for line in result.stdout.split("\n"):
            if "violations found" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if "violations" in part and i > 0:
                        violations = int(parts[i - 1])

                        if violations == 1616:
                            print(
                                f"✅ Rollback successful: {violations} violations (baseline restored)"
                            )
                            return True
                        else:
                            print(
                                f"⚠️ Rollback incomplete: {violations} violations (expected 1616)"
                            )
                            return False

        print("❌ Could not parse violation count")
        return False

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."

    # Execute rollback
    if rollback_from_backups(root):
        # Verify restoration
        if verify_baseline(root):
            print("\n" + "=" * 60)
            print("✅ ROLLBACK COMPLETE")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Review changes: git status")
            print(
                "2. Commit rollback: git commit -m 'revert(zero-sim): rollback Batch 1'"
            )
            print(
                "3. Proceed with Batch 2: python v13/tools/phase3_batch2_sorted_iterations.py"
            )
            sys.exit(0)
        else:
            print("\n⚠️ Baseline not fully restored. Manual review required.")
            sys.exit(1)
    else:
        print("\n❌ No backups found or rollback failed.")
        sys.exit(1)
