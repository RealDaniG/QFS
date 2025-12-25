"""
Test OAuth state parameter handling.
Validates session_id encoding/decoding through GitHub redirect.
"""

import unittest
import base64
import json
import time
from fastapi.exceptions import HTTPException

# Mocking the actual function since it's inline in the router in current implementation
# But wait, the user prompt suggests importing `encode_oauth_state`.
# The current implementation in github_oauth.py DOES NOT have `encode_oauth_state` as a separate function.
# It does it inline in `github_login` and `github_callback`.
# I should REFACTOR github_oauth.py to extract these helpers to make them testable,
# OR I should copy the logic here, OR I should use the Integration test approach mainly.
# The user explicitly asked for `test_github_oauth_state.py` importing `encode_oauth_state`.
# So I MUST refactor github_oauth.py first to export these helpers.

# Refactoring plan:
# 1. Modify v15/api/github_oauth.py to extract encode_oauth_state and decode_oauth_state.
# 2. Then this test will work.

# I will write the test assuming the refactor happens.
from v15.api.github_oauth import encode_oauth_state, decode_oauth_state


class TestGitHubOAuthState(unittest.TestCase):
    """
    Validates session_id survives GitHub OAuth round-trip.
    """

    def test_state_encoding_deterministic(self):
        """State encoding must be deterministic for same input."""
        session_id = "test_session_123"

        timestamp = 1735130000
        state_1 = encode_oauth_state(session_id, timestamp)
        state_2 = encode_oauth_state(session_id, timestamp)

        self.assertEqual(state_1, state_2)

    def test_state_decoding_correct(self):
        """Decoded state must match original session_id."""
        session_id = "test_session_456"

        timestamp = 1735130000
        state = encode_oauth_state(session_id, timestamp)
        decoded_session_id = decode_oauth_state(state, timestamp)

        self.assertEqual(decoded_session_id, session_id)

    def test_state_includes_timestamp(self):
        """State should include timestamp for expiry checks."""
        session_id = "test_session_789"
        timestamp = 1735130000
        state = encode_oauth_state(session_id, timestamp)

        # Decode manually to inspect
        decoded = json.loads(base64.urlsafe_b64decode(state))

        self.assertIn("session_id", decoded)
        self.assertIn("timestamp", decoded)
        self.assertEqual(decoded["session_id"], session_id)

    def test_expired_state_rejected(self):
        """State older than 5 minutes should be rejected."""

        current_time = int(time.time())
        old_state = base64.urlsafe_b64encode(
            json.dumps(
                {
                    "session_id": "old_session",
                    "timestamp": current_time - 360,  # 6 minutes ago
                }
            ).encode()
        ).decode()

        with self.assertRaises(ValueError):
            decode_oauth_state(old_state, current_time, max_age=300)  # 5 min max


if __name__ == "__main__":
    unittest.main()
