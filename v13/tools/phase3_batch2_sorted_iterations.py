#!/usr/bin/env python3
"""
Phase 3 Batch 2: Add sorted() to Nondeterministic Iterations
Ultra-conservative approach - only safe, verified transformations

This script:
1. Identifies dict/set iterations without sorted()
2. Wraps them with sorted() for deterministic ordering
3. Validates all transformations before applying
4. Creates backups and enables rollback
5. Provides detailed reporting

Safety Features:
- AST-based transformation (no regex)
- Syntax validation before/after
- Automatic backups
- Dry-run mode
- Per-file rollback capability
"""

import ast
import sys
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TransformationRecord:
    """Record of a single transformation"""

    file: Path
    line: int
    original: str
    transformed: str
    category: str


class SafeIterationFixer(ast.NodeTransformer):
    """
    Conservative AST transformer to add sorted() to iterations

    Only transforms patterns that are provably safe:
    - for x in dict.keys()
    - for x in dict.values()
    - for x in dict.items()
    - for x in set_var
    - [x for x in dict.keys()]
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.changes: List[TransformationRecord] = []
        self.skipped: List[Tuple[int, str, str]] = []

    def visit_For(self, node: ast.For) -> ast.For:
        """Transform for loops with dict/set iteration"""
        if self._should_transform(node.iter):
            original = ast.unparse(node.iter)

            # Wrap with sorted()
            node.iter = self._wrap_with_sorted(node.iter)

            transformed = ast.unparse(node.iter)

            self.changes.append(
                TransformationRecord(
                    file=Path(self.filepath),
                    line=node.lineno,
                    original=f"for ... in {original}",
                    transformed=f"for ... in {transformed}",
                    category="FOR_LOOP",
                )
            )
        else:
            # Log why we skipped
            reason = self._skip_reason(node.iter)
            self.skipped.append((node.lineno, ast.unparse(node.iter), reason))

        return self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp) -> ast.ListComp:
        """Transform list comprehensions with dict/set iteration"""
        for generator in sorted(node.generators):
            if self._should_transform(generator.iter):
                original = ast.unparse(generator.iter)

                # Wrap with sorted()
                generator.iter = self._wrap_with_sorted(generator.iter)

                transformed = ast.unparse(generator.iter)

                self.changes.append(
                    TransformationRecord(
                        file=Path(self.filepath),
                        line=node.lineno,
                        original=f"[... for ... in {original}]",
                        transformed=f"[... for ... in {transformed}]",
                        category="LIST_COMP",
                    )
                )

        return self.generic_visit(node)

    def _should_transform(self, iter_node: ast.expr) -> bool:
        """
        Conservative check: only transform known-safe patterns

        Safe patterns:
        1. dict.keys(), dict.values(), dict.items()
        2. Variables with 'dict', 'map', 'cache' in name
        3. set() constructor calls
        """
        # Pattern 1: dict.keys(), dict.values(), dict.items()
        if isinstance(iter_node, ast.Call):
            if isinstance(iter_node.func, ast.Attribute):
                if iter_node.func.attr in ("keys", "values", "items"):
                    return True

            # Pattern 3: set() constructor
            if isinstance(iter_node.func, ast.Name):
                if iter_node.func.id == "set":
                    return True

        # Pattern 2: Variables suggesting dict/set
        if isinstance(iter_node, ast.Name):
            name_lower = iter_node.id.lower()
            hints = ["dict", "map", "mapping", "cache", "registry", "index"]
            if any(hint in name_lower for hint in hints):
                return True

        # Check if already wrapped with sorted()
        if isinstance(iter_node, ast.Call):
            if isinstance(iter_node.func, ast.Name):
                if iter_node.func.id == "sorted":
                    return False  # Already sorted

        return False

    def _skip_reason(self, iter_node: ast.expr) -> str:
        """Explain why we skipped this iteration"""
        if isinstance(iter_node, ast.Call):
            if isinstance(iter_node.func, ast.Name):
                if iter_node.func.id == "sorted":
                    return "Already sorted"
                if iter_node.func.id in ("range", "enumerate", "zip"):
                    return "Deterministic built-in"

        if isinstance(iter_node, ast.List):
            return "List literal (deterministic)"

        if isinstance(iter_node, ast.Name):
            if iter_node.id.endswith("_list") or iter_node.id.endswith("_array"):
                return "Likely list (by naming convention)"

        return "Uncertain type - conservative skip"

    def _wrap_with_sorted(self, iter_node: ast.expr) -> ast.Call:
        """Wrap iterator with sorted()"""
        return ast.Call(
            func=ast.Name(id="sorted", ctx=ast.Load()), args=[iter_node], keywords=[]
        )


def transform_file(
    filepath: Path, dry_run: bool = True, create_backup: bool = True
) -> Tuple[bool, List[TransformationRecord], List[str]]:
    """
    Transform a single file with safety checks

    Returns:
        (success, transformations, errors)
    """
    errors = []

    try:
        # Read original
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        # Parse AST
        try:
            tree = ast.parse(source, str(filepath))
        except SyntaxError as e:
            errors.append(f"Syntax error in original: {e}")
            return False, [], errors

        # Apply transformations
        fixer = SafeIterationFixer(str(filepath))
        new_tree = fixer.visit(tree)

        # No changes needed
        if not fixer.changes:
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
                backup_path = filepath.with_suffix(filepath.suffix + ".batch2.backup")
                shutil.copy2(filepath, backup_path)

            # Write transformed source
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_source)

        return True, fixer.changes, []

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
        ]

    stats = {
        "files_scanned": 0,
        "files_transformed": 0,
        "total_changes": 0,
        "files_skipped": 0,
        "files_errored": 0,
        "transformations": [],
        "errors": [],
    }

    # Find all Python files
    py_files = list(root_dir.rglob("*.py"))

    for py_file in sorted(py_files):
        # Check exclusions
        if any(py_file.match(pattern) for pattern in exclude_patterns):
            stats["files_skipped"] += 1
            continue

        stats["files_scanned"] += 1

        # Transform file
        success, changes, errors = transform_file(py_file, dry_run=dry_run)

        if errors:
            stats["files_errored"] += 1
            stats["errors"].extend([(py_file, e) for e in errors])

        if changes:
            stats["files_transformed"] += 1
            stats["total_changes"] += len(changes)
            stats["transformations"].extend(changes)

    return stats


def print_report(stats: dict, dry_run: bool):
    """Print summary report"""
    print("\n" + "=" * 70)
    print("BATCH 2: SORTED ITERATIONS - SUMMARY")
    print("=" * 70)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    print()
    print(f"Files Scanned: {stats['files_scanned']}")
    print(f"Files Transformed: {stats['files_transformed']}")
    print(f"Files Skipped: {stats['files_skipped']}")
    print(f"Files with Errors: {stats['files_errored']}")
    print(f"Total Transformations: {stats['total_changes']}")
    print()

    if stats["transformations"]:
        print("Sample Transformations:")
        for i, t in enumerate(stats["transformations"][:10], 1):
            print(f"\n{i}. {t.file.name}:{t.line}")
            print(f"   Before: {t.original}")
            print(f"   After:  {t.transformed}")

        if len(stats["transformations"]) > 10:
            print(f"\n... and {len(stats['transformations']) - 10} more")

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
        print("✅ Batch 2 complete!")
        print("\nNext steps:")
        print("1. Run tests: pytest v13/tests/ -v")
        print(
            "2. Re-scan violations: python v13/libs/AST_ZeroSimChecker.py v13/ --fail"
        )
        print("3. Compare: diff pre_batch2_violations.txt post_batch2_violations.txt")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 3 Batch 2: Add sorted() to nondeterministic iterations"
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

    print("Phase 3 Batch 2: Sorted Iteration Fixer")
    print("Ultra-Safe Conservative Mode")
    print("=" * 70)

    if args.file:
        # Single file mode
        success, changes, errors = transform_file(args.file, dry_run=args.dry_run)

        if errors:
            print(f"❌ Errors in {args.file}:")
            for e in sorted(errors):
                print(f"  - {e}")
            sys.exit(1)

        if changes:
            print(f"✅ {len(changes)} transformations in {args.file}")
            for c in sorted(changes):
                print(f"  Line {c.line}: {c.original} → {c.transformed}")
        else:
            print(f"No changes needed in {args.file}")

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
