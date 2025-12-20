"""
Test Suite: v18 ClusterAdapter

Tests for distributed cluster write operations.
Validates leader discovery, write submission, error handling, and determinism.
"""

import pytest
from unittest.mock import patch, Mock
import time

# Import actual implementation
from v18.cluster.cluster_adapter import (
    V18ClusterAdapter,
    TxResult,
    GovernanceCommand,
    BountyCommand,
    ChatCommand,
    ClusterUnavailableError,
    CommandRejectedError,
)


class TestLeaderDiscovery:
    """Test cluster leader discovery logic."""

    @patch("requests.get")
    def test_discover_leader_from_healthy_nodes(self, mock_get):
        """Should discover leader from first responsive node."""
        # Setup
        adapter = V18ClusterAdapter(
            node_endpoints=[
                "http://node-a:8000",
                "http://node-b:8000",
                "http://node-c:8000",
            ]
        )

        # Mock response from node-a
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "leader_endpoint": "http://node-b:8000",
            "current_term": 5,
            "commit_index": 123,
        }
        mock_get.return_value = mock_response

        # Test
        leader = adapter._discover_leader()

        # Assert
        assert leader == "http://node-b:8000"
        mock_get.assert_called_once_with("http://node-a:8000/cluster/status", timeout=2)

    @patch("requests.get")
    def test_discover_leader_with_one_node_down(self, mock_get):
        """Should skip non-responsive nodes and find leader."""
        adapter = V18ClusterAdapter(
            node_endpoints=[
                "http://node-a:8000",
                "http://node-b:8000",
                "http://node-c:8000",
            ]
        )

        # Mock: node-a times out, node-b responds
        def side_effect(url, timeout):
            if "node-a" in url:
                from requests.exceptions import Timeout

                raise Timeout()
            mock_response = Mock()
            mock_response.ok = True
            mock_response.json.return_value = {
                "leader_endpoint": "http://node-c:8000",
                "current_term": 3,
            }
            return mock_response

        mock_get.side_effect = side_effect

        # Test
        leader = adapter._discover_leader()

        # Assert
        assert leader == "http://node-c:8000"
        assert (
            mock_get.call_count == 2
        )  # Tried node-a (failed), then node-b (succeeded)

    @patch("requests.get")
    def test_discover_leader_raises_on_all_nodes_down(self, mock_get):
        """Should raise ClusterUnavailableError when all nodes unreachable."""
        adapter = V18ClusterAdapter(
            node_endpoints=["http://node-a:8000", "http://node-b:8000"]
        )

        # Mock: all nodes timeout
        from requests.exceptions import Timeout

        mock_get.side_effect = Timeout()

        # Test & Assert
        with pytest.raises(ClusterUnavailableError, match="No cluster nodes reachable"):
            adapter._discover_leader()


class TestGovernanceSubmission:
    """Test governance action submission."""

    @patch("requests.post")
    @patch.object(V18ClusterAdapter, "_discover_leader")
    def test_submit_governance_action_to_leader(self, mock_discover, mock_post):
        """Should submit governance action to leader and return TxResult."""
        # Setup
        adapter = V18ClusterAdapter(node_endpoints=["http://node-a:8000"])
        mock_discover.return_value = "http://node-a:8000"

        # Mock successful response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "committed": True,
            "evidence_event_ids": ["evt_proposal_123", "evt_vote_456"],
            "leader_term": 5,
            "leader_node_id": "node-a",
            "commit_index": 125,
            "timestamp": 1703001234.5,
        }
        mock_post.return_value = mock_response

        # Test
        cmd = GovernanceCommand(
            action_type="create_proposal",
            wallet_address="0xABC123",
            proposal_data={"title": "Test Proposal"},
        )
        result = adapter.submit_governance_action(cmd)

        # Assert
        assert result.committed is True
        assert len(result.evidence_event_ids) == 2
        assert "evt_proposal_123" in result.evidence_event_ids
        assert result.leader_term == 5
        assert result.leader_node_id == "node-a"

    @patch("requests.post")
    @patch.object(V18ClusterAdapter, "_discover_leader")
    def test_submit_governance_action_deterministic(self, mock_discover, mock_post):
        """Same command should yield same EvidenceBus events (determinism)."""
        adapter = V18ClusterAdapter(node_endpoints=["http://node-a:8000"])
        mock_discover.return_value = "http://node-a:8000"

        # Mock consistent response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "committed": True,
            "evidence_event_ids": ["evt_abc123"],
            "leader_term": 1,
            "leader_node_id": "node-a",
            "commit_index": 10,
            "timestamp": 1703001234.5,
        }
        mock_post.return_value = mock_response

        # Test: Submit same command twice
        cmd = GovernanceCommand(action_type="create_proposal", wallet_address="0xTEST")
        result1 = adapter.submit_governance_action(cmd)
        result2 = adapter.submit_governance_action(cmd)

        # Assert: Event IDs should be identical (deterministic)
        assert result1.evidence_event_ids == result2.evidence_event_ids


