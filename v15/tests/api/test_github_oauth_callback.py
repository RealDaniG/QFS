"""
Test GitHub OAuth callback endpoint.
"""

import unittest
from fastapi.testclient import TestClient
from v15.services.auth_service import app
from v15.api.github_oauth import encode_oauth_state


class TestGitHubOAuthCallback(unittest.TestCase):
    """
    Test /auth/github/callback endpoint behavior.
    """

    def setUp(self):
        from v15.api.time_provider import set_test_time

        self.timestamp = 1735130000
        set_test_time(self.timestamp)
        self.client = TestClient(app)

    def tearDown(self):
        from v15.api.time_provider import clear_test_time

        clear_test_time()

    def test_callback_with_valid_state(self):
        """Valid state should trigger identity link."""
        session_id = "valid_session_123"
        state = encode_oauth_state(session_id, self.timestamp)

        from unittest.mock import patch, MagicMock

        mock_adapter = MagicMock()

        # Override dependency in FastAPI
        from v15.api.github_oauth import get_evidence_adapter

        app.dependency_overrides[get_evidence_adapter] = lambda: mock_adapter

        try:
            with (
                patch("v15.api.github_oauth.GITHUB_CLIENT_ID", "mock_id"),
                patch("v15.api.github_oauth.GITHUB_CLIENT_SECRET", "mock_secret"),
                patch("v15.api.github_oauth.requests") as mock_requests,
            ):
                mock_requests.post.return_value.status_code = 200
                mock_requests.post.return_value.json.return_value = {
                    "access_token": "token",
                    "token_type": "bearer",
                    "scope": "read:user",
                }

                mock_requests.get.return_value.status_code = 200
                mock_requests.get.return_value.json.return_value = {
                    "id": 123,
                    "login": "testuser",
                    "avatar_url": "http://avatar",
                }

                response = self.client.get(
                    f"/auth/github/callback?code=mock_code&state={state}"
                )

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["status"], "success")
                self.assertEqual(data["handle"], "testuser")
                mock_adapter.emit.assert_called_once()
        finally:
            # Clean up override
            app.dependency_overrides.clear()

    def test_callback_with_invalid_state(self):
        """Invalid state should return 400."""
        response = self.client.get(
            "/auth/github/callback?code=mock_code&state=invalid_state"
        )

        self.assertEqual(response.status_code, 400)

    def test_callback_without_code(self):
        """Missing code parameter should return 422 (FastAPI validation)."""
        state = encode_oauth_state("session_123", self.timestamp)

        response = self.client.get(f"/auth/github/callback?state={state}")

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
