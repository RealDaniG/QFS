import sys
import os

# Mimic conftest.py path setup
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))  # root/
_V13_ROOT = os.path.join(_THIS_DIR, "v13")
_V13_LIBS = os.path.join(_V13_ROOT, "libs")
_V13_CORE = os.path.join(_V13_ROOT, "core")
_V13_UTILS = os.path.join(_V13_ROOT, "utils")

paths = [_THIS_DIR, _V13_ROOT, _V13_LIBS, _V13_CORE, _V13_UTILS]
for p in paths:
    if p not in sys.path:
        sys.path.insert(0, p)
        print(f"Added to path: {p}")

print(f"Sys.path: {sys.path}")

try:
    from v13.libs.logging.qfs_logger import QFSLogger, LogCategory

    print("Import v13.libs.logging.qfs_logger successful")

    l = QFSLogger("pytest_session", context={"env": "test"})
    print("Logger instance created")

    l.info(LogCategory.TESTING, "Pytest session configuring")
    print("Logger info called - SUCCESS")

except Exception as e:
    print(f"FAILED: {e}")
    import traceback

    traceback.print_exc()
