"""
Syntax-preserving auto-fix for zero-sim violations.
Uses libcst to maintain formatting, comments, and structure.

This module provides safe, automated fixes for zero-sim violations.
"""

import libcst as cst
import libcst.matchers as m
from pathlib import Path
from typing import Tuple, List, Dict, Any, Set
import json
import logging
from fractions import Fraction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AddImportsTransformer(cst.CSTTransformer):
    """Add missing imports to the module"""

    def __init__(self, imports_to_add: Set[str]):
        self.imports_to_add = imports_to_add  # e.g. {"from fractions import Fraction"}
        self.added_count = 0
        self.existing_imports = set()

    def visit_ImportFrom(self, node: cst.ImportFrom):
        # Track existing imports to avoid duplicates
        if node.module:
            module_name = cst.helpers.get_full_name_for_node(node.module)
            for alias in node.names:
                if isinstance(alias, cst.ImportAlias):
                    name = alias.name.value
                    self.existing_imports.add(f"from {module_name} import {name}")
        return True

    def leave_Module(
        self, original_node: cst.Module, updated_node: cst.Module
    ) -> cst.Module:
        # Simple insertion at the top (after docstrings if possible, or just start)
        # This is basic; a full codemod is better but this suffices for "quick wins"

        new_body = list(updated_node.body)
        insertion_index = 0

        # Skip docstring and future imports
        for i, stmt in enumerate(new_body):
            if isinstance(stmt, cst.SimpleStatementLine):
                if isinstance(stmt.body[0], cst.Expr) and isinstance(
                    stmt.body[0].value, cst.SimpleString
                ):
                    insertion_index = i + 1
                    continue
                if (
                    isinstance(stmt.body[0], cst.ImportFrom)
                    and stmt.body[0].module
                    and stmt.body[0].module.value == "__future__"
                ):
                    insertion_index = i + 1
                    continue
            break

        added_stmts = []
        for imp_str in self.imports_to_add:
            if imp_str not in self.existing_imports:
                if imp_str == "from fractions import Fraction":
                    added_stmts.append(
                        cst.SimpleStatementLine(
                            body=[
                                cst.ImportFrom(
                                    module=cst.Name("fractions"),
                                    names=[cst.ImportAlias(name=cst.Name("Fraction"))],
                                )
                            ]
                        )
                    )
                    self.added_count += 1

        if added_stmts:
            for stmt in reversed(added_stmts):
                new_body.insert(insertion_index, stmt)
            return updated_node.with_changes(body=new_body)

        return updated_node


class PrintRemovalTransformer(cst.CSTTransformer):
    """Remove or convert print() calls to logging"""

    def __init__(self, mode="remove"):
        self.mode = mode
        self.removed_count = 0

    def leave_SimpleStatementLine(
        self,
        original_node: cst.SimpleStatementLine,
        updated_node: cst.SimpleStatementLine,
    ) -> cst.SimpleStatementLine:
        if len(updated_node.body) == 1:
            stmt = updated_node.body[0]
            if isinstance(stmt, cst.Expr) and isinstance(stmt.value, cst.Call):
                call = stmt.value
                if isinstance(call.func, cst.Name) and call.func.value == "print":
                    self.removed_count += 1
                    if self.mode == "remove":
                        return cst.RemovalSentinel.REMOVE
        return updated_node


class DivisionFixTransformer(cst.CSTTransformer):
    """Replace / with // or wrap in CertifiedMath.idiv()"""

    def __init__(self, mode="floor_div"):
        self.mode = mode
        self.fixed_count = 0

    def leave_BinaryOperation(
        self, original_node: cst.BinaryOperation, updated_node: cst.BinaryOperation
    ) -> cst.BaseExpression:
        if isinstance(updated_node.operator, cst.Divide):
            self.fixed_count += 1
            if self.mode == "floor_div":
                return updated_node.with_changes(operator=cst.FloorDivide())
        return updated_node


