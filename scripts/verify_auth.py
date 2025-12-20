import requests
import sys
from eth_account import Account
from eth_account.messages import encode_defunct

# Ensure we print utf-8
sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://localhost:8001/api/v1/auth"


def test_auth_flow():
    print("Testing Auth Flow...")

    # Generate random wallet
    acct = Account.create()
    address = acct.address
    print(f"Generated Wallet: {address}")

    # 1. Get Nonce
    try:
        resp = requests.get(f"{BASE_URL}/nonce")
        resp.raise_for_status()
        nonce = resp.json()["nonce"]
        print(f"Got Nonce: {nonce}")
    except Exception as e:
        print(f"Failed to get nonce: {e}")
        return

    # 2. Sign Nonce
    try:
        msg = encode_defunct(text=nonce)
        signed_msg = acct.sign_message(msg)
        signature = signed_msg.signature.hex()
        # print(f"Signature: {signature}")
    except Exception as e:
        print(f"Failed to sign: {e}")
        return

    # 3. Login
    payload = {"nonce": nonce, "signature": signature, "wallet_address": address}

    try:
        resp = requests.post(f"{BASE_URL}/login", json=payload)
        if resp.status_code != 200:
            print(f"Login Failed ({resp.status_code}): {resp.text}")
            sys.exit(1)

        data = resp.json()
        token = data.get("session_token")
        if token:
            print(f"Login Successful. Token: {token[:15]}...")
        else:
            print("Login response missing token!")
            sys.exit(1)

    except Exception as e:
        print(f"Login Request Error: {e}")
        sys.exit(1)

    print("✅ Auth Flow Verified Successfully")


if __name__ == "__main__":
    test_auth_flow()
