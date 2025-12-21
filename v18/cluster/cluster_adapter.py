"""
v18 Cluster Adapter

Bridges ATLAS application writes to the distributed Raft-backed cluster.
Handles leader discovery, request forwarding, retries, and error handling.
"""

import time
import requests
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from requests.exceptions import RequestException, Timeout

from v15.evidence.bus import EvidenceBus


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class TxResult:
    """
    Result of a cluster write operation.

    All fields are deterministic and replayable in controlled environments.
    """

    committed: bool
    """Whether the transaction was committed to the Raft log."""

    evidence_event_ids: List[str]
    """Event IDs (or hashes) emitted to EvidenceBus."""

    leader_term: int
    """Raft term when transaction was committed."""

    leader_node_id: str
    """Node ID of the leader that committed the transaction."""

    commit_index: int
    """Raft log index of the committed entry."""

    timestamp: float
    """Commit timestamp."""

    error_code: Optional[str] = None
    """Error code if commit failed."""

    error_message: Optional[str] = None
    """Human-readable error message."""


@dataclass
class GovernanceCommand:
    """Command for governance actions."""

    action_type: str  # 'create_proposal', 'cast_vote', 'finalize'
    wallet_address: str
    proposal_id: Optional[str] = None
    vote_value: Optional[str] = None
    proposal_data: Optional[Dict[str, Any]] = None


@dataclass
class BountyCommand:
    """Command for bounty operations."""

    action_type: str  # 'create', 'claim', 'pay'
    wallet_address: str
    bounty_id: Optional[str] = None
    amount: Optional[float] = None
    bounty_data: Optional[Dict[str, Any]] = None


@dataclass
class ChatCommand:
    """Command for chat messages."""

    action_type: str  # 'post', 'react', 'edit'
    sender_wallet: str
    channel_id: str
    message_content: Optional[str] = None
    message_hash: Optional[str] = None


@dataclass
class ClusterStatus:
    """Current state of the Raft cluster."""

    leader_node_id: str
    leader_endpoint: str
    current_term: int
    commit_index: int


# ============================================================================
# Exceptions
# ============================================================================


class ClusterUnavailableError(Exception):
    """Raised when no cluster nodes are reachable."""

    pass


class CommandRejectedError(Exception):
    """Raised when leader rejects command."""

    pass


# ============================================================================
# V18 Cluster Adapter
# ============================================================================


