"""
Pre-push validation to catch pipeline issues locally.
"""

import os
import sys


def check_file_exists(filepath):
    """Check if required file exists."""
    if os.path.exists(filepath):
        print(f"✅ {filepath}")
        return True
    else:
        print(f"❌ MISSING: {filepath}")
        return False


def main():
    print("=" * 60)
    print("PRE-PUSH VALIDATION")
    print("=" * 60)

    checks = []

    # Required files
    required_files = [
        "v15/requirements.txt",
        "v15/__init__.py",
        "v15/auth/__init__.py",
        "v15/auth/session.py",
        "v15/auth/events.py",
        ".github/workflows/v20_auth_pipeline.yml",
    ]

    print("\n[REQUIRED FILES]")
    for f in required_files:
        checks.append(check_file_exists(f))

    # Check Python syntax
    print("\n[PYTHON SYNTAX]")
    python_files = ["v15/auth/session.py", "v15/api/github_oauth.py"]

    for pyfile in python_files:
        if os.path.exists(pyfile):
            result = os.system(f"python -m py_compile {pyfile} 2>nul")
            if result == 0:
                print(f"✅ {pyfile} - Valid syntax")
                checks.append(True)
            else:
                print(f"❌ {pyfile} - Syntax error")
                checks.append(False)

    # Check imports
    print("\n[IMPORTS]")
    test_imports = [
        ("v15.auth.session", "Session"),
        ("v15.auth.events", "create_identity_link_event"),
    ]

    # Assuming we are running from root and PYTHONPATH is set or we append .
    sys.path.append(os.getcwd())

    for module, obj in test_imports:
        try:
            exec(f"from {module} import {obj}")
            print(f"✅ Can import {obj} from {module}")
            checks.append(True)
        except Exception as e:
            print(f"❌ Cannot import {obj} from {module}: {e}")
            checks.append(False)

    print("\n" + "=" * 60)
    if all(checks):
        print("✅ ALL CHECKS PASSED - Safe to push")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Fix before pushing")
        return 1


if __name__ == "__main__":
    sys.exit(main())