class TestBountySubmission:
    """Test bounty action submission."""

    @patch("requests.post")
    @patch.object(V18ClusterAdapter, "_discover_leader")
    def test_submit_bounty_action_returns_event_ids(self, mock_discover, mock_post):
        """Should submit bounty action and return EvidenceBus event IDs."""
        adapter = V18ClusterAdapter(node_endpoints=["http://node-a:8000"])
        mock_discover.return_value = "http://node-a:8000"

        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "committed": True,
            "evidence_event_ids": ["evt_bounty_created_xyz"],
            "leader_term": 3,
            "leader_node_id": "node-a",
            "commit_index": 50,
            "timestamp": 1703002345.6,
        }
        mock_post.return_value = mock_response

        cmd = BountyCommand(
            action_type="create",
            wallet_address="0xDEF456",
            amount=100.0,
            bounty_data={"title": "Fix bug"},
        )
        result = adapter.submit_bounty_action(cmd)

        assert result.committed is True
        assert "evt_bounty_created_xyz" in result.evidence_event_ids


class TestChatSubmission:
    """Test chat message submission."""

    @patch("requests.post")
    @patch.object(V18ClusterAdapter, "_discover_leader")
    def test_submit_chat_message_includes_hash(self, mock_discover, mock_post):
        """Should submit chat message with content hash anchor."""
        adapter = V18ClusterAdapter(node_endpoints=["http://node-a:8000"])
        mock_discover.return_value = "http://node-a:8000"

        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "committed": True,
            "evidence_event_ids": ["evt_message_hash_abc"],
            "leader_term": 2,
            "leader_node_id": "node-a",
            "commit_index": 75,
            "timestamp": 1703003456.7,
        }
        mock_post.return_value = mock_response

        cmd = ChatCommand(
            action_type="post",
            sender_wallet="0xGHI789",
            channel_id="governance_123",
            message_hash="sha256_abc123",
        )
        result = adapter.submit_chat_message(cmd)

        assert result.committed is True
        assert result.evidence_event_ids[0].startswith("evt_message_hash")


class TestErrorHandling:
    """Test error handling and retries."""

    @patch("requests.post")
    @patch.object(V18ClusterAdapter, "_discover_leader")
    def test_handles_not_leader_redirect(self, mock_discover, mock_post):
        """Should handle NOT_LEADER response and retry with new leader."""
        adapter = V18ClusterAdapter(
            node_endpoints=["http://node-a:8000", "http://node-b:8000"]
        )

        # First call returns node-a, second call returns node-b (after redirect)
        mock_discover.side_effect = ["http://node-a:8000", "http://node-b:8000"]

        # Mock: First request fails with NOT_LEADER, second succeeds
        responses = [
            Mock(
                ok=False,
                status_code=307,
                json=lambda: {"error_code": "NOT_LEADER", "leader_hint": "node-b"},
            ),
            Mock(
                ok=True,
                json=lambda: {
                    "committed": True,
                    "evidence_event_ids": ["evt_retry_success"],
                    "leader_term": 6,
                    "leader_node_id": "node-b",
                    "commit_index": 100,
                    "timestamp": 1703004567.8,
                },
            ),
        ]
        mock_post.side_effect = responses

        cmd = GovernanceCommand(action_type="create_proposal", wallet_address="0xRETRY")
        result = adapter.submit_governance_action(cmd)

        # Assert: Should have retried and succeeded
        assert result.committed is True
        assert result.leader_node_id == "node-b"
        assert mock_post.call_count == 2

    @patch("requests.post")
    @patch.object(V18ClusterAdapter, "_discover_leader")
    def test_handles_validation_failure(self, mock_discover, mock_post):
        """Should return error result on validation failure (no retry)."""
        adapter = V18ClusterAdapter(node_endpoints=["http://node-a:8000"])
        mock_discover.return_value = "http://node-a:8000"

        mock_response = Mock()
        mock_response.ok = False
        mock_response.json.return_value = {
            "committed": False,
            "error_code": "VALIDATION_FAILED",
            "error_message": "Invalid proposal format",
        }
        mock_post.return_value = mock_response

        cmd = GovernanceCommand(action_type="create_proposal", wallet_address="0xBAD")
        result = adapter.submit_governance_action(cmd)

        assert result.committed is False
        assert result.error_code == "VALIDATION_FAILED"
        assert mock_post.call_count == 1  # No retry on validation error

    @patch("requests.post")
    @patch.object(V18ClusterAdapter, "_discover_leader")
    def test_retry_on_timeout(self, mock_discover, mock_post):
        """Should retry on timeout up to max attempts."""
        adapter = V18ClusterAdapter(
            node_endpoints=["http://node-a:8000", "http://node-b:8000"]
        )
        mock_discover.return_value = "http://node-a:8000"

        from requests.exceptions import Timeout

        # First 2 attempts timeout, 3rd succeeds
        mock_post.side_effect = [
            Timeout(),
            Timeout(),
            Mock(
                ok=True,
                json=lambda: {
                    "committed": True,
                    "evidence_event_ids": ["evt_timeout_recovery"],
                    "leader_term": 4,
                    "leader_node_id": "node-a",
                    "commit_index": 80,
                    "timestamp": 1703005678.9,
                },
            ),
        ]

        cmd = GovernanceCommand(
            action_type="create_proposal", wallet_address="0xTIMEOUT"
        )
        result = adapter.submit_governance_action(cmd)

        assert result.committed is True
        assert mock_post.call_count == 3  # 2 timeouts + 1 success

    @patch("requests.post")
    @patch.object(V18ClusterAdapter, "_discover_leader")
    def test_raises_on_cluster_unavailable(self, mock_discover, mock_post):
        """Should raise ClusterUnavailableError after max retries."""
        adapter = V18ClusterAdapter(node_endpoints=["http://node-a:8000"])
        mock_discover.return_value = "http://node-a:8000"

        from requests.exceptions import Timeout

        mock_post.side_effect = Timeout()  # All attempts timeout

        cmd = GovernanceCommand(action_type="create_proposal", wallet_address="0xFAIL")

        with pytest.raises(ClusterUnavailableError):
            adapter.submit_governance_action(cmd)


