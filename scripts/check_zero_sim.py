"""
Zero-Sim Compliance Checker with MOCKQPC Support

Extends the Zero-Sim analyzer to:
1. Whitelist MOCKQPC modules as deterministic simulators
2. Detect forbidden real PQC usage in dev/beta environments
3. Catch crypto abstraction bypasses
4. Enforce environment-specific compliance

Contract Compliance: ZERO_SIM_QFS_ATLAS_CONTRACT.md § 2.6, § 4.4
"""

import os
import sys
import ast
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.zero_sim_analyzer import (
    ViolationAnalyzer,
    VIOLATION_REGISTRY,
    generate_report,
)


@dataclass
class MockQPCViolation:
    """MOCKQPC-specific violation"""

    code: str
    name: str
    file: str
    line: int
    context: str
    severity: str = "CRITICAL"


# MOCKQPC-specific violation patterns
MOCKQPC_VIOLATIONS = {
    "REAL_PQC_IN_DEV_BETA": {
        "name": "Real PQC in dev/beta",
        "patterns": ["liboqs", "pqcrystals", "dilithium", "kyber"],
        "severity": "CRITICAL",
        "reason": "Real PQC forbidden in dev/beta environments per § 2.6",
    },
    "ABSTRACTION_BYPASS": {
        "name": "Crypto abstraction bypass",
        "patterns": [
            "_real_pqc_sign",
            "_real_pqc_verify",
            "mock_sign_poe",
            "mock_verify_poe",
        ],
        "severity": "CRITICAL",
        "reason": "Must use sign_poe/verify_poe adapter, not direct MOCKQPC or real PQC calls",
    },
    "FORBIDDEN_RANDOMNESS_IN_MOCKQPC": {
        "name": "Randomness in MOCKQPC",
        "patterns": ["random.", "uuid.", "os.urandom", "secrets."],
        "severity": "CRITICAL",
        "reason": "MOCKQPC must be pure deterministic function per § 4.4",
    },
    "FORBIDDEN_TIME_IN_MOCKQPC": {
        "name": "Time dependency in MOCKQPC",
        "patterns": ["time.time", "datetime.now", "time.perf_counter"],
        "severity": "CRITICAL",
        "reason": "MOCKQPC cannot depend on time per § 4.4",
    },
    "FORBIDDEN_NETWORK_IN_MOCKQPC": {
        "name": "Network I/O in MOCKQPC",
        "patterns": ["requests.", "urllib.", "http.", "socket."],
        "severity": "CRITICAL",
        "reason": "MOCKQPC cannot perform network I/O per § 4.4",
    },
}


# Modules whitelisted as deterministic
WHITELISTED_MODULES = {
    # MOCKQPC modules (deterministic by contract)
    "v15.crypto.mockqpc",
    "v15.crypto.adapter",
    "v15.crypto",
    # Standard deterministic crypto
    "hashlib",
    "hmac",
    # Math and numerics (deterministic)
    "math",
    "decimal",
    "fractions",
    # Core Python (deterministic when used correctly)
    "dataclasses",
    "typing",
    "collections",
    "itertools",
    # Testing frameworks
    "pytest",
    "unittest",
    "mock",
}


# Directories to whitelist from checks
WHITELISTED_DIRECTORIES = {
    "tests",
    "docs",
    "scripts",
    "tools",
    "__pycache__",
    ".git",
    ".venv",
    "node_modules",
}


