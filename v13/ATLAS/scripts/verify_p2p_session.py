import requests
import json
import sys
from eth_account import Account
from eth_account.messages import encode_defunct

# Constants
BASE_URL = "http://localhost:8001"
# Use a known test wallet or random
# Private key: 0x...
TEST_PRIV_KEY = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
account = Account.from_key(TEST_PRIV_KEY)
WALLET_ADDRESS = account.address

print(f"Testing with Wallet: {WALLET_ADDRESS}")


def main():
    s = requests.Session()

    # 1. Get Nonce
    print("[1] Requesting Nonce...")
    try:
        resp = s.get(f"{BASE_URL}/api/v1/auth/nonce?wallet_address={WALLET_ADDRESS}")
        if resp.status_code != 200:
            print(f"FAILED to get nonce: {resp.text}")
            sys.exit(1)
        nonce = resp.json()["nonce"]
        print(f"    Nonce: {nonce}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # 2. Sign Nonce
    print("[2] Signing Nonce...")
    msg = f"Sign this nonce to verify: {nonce}"
    signed = Account.sign_message(encode_defunct(text=msg), private_key=TEST_PRIV_KEY)
    signature = signed.signature.hex()

    # 3. Verify / Login
    print("[3] Logging in...")
    try:
        payload = {
            "wallet_address": WALLET_ADDRESS,
            "signature": signature,
            "nonce": nonce,
        }
        resp = s.post(f"{BASE_URL}/api/v1/auth/verify", json=payload)
        if resp.status_code != 200:
            print(f"FAILED to login: {resp.text}")
            sys.exit(1)
        token = resp.json()["token"]
        print(f"    Session Token: {token[:20]}...")
        s.headers.update({"Authorization": f"Bearer {token}"})
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # 4. Get P2P Session Params
    print("[4] Fetching P2P Session Params...")
    try:
        resp = s.get(f"{BASE_URL}/api/p2p/session?space_id=general")
        if resp.status_code != 200:
            print(f"FAILED to get params: {resp.text}")
            sys.exit(1)

        data = resp.json()
        print(f"    Success! Data: {json.dumps(data, indent=2)}")

        if "session_nonce" not in data or "evidence_head" not in data:
            print("FAILED: Missing fields in response")
            sys.exit(1)

        print("P2P Session Verification PASSED.")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
