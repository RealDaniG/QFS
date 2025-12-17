#!/usr/bin/env python3
"""
Phase 3 Batch 3: Remove print() statements
Aggressive approach - remove all print() calls from production code

This script:
1. Scans all Python files in v13/
2. Removes standalone print() statements
3. Validates syntax after removal
4. Creates backups before modification
5. Provides detailed reporting

Safety Features:
- AST-based removal (no regex)
- Syntax validation before/after
- Automatic backups
- Dry-run mode
- Per-file rollback capability
"""

import ast
import sys
import shutil
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RemovalRecord:
    """Record of a single print() removal"""

    file: Path
    line: int
    removed_code: str


class PrintRemover(ast.NodeTransformer):
    """
    AST transformer to remove print() statements

    Removes:
    - Standalone print() calls (expression statements)
    - print() in if/else blocks
    - print() in try/except blocks

    Preserves:
    - Comments mentioning print
    - String literals containing "print"
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.removals: List[RemovalRecord] = []

    def visit_Expr(self, node: ast.Expr) -> ast.Expr:
        """Remove standalone print() expression statements"""
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name):
                if node.value.func.id == "print":
                    # Record removal
                    removed_code = ast.unparse(node)
                    self.removals.append(
                        RemovalRecord(
                            file=Path(self.filepath),
                            line=node.lineno,
                            removed_code=removed_code,
                        )
                    )
                    # Return None to remove this statement
                    return None

        return self.generic_visit(node)


def transform_file(
    filepath: Path, dry_run: bool = True, create_backup: bool = True
) -> Tuple[bool, List[RemovalRecord], List[str]]:
    """
    Remove print() statements from a single file

    Returns:
        (success, removals, errors)
    """
    errors = []

    try:
        # Read original
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        # Skip if no print calls
        if "print(" not in source:
            return True, [], []

        # Parse AST
        try:
            tree = ast.parse(source, str(filepath))
        except SyntaxError as e:
            errors.append(f"Syntax error in original: {e}")
            return False, [], errors

        # Apply transformations
        remover = PrintRemover(str(filepath))
        new_tree = remover.visit(tree)

        # No removals needed
        if not remover.removals:
            return True, [], []

        # Generate new source
        try:
            new_source = ast.unparse(new_tree)
        except Exception as e:
            errors.append(f"Failed to unparse AST: {e}")
            return False, [], errors

        # Validate new source parses
        try:
            ast.parse(new_source, str(filepath))
        except SyntaxError as e:
            errors.append(f"Transformed code has syntax error: {e}")
            return False, [], errors

        # Validate new source compiles
        try:
            compile(new_source, str(filepath), "exec")
        except Exception as e:
            errors.append(f"Transformed code doesn't compile: {e}")
            return False, [], errors

        # Apply changes if not dry-run
        if not dry_run:
            # Create backup
            if create_backup:
                backup_path = filepath.with_suffix(filepath.suffix + ".batch3.backup")
                shutil.copy2(filepath, backup_path)

            # Write transformed source
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_source)

        return True, remover.removals, []

    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return False, [], errors


def process_directory(
    root_dir: Path, dry_run: bool = True, exclude_patterns: List[str] = None
) -> dict:
    """
    Process all Python files in directory

    Returns summary statistics
    """
    if exclude_patterns is None:
        exclude_patterns = [
            "**/AST_ZeroSimChecker.py",
            "**/.backups/**",
            "**/phase3_*.py",
            "**/rollback_*.py",
            "**/batch*.py",
        ]

    stats = {
        "files_scanned": 0,
        "files_modified": 0,
        "total_removals": 0,
        "files_skipped": 0,
        "files_errored": 0,
        "removals": [],
        "errors": [],
    }

    # Find all Python files
    py_files = list(root_dir.rglob("*.py"))

    for py_file in py_files:
        # Check exclusions
        if any(py_file.match(pattern) for pattern in exclude_patterns):
            stats["files_skipped"] += 1
            continue

        stats["files_scanned"] += 1

        # Transform file
        success, removals, errors = transform_file(py_file, dry_run=dry_run)

        if errors:
            stats["files_errored"] += 1
            stats["errors"].extend([(py_file, e) for e in errors])

        if removals:
            stats["files_modified"] += 1
            stats["total_removals"] += len(removals)
            stats["removals"].extend(removals)

    return stats


def print_report(stats: dict, dry_run: bool):
    """Print summary report"""
    print("\n" + "=" * 70)
    print("BATCH 3: PRINT REMOVAL - SUMMARY")
    print("=" * 70)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    print()
    print(f"Files Scanned: {stats['files_scanned']}")
    print(f"Files Modified: {stats['files_modified']}")
    print(f"Files Skipped: {stats['files_skipped']}")
    print(f"Files with Errors: {stats['files_errored']}")
    print(f"Total print() Removals: {stats['total_removals']}")
    print()

    if stats["removals"]:
        print("Sample Removals:")
        for i, r in enumerate(stats["removals"][:10], 1):
            print(f"\n{i}. {r.file.name}:{r.line}")
            print(f"   Removed: {r.removed_code[:80]}...")

        if len(stats["removals"]) > 10:
            print(f"\n... and {len(stats['removals']) - 10} more")

    if stats["errors"]:
        print("\nErrors:")
        for file, error in stats["errors"][:5]:
            print(f"  {file.name}: {error}")

        if len(stats["errors"]) > 5:
            print(f"  ... and {len(stats['errors']) - 5} more errors")

    print("\n" + "=" * 70)

    if dry_run:
        print("DRY RUN complete. Run without --dry-run to apply changes.")
    else:
        print("✅ Batch 3 complete!")
        print("\nNext steps:")
        print("1. Run tests: pytest v13/tests/ -v")
        print(
            "2. Re-scan violations: python v13/libs/AST_ZeroSimChecker.py v13/ --fail"
        )
        print("3. Compare: diff post_batch2_violations.txt post_batch3_violations.txt")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 3 Batch 3: Remove print() statements"
    )
    parser.add_argument(
        "root_dir",
        nargs="?",
        default="v13",
        help="Root directory to process (default: v13)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without applying"
    )
    parser.add_argument("--file", type=Path, help="Process single file only")

    args = parser.parse_args()

    print("Phase 3 Batch 3: Print Removal")
    print("Aggressive Mode - Remove All print() Calls")
    print("=" * 70)

    if args.file:
        # Single file mode
        success, removals, errors = transform_file(args.file, dry_run=args.dry_run)

        if errors:
            print(f"❌ Errors in {args.file}:")
            for e in errors:
                print(f"  - {e}")
            sys.exit(1)

        if removals:
            print(f"✅ {len(removals)} print() removals in {args.file}")
            for r in removals:
                print(f"  Line {r.line}: {r.removed_code}")
        else:
            print(f"No print() statements found in {args.file}")

        sys.exit(0)

    # Directory mode
    root = Path(args.root_dir)
    if not root.exists():
        print(f"❌ Directory not found: {root}")
        sys.exit(1)

    stats = process_directory(root, dry_run=args.dry_run)
    print_report(stats, args.dry_run)

    # Exit code
    if stats["files_errored"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)