class V18ClusterAdapter:
    """
    Adapter for submitting write operations to the v18 distributed cluster.

    Handles:
    - Leader discovery and caching
    - Request forwarding to leader
    - Retry logic with exponential backoff
    - Error handling and PoE logging
    """

    def __init__(self, node_endpoints: List[str], timeout_seconds: int = 10):
        """
        Initialize cluster adapter.

        Args:
            node_endpoints: List of Tier A node URLs (e.g., ["http://node-a:8000", ...])
            timeout_seconds: Request timeout for cluster operations
        """
        self.node_endpoints = node_endpoints
        self.timeout_seconds = timeout_seconds
        self._leader_cache: Optional[str] = None
        self._leader_term: Optional[int] = None
        self._max_retries = 3
        self._retry_delays = [0.1, 0.2, 0.4]  # Exponential backoff in seconds

    def submit_governance_action(self, cmd: GovernanceCommand) -> TxResult:
        """
        Submit a governance action to the cluster.

        Args:
            cmd: Governance command (proposal creation, vote, finalization)

        Returns:
            TxResult with commit status and EvidenceBus event IDs

        Raises:
            ClusterUnavailableError: All nodes unreachable
        """
        # Emit PoE event
        EvidenceBus.emit(
            "CLUSTER_WRITE_SUBMITTED",
            {
                "command_type": "governance",
                "action_type": cmd.action_type,
                "wallet": cmd.wallet_address,
                "proposal_id": cmd.proposal_id,
            },
        )

        # Submit to cluster
        return self._submit_to_cluster("governance", cmd.__dict__)

    def submit_bounty_action(self, cmd: BountyCommand) -> TxResult:
        """
        Submit a bounty action to the cluster.

        Args:
            cmd: Bounty command (creation, claim, payment)

        Returns:
            TxResult with commit status and EvidenceBus event IDs
        """
        EvidenceBus.emit(
            "CLUSTER_WRITE_SUBMITTED",
            {
                "command_type": "bounty",
                "action_type": cmd.action_type,
                "wallet": cmd.wallet_address,
                "bounty_id": cmd.bounty_id,
            },
        )

        return self._submit_to_cluster("bounty", cmd.__dict__)

    def submit_chat_message(self, cmd: ChatCommand) -> TxResult:
        """
        Submit a chat message to the cluster.

        Args:
            cmd: Chat command (message post, reaction, edit)

        Returns:
            TxResult with commit status and EvidenceBus event IDs
        """
        EvidenceBus.emit(
            "CLUSTER_WRITE_SUBMITTED",
            {
                "command_type": "chat",
                "action_type": cmd.action_type,
                "sender_wallet": cmd.sender_wallet,
                "channel_id": cmd.channel_id,
            },
        )

        return self._submit_to_cluster("chat", cmd.__dict__)

    def get_cluster_status(self) -> ClusterStatus:
        """
        Query current cluster health and leader information.

        Returns:
            ClusterStatus with leader, term, and node health

        Raises:
            ClusterUnavailableError: No nodes reachable
        """
        for endpoint in self.node_endpoints:
            try:
                response = requests.get(f"{endpoint}/cluster/status", timeout=2)
                if response.ok:
                    data = response.json()
                    return ClusterStatus(
                        leader_node_id=data["leader_node_id"],
                        leader_endpoint=data["leader_endpoint"],
                        current_term=data["current_term"],
                        commit_index=data["commit_index"],
                    )
            except RequestException:
                continue

        raise ClusterUnavailableError("No cluster nodes reachable")

    def _discover_leader(self) -> str:
        """
        Discover current Raft leader.

        Returns:
            Leader endpoint URL

        Raises:
            ClusterUnavailableError: No nodes reachable
        """
        for endpoint in self.node_endpoints:
            try:
                response = requests.get(f"{endpoint}/cluster/status", timeout=2)
                if response.ok:
                    data = response.json()
                    leader = data["leader_endpoint"]
                    term = data.get("current_term", 0)

                    # Cache leader and term
                    self._leader_cache = leader
                    self._leader_term = term

                    # Emit PoE event
                    EvidenceBus.emit(
                        "CLUSTER_LEADER_DISCOVERED",
                        {
                            "leader_endpoint": leader,
                            "term": term,
                        },
                    )

                    return leader
            except RequestException:
                continue

        raise ClusterUnavailableError("No cluster nodes reachable")

    def _submit_to_cluster(
        self, command_type: str, command_data: Dict[str, Any]
    ) -> TxResult:
        """
        Internal method to submit a command to the cluster with retry logic.

        Args:
            command_type: Type of command ('governance', 'bounty', 'chat')
            command_data: Command payload

        Returns:
            TxResult from successful commit

        Raises:
            ClusterUnavailableError: Max retries exceeded
        """
        attempt = 0
        last_error = None

        while attempt < self._max_retries:
            try:
                # Get leader (use cache if available)
                if not self._leader_cache:
                    leader = self._discover_leader()
                else:
                    leader = self._leader_cache

                # Submit to leader
                response = requests.post(
                    f"{leader}/cluster/submit",
                    json={
                        "command_type": command_type,
                        "command_data": command_data,
                    },
                    timeout=self.timeout_seconds,
                )

                # Handle response
                if response.ok:
                    data = response.json()

                    # Create TxResult
                    result = TxResult(
                        committed=data["committed"],
                        evidence_event_ids=data["evidence_event_ids"],
                        leader_term=data["leader_term"],
                        leader_node_id=data["leader_node_id"],
                        commit_index=data["commit_index"],
                        timestamp=data["timestamp"],
                    )

                    # Emit success PoE event
                    EvidenceBus.emit(
                        "CLUSTER_WRITE_COMMITTED",
                        {
                            "command_type": command_type,
                            "event_ids": data["evidence_event_ids"],
                            "commit_index": data["commit_index"],
                            "term": data["leader_term"],
                        },
                    )

                    return result

                # Handle NOT_LEADER (redirect)
                elif response.status_code == 307:
                    data = response.json()
                    error_code = data.get("error_code")

                    if error_code == "NOT_LEADER":
                        # Emit redirect PoE event
                        EvidenceBus.emit(
                            "CLUSTER_WRITE_REDIRECTED",
                            {
                                "from_node": leader,
                                "to_node": data.get("leader_hint", "unknown"),
                            },
                        )

                        # Clear cache and retry
                        self._leader_cache = None
                        attempt += 1
                        if attempt < self._max_retries:
                            time.sleep(
                                self._retry_delays[
                                    min(attempt - 1, len(self._retry_delays) - 1)
                                ]
                            )
                        continue

                # Handle validation failure (no retry)
                else:
                    data = response.json()
                    error_code = data.get("error_code", "UNKNOWN_ERROR")
                    error_message = data.get("error_message", "Unknown error")

                    if error_code == "VALIDATION_FAILED":
                        # Return error result (don't retry)
                        return TxResult(
                            committed=False,
                            evidence_event_ids=[],
                            leader_term=0,
                            leader_node_id="",
                            commit_index=0,
                            timestamp=time.time(),
                            error_code=error_code,
                            error_message=error_message,
                        )

                    # Other errors: retry
                    last_error = error_message
                    attempt += 1
                    if attempt < self._max_retries:
                        time.sleep(
                            self._retry_delays[
                                min(attempt - 1, len(self._retry_delays) - 1)
                            ]
                        )

            except Timeout:
                # Timeout: try next node
                self._leader_cache = None
                last_error = "Request timeout"
                attempt += 1
                if attempt < self._max_retries:
                    time.sleep(
                        self._retry_delays[
                            min(attempt - 1, len(self._retry_delays) - 1)
                        ]
                    )

            except RequestException as e:
                # Connection error: try next node
                self._leader_cache = None
                last_error = str(e)
                attempt += 1
                if attempt < self._max_retries:
                    time.sleep(
                        self._retry_delays[
                            min(attempt - 1, len(self._retry_delays) - 1)
                        ]
                    )

        # Max retries exceeded
        raise ClusterUnavailableError(
            f"Failed to submit command after {self._max_retries} attempts. Last error: {last_error}"
        )
