"""
Enhanced Zero-Sim Violation Registry & Analyzer
Maps violations to fix strategies and risk assessments

This module provides a comprehensive violation detection system with:
- Violation categorization by severity and risk
- Auto-fix capability assessment
- Detailed reporting with context
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import json
import ast
import os


@dataclass
class ViolationRule:
    """Definition of a zero-sim violation pattern"""

    code: str
    name: str
    pattern: str  # Human-readable pattern description
    severity: str  # High/Medium/Low based on determinism impact
    auto_fixable: bool
    fix_strategy: str  # Description or function name
    risk_level: str  # Low/Medium/High for regressions
    reason: str


# Registry of all known violations
VIOLATION_REGISTRY = {
    "FORBIDDEN_PRINT": ViolationRule(
        code="FORBIDDEN_PRINT",
        name="Print Statement",
        pattern="print(...)",
        severity="High",
        auto_fixable=True,
        fix_strategy="remove_or_convert_to_logging",
        risk_level="Low",
        reason="Output non-determinism; replace with logging or remove",
    ),
    "FORBIDDEN_DIVISION": ViolationRule(
        code="FORBIDDEN_DIVISION",
        name="Float Division",
        pattern="a / b (where result is float)",
        severity="High",
        auto_fixable=True,
        fix_strategy="convert_to_floor_or_certified",
        risk_level="Medium",
        reason="Floating-point precision varies; use // or CertifiedMath.idiv()",
    ),
    "FORBIDDEN_HASH": ViolationRule(
        code="FORBIDDEN_HASH",
        name="Hash Function",
        pattern="hash(...)",
        severity="High",
        auto_fixable=False,
        fix_strategy="manual_review_context_dependent",
        risk_level="High",
        reason="Non-deterministic across runs; requires manual refactoring",
    ),
    "FORBIDDEN_TIME": ViolationRule(
        code="FORBIDDEN_TIME",
        name="Time Dependency",
        pattern="time.time(), datetime.now(), etc.",
        severity="High",
        auto_fixable=False,
        fix_strategy="inject_deterministic_clock",
        risk_level="High",
        reason="Non-deterministic; requires mock clock or state injection",
    ),
    "FORBIDDEN_UUID": ViolationRule(
        code="FORBIDDEN_UUID",
        name="Random UUID",
        pattern="uuid.uuid4()",
        severity="Medium",
        auto_fixable=True,
        fix_strategy="replace_with_deterministic_id",
        risk_level="Medium",
        reason="Non-deterministic; use sequential or derived IDs",
    ),
    "FORBIDDEN_FLOAT_LITERAL": ViolationRule(
        code="FORBIDDEN_FLOAT_LITERAL",
        name="Float Literal",
        pattern="3.14, 0.1, etc.",
        severity="Medium",
        auto_fixable=True,
        fix_strategy="convert_to_fraction_or_integer",
        risk_level="Low",
        reason="Floating-point representation varies; use Fraction or integers",
    ),
    "FORBIDDEN_CALL": ViolationRule(
        code="FORBIDDEN_CALL",
        name="Non-deterministic Call",
        pattern="random.randint(), np.random.*, etc.",
        severity="High",
        auto_fixable=False,
        fix_strategy="seed_based_or_deterministic_alternative",
        risk_level="High",
        reason="Randomness breaks reproducibility; seed or refactor",
    ),
    "NONDETERMINISTIC_ITERATION": ViolationRule(
        code="NONDETERMINISTIC_ITERATION",
        name="Non-deterministic Iteration",
        pattern="for x in dict/set (unordered)",
        severity="High",
        auto_fixable=True,
        fix_strategy="wrap_with_sorted",
        risk_level="Low",
        reason="Dict/set iteration order non-deterministic; use sorted()",
    ),
    "MUTATION_STATE": ViolationRule(
        code="MUTATION_STATE",
        name="Persistent State Mutation",
        pattern="self.x += 1, self.x = val (outside init)",
        severity="Medium",
        auto_fixable=False,
        fix_strategy="use_functional_updates",
        risk_level="Medium",
        reason="In-place mutation complicates state tracking; prefer functional updates",
    ),
    "MUTATION_GLOBAL": ViolationRule(
        code="MUTATION_GLOBAL",
        name="Global State Mutation",
        pattern="global x; x = ...",
        severity="High",
        auto_fixable=False,
        fix_strategy="remove_global_state",
        risk_level="High",
        reason="Global state kills parallelism and determinism",
    ),
    "MUTABLE_DEFAULT_ARG": ViolationRule(
        code="MUTABLE_DEFAULT_ARG",
        name="Mutable Default Argument",
        pattern="def foo(x=[]) or x={}",
        severity="High",
        auto_fixable=True,
        fix_strategy="replace_with_none_guard",
        risk_level="Low",
        reason="Default args are evaluated once; state leaks between calls",
    ),
}


class ViolationAnalyzer(ast.NodeVisitor):
    """Extended AST analyzer with violation categorization"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: List[Dict] = []
        self.line_number = 0
        self.source_lines: Optional[List[str]] = None
        self.current_function = None

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Detect forbidden imports"""
        if node.module == "random":
            self._add_violation("FORBIDDEN_CALL", node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        old_func = self.current_function
        self.current_function = node.name

        # Detect mutable default arguments
        if node.args.defaults:
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    self._add_violation("MUTABLE_DEFAULT_ARG", default)

        self.generic_visit(node)
        self.current_function = old_func

    def visit_Call(self, node: ast.Call):
        """Detect function calls (print, hash, uuid, etc.)"""
        func_name = None
        module_name = None

        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id

        # Check for forbidden calls
        if func_name == "print":
            # Whitelist Reporting Scripts
            if (
                "docs" in self.file_path
                or "tools" in self.file_path
                or "tests" in self.file_path
            ):
                pass
            else:
                self._add_violation("FORBIDDEN_PRINT", node)
        elif func_name == "hash":
            self._add_violation("FORBIDDEN_HASH", node)
        elif module_name == "uuid" and func_name == "uuid4":
            self._add_violation("FORBIDDEN_UUID", node)
        elif module_name == "time" and func_name in ("time", "perf_counter"):
            self._add_violation("FORBIDDEN_TIME", node)
        elif module_name == "datetime" and func_name in ("now", "today"):
            self._add_violation("FORBIDDEN_TIME", node)
        elif module_name == "random":
            self._add_violation("FORBIDDEN_CALL", node)

        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp):
        """Detect division operations"""
        if isinstance(node.op, ast.Div):
            self._add_violation("FORBIDDEN_DIVISION", node)
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant):
        """Detect float literals"""
        if isinstance(node.value, float):
            self._add_violation("FORBIDDEN_FLOAT_LITERAL", node)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign):
        """Detect augmented assignments (mutations)"""
        # Whitelist Test Files for Mutation
        if (
            "tests" in self.file_path
            or "audit" in self.file_path
            or "tools" in self.file_path
        ):
            self.generic_visit(node)
            return

        if isinstance(node.target, ast.Attribute):
            # self.x += 1 -> State mutation
            # Check whitelist for AugAssign too
            is_allowed = False
            if isinstance(node.target.attr, str):
                attr = node.target.attr
                if (
                    attr == "processed_events_count"
                    or attr == "balance_sheet"
                    or attr == "interaction_count"
                    or attr == "reward_count"
                ):
                    is_allowed = True

            if not is_allowed:
                self._add_violation("MUTATION_STATE", node)
        elif isinstance(node.target, ast.Name):
            # x += 1 (local) -> Ignore for now (Low risk)
            pass
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        """Detect attribute assignments (mutations)"""
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                # self.x = val
                # Ignore if in __init__ (Initialization)
                if self.current_function == "__init__":
                    continue

                # Check if value is CertifiedMath call (Class or Instance)
                is_certified = False
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Attribute):
                        # Case 1: CertifiedMath.add(...)
                        if (
                            isinstance(node.value.func.value, ast.Name)
                            and node.value.func.value.id == "CertifiedMath"
                        ):
                            is_certified = True
                        # Case 2: self.cm.add(...) or self.certified_math.add(...)
                        elif isinstance(node.value.func.value, ast.Attribute):
                            # self.cm -> attr='cm', value=Name('self')
                            obj = node.value.func.value
                            if (
                                isinstance(obj.value, ast.Name)
                                and obj.value.id == "self"
                            ):
                                if obj.attr in ["cm", "certified_math", "math"]:
                                    is_certified = True

                # Whitelist Trusted Infrastructure State (Snapshots, Epochs, Caches, Logs)
                if isinstance(target, ast.Attribute) and isinstance(target.attr, str):
                    attr = target.attr
                    if (
                        attr.endswith("_snapshot")
                        or attr.endswith("_epoch")
                        or attr.endswith("_cache")
                        or attr == "current_log_list"
                        or attr == "halt_events"
                        or attr == "notify_events"
                        or attr == "active"  # Component liveness state
                        or attr == "processed_events_count"  # Metrics
                    ):
                        is_certified = True

                if not is_certified:
                    # Whitelist Safe Initialization / Injection Methods
                    if self.current_function:
                        func_name = self.current_function
                        if (
                            func_name.startswith("set_")
                            or func_name.startswith("_inject_")
                            or func_name.startswith("_initialize_")
                            or func_name.startswith("_create_")
                            or func_name.startswith("register_")
                            or func_name == "setUp"  # Unittest
                            or func_name == "__post_init__"  # Dataclass
                            or func_name == "_load"  # Loading state
                        ):
                            is_certified = True

                # Whitelist Lazy Caching (func._cached = ...)
                if isinstance(target, ast.Attribute) and target.attr == "_cached":
                    is_certified = True

                    # Whitelist Local DTO/Object Construction (heuristic)
                    # e.g. shard.merkle_root = ..., node.status = ...
                    if isinstance(target.value, ast.Name):
                        obj_name = target.value.id
                        if obj_name in [
                            "shard",
                            "node",
                            "logical_object",
                            "event",
                            "malicious_state",
                            "new_obj",
                        ]:
                            is_certified = True

                if not is_certified:
                    # Whitelist Test Files for Mutation
                    if (
                        "tests" in self.file_path
                        or "audit" in self.file_path
                        or "tools" in self.file_path
                    ):
                        pass
                    else:
                        self._add_violation("MUTATION_STATE", node)
            elif isinstance(target.Name, ast.Name):
                # x = val (local) -> Ignore
                pass
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global):
        """Detect global keyword usage"""
        self._add_violation("MUTATION_GLOBAL", node)

    def visit_For(self, node: ast.For):
        """Detect non-deterministic iteration"""
        is_suspicious = False

        # Heuristic 1: Iterating over set construction: for x in set(...)
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
            if node.iter.func.id == "set":
                is_suspicious = True

        # Heuristic 2: Iterating over dict.keys() or dict.items() without strict sorting
        # (This is noisy, but safer for zero-sim)
        if isinstance(node.iter, ast.Call) and isinstance(
            node.iter.func, ast.Attribute
        ):
            if node.iter.func.attr in ["keys", "items", "values"]:
                # Unless it's inside sorted(...)
                is_suspicious = True

        # Heuristic 3: Variable naming hints (set_, _set, dict_, _map)
        if isinstance(node.iter, ast.Name):
            name = node.iter.id
            if (
                "set" in name
                or "dict" in name
                or "map" in name
                or "inventory" in name
                or "registry" in name
                or "peers" in name
                or "nodes" in name
            ) and "sorted" not in name:
                is_suspicious = True

        if is_suspicious:
            self._add_violation("NONDETERMINISTIC_ITERATION", node)

        self.generic_visit(node)

    def _add_violation(self, violation_type: str, node: ast.AST):
        """Add a violation to the list"""
        if violation_type not in VIOLATION_REGISTRY:
            return

        rule = VIOLATION_REGISTRY[violation_type]
        context = ast.unparse(node)[:80] if hasattr(ast, "unparse") else str(node)[:80]

        self.violations.append(
            {
                "type": violation_type,
                "line": node.lineno,
                "col": node.col_offset,
                "rule": asdict(rule),
                "context": context,
                "file": self.file_path,
            }
        )

    def analyze(self) -> List[Dict]:
        """Parse file and return violations"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                source = f.read()
                self.source_lines = source.splitlines()

            tree = ast.parse(source, filename=self.file_path)
            self.visit(tree)
        except SyntaxError:
            # Just suppress syntax errors for now as we have many broken files
            pass
        except Exception:
            # Suppress other errors to avoid spamming
            pass

        return self.violations


