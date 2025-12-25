import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from v15.services.auth_service import app
from v15.api.github_oauth import get_evidence_adapter


# Mocking the adapter for testing
class MockEvidenceBus:
    def __init__(self):
        self.events = []

    def emit(self, event):
        self.events.append(event)

    # Helper to inspect events in test
    def get_events_by_type(self, event_type):
        return [e for e in self.events if e.get("event_type") == event_type]


class TestGitHubOAuthFlowIntegration(unittest.TestCase):
    """
    Simulates complete OAuth flow without real GitHub API calls.
    """

    def setUp(self):
        self.mock_bus = MockEvidenceBus()
        # Override dependency
        app.dependency_overrides[get_evidence_adapter] = lambda: self.mock_bus
        self.client = TestClient(app)
        self.wallet_address = "0xTEST_WALLET"

    def tearDown(self):
        app.dependency_overrides = {}

    @patch("v15.api.github_oauth.requests")
    @patch("v15.api.github_oauth.GITHUB_CLIENT_ID", "mock_client_id")
    @patch("v15.api.github_oauth.GITHUB_CLIENT_SECRET", "mock_client_secret")
    def test_complete_oauth_flow(self, mock_requests):
        """
        Test complete flow:
        1. Initiate OAuth (Login)
        2. Simulate GitHub callback
        3. Verify identity link event
        """

        # Mock GitHub API responses
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.json.return_value = {
            "access_token": "mock_github_token",
            "token_type": "bearer",
            "scope": "read:user",
        }

        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.json.return_value = {
            "login": "RealDaniG",
            "id": 12345678,
            "avatar_url": "http://avatar",
            "name": "Dani",
            "email": "dani@example.com",
        }

        # Step 1: Initiate OAuth
        session_id = "test_session_flow_123"
        login_response = self.client.get(
            f"/auth/github/login?session_id={session_id}", follow_redirects=False
        )

        # Check redirect (307 or 302 depending on FastAPI version/response, usually 307 for RedirectResponse)
        self.assertEqual(login_response.status_code, 307)
        auth_url = login_response.headers["location"]
        self.assertIn("github.com/login/oauth/authorize", auth_url)

        # Extract state from auth_url
        import urllib.parse

        parsed = urllib.parse.urlparse(auth_url)
        query = urllib.parse.parse_qs(parsed.query)
        state = query["state"][0]

        # Step 2: Simulate GitHub callback
        callback_response = self.client.get(
            f"/auth/github/callback?code=mock_code&state={state}"
        )

        self.assertEqual(callback_response.status_code, 200)
        data = callback_response.json()
        self.assertEqual(data["handle"], "RealDaniG")

        # Step 3: Verify event was emitted
        events = self.mock_bus.get_events_by_type("IDENTITY_LINK_GITHUB")
        self.assertTrue(len(events) > 0, "No IDENTITY_LINK_GITHUB event emitted")

        event = events[0]
        self.assertEqual(event["session_id"], session_id)
        self.assertEqual(event["external_handle"], "RealDaniG")


if __name__ == "__main__":
    unittest.main()
