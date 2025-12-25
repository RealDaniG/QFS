import sys
import os

print("PYTHONPATH:", os.environ.get("PYTHONPATH"))
print("CWD:", os.getcwd())

try:
    print("Importing v15.auth.session_manager...")
    import v15.auth.session_manager

    print("SUCCESS: v15.auth.session_manager")
except ImportError as e:
    print(f"FAIL: v15.auth.session_manager: {e}")

try:
    print("Importing v17.ui.governance_projection...")
    import v17.ui.governance_projection

    print("SUCCESS: v17.ui.governance_projection")
except ImportError as e:
    print(f"FAIL: v17.ui.governance_projection: {e}")

try:
    print("Importing v13.atlas.src.main_minimal...")
    import v13.atlas.src.main_minimal

    print("SUCCESS: v13.atlas.src.main_minimal")
except Exception as e:
    print(f"FAIL: v13.atlas.src.main_minimal: {e}")
    import traceback

    traceback.print_exc()
