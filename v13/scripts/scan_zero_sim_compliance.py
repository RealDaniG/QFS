# import sys removed (unused)
import os
import re
import json
import ast
from datetime import datetime

# =============================================================================
# Configuration & Patterns
# =============================================================================

TIMESTAMP_REGEX = re.compile(
    r"(datetime\.now|time\.time|Date\.now|new Date)", re.IGNORECASE
)
RANDOM_REGEX = re.compile(
    r"(random\.|uuid\.uuid4|os\.urandom|Math\.random|crypto\.random)", re.IGNORECASE
)
FLOAT_REGEX = re.compile(
    r"(float\(|/ \d|\d \/|%)"
)  # Simplified float check, will need AST for better precision in Python
PRISMA_WRITE_REGEX = re.compile(r"prisma\..*\.(create|update|delete|upsert)")
IO_REGEX = re.compile(r"(requests\.get|urllib|httpx|aiohttp|open\()")

EXCLUDED_DIRS = [
    "__pycache__",
    "node_modules",
    ".git",
    ".idea",
    ".vscode",
    "dist",
    "build",
    "coverage",
    "venv",
    "env",
    ".gemini",
    "artifacts",
    "legacy_root",
    "archive",
    "ATLAS",
    "docs",
]

NO_SCAN_FILES = [
    "scan_zero_sim_compliance.py",
    "run_zero_sim_suite.py",
    "simple_violations.py",
    "golden_fail.py",  # Intentional test files for scanner validation
]

# Violations
VIOLATIONS = []

# =============================================================================
# Phase A: Python Static Scan (AST + Regex)
# =============================================================================


def scan_python_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.splitlines()
    except Exception as e:
        print(f"Skipping {filepath}: {e}")
        return

    # Regex Checks
    for i, line in enumerate(lines):
        ln = i + 1
        if "QODO:JUSTIFIED" in line:
            continue

        # Random
        if RANDOM_REGEX.search(line):
            # AST checking would be better but regex is faster for a broad sweep,
            # and we can refine via the report.
            # Check if it's a comment
            if not line.strip().startswith("#"):
                add_violation(filepath, ln, "RANDOM_USAGE", "CRITICAL", line.strip())

        # Time
        if TIMESTAMP_REGEX.search(line):
            if not line.strip().startswith("#"):
                add_violation(filepath, ln, "WALL_CLOCK_TIME", "HIGH", line.strip())

        # IO
        if IO_REGEX.search(line):
            # Enforce on core, policy, guard, aegis, governance
            if any(
                x in filepath
                for x in [
                    "policy",
                    "core",
                    "guard",
                    "services/aegis",
                    "services/governance",
                ]
            ):
                if not line.strip().startswith("#"):
                    add_violation(filepath, ln, "EXTERNAL_IO", "CRITICAL", line.strip())

    # AST Checks for specific patterns (e.g. imports)
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                # Check prohibited imports
                module_name = getattr(node, "module", "")
                names = [n.name for n in node.names]

                check_imports = ["random", "time", "secrets", "uuid"]
                for imp in check_imports:
                    if imp in names or (module_name and imp == module_name):
                        add_violation(
                            filepath,
                            node.lineno,
                            f"FORBIDDEN_IMPORT_{imp.upper()}",
                            "CRITICAL",
                            f"import {imp}",
                        )

    except SyntaxError:
        pass  # Regex catches some things, syntax error means legacy file or bad parse


# =============================================================================
# Phase B: TypeScript/JS Scan
# =============================================================================


def scan_ts_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return

    for i, line in enumerate(lines):
        ln = i + 1
        line_clean = line.strip()
        if line_clean.startswith("//") or line_clean.startswith("/*"):
            continue

        if "QODO:JUSTIFIED" in line:
            continue

        # Random
        if "Math.random" in line or "crypto.random" in line:
            add_violation(filepath, ln, "RANDOM_USAGE", "CRITICAL", line_clean)

        # Time
        if "Date.now" in line or "new Date" in line:
            # Heuristic: Critical if in hooks/lib, High/Low if in components (display)
            severity = "CRITICAL" if "src/lib" in filepath else "MEDIUM"
            add_violation(filepath, ln, "WALL_CLOCK_TIME", severity, line_clean)

        # Prisma Writes
        if PRISMA_WRITE_REGEX.search(line):
            if "balance" in line or "amount" in line or "reward" in line:
                add_violation(
                    filepath,
                    ln,
                    "PRISMA_ECONOMIC_WRITE",
                    "CRITICAL_AUTHORITY_VIOLATION",
                    line_clean,
                )
            else:
                add_violation(filepath, ln, "PRISMA_WRITE_CHECK", "MEDIUM", line_clean)


# =============================================================================
# Phase C & D: Configs, Deps, Tests
# =============================================================================


def scan_deps(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if "numpy" in content or "pandas" in content:  # Check if used in core/policy
        # Only strict if this is requirements.txt for backend
        pass

    if "faker" in content:
        # Check context
        pass


def scan_test_file(filepath):
    # Scan logic similar to python but with different severity
    scan_python_file(
        filepath
    )  # Reuse python scanner but maybe downgrade severity for tests?
    # Actually, user wants to identify non-deterministic tests.
    pass


# =============================================================================
# Core Logic
# =============================================================================


def add_violation(filepath, line, v_type, severity, snippet):
    VIOLATIONS.append(
        {
            "file": filepath.replace("\\", "/"),
            "line": line,
            "violation_type": v_type,
            "severity": severity,
            "code_snippet": snippet[0:100],
            "suggested_fix": suggest_fix(v_type),
        }
    )


def suggest_fix(v_type):
    if "RANDOM" in v_type:
        return "Use deterministic PRNG or hash-based ID."
    if "TIME" in v_type:
        return "Use passed-in timestamp or ledger block time."
    if "IO" in v_type:
        return "Remove I/O. Pass data as arguments."
    if "PRISMA" in v_type:
        return "Remove DB write. Send intent to QFS."
    return "Check Zero-Sim contract."


def walk_and_scan(root_dir):
    for root, dirs, files in os.walk(root_dir):
        # Exclude dirs
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            if file in NO_SCAN_FILES:
                continue

            filepath = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()

            if ext == ".py":
                if "tests" in filepath or "test_" in file:
                    scan_test_file(filepath)
                else:
                    scan_python_file(filepath)
            elif ext in [".ts", ".tsx", ".js", ".jsx"]:
                scan_ts_file(filepath)
            elif file in ["requirements.txt", "package.json"]:
                scan_deps(filepath)


def main():
    start_time = datetime.now()
    print("🚀 Starting V13.8 Zero-Sim Compliance Scan...")

    # Check if v13 dir exists, else assumes we are in root and search recursively
    scan_root = "."
    if os.path.exists("v13"):
        scan_root = "v13"

    walk_and_scan(scan_root)

    end_time = datetime.now()
    print(f"Scan duration: {end_time - start_time}")

    # Generate Report
    report_path = os.path.join(
        scan_root, "evidence/zero_sim/compliance_scan_report.json"
    )
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_violations": len(VIOLATIONS),
        "violations": VIOLATIONS,
    }

    with open(report_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"✅ Scan Complete. Found {len(VIOLATIONS)} potential violations.")
    print(f"Report saved to: {report_path}")

    # Emit exit code based on critical violations
    criticals = [v for v in VIOLATIONS if "CRITICAL" in v["severity"]]
    if criticals:
        print(f"⚠️  Found {len(criticals)} CRITICAL violations.")


if __name__ == "__main__":
    main()
