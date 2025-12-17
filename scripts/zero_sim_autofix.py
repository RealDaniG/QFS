"""
Syntax-preserving auto-fix for zero-sim violations.
Uses libcst to maintain formatting, comments, and structure.

This module provides safe, automated fixes for determinism violations while
preserving code structure, comments, and formatting.
"""

import libcst as cst
import libcst.matchers as m
from pathlib import Path
from typing import Tuple, List, Dict, Any
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PrintRemovalTransformer(cst.CSTTransformer):
    """Remove or convert print() calls to logging"""

    def __init__(self, mode="remove", use_logging=False):
        self.mode = mode  # 'remove' or 'convert_to_logging'
        self.use_logging = use_logging
        self.removed_count = 0

    def leave_SimpleStatementLine(
        self,
        original_node: cst.SimpleStatementLine,
        updated_node: cst.SimpleStatementLine,
    ) -> cst.SimpleStatementLine:
        """Remove print statements while preserving structure"""
        # Check if this is a print() call
        if len(updated_node.body) == 1:
            stmt = updated_node.body[0]
            if isinstance(stmt, cst.Expr) and isinstance(stmt.value, cst.Call):
                call = stmt.value
                if isinstance(call.func, cst.Name) and call.func.value == "print":
                    self.removed_count += 1
                    if self.mode == "remove":
                        # Return RemovalSentinel to remove the statement
                        return cst.RemovalSentinel.REMOVE
                    elif self.mode == "convert_to_logging":
                        # Convert to logger.info(...) if logging imported
                        # For now, just remove; full implementation would check imports
                        return cst.RemovalSentinel.REMOVE
        return updated_node


class DivisionFixTransformer(cst.CSTTransformer):
    """Replace / with // or wrap in CertifiedMath.idiv()"""

    def __init__(self, mode="floor_div"):
        self.mode = mode  # 'floor_div' or 'certified_math'
        self.fixed_count = 0

    def leave_BinaryOperation(
        self, original_node: cst.BinaryOperation, updated_node: cst.BinaryOperation
    ) -> cst.BaseExpression:
        """Replace division operators"""
        if isinstance(updated_node.operator, cst.Divide):
            self.fixed_count += 1
            if self.mode == "floor_div":
                return updated_node.with_changes(operator=cst.FloorDivide())
            elif self.mode == "certified_math":
                # Wrap in CertifiedMath.idiv(left, right)
                call = cst.Call(
                    func=cst.Attribute(
                        value=cst.Name("CertifiedMath"), attr=cst.Name("idiv")
                    ),
                    args=[
                        cst.Arg(value=updated_node.left),
                        cst.Arg(value=updated_node.right),
                    ],
                )
                return call
        return updated_node


class UUIDFixTransformer(cst.CSTTransformer):
    """Replace uuid.uuid4() with deterministic ID"""

    def __init__(self, strategy="counter"):
        self.strategy = strategy  # 'counter', 'hash', or 'derived'
        self.fixed_count = 0

    def leave_Call(
        self, original_node: cst.Call, updated_node: cst.Call
    ) -> cst.BaseExpression:
        """Replace uuid.uuid4() calls"""
        # Match uuid.uuid4()
        if m.matches(
            updated_node,
            m.Call(func=m.Attribute(value=m.Name("uuid"), attr=m.Name("uuid4"))),
        ):
            self.fixed_count += 1
            if self.strategy == "counter":
                # Replace with DeterministicID.next()
                return cst.Call(
                    func=cst.Attribute(
                        value=cst.Name("DeterministicID"), attr=cst.Name("next")
                    ),
                    args=[],
                )
        return updated_node


class FloatLiteralFixTransformer(cst.CSTTransformer):
    """Replace float literals with integers or Fractions"""

    def __init__(self, strategy="category-a-only"):
        self.strategy = strategy  # 'category-a-only'
        self.fixed_count = 0

    def leave_Float(
        self, original_node: cst.Float, updated_node: cst.Float
    ) -> cst.BaseExpression:
        """Replace floating point literals"""
        try:
            val = float(original_node.value)

            # Category A1: Whole Numbers (e.g., 3.0 -> 3)
            # Check if it has no fractional part
            if val.is_integer():
                self.fixed_count += 1
                return cst.Integer(value=str(int(val)))

            # Note: Category A2 (Simple Decimals -> Fraction) implementation deferred
            # to avoid import complexity. Future batch will handle this via AddImports.

        except ValueError:
            pass

        return updated_node


class NonDeterministicIterationFix(cst.CSTTransformer):
    """Wrap dict/set iterations with sorted()"""

    def __init__(self):
        self.fixed_count = 0

    def leave_For(self, original_node: cst.For, updated_node: cst.For) -> cst.For:
        """Wrap iteration targets with sorted() if needed"""
        # Simplified: wrap all iterations with sorted()
        # Full implementation would check if iterating over dict/set
        if not isinstance(updated_node.iter, cst.Call):
            # Not already a function call, potentially needs wrapping
            # Check if it's a simple name or attribute (could be dict/set)
            if isinstance(updated_node.iter, (cst.Name, cst.Attribute)):
                self.fixed_count += 1
                wrapped = cst.Call(
                    func=cst.Name("sorted"), args=[cst.Arg(value=updated_node.iter)]
                )
                return updated_node.with_changes(iter=wrapped)
        return updated_node


