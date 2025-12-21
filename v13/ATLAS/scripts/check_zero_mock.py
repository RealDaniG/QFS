import ast
import os
import sys

# Patterns that indicate mock data (adjust as needed)
MOCK_INDICATORS = [
    "MOCK_",
    "mock_data",
    "hardcoded_",
    "static_user",
    "fake_balance",
    "# TODO: replace with real",
    "# MOCK",
]

# Files/Dirs to ignore
IGNORE_PATHS = [
    "verify_atlas_e2e.py",
    "scripts/check_zero_mock.py",
    "tests/",
    "node_modules/",
    ".next/",
    "dist/",
    "build/",
    "__pycache__",
    "check_zero_mock.py",
]


def should_ignore(filepath):
    """Check if file should be ignored."""
    # Normalize path separators
    filepath = filepath.replace("\\", "/")
    for ignore in IGNORE_PATHS:
        if ignore in filepath:
            return True
    return False


def check_file(filepath):
    """Check a Python file for mock indicators."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

    violations = []
    for line_num, line in enumerate(content.split("\n"), 1):
        for indicator in MOCK_INDICATORS:
            if indicator in line:
                # Skip if it has a specific ignore comment
                if "# noqa: mock-ok" in line:
                    continue
                violations.append((line_num, line.strip()))
    return violations


def check_ts_file(filepath):
    """Check a TypeScript file for mock indicators."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

    violations = []
    for line_num, line in enumerate(content.split("\n"), 1):
        for indicator in MOCK_INDICATORS:
            if indicator in line:
                if line.strip().startswith("//") or line.strip().startswith("/*"):
                    # Still flag comments if they are TODOs about mocks, but maybe be lenient?
                    # The prompt says "# TODO: replace with real" IS an indicator.
                    pass
                if "// noqa: mock-ok" in line:
                    continue

                violations.append((line_num, line.strip()))
    return violations


def main():
    root_dir = "v13/atlas"
    if not os.path.exists(root_dir):
        # Fallback to current dir if v13/atlas not found (relative path adjustment)
        if os.path.exists("src"):
            root_dir = "."
        else:
            print(f"Root dir {root_dir} not found.")
            return

    issues = {}

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)

            if should_ignore(filepath):
                continue

            if filename.endswith(".py"):
                violations = check_file(filepath)
                if violations:
                    issues[filepath] = violations
            elif filename.endswith((".ts", ".tsx")):
                violations = check_ts_file(filepath)
                if violations:
                    issues[filepath] = violations

    if issues:
        print("❌ MOCK DATA DETECTED:\n")
        for filepath, violations in issues.items():
            print(f"{filepath}:")
            for line_num, line in violations:
                print(f"  Line {line_num}: {line}")
            print()
        sys.exit(1)
    else:
        print("✅ ZERO-MOCK CHECK PASSED: No mock indicators found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
