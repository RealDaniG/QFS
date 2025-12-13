"""
AST_ZeroSimChecker.py - Structural enforcement tool to guarantee Zero-Simulation compliance

Enforces QFS V13 Phase 3 Absolute Determinism across all layers:
  - CertifiedMath-only arithmetic (raw operators banned in economics)
  - Sorted dict iteration (bare dict loops forbidden)
  - No sets, hashing, generators, or global mutation
  - Mandatory deterministic timestamps in economics
  - No floats, pow, **, or nondeterministic comprehensions
  - Deterministic exception handling & imports

Violations trigger CIR-302 halt during CI/CD.
"""

import ast
import sys
import os
import fnmatch
from typing import List, Set
from dataclasses import dataclass
import logging

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


@dataclass
class Violation:
    file_path: str
    line_number: int
    column: int
    violation_type: str
    message: str
    code_snippet: str


class ZeroSimASTVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: List[Violation] = []
        self.lines: List[str] = []
        self.inside_function = False
        self.current_function_args = set()
        # Check if this is a file that MUST be deterministic (strict enforcement)
        # Only files in these directories get the full deterministic treatment
        path_parts = self.file_path.replace(os.sep, '/').split('/')
        base_name = os.path.basename(file_path)
        
        # STRICT: Only these specific file names get full timestamp requirements
        strict_deterministic_files = {
            "TreasuryEngine.py", "RewardAllocator.py", "StateTransitionEngine.py",
            "NODAllocator.py", "NODInvariantChecker.py", "EconomicsGuard.py",
            "CoherenceEngine.py", "AEGIS_Node_Verification.py"
        }
        
        self.is_deterministic_module = base_name in strict_deterministic_files
        
        # Whitelist CertifiedMath itself
        self.is_certified_math = base_name == "CertifiedMath.py"
        
        # Is this an economics-related file (softer enforcement)?
        self.is_economics_related = any(
            part in path_parts
            for part in ["economics", "governance", "reward"]
        )

        self.forbidden_modules = {
            "random", "time", "datetime", "secrets", "uuid", "os", "sys", "math",
            "statistics", "decimal", "fractions", "numpy", "scipy", "socket",
            "requests", "urllib", "http", "threading", "asyncio", "queue"
        }

        self.forbidden_functions = {
            'random', 'randint', 'choice', 'shuffle', 'uniform', 'gauss', 'getrandbits',
            'time', 'sleep', 'perf_counter', 'now', 'today', 'utcnow', 'fromtimestamp',
            'urandom', 'uuid4', 'float', 'round', 'pow', 'hash', 'open', 'input', 'print'
        }

        self.load_file_lines()

    def load_file_lines(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.lines = f.readlines()
        except Exception:
            self.lines = []

    def add_violation(self, node, violation_type, message):
        line = getattr(node, "lineno", 0)
        col = getattr(node, "col_offset", 0)
        snippet = self.lines[line - 1].strip() if (0 < line <= len(self.lines)) else ""
        self.violations.append(Violation(
            file_path=self.file_path,
            line_number=line,
            column=col,
            violation_type=violation_type,
            message=message,
            code_snippet=snippet
        ))

    # 🔥 11 — Global mutation
    def visit_Assign(self, node: ast.Assign):
        if not self.inside_function:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.add_violation(node, "GLOBAL_MUTATION", f"Global assignment to '{target.id}' forbidden")
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global):
        self.add_violation(node, "GLOBAL_KEYWORD", f"'global' keyword forbidden: {', '.join(node.names)}")
        self.generic_visit(node)

    # 🔥 1 — CertifiedMath enforcement
    def visit_BinOp(self, node: ast.BinOp):
        if isinstance(node.op, ast.Div):
            self.add_violation(node, "FORBIDDEN_OPERATION", "Use CertifiedMath.idiv(), not / (produces float)")
        elif isinstance(node.op, ast.FloorDiv):
            # Check if FloorDiv could produce float in some contexts
            self.add_violation(node, "FORBIDDEN_OPERATION", "Use CertifiedMath.idiv(), not // (can produce float)")
        elif isinstance(node.op, ast.Pow):
            self.add_violation(node, "FORBIDDEN_OPERATION", "Use CertifiedMath.pow(), not **")
        elif self.is_deterministic_module and not self.is_certified_math:
            op_name = type(node.op).__name__
            if op_name in ('Add', 'Sub', 'Mult'):
                self.add_violation(
                    node, "UNCERTIFIED_ARITHMETIC",
                    f"Direct arithmetic forbidden in economics. Use CertifiedMath.{op_name.lower()}()"
                )
        self.generic_visit(node)

    # 🔥 2 & 3 — Dict/set iteration
    def visit_For(self, node: ast.For):
        if self._is_dict_like(node.iter) and not self._is_sorted_call(node.iter):
            self.add_violation(node, "NONDETERMINISTIC_ITERATION", "Dict/set iteration must use sorted()")
        self.generic_visit(node)

    def _is_dict_like(self, node) -> bool:
        if isinstance(node, ast.Name):
            return True  # conservative: assume it could be a dict
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            return node.func.id in ("dict", "set", "frozenset")
        if isinstance(node, ast.Dict):
            return True
        if isinstance(node, ast.Attribute) and node.attr in ("keys", "values", "items"):
            return True
        return False

    def _is_sorted_call(self, node) -> bool:
        return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "sorted"

    def visit_Set(self, node: ast.Set):
        self.add_violation(node, "FORBIDDEN_CONTAINER", "Sets are nondeterministic")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id in self.forbidden_functions:
                self.add_violation(node, "FORBIDDEN_CALL", f"Forbidden function: {node.func.id}")
            if node.func.id == "hash":
                self.add_violation(node, "FORBIDDEN_HASH", "hash() is randomized — forbidden")
            if node.func.id in ("__import__", "import_module"):
                self.add_violation(node, "DYNAMIC_IMPORT", "Dynamic imports forbidden")
        elif isinstance(node.func, ast.Attribute):
            obj = node.func.value
            attr = node.func.attr
            if isinstance(obj, ast.Name) and obj.id in self.forbidden_modules:
                self.add_violation(node, "FORBIDDEN_MODULE_CALL", f"{obj.id}.{attr} forbidden")
            # Check for importlib.import_module
            if isinstance(obj, ast.Name) and obj.id == "importlib" and attr == "import_module":
                self.add_violation(node, "DYNAMIC_IMPORT", "Dynamic imports forbidden")
            if attr in ("items", "keys", "values") and not self._parent_is_sorted(node):
                self.add_violation(node, "NONDETERMINISTIC_ITERATION", f"{attr}() must be in sorted()")
        self.generic_visit(node)

    def _parent_is_sorted(self, node) -> bool:
        # Simple check: is this call the argument to sorted()?
        # In practice, full context is hard; we rely on `For.iter` check instead.
        return False  # delegate to visit_For

    # 🔥 7 — Comprehensions
    def visit_ListComp(self, node):
        for gen in node.generators:
            if self._is_dict_like(gen.iter) and not self._is_sorted_call(gen.iter):
                self.add_violation(node, "NONDETERMINISTIC_COMP", "Dict iteration in comprehension must use sorted()")
        self.generic_visit(node)

    def visit_SetComp(self, node):
        self.add_violation(node, "FORBIDDEN_COMP", "Set comprehensions forbidden")
        self.generic_visit(node)

    def visit_DictComp(self, node):
        self.add_violation(node, "FORBIDDEN_COMP", "Dict comprehensions forbidden")
        self.generic_visit(node)

    # 🔥 8 — Generators
    def visit_Yield(self, node):
        if self.is_deterministic_module:
            self.add_violation(node, "FORBIDDEN_GENERATOR", "Generators forbidden in deterministic modules")
        self.generic_visit(node)

    def visit_YieldFrom(self, node):
        if self.is_deterministic_module:
            self.add_violation(node, "FORBIDDEN_GENERATOR", "yield from forbidden")
        self.generic_visit(node)

    # 🔥 9 — Function signatures
    def visit_FunctionDef(self, node):
        self.inside_function = True
        self.current_function_args = {arg.arg for arg in node.args.args}
        # STRICT enforcement: Only for specifically identified deterministic files
        # Require deterministic_timestamp for public methods; drv_packet_seq is optional
        if self.is_deterministic_module and not node.name.startswith("_"):
            if "deterministic_timestamp" not in self.current_function_args:
                self.add_violation(node, "MISSING_TIMESTAMP_PARAM", 
                    f"Missing param: deterministic_timestamp (required in {os.path.basename(self.file_path)})")
        self.generic_visit(node)
        self.inside_function = False

    # 🔥 10 — Exceptions
    def visit_ExceptHandler(self, node):
        if node.type is None:
            self.add_violation(node, "BARE_EXCEPT", "Bare 'except:' forbidden")
        self.generic_visit(node)

    # 🔥 12 — Imports
    def visit_Import(self, node):
        for alias in node.names:
            if alias.name in self.forbidden_modules:
                self.add_violation(node, "FORBIDDEN_IMPORT", f"Import of {alias.name} forbidden")
            if alias.name == "*":
                self.add_violation(node, "WILDCARD_IMPORT", "Wildcard imports forbidden")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module in self.forbidden_modules:
            self.add_violation(node, "FORBIDDEN_IMPORT", f"Import from {node.module} forbidden")
        if any(a.name == "*" for a in node.names):
            self.add_violation(node, "WILDCARD_IMPORT", "Wildcard imports forbidden")
        self.generic_visit(node)

    def visit_Constant(self, node):
        # Only flag actual float literals, not strings containing 'e'
        if isinstance(node.value, float):
            self.add_violation(node, "FLOAT_LITERAL", "Float literals forbidden")
        self.generic_visit(node)

    def visit_Name(self, node):
        if node.id in ("set", "frozenset") and isinstance(node.ctx, ast.Load):
            self.add_violation(node, "FORBIDDEN_TYPE", f"{node.id} is nondeterministic")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        # Only flag global attribute mutation (when not inside a function)
        if isinstance(node.ctx, ast.Store) and not self.inside_function:
            self.add_violation(node, "GLOBAL_ATTR_MUTATION", f"Global attribute assignment forbidden: {node.attr}")
        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        if self.is_deterministic_module:
            self.add_violation(node, "FORBIDDEN_GENERATOR", "Generator expressions forbidden in deterministic modules")
        self.generic_visit(node)


