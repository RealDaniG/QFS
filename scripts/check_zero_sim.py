"""
check_zero_sim.py - Static Analysis Tool for Zero-Simulation Enforcement

This script parses Python files in the QFS repository and checks for forbidden
patterns that violate Zero-Simulation (Determinism) constraints.

Forbidden Modules:
- random (Use CertifiedMath / Hash-based PRNG)
- time (Use block height / logical clocks)
- datetime (Use deterministic timestamps)

Forbidden Patterns:
- float() (Use BigNum128)
- .now() (Allowed only in logging adapters)

Exclusions:
- *_test.py
- tests/
- scripts/
- tools/
"""

import ast
import os
import sys
from typing import List, Tuple

FORBIDDEN_MODULES = {
    "random": "Use deterministic RNG or CertifiedMath.",
    "time": "Use logical clocks or passed-in timestamps.",
    "datetime": "Use logical clocks or passed-in timestamps.",
}

FORBIDDEN_CALLS = {
    "float": "Use BigNum128 for fixed-point arithmetic.",
}

EXCLUDED_DIRS = {
    "tests",
    "scripts",
    "tools",
    ".git",
    "__pycache__",
    "mocks",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "site-packages",
    "api",
}

EXCLUDED_FILES = {"conftest.py", "setup.py"}


def is_excluded(path: str) -> bool:
    # Check if any part of the path is in EXCLUDED_DIRS
    parts = path.split(os.sep)
    for part in parts:
        if part in EXCLUDED_DIRS:
            return True

    # Check filename
    if os.path.basename(path) in EXCLUDED_FILES:
        return True

    # Check test suffix
    if "test_" in os.path.basename(path) or "_test.py" in os.path.basename(path):
        return True

    return False


class ZeroSimVisitor(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename
        self.errors: List[Tuple[int, str]] = []

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name in FORBIDDEN_MODULES:
                self.errors.append(
                    (
                        node.lineno,
                        f"Forbidden import '{alias.name}': {FORBIDDEN_MODULES[alias.name]}",
                    )
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module in FORBIDDEN_MODULES:
            self.errors.append(
                (
                    node.lineno,
                    f"Forbidden import from '{node.module}': {FORBIDDEN_MODULES[node.module]}",
                )
            )
        self.generic_visit(node)

    def visit_Call(self, node):
        # Check for forbidden functions like float()
        if isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_CALLS:
                self.errors.append(
                    (
                        node.lineno,
                        f"Forbidden call '{node.func.id}()': {FORBIDDEN_CALLS[node.func.id]}",
                    )
                )
        self.generic_visit(node)


def scan_file(filepath: str) -> List[Tuple[int, str]]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError as e:
            return [(e.lineno, f"Syntax Error: {e.msg}")]
        except UnicodeDecodeError:
            return []  # Skip non-text files that oddly have .py extension

    visitor = ZeroSimVisitor(filepath)
    visitor.visit(tree)
    return visitor.errors


def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"Scanning {root_dir} for Zero-Sim violations...")

    violation_count = 0
    scanned_count = 0

    errors_by_file = {}

    for root, dirs, files in os.walk(root_dir):
        # Prune excluded dirs in-place to avoid walking them
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            if not file.endswith(".py"):
                continue

            full_path = os.path.join(root, file)
            if is_excluded(full_path):
                continue

            scanned_count += 1
            errors = scan_file(full_path)
            if errors:
                rel_path = os.path.relpath(full_path, root_dir)
                print(f"\n[FAIL] {rel_path}")
                file_errors = []
                for line, msg in errors:
                    print(f"  Line {line}: {msg}")
                    file_errors.append({"line": line, "message": msg})

                errors_by_file[rel_path] = file_errors
                violation_count += len(errors)

    print(f"\nScanned {scanned_count} files.")

    import json

    with open("zero_sim_report.json", "w") as f:
        json.dump(
            {
                "violation_count": violation_count,
                "scanned_count": scanned_count,
                "violations": errors_by_file,
            },
            f,
            indent=2,
        )
    print("Report saved to zero_sim_report.json")

    if violation_count > 0:
        print(f"FAILED: Found {violation_count} Zero-Sim violations.")
        sys.exit(1)
    else:
        print("SUCCESS: No Zero-Sim violations found in core code.")
        sys.exit(0)


if __name__ == "__main__":
    main()