class UUIDFixTransformer(cst.CSTTransformer):
    """Replace uuid.uuid4() with deterministic ID"""

    def __init__(self, strategy="counter"):
        self.strategy = strategy
        self.fixed_count = 0

    def leave_Call(
        self, original_node: cst.Call, updated_node: cst.Call
    ) -> cst.BaseExpression:
        if m.matches(
            updated_node,
            m.Call(func=m.Attribute(value=m.Name("uuid"), attr=m.Name("uuid4"))),
        ):
            self.fixed_count += 1
            if self.strategy == "counter":
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
        self.strategy = strategy
        self.fixed_count = 0
        self.needs_fraction_import = False

    def leave_Float(
        self, original_node: cst.Float, updated_node: cst.Float
    ) -> cst.BaseExpression:
        try:
            val = float(original_node.value)

            # Category A1: Whole Numbers (e.g., 3.0 -> 3)
            if val.is_integer():
                self.fixed_count += 1
                return cst.Integer(value=str(int(val)))

            # Category A2: Simple Decimals (e.g. 0.5 -> Fraction(1, 2))
            if self.strategy in ("category-a-only", "aggressive"):
                # Safety check: simplistic conversion for now
                # Use standard library Fraction to find rational representation
                # Limit denominator to reasonable size to avoid crazy fractions for floating point errors
                f = Fraction(val).limit_denominator(100)

                # Check if exact match (or very close) and simple denominator
                if abs(float(f) - val) < 1e-9 and f.denominator in (
                    2,
                    4,
                    5,
                    8,
                    10,
                    20,
                    25,
                    50,
                    100,
                ):
                    self.fixed_count += 1
                    self.needs_fraction_import = True
                    return cst.Call(
                        func=cst.Name("Fraction"),
                        args=[
                            cst.Arg(cst.Integer(str(f.numerator))),
                            cst.Arg(cst.Integer(str(f.denominator))),
                        ],
                    )

        except ValueError:
            pass

        return updated_node


class NonDeterministicIterationFix(cst.CSTTransformer):
    """Wrap dict/set iterations with sorted()"""

    def __init__(self):
        self.fixed_count = 0

    def leave_For(self, original_node: cst.For, updated_node: cst.For) -> cst.For:
        if not isinstance(updated_node.iter, cst.Call):
            if isinstance(updated_node.iter, (cst.Name, cst.Attribute)):
                self.fixed_count += 1
                wrapped = cst.Call(
                    func=cst.Name("sorted"), args=[cst.Arg(value=updated_node.iter)]
                )
                return updated_node.with_changes(iter=wrapped)
        return updated_node


def apply_fixes(file_path: str, fixes: List[Tuple[str, dict]], dry_run=True) -> dict:
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

        # Track imports explicitly needed
        needed_imports = set()

        for fix_name, config in fixes:
            if fix_name == "PrintRemoval":
                transformer = PrintRemovalTransformer(**config)
                module = module.visit(transformer)
                count = transformer.removed_count
            elif fix_name == "DivisionFix":
                transformer = DivisionFixTransformer(**config)
                module = module.visit(transformer)
                count = transformer.fixed_count
            elif fix_name == "UUIDFix":
                transformer = UUIDFixTransformer(**config)
                module = module.visit(transformer)
                count = transformer.fixed_count
            elif fix_name == "FloatLiteralFix":
                transformer = FloatLiteralFixTransformer(**config)
                module = module.visit(transformer)
                count = transformer.fixed_count
                if transformer.needs_fraction_import:
                    needed_imports.add("from fractions import Fraction")
            elif fix_name == "IterationFix":
                transformer = NonDeterministicIterationFix()
                module = module.visit(transformer)
                count = transformer.fixed_count
            else:
                count = 0

            if count > 0:
                result["fixes_applied"].append({"type": fix_name, "count": count})

        # Apply imports if needed
        if needed_imports:
            import_transformer = AddImportsTransformer(needed_imports)
            module = module.visit(import_transformer)
            # Don't strictly count imports as "fixes" but they are changes

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
    parser.add_argument("--strategy", default="category-a-only", help="Fix strategy")
    args = parser.parse_args()

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
    print(f"Mode: {'DRY RUN' if args.dry_run else 'APPLIED'}")
    print(f"Report saved to: {args.output}")
    print("=" * 60)


if __name__ == "__main__":
    main()
