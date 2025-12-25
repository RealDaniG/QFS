import pytest
from unittest.mock import MagicMock, patch
from v15.api.github_oauth import github_callback, GitHubUser
from v15.tools.github_import_contributions import (
    fetch_repo_activity,
    create_contrib_recorded_event,
)
from fastapi import HTTPException

# --- Phase 1 Tests: GitHub OAuth ---


@pytest.mark.asyncio
async def test_github_callback_success():
    """
    Test successful exchange of code for token and identity linking.
    """
    mock_adapter = MagicMock()

    with (
        patch("v15.api.github_oauth.requests") as mock_requests,
        patch("v15.api.github_oauth.GITHUB_CLIENT_ID", "mock_id"),
        patch("v15.api.github_oauth.GITHUB_CLIENT_SECRET", "mock_secret"),
    ):
        # Mock Token Exchange
        mock_requests.post.return_value.json.return_value = {
            "access_token": "mock_gh_token",
            "scope": "read:user",
        }
        mock_requests.post.return_value.status_code = 200

        # Mock User Profile Fetch
        mock_requests.get.return_value.json.return_value = {
            "id": 12345,
            "login": "testuser",
            "avatar_url": "http://avatar",
        }
        mock_requests.get.return_value.status_code = 200

        response = await github_callback(
            code="mock_code", session_id="sess_001", adapter=mock_adapter
        )

        assert response["status"] == "success"
        assert response["handle"] == "testuser"

        # Verify specific event emission
        mock_adapter.emit.assert_called_once()
        event = mock_adapter.emit.call_args[0][0]
        assert event["event_type"] == "IDENTITY_LINK_GITHUB"
        assert event["external_handle"] == "testuser"
        assert event["session_id"] == "sess_001"


@pytest.mark.asyncio
async def test_github_callback_failure():
    """Test handling of GitHub API errors."""
    mock_adapter = MagicMock()
    with patch("v15.api.github_oauth.requests") as mock_requests:
        mock_requests.post.return_value.json.return_value = {"error": "bad_code"}

        with pytest.raises(HTTPException):
            await github_callback("bad_code", "sess", mock_adapter)


# --- Phase 1 Tests: Contribution Import ---


def test_create_contrib_event_structure():
    """Verify CONTRIB_RECORDED event structure."""
    event = create_contrib_recorded_event(
        repo_owner="owner",
        repo_name="repo",
        item_type="pr",
        item_id=101,
        user_handle="dev1",
        created_at_iso="2025-01-01T00:00:00Z",
        url="http://pr/101",
    )

    assert event.event_type == "CONTRIB_RECORDED"
    assert event.payload["repo"] == "owner/repo"
    assert event.payload["type"] == "pr"
    assert event.payload["id"] == 101


@patch("v15.tools.github_import_contributions.EvidenceBusAdapter")
@patch("v15.tools.github_import_contributions.requests")
def test_fetch_repo_activity_flow(mock_requests, MockAdapter):
    """
    Simulate fetching PRs and Issues and verify event emission.
    """
    mock_adapter_instance = MockAdapter.return_value

    # Mock PR response
    mock_requests.get.side_effect = [
        # 1. PRs Page 1
        MagicMock(
            status_code=200,
            json=lambda: [
                {
                    "number": 1,
                    "user": {"login": "user1"},
                    "created_at": "2025-01-01",
                    "html_url": "url1",
                }
            ],
        ),
        # 2. PRs Page 2 (Empty -> Stop)
        MagicMock(status_code=200, json=lambda: []),
        # 3. Issues Page 1 (One issue, one PR to skip)
        MagicMock(
            status_code=200,
            json=lambda: [
                {
                    "number": 2,
                    "user": {"login": "user2"},
                    "created_at": "2025-01-02",
                    "html_url": "url2",
                },  # Real Issue
                {
                    "number": 1,
                    "pull_request": {},
                    "user": {"login": "user1"},
                },  # PR disguised as issue -> Skip
            ],
        ),
        # 4. Issues Page 2 (Empty -> Stop)
        MagicMock(status_code=200, json=lambda: []),
    ]

    fetch_repo_activity("owner", "repo")

    # Expect 2 events: 1 PR, 1 Issue (skipped the duplicate PR-as-issue)
    assert mock_adapter_instance.emit.call_count == 2

    events = [call.args[0] for call in mock_adapter_instance.emit.call_args_list]
    assert events[0].payload["type"] == "pr"
    assert events[0].payload["id"] == 1
    assert events[1].payload["type"] == "issue"
    assert events[1].payload["id"] == 2
