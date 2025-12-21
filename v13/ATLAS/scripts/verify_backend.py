import requests
import sys

BASE_URL = "http://localhost:8000"


def check_health():
    try:
        print(f"Checking {BASE_URL}...")
        resp = requests.get(f"{BASE_URL}/docs")
        if resp.status_code == 200:
            print("SUCCESS: Backend is reachable and serving docs.")
            return True
        else:
            print(f"WARNING: Backend returned status {resp.status_code}")
            return False
    except Exception as e:
        print(f"FAILURE: Could not connect to backend: {e}")
        return False


if __name__ == "__main__":
    if check_health():
        sys.exit(0)
    else:
        sys.exit(1)
