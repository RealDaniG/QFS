#!/usr/bin/env python3
"""
Phase 3 Batch 1: Test Infrastructure Cleanup
Replaces print() with structured logging in test files.

Usage:
    python v13/tools/phase3_batch1_test_cleanup.py [root_dir]

This script:
1. Scans all test files in v13/tests/
2. Adds logging imports if missing
3. Replaces print() calls with logger.info()
4. Preserves commented print statements
5. Creates backup before modification
"""

import re
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Tuple

# Statistics
stats = {
    "files_processed": 0,
    "files_modified": 0,
    "print_calls_replaced": 0,
    "errors": [],
}


def backup_file(filepath: Path) -> Path:
    """Create timestamped backup of file"""
    backup_dir = filepath.parent / ".backups"
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{filepath.stem}_{timestamp}{filepath.suffix}"
    shutil.copy2(filepath, backup_path)
    return backup_path


def has_logging_import(content: str) -> bool:
    """Check if file already imports logging"""
    return bool(re.search(r"^import logging", content, re.MULTILINE))


def has_logger_definition(content: str) -> bool:
    """Check if file already defines logger"""
    return bool(re.search(r"logger\s*=\s*logging\.getLogger", content))


def add_logging_setup(content: str) -> str:
    """Add logging import and logger definition if missing"""
    lines = content.split("\n")

    # Find where to insert imports (after docstring, before other imports)
    insert_idx = 0
    in_docstring = False
    docstring_char = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track docstrings
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if not in_docstring:
                in_docstring = True
                docstring_char = stripped[:3]
            elif stripped.endswith(docstring_char):
                in_docstring = False
                insert_idx = i + 1
                continue

        # Skip if in docstring
        if in_docstring:
            continue

        # Find first import
        if stripped.startswith("import ") or stripped.startswith("from "):
            insert_idx = i
            break

    # Add logging import if missing
    if not has_logging_import(content):
        lines.insert(insert_idx, "import logging")
        insert_idx += 1

    # Add logger definition if missing
    if not has_logger_definition(content):
        # Find end of imports
        for i in range(insert_idx, len(lines)):
            if not (
                lines[i].strip().startswith("import ")
                or lines[i].strip().startswith("from ")
                or lines[i].strip() == ""
            ):
                lines.insert(i, "\nlogger = logging.getLogger(__name__)\n")
                break

    return "\n".join(lines)


def transform_print_calls(content: str) -> Tuple[str, int]:
    """
    Transform print() calls to logger.info()
    Returns: (transformed_content, count_of_replacements)
    """
    count = 0

    # Pattern to match print() calls (not in comments)
    # Handles: print(...), print(f"..."), print("...", ...)
    pattern = r"(?<!#\s)(?<!#)print\s*\((.*?)\)(?!\s*#.*print)"

    def replace_print(match):
        nonlocal count
        args = match.group(1)
        count += 1
        return f"logger.info({args})"

    # Replace print calls
    transformed = re.sub(pattern, replace_print, content)

    return transformed, count


def process_file(filepath: Path, dry_run: bool = False) -> bool:
    """
    Process a single Python file
    Returns: True if file was modified
    """
    try:
        stats["files_processed"] += 1

        # Read original content
        with open(filepath, "r", encoding="utf-8") as f:
            original = f.read()

        # Skip if no print calls
        if "print(" not in original:
            return False

        # Transform content
        transformed = add_logging_setup(original)
        transformed, print_count = transform_print_calls(transformed)

        # Check if actually changed
        if transformed == original:
            return False

        if not dry_run:
            # Backup original
            backup_path = backup_file(filepath)

            # Write transformed content
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(transformed)

            print(
                f"✓ {filepath.relative_to(filepath.parents[2])}: {print_count} print() → logger.info()"
            )
            print(f"  Backup: {backup_path.relative_to(filepath.parents[2])}")
        else:
            print(f"[DRY RUN] Would transform {filepath}: {print_count} replacements")

        stats["files_modified"] += 1
        stats["print_calls_replaced"] += print_count
        return True

    except Exception as e:
        error_msg = f"Error processing {filepath}: {e}"
        stats["errors"].append(error_msg)
        print(f"✗ {error_msg}")
        return False


def process_directory(root_dir: str, dry_run: bool = False):
    """Process all test files in directory"""
    test_dir = Path(root_dir) / "v13" / "tests"

    if not test_dir.exists():
        print(f"Error: Test directory not found: {test_dir}")
        return

    print(f"Scanning: {test_dir}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("=" * 60)

    # Process all Python files
    py_files = list(test_dir.rglob("*.py"))

    for py_file in sorted(py_files):
        # Skip __init__.py and backup files
        if py_file.name == "__init__.py" or ".backups" in str(py_file):
            continue

        process_file(py_file, dry_run)

    # Print summary
    print("\n" + "=" * 60)
    print("BATCH 1 SUMMARY")
    print("=" * 60)
    print(f"Files Scanned: {stats['files_processed']}")
    print(f"Files Modified: {stats['files_modified']}")
    print(f"print() Calls Replaced: {stats['print_calls_replaced']}")
    print(f"Errors: {len(stats['errors'])}")

    if stats["errors"]:
        print("\nErrors:")
        for error in stats["errors"]:
            print(f"  - {error}")

    print("\n" + "=" * 60)
    if not dry_run:
        print("✅ Batch 1 complete!")
        print("\nNext steps:")
        print("1. Run tests: pytest v13/tests/ -v")
        print(
            "2. Verify no print() remaining: grep -r 'print(' v13/tests/ | grep -v '# print'"
        )
        print(
            "3. Re-scan violations: python v13/libs/AST_ZeroSimChecker.py v13/tests/ --fail"
        )
    else:
        print("DRY RUN complete. Run without --dry-run to apply changes.")


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 3 Batch 1: Test Infrastructure Cleanup"
    )
    parser.add_argument(
        "root_dir", nargs="?", default=".", help="Root directory (default: current)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without applying"
    )

    args = parser.parse_args()

    process_directory(args.root_dir, args.dry_run)
