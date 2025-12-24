"""Wallet Functionality Test"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from v13.libs.CertifiedMath import CertifiedMath
from v13.libs.BigNum128 import BigNum128

def test_wallet():
    print("Testing Wallet...")
    try:
        cm = CertifiedMath()
        bal = BigNum128.from_int(1000)
        tx = BigNum128.from_int(100)
        new_bal = cm.sub(bal, tx, [])
        print(f"Balance: {new_bal.value}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if test_wallet() else 1)