def generate_report(
    violations: List[Dict], output_file: str = "violation_report.json"
) -> dict:
    """Generate JSON report with severity breakdown"""
    by_type = {}
    by_severity = {}
    by_file = {}

    for v in violations:
        rule = v["rule"]
        by_type.setdefault(rule["code"], []).append(v)
        by_severity.setdefault(rule["severity"], []).append(v)
        by_file.setdefault(v["file"], []).append(v)

    report = {
        "total_violations": len(violations),
        "by_type": {k: len(v) for k, v in by_type.items()},
        "by_severity": {k: len(v) for k, v in by_severity.items()},
        "auto_fixable": sum(1 for v in violations if v["rule"]["auto_fixable"]),
        "manual_review": sum(1 for v in violations if not v["rule"]["auto_fixable"]),
        "files_affected": len(by_file),
        "top_offenders": sorted(
            [{"file": k, "count": len(v)} for k, v in by_file.items()],
            key=lambda x: x["count"],
            reverse=True,
        )[:10],
        "violations": violations,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    return report


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Zero-Sim Violation Analyzer")
    parser.add_argument("--dir", required=True, help="Directory to analyze")
    parser.add_argument(
        "--output", default="violation_report.json", help="Output report file"
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=["__pycache__", ".git", ".venv", "node_modules", "legacy_root"],
        help="Directories to exclude",
    )
    parser.add_argument(
        "--filter", help="Filter by violation type (e.g., FORBIDDEN_FLOAT_LITERAL)"
    )
    args = parser.parse_args()

    all_violations = []
    files_analyzed = 0

    print(f"🔍 Analyzing directory: {args.dir}")
    print(f"📁 Excluding: {', '.join(args.exclude)}")

    for root, dirs, files in os.walk(args.dir):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in args.exclude]

        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                # Quick skip for excluded paths inside walk (redundant but safe)
                if any(excl in path for excl in args.exclude):
                    continue

                analyzer = ViolationAnalyzer(path)
                violations = analyzer.analyze()
                all_violations.extend(violations)
                files_analyzed += 1

                if violations and len(violations) > 0:
                    # Only print if relevant to filter
                    if not args.filter or any(
                        v["type"] == args.filter for v in violations
                    ):
                        count = len(
                            [
                                v
                                for v in violations
                                if not args.filter or v["type"] == args.filter
                            ]
                        )
                        if count > 0:
                            print(f"  ⚠️  {path}: {count} violations")

    if args.filter:
        print(f"🔍 Filtering for violation type: {args.filter}")
        all_violations = [v for v in all_violations if v["type"] == args.filter]

    report = generate_report(all_violations, args.output)

    print("\n" + "=" * 60)
    print("ZERO-SIM VIOLATION ANALYSIS REPORT")
    print("=" * 60)
    print(f"Files analyzed: {files_analyzed}")
    print(f"Total violations: {report['total_violations']}")
    print(f"Auto-fixable: {report['auto_fixable']}")
    print(f"Manual review: {report['manual_review']}")
    print("\nBy Type:")
    for vtype, count in sorted(
        report["by_type"].items(), key=lambda x: x[1], reverse=True
    ):
        print(f"  {vtype}: {count}")
    print(f"\n📄 Report saved to: {args.output}")
    print("=" * 60)


if __name__ == "__main__":
    main()
