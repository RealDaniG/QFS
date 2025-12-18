import sys
import os

# Ensure v13 is in path
sys.path.insert(0, os.getcwd())

try:
    from v13.libs.logging.qfs_logger import QFSLogger, LogCategory

    print("Import successful")

    l = QFSLogger("pytest_session", context={"env": "test"})
    print("Logger instance created")

    l.info(LogCategory.TESTING, "Pytest session configuring")
    print("Logger info called")

except Exception as e:
    print(f"FAILED: {e}")
    import traceback

    traceback.print_exc()
