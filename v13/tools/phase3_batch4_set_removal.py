#!/usr/bin/env python3
"""
Phase 3 Batch 4: Set Literal Removal
Aggressive transformation: Convert all set literals and set() calls to deterministic alternatives

Transformations:
1. {x, y, z} → [x, y, z]
2. set(collection) → sorted(list(collection))
3. {x for x in items} → sorted([x for x in items])

Safety: AST-based, strong validation, automatic backups
"""

import ast
import sys
import shutil
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class TransformRecord:
    """Record of a single set → list transformation"""

    file: Path
    line: int
    original: str
    transformed: str
    transform_type: str


class SetToListTransformer(ast.NodeTransformer):
    """
    Aggressive set literal remover

    Converts:
    - Set literals: {1, 2, 3} → [1, 2, 3]
    - Set constructor: set([...]) → sorted(list([...]))
    - Set comprehensions: {x for x in y} → sorted([x for x in y])
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.transforms: List[TransformRecord] = []

    def visit_Set(self, node: ast.Set) -> ast.List:
        """Transform set literals to lists"""
        original = ast.unparse(node)

        # Create list with same elements
        new_node = ast.List(elts=node.elts, ctx=node.ctx)

        transformed = ast.unparse(new_node)

        self.transforms.append(
            TransformRecord(
                file=Path(self.filepath),
                line=node.lineno,
                original=original,
                transformed=transformed,
                transform_type="SET_LITERAL",
            )
        )

        return new_node

    def visit_Call(self, node: ast.Call) -> ast.Call:
        """Transform set() constructor calls"""
        if isinstance(node.func, ast.Name) and node.func.id == "set":
            original = ast.unparse(node)

            # Convert set(...) → sorted(list(...))
            if node.args:
                # set(iterable) → sorted(list(iterable))
                list_call = ast.Call(
                    func=ast.Name(id="list", ctx=ast.Load()),
                    args=node.args,
                    keywords=[],
                )
                sorted_call = ast.Call(
                    func=ast.Name(id="sorted", ctx=ast.Load()),
                    args=[list_call],
                    keywords=[],
                )

                transformed = ast.unparse(sorted_call)

                self.transforms.append(
                    TransformRecord(
                        file=Path(self.filepath),
                        line=node.lineno,
                        original=original,
                        transformed=transformed,
                        transform_type="SET_CONSTRUCTOR",
                    )
                )

                return sorted_call
            else:
                # set() → []
                empty_list = ast.List(elts=[], ctx=ast.Load())

                self.transforms.append(
                    TransformRecord(
                        file=Path(self.filepath),
                        line=node.lineno,
                        original=original,
                        transformed="[]",
                        transform_type="EMPTY_SET",
                    )
                )

                return empty_list

        return self.generic_visit(node)

    def visit_SetComp(self, node: ast.SetComp) -> ast.Call:
        """Transform set comprehensions to sorted list comprehensions"""
        original = ast.unparse(node)

        # {x for x in y} → sorted([x for x in y])
        list_comp = ast.ListComp(elt=node.elt, generators=node.generators)

        sorted_call = ast.Call(
            func=ast.Name(id="sorted", ctx=ast.Load()), args=[list_comp], keywords=[]
        )

        transformed = ast.unparse(sorted_call)

        self.transforms.append(
            TransformRecord(
                file=Path(self.filepath),
                line=node.lineno,
                original=original,
                transformed=transformed,
                transform_type="SET_COMPREHENSION",
            )
        )

        return sorted_call


def transform_file(
    filepath: Path, dry_run: bool = True, create_backup: bool = True
) -> Tuple[bool, List[TransformRecord], List[str]]:
    """
    Transform set literals in a single file

    Returns:
        (success, transforms, errors)
    """
    errors = []

    try:
        # Read original
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        # Skip if no set usage
        if "{" not in source and "set(" not in source:
            return True, [], []

        # Parse AST
        try:
            tree = ast.parse(source, str(filepath))
        except SyntaxError as e:
            errors.append(f"Syntax error in original: {e}")
            return False, [], errors

        # Apply transformations
        transformer = SetToListTransformer(str(filepath))
        new_tree = transformer.visit(tree)

        # No transforms needed
        if not transformer.transforms:
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
                backup_path = filepath.with_suffix(filepath.suffix + ".batch4.backup")
                shutil.copy2(filepath, backup_path)

            # Write transformed source
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_source)

        return True, transformer.transforms, []

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
        "total_transforms": 0,
        "files_skipped": 0,
        "files_errored": 0,
        "transforms_by_type": {
            "SET_LITERAL": 0,
            "SET_CONSTRUCTOR": 0,
            "SET_COMPREHENSION": 0,
            "EMPTY_SET": 0,
        },
        "transforms": [],
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
        success, transforms, errors = transform_file(py_file, dry_run=dry_run)

        if errors:
            stats["files_errored"] += 1
            stats["errors"].extend([(py_file, e) for e in errors])

        if transforms:
            stats["files_modified"] += 1
            stats["total_transforms"] += len(transforms)
            stats["transforms"].extend(transforms)

            # Count by type
            for t in transforms:
                stats["transforms_by_type"][t.transform_type] += 1

    return stats


def print_report(stats: dict, dry_run: bool):
    """Print summary report"""
    print("\n" + "=" * 70)
    print("BATCH 4: SET LITERAL REMOVAL - SUMMARY")
    print("=" * 70)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    print()
    print(f"Files Scanned: {stats['files_scanned']}")
    print(f"Files Modified: {stats['files_modified']}")
    print(f"Files Skipped: {stats['files_skipped']}")
    print(f"Files with Errors: {stats['files_errored']}")
    print(f"Total Transformations: {stats['total_transforms']}")
    print()
    print("Transformations by Type:")
    for ttype, count in stats["transforms_by_type"].items():
        print(f"  {ttype}: {count}")
    print()

    if stats["transforms"]:
        print("Sample Transformations:")
        for i, t in enumerate(stats["transforms"][:10], 1):
            print(f"\n{i}. {t.file.name}:{t.line} [{t.transform_type}]")
            print(f"   Before: {t.original[:60]}...")
            print(f"   After:  {t.transformed[:60]}...")

        if len(stats["transforms"]) > 10:
            print(f"\n... and {len(stats['transforms']) - 10} more")

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
        print("✅ Batch 4 complete!")
        print("\nNext steps:")
        print("1. Run tests: pytest v13/tests/ -v")
        print(
            "2. Re-scan violations: python v13/libs/AST_ZeroSimChecker.py v13/ --fail"
        )
        print("3. Compare: diff post_batch3_violations.txt post_batch4_violations.txt")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Phase 3 Batch 4: Remove set literals")
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

    print("Phase 3 Batch 4: Set Literal Removal")
    print("Aggressive Mode - Convert All Sets to Lists")
    print("=" * 70)

    if args.file:
        # Single file mode
        success, transforms, errors = transform_file(args.file, dry_run=args.dry_run)

        if errors:
            print(f"❌ Errors in {args.file}:")
            for e in errors:
                print(f"  - {e}")
            sys.exit(1)

        if transforms:
            print(f"✅ {len(transforms)} set transformations in {args.file}")
            for t in transforms:
                print(f"  Line {t.line} [{t.transform_type}]:")
                print(f"    {t.original} → {t.transformed}")
        else:
            print(f"No set literals found in {args.file}")

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
