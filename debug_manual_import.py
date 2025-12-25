import sys
import os

print("Starting Manual Import Test...")
try:
    print("Importing v15.api.github_oauth...")
    from v15.api import github_oauth

    print("✅ Success")
except ImportError as e:
    print(f"❌ Failed to import github_oauth: {e}")

try:
    print("Importing v15.tools.github_import_contributions...")
    from v15.tools import github_import_contributions

    print("✅ Success")
except ImportError as e:
    print(f"❌ Failed to import github_import_contributions: {e}")

try:
    print("Importing python-multipart via module name 'multipart'...")
    import multipart

    print(f"✅ Success: {multipart.__file__}")
except ImportError as e:
    print(f"❌ Failed to import multipart: {e}")
except Exception as e:
    print(f"❌ Other error importing multipart: {e}")