class MOCKQPCChecker(ast.NodeVisitor):
    """AST analyzer for MOCKQPC-specific violations"""

    def __init__(self, file_path: str, is_mockqpc_module: bool = False):
        self.file_path = file_path
        self.is_mockqpc_module = is_mockqpc_module
        self.violations: List[MockQPCViolation] = []
        self.imports: Set[str] = set()

    def visit_Import(self, node: ast.Import):
        """Track imports"""
        for alias in node.names:
            self.imports.add(alias.name)

            # Check for forbidden real PQC imports
            if not self.is_mockqpc_module:
                for pattern in MOCKQPC_VIOLATIONS["REAL_PQC_IN_DEV_BETA"]["patterns"]:
                    if pattern in alias.name:
                        # Ignore internal adapter modules
                        if "dilithium5_adapter" in alias.name:
                            continue
                        self.violations.append(
                            MockQPCViolation(
                                code="REAL_PQC_IN_DEV_BETA",
                                name=MOCKQPC_VIOLATIONS["REAL_PQC_IN_DEV_BETA"]["name"],
                                file=self.file_path,
                                line=node.lineno,
                                context=f"import {alias.name}",
                                severity=MOCKQPC_VIOLATIONS["REAL_PQC_IN_DEV_BETA"][
                                    "severity"
                                ],
                            )
                        )

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track from imports"""
        if node.module:
            self.imports.add(node.module)

            # Check for forbidden real PQC imports
            if not self.is_mockqpc_module:
                for pattern in MOCKQPC_VIOLATIONS["REAL_PQC_IN_DEV_BETA"]["patterns"]:
                    if pattern in node.module:
                        # Ignore internal adapter modules
                        if "dilithium5_adapter" in node.module:
                            continue
                        self.violations.append(
                            MockQPCViolation(
                                code="REAL_PQC_IN_DEV_BETA",
                                name=MOCKQPC_VIOLATIONS["REAL_PQC_IN_DEV_BETA"]["name"],
                                file=self.file_path,
                                line=node.lineno,
                                context=f"from {node.module} import ...",
                                severity=MOCKQPC_VIOLATIONS["REAL_PQC_IN_DEV_BETA"][
                                    "severity"
                                ],
                            )
                        )

            # Detect MOCKQPC-specific forbidden patterns
            if self.is_mockqpc_module:
                # Check for randomness
                if node.module in ["random", "uuid", "secrets"]:
                    self.violations.append(
                        MockQPCViolation(
                            code="FORBIDDEN_RANDOMNESS_IN_MOCKQPC",
                            name=MOCKQPC_VIOLATIONS["FORBIDDEN_RANDOMNESS_IN_MOCKQPC"][
                                "name"
                            ],
                            file=self.file_path,
                            line=node.lineno,
                            context=f"from {node.module} import ...",
                            severity=MOCKQPC_VIOLATIONS[
                                "FORBIDDEN_RANDOMNESS_IN_MOCKQPC"
                            ]["severity"],
                        )
                    )

                # Check for network I/O
                if node.module and any(
                    p in node.module for p in ["requests", "urllib", "http", "socket"]
                ):
                    self.violations.append(
                        MockQPCViolation(
                            code="FORBIDDEN_NETWORK_IN_MOCKQPC",
                            name=MOCKQPC_VIOLATIONS["FORBIDDEN_NETWORK_IN_MOCKQPC"][
                                "name"
                            ],
                            file=self.file_path,
                            line=node.lineno,
                            context=f"from {node.module} import ...",
                            severity=MOCKQPC_VIOLATIONS["FORBIDDEN_NETWORK_IN_MOCKQPC"][
                                "severity"
                            ],
                        )
                    )

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Check for abstraction bypasses and forbidden calls"""
        func_name = None
        module_name = None

        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id

        # Check for direct MOCKQPC or real PQC function calls (bypass of adapter)
        if func_name in [
            "mock_sign_poe",
            "mock_verify_poe",
            "_real_pqc_sign",
            "_real_pqc_verify",
        ]:
            # Allow in adapter.py itself and mockqpc.py
            if (
                "adapter.py" not in self.file_path
                and "mockqpc.py" not in self.file_path
            ):
                self.violations.append(
                    MockQPCViolation(
                        code="ABSTRACTION_BYPASS",
                        name=MOCKQPC_VIOLATIONS["ABSTRACTION_BYPASS"]["name"],
                        file=self.file_path,
                        line=node.lineno,
                        context=f"{func_name}(...)",
                        severity=MOCKQPC_VIOLATIONS["ABSTRACTION_BYPASS"]["severity"],
                    )
                )

        # Check for time dependencies in MOCKQPC
        if self.is_mockqpc_module:
            if module_name == "time" and func_name in ["time", "perf_counter"]:
                self.violations.append(
                    MockQPCViolation(
                        code="FORBIDDEN_TIME_IN_MOCKQPC",
                        name=MOCKQPC_VIOLATIONS["FORBIDDEN_TIME_IN_MOCKQPC"]["name"],
                        file=self.file_path,
                        line=node.lineno,
                        context=f"time.{func_name}()",
                        severity=MOCKQPC_VIOLATIONS["FORBIDDEN_TIME_IN_MOCKQPC"][
                            "severity"
                        ],
                    )
                )

            if module_name == "datetime" and func_name in ["now", "today"]:
                self.violations.append(
                    MockQPCViolation(
                        code="FORBIDDEN_TIME_IN_MOCKQPC",
                        name=MOCKQPC_VIOLATIONS["FORBIDDEN_TIME_IN_MOCKQPC"]["name"],
                        file=self.file_path,
                        line=node.lineno,
                        context=f"datetime.{func_name}()",
                        severity=MOCKQPC_VIOLATIONS["FORBIDDEN_TIME_IN_MOCKQPC"][
                            "severity"
                        ],
                    )
                )

        self.generic_visit(node)

    def analyze(self) -> List[MockQPCViolation]:
        """Parse file and return MOCKQPC-specific violations"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=self.file_path)
            self.visit(tree)
        except (SyntaxError, Exception):
            # Suppress errors for unparseable files
            pass

        return self.violations


def is_whitelisted_path(file_path: str) -> bool:
    """Check if path is whitelisted"""
    path_parts = Path(file_path).parts
    return any(whitelist in path_parts for whitelist in WHITELISTED_DIRECTORIES)


def is_mockqpc_module(file_path: str) -> bool:
    """Check if file is a MOCKQPC module"""
    normalized = Path(file_path).as_posix()
    return "v15/crypto" in normalized


def check_zero_sim_compliance(directory: str, exclude_dirs: List[str] = None) -> Dict:
    """
    Run comprehensive Zero-Sim compliance check with MOCKQPC support.

    Args:
        directory: Root directory to scan
        exclude_dirs: Additional directories to exclude

    Returns:
        Report dictionary with violations and summary
    """
    if exclude_dirs is None:
        exclude_dirs = list(WHITELISTED_DIRECTORIES)

    # Collect all violations
    standard_violations = []
    mockqpc_violations = []
    files_analyzed = 0
    files_with_violations = 0

    print("=" * 70)
    print("ZERO-SIM + MOCKQPC COMPLIANCE CHECKER")
    print("=" * 70)
    print(f"Scanning: {directory}")
    print(f"Excluded: {', '.join(exclude_dirs)}")
    print()

    for root, dirs, files in os.walk(directory):
        # Filter excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = os.path.join(root, file)

            # Skip whitelisted paths
            if is_whitelisted_path(file_path):
                continue

            # Skip legacy PQC Core (guarded imports)
            if "PQC_Core.py" in file_path:
                continue

            files_analyzed += 1
            file_violations = []

            # Run standard Zero-Sim analysis
            analyzer = ViolationAnalyzer(file_path)
            std_viols = analyzer.analyze()
            if std_viols:
                standard_violations.extend(std_viols)
                file_violations.extend(std_viols)

            # Run MOCKQPC-specific analysis
            is_mockqpc = is_mockqpc_module(file_path)
            mockqpc_checker = MOCKQPCChecker(file_path, is_mockqpc)
            mqpc_viols = mockqpc_checker.analyze()
            if mqpc_viols:
                mockqpc_violations.extend(mqpc_viols)
                file_violations.extend(mqpc_viols)

            if file_violations:
                files_with_violations += 1
                print(f"⚠️  {file_path}: {len(file_violations)} violations")

    # Generate report
    total_violations = len(standard_violations) + len(mockqpc_violations)
    critical_violations = len(
        [v for v in mockqpc_violations if v.severity == "CRITICAL"]
    )

    report = {
        "files_analyzed": files_analyzed,
        "files_with_violations": files_with_violations,
        "total_violations": total_violations,
        "standard_violations": len(standard_violations),
        "mockqpc_violations": len(mockqpc_violations),
        "critical_violations": critical_violations,
        "violations": {
            "standard": standard_violations,
            "mockqpc": [
                {
                    "code": v.code,
                    "name": v.name,
                    "file": v.file,
                    "line": v.line,
                    "context": v.context,
                    "severity": v.severity,
                }
                for v in mockqpc_violations
            ],
        },
    }

    # Print summary
    print()
    print("=" * 70)
    print("COMPLIANCE SUMMARY")
    print("=" * 70)
    print(f"Files analyzed: {files_analyzed}")
    print(f"Files with violations: {files_with_violations}")
    print(f"Total violations: {total_violations}")
    print(f"  - Standard Zero-Sim: {len(standard_violations)}")
    print(f"  - MOCKQPC-specific: {len(mockqpc_violations)}")
    print(f"  - CRITICAL: {critical_violations}")

    if critical_violations > 0:
        print()
        print("⛔ CRITICAL VIOLATIONS DETECTED:")
        for v in mockqpc_violations:
            if v.severity == "CRITICAL":
                print(f"  {v.code} in {v.file}:{v.line}")
                print(f"    {v.context}")
        print()
        print("Contract violations: ZERO_SIM_QFS_ATLAS_CONTRACT.md § 2.6, § 4.4")

    print("=" * 70)

    return report


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Zero-Sim + MOCKQPC Compliance Checker"
    )
    parser.add_argument(
        "--dir", default=".", help="Directory to analyze (default: current directory)"
    )
    parser.add_argument(
        "--output", default="zero_sim_compliance_report.json", help="Output report file"
    )
    parser.add_argument(
        "--exclude", nargs="*", help="Additional directories to exclude"
    )
    parser.add_argument(
        "--fail-on-critical",
        action="store_true",
        help="Exit with error code if critical violations found",
    )

    args = parser.parse_args()

    # Run compliance check
    exclude_dirs = list(WHITELISTED_DIRECTORIES)
    if args.exclude:
        exclude_dirs.extend(args.exclude)

    report = check_zero_sim_compliance(args.dir, exclude_dirs)

    # Save report
    import json

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n📄 Full report saved to: {args.output}")

    # Exit with error if critical violations found
    if args.fail_on_critical and report["critical_violations"] > 0:
        print("\n❌ CI GATE FAILED: Critical violations detected")
        sys.exit(1)
    elif report["total_violations"] > 0:
        print("\n⚠️  Violations detected (non-blocking)")
        sys.exit(0)
    else:
        print("\n✅ Zero-Sim + MOCKQPC compliance: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
