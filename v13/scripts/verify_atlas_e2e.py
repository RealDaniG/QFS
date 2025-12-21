import urllib.request
import json
import sys

BASE_URL = "http://localhost:8001"


def check(endpoint, name):
    url = f"{BASE_URL}{endpoint}"
    print(f"Checking {name} ({url})...")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            status = response.status
            data = response.read()
            json_data = json.loads(data)
            print(f"[OK] {name}: {status}")

            keys = "Unknown"
            if isinstance(json_data, list) and json_data:
                keys = list(json_data[0].keys())
            elif isinstance(json_data, dict):
                keys = list(json_data.keys())
            else:
                keys = "Scalar/Empty"

            print(f"   Keys: {keys}")
            print(f"   Sample: {str(json_data)[:150]}...")
            return True
    except Exception as e:
        print(f"[FAIL] {name}: Failed - {e}")
        try:
            if hasattr(e, "read"):
                print(f"   Body: {e.read().decode('utf-8')[:200]}")
        except:
            pass
        return False


print("=== ATLAS v18 E2E Verification ===")
success = True
success &= check("/health", "Health")
success &= check("/api/v18/governance/proposals", "Governance Proposals")
success &= check("/api/v18/content/feed", "Content Feed")
success &= check("/api/v1/wallets/", "Wallets List (/)") or check(
    "/api/v1/wallets", "Wallets List"
)
success &= check("/api/v1/transactions/", "Transactions List (/)") or check(
    "/api/v1/transactions", "Transactions List"
)

if success:
    print("\nALL CHECKS PASSED.")
    sys.exit(0)
else:
    print("\nSOME CHECKS FAILED.")
    sys.exit(1)
