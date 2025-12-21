import requests
import sys

BASE_URL = "http://localhost:8000"


def check_health():
    try:
        print(f"Checking {BASE_URL}/health...")
        resp = requests.get(f"{BASE_URL}/health")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        if resp.status_code != 200:
            sys.exit(1)
    except Exception as e:
        print(f"Health check failed: {e}")
        sys.exit(1)


def check_auth_challenge():
    try:
        print(f"\nRequesting challenge for 0xTEST...")
        resp = requests.get(f"{BASE_URL}/api/v18/auth/challenge?wallet=0xTEST")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        if resp.status_code != 200:
            sys.exit(1)

        data = resp.json()
        if "challenge_id" not in data:
            print("Error: No challenge_id in response")
            sys.exit(1)

        return data["challenge_id"]
    except Exception as e:
        print(f"Auth challenge failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    check_health()
    check_auth_challenge()
    print("\nBackend verification successful!")