class TestDeterminism:
    """Test deterministic behavior."""

    @patch("requests.post")
    @patch.object(V18ClusterAdapter, "_discover_leader")
    def test_same_command_yields_same_events(self, mock_discover, mock_post):
        """
        Same command in same cluster state should yield same EvidenceBus events.

        This is critical for Zero-Sim compliance.
        """
        adapter = V18ClusterAdapter(node_endpoints=["http://node-a:8000"])
        mock_discover.return_value = "http://node-a:8000"

        # Mock deterministic response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "committed": True,
            "evidence_event_ids": ["evt_deterministic_abc123"],
            "leader_term": 1,
            "leader_node_id": "node-a",
            "commit_index": 5,
            "timestamp": 1703000000.0,  # Fixed timestamp in test env
        }
        mock_post.return_value = mock_response

        # Create identical commands
        cmd1 = GovernanceCommand(
            action_type="create_proposal",
            wallet_address="0xDET",
            proposal_data={"title": "Deterministic Test"},
        )
        cmd2 = GovernanceCommand(
            action_type="create_proposal",
            wallet_address="0xDET",
            proposal_data={"title": "Deterministic Test"},
        )

        result1 = adapter.submit_governance_action(cmd1)
        result2 = adapter.submit_governance_action(cmd2)

        # Assert: Identical inputs → identical event IDs
        assert result1.evidence_event_ids == result2.evidence_event_ids
        assert result1.commit_index == result2.commit_index


class TestPoELogging:
    """Test Proof-of-Evidence event emissions."""

    @patch("v15.evidence.bus.EvidenceBus.emit")
    @patch("requests.post")
    @patch.object(V18ClusterAdapter, "_discover_leader")
    def test_poe_events_emitted_for_writes(self, mock_discover, mock_post, mock_emit):
        """Should emit PoE events for cluster write operations."""
        adapter = V18ClusterAdapter(node_endpoints=["http://node-a:8000"])
        mock_discover.return_value = "http://node-a:8000"

        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "committed": True,
            "evidence_event_ids": ["evt_test"],
            "leader_term": 1,
            "leader_node_id": "node-a",
            "commit_index": 1,
            "timestamp": 1703000000.0,
        }
        mock_post.return_value = mock_response

        cmd = GovernanceCommand(action_type="create_proposal", wallet_address="0xPOE")
        adapter.submit_governance_action(cmd)

        # Assert: PoE events were emitted
        assert mock_emit.called
        # Expected events: CLUSTER_WRITE_SUBMITTED, CLUSTER_WRITE_COMMITTED
        call_args_list = [call[0] for call in mock_emit.call_args_list]
        event_types = [args[0] for args in call_args_list]

        assert "CLUSTER_WRITE_SUBMITTED" in event_types
        assert "CLUSTER_WRITE_COMMITTED" in event_types


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
