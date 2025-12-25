import sys
import os


def test_environment_details():
    print("\n--- Environment Diagnostics ---")
    print(f"Python: {sys.executable}")
    print(f"Path: {sys.path}")
    print(f"CWD: {os.getcwd()}")

    try:
        import multipart

        print(f"✅ multipart imported: {multipart.__file__}")
    except ImportError as e:
        print(f"❌ multipart failed: {e}")

    try:
        import fastapi

        print(f"✅ fastapi imported: {fastapi.__file__}")
    except ImportError as e:
        print(f"❌ fastapi failed: {e}")

    try:
        from v15.api import github_oauth

        print(f"✅ github_oauth imported: {github_oauth.__file__}")
    except ImportError as e:
        print(f"❌ github_oauth failed: {e}")