def apply_fixes(file_path: str, fixes: List[Tuple[str, dict]], dry_run=True) -> dict:
    """
    Apply a series of fixes to a file.

    Args:
        file_path: Path to Python file
        fixes: List of (transformer_class_name, config_dict)
        dry_run: If True, don't write changes

    Returns:
        dict with counts and status
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()

        module = cst.parse_module(source_code)
        result = {
            "file": file_path,
            "original_length": len(source_code),
            "fixes_applied": [],
            "error": None,
        }

        for fix_name, config in fixes:
            if fix_name == "PrintRemoval":
                transformer = PrintRemovalTransformer(**config)
                module = module.visit(transformer)
                result["fixes_applied"].append(
                    {
                        "type": "PrintRemoval",
                        "count": transformer.removed_count,
                    }
                )
            elif fix_name == "DivisionFix":
                transformer = DivisionFixTransformer(**config)
                module = module.visit(transformer)
                result["fixes_applied"].append(
                    {
                        "type": "DivisionFix",
                        "count": transformer.fixed_count,
                    }
                )
            elif fix_name == "UUIDFix":
                transformer = UUIDFixTransformer(**config)
                module = module.visit(transformer)
                result["fixes_applied"].append(
                    {
                        "type": "UUIDFix",
                        "count": transformer.fixed_count,
                    }
                )
            elif fix_name == "FloatLiteralFix":
                transformer = FloatLiteralFixTransformer(**config)
                module = module.visit(transformer)
                result["fixes_applied"].append(
                    {
                        "type": "FloatLiteralFix",
                        "count": transformer.fixed_count,
                    }
                )
            elif fix_name == "IterationFix":
                transformer = NonDeterministicIterationFix()
                module = module.visit(transformer)
                result["fixes_applied"].append(
                    {
                        "type": "IterationFix",
                        "count": transformer.fixed_count,
                    }
                )

        new_code = module.code
        result["new_length"] = len(new_code)
        result["changed"] = new_code != source_code

        if not dry_run and result["changed"]:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_code)
            total_fixes = sum(f["count"] for f in result["fixes_applied"])
            logger.info(f"✅ Fixed {file_path}: {total_fixes} issues")

        return result

    except Exception as e:
        logger.error(f"❌ Error processing {file_path}: {e}")
        return {
            "file": file_path,
            "error": str(e),
            "fixes_applied": [],
            "changed": False,
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Zero-Sim Auto-Fix with libcst")
    parser.add_argument("--dir", required=True, help="Directory to fix")
    parser.add_argument(
        "--fixes", default="PrintRemoval,DivisionFix", help="Comma-separated fix list"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    parser.add_argument("--output", default="fix_report.json", help="Report file")
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=["__pycache__", ".git", ".venv", "node_modules"],
        help="Directories to exclude",
    )
    parser.add_argument(
        "--strategy",
        default="category-a-only",
        help="Fix strategy needed for FloatLiteralFix",
    )
    args = parser.parse_args()

    # Parse fix configuration
    fix_configs = {
        "PrintRemoval": {"mode": "remove"},
        "DivisionFix": {"mode": "floor_div"},
        "UUIDFix": {"strategy": "counter"},
        "FloatLiteralFix": {"strategy": args.strategy},
        "IterationFix": {},
    }

    requested_fixes = args.fixes.split(",")
    fixes = [
        (name.strip(), fix_configs.get(name.strip(), {}))
        for name in requested_fixes
        if name.strip() in fix_configs
    ]

    print(f"🔧 Auto-Fix Configuration:")
    print(f"  Directory: {args.dir}")
    print(f"  Fixes: {', '.join(f[0] for f in fixes)}")
    print(f"  Strategy: {args.strategy}")
    print(f"  Dry Run: {args.dry_run}")
    print()

    results = []
    files_processed = 0
    files_changed = 0

    for py_file in Path(args.dir).rglob("*.py"):
        # Skip excluded directories
        if any(excl in str(py_file) for excl in args.exclude):
            continue

        result = apply_fixes(str(py_file), fixes, dry_run=args.dry_run)
        results.append(result)
        files_processed += 1

        if result.get("changed"):
            files_changed += 1
            total_fixes = sum(f["count"] for f in result["fixes_applied"])
            print(
                f"  {'[DRY RUN] ' if args.dry_run else ''}Fixed {py_file.name}: {total_fixes} issues"
            )

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print("AUTO-FIX SUMMARY")
    print("=" * 60)
    print(f"Files processed: {files_processed}")
    print(f"Files changed: {files_changed}")
    print(f"Mode: {'DRY RUN (no changes written)' if args.dry_run else 'APPLIED'}")
    print(f"Report saved to: {args.output}")
    print("=" * 60)


if __name__ == "__main__":
    main()