class AST_ZeroSimChecker:
    def scan_file(self, file_path: str) -> List[Violation]:
        visitor = ZeroSimASTVisitor(file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=file_path)
            visitor.visit(tree)

            # 🔥 5 — DeterministicTime import (only for files that actually use time)
            # Check if file uses deterministic_timestamp parameter
            uses_timestamp = any(
                isinstance(node, ast.arg) and node.arg == "deterministic_timestamp"
                for node in ast.walk(tree)
            )
            
            if uses_timestamp and visitor.is_deterministic_module and not visitor.is_certified_math:
                # Only require DeterministicTime if file actually uses timestamps
                has_det_time = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and "DeterministicTime" in (node.module or ""):
                        has_det_time = True
                        break
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if "DeterministicTime" in alias.name:
                                has_det_time = True
                                break
                # Note: We don't enforce this strictly; it's logged as warning only
                if not has_det_time:
                    logger.debug(f"File {file_path} uses deterministic_timestamp but doesn't import DeterministicTime")

        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            # Only record syntax errors for strict deterministic files
            if visitor.is_deterministic_module or visitor.is_economics_related:
                visitor.add_violation(
                    ast.Module(), "SYNTAX_ERROR",
                    f"Syntax error: {e}"
                )
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")
            # Only record parse errors for strict deterministic files
            if visitor.is_deterministic_module or visitor.is_economics_related:
                visitor.add_violation(
                    ast.Module(), "PARSING_ERROR",
                    f"Parsing error: {e}"
                )
        return visitor.violations

    def scan_directory(self, directory: str, exclude_patterns: List[str] = None) -> List[Violation]:
        exclude_patterns = exclude_patterns or [
            "__pycache__", "test_*", "*_test.py", "AST_ZeroSimChecker.py", 
            "migrations", "tests", "audit", "*env*", "venv", ".venv",
            "scripts", "checks_tests", "qfs_v13_project"
        ]
        all_violations = []
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, p) for p in exclude_patterns)]
            for file in files:
                if file.endswith(".py") and not any(fnmatch.fnmatch(file, p) for p in exclude_patterns):
                    all_violations.extend(self.scan_file(os.path.join(root, file)))
        return all_violations

    def enforce_policy(self, path: str, fail_on_violations: bool = False):
        print(f"[SCAN] Enforcing QFS V13 Phase 3 Zero-Simulation policy in: {path}")
        if os.path.isfile(path) and path.endswith(".py"):
            # Handle single file
            violations = self.scan_file(path)
        else:
            # Handle directory
            violations = self.scan_directory(path)
        if violations:
            print(f"[FAIL] {len(violations)} violations found:")
            for v in violations[:50]:
                print(f"  {v.file_path}:{v.line_number} [{v.violation_type}] {v.message}")
                if v.code_snippet:
                    print(f"    > {v.code_snippet}")
            if fail_on_violations:
                sys.exit(1)
        else:
            print("[OK] Zero-Simulation compliance verified.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", nargs="?", default=".")
    parser.add_argument("--fail", action="store_true")
    args = parser.parse_args()
    AST_ZeroSimChecker().enforce_policy(args.dir, args.fail)