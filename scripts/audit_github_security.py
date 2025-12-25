"""
Security audit for GitHub OAuth integration.
Checks for common OAuth vulnerabilities.
"""

import subprocess
import re
import os
import sys


def audit_oauth_security():
    """Run security checks on OAuth implementation."""

    print("=" * 60)
    print("SECURITY AUDIT: GitHub OAuth")
    print("=" * 60)

    issues = []

    # Check 1: State parameter tampering protection
    print("\n[CHECK 1] State parameter tampering protection...")

    oauth_file_path = "v15/api/github_oauth.py"
    if not os.path.exists(oauth_file_path):
        print("❌ FAIL: v15/api/github_oauth.py not found")
        return False

    try:
        with open(oauth_file_path, "r") as f:
            oauth_code = f.read()

            if (
                "decode_oauth_state" in oauth_code
                and "encode_oauth_state" in oauth_code
            ):
                print("✅ PASS: State encoding/decoding usage detected.")
            else:
                issues.append("Missing explicit state helper usage in github_oauth.py")
                print("❌ FAIL: State helpers not clearly used.")

            if "timestamp" in oauth_code and "max_age" in oauth_code:
                print("✅ PASS: State expiry check detected.")
            else:
                issues.append("State parameter might missing timestamp/expiry check")
                print("⚠️ WARN: Timestamp check not explicitly obvious in naive regex.")

    except Exception as e:
        issues.append(f"Audit failed: {e}")

    if not issues:
        print("\n✅ SECURITY AUDIT PASSED")
        return True
    else:
        print("\n❌ SECURITY AUDIT FAILED")
        for i in issues:
            print(f"- {i}")
        return False


if __name__ == "__main__":
    success = audit_oauth_security()
    sys.exit(0 if success else 1)
