from typing import List, Optional, Any, Dict
from v18.consensus.schemas import (
    RequestVote,
    RequestVoteResponse,
    AppendEntries,
    AppendEntriesResponse,
    LogEntry,
)
from v18.consensus.interfaces import IConsensusLog


class ConsensusNode:
    """
    Deterministic Raft node state machine.
    Manages state transitions and RPC responses for F-layer replication.
    """

    def __init__(self, node_id: str, log: IConsensusLog, peer_ids: List[str]):
        self.node_id = node_id
        self.log = log
        self.peer_ids = peer_ids

        # PERSISTENT state on all servers (Updated on stable storage before responding to RPCs)
        self.current_term = 0
        self.voted_for: Optional[str] = None

        # VOLATILE state on all servers
        self.commit_index = 0
        self.last_applied = 0
        self.state = "follower"  # follower, candidate, leader

        # VOLATILE state on leaders (Reinitialized after election)
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}

        # Callbacks
        self.on_commit_callbacks: List[Any] = []

        # Simulation/Timing state (Logical units)
        self.election_timeout = 10
        self.heartbeat_timeout = 3
        self.time_since_last_event = 0
        self.votes_received = set()

    def handle_request_vote(self, rpc: RequestVote) -> RequestVoteResponse:
        """Process RequestVote RPC according to Raft safety rules."""
        # 1. Reply false if term < currentTerm
        if rpc.term < self.current_term:
            return RequestVoteResponse(
                term=self.current_term, sender_id=self.node_id, vote_granted=False
            )

        # If term > currentTerm, update currentTerm and step down to follower
        if rpc.term > self.current_term:
            self.current_term = rpc.term
            self.voted_for = None
            self.state = "follower"
            self.time_since_last_event = 0  # Step down resets clock

        # 2. If votedFor is null or candidateId, and candidate's log is at
        # least as up-to-date as receiver's log, grant vote
        can_vote = self.voted_for is None or self.voted_for == rpc.candidate_id

        # Log is up-to-date check (Raft 5.4.1)
        my_last_index = self.log.last_index()
        my_last_term = self.log.last_term()

        # Candidate's log is up-to-date if:
        # - candidate's last term is greater than receiver's last term
        # - terms match, but candidate's last index is >= receiver's last index
        log_is_up_to_date = (rpc.last_log_term > my_last_term) or (
            rpc.last_log_term == my_last_term and rpc.last_log_index >= my_last_index
        )

        if can_vote and log_is_up_to_date:
            self.voted_for = rpc.candidate_id
            self.time_since_last_event = 0  # Granting vote resets election timeout
            return RequestVoteResponse(
                term=self.current_term, sender_id=self.node_id, vote_granted=True
            )
        else:
            return RequestVoteResponse(
                term=self.current_term, sender_id=self.node_id, vote_granted=False
            )

    def handle_append_entries(self, rpc: AppendEntries) -> AppendEntriesResponse:
        """Process AppendEntries RPC (replication & heartbeats)."""
        # 1. Reply false if term < currentTerm
        if rpc.term < self.current_term:
            return AppendEntriesResponse(
                term=self.current_term,
                sender_id=self.node_id,
                success=False,
                match_index=self.log.last_index(),
            )

        # If term >= currentTerm, update currentTerm and step down to follower
        if rpc.term > self.current_term:
            self.current_term = rpc.term
            self.voted_for = None

        self.state = "follower"
        self.time_since_last_event = 0  # Heartbeat resets clock

        # 2. Reply false if log doesn't contain an entry at prevLogIndex
        # whose term matches prevLogTerm
        # (TODO: Implement log consistency check in implementation phase)

        # 4. Append any new entries not already in the log
        for entry in rpc.entries:
            if entry.index > self.log.last_index():
                self.log.append({"term": entry.term, "command": entry.command})

        # 5. If leaderCommit > commitIndex, set commitIndex = min(leaderCommit, index of last new entry)
        if rpc.leader_commit > self.commit_index:
            old_commit = self.commit_index
            self.commit_index = min(rpc.leader_commit, self.log.last_index())
            if self.commit_index > old_commit:
                self._trigger_commit_callbacks(old_commit + 1, self.commit_index)

        return AppendEntriesResponse(
            term=self.current_term,
            sender_id=self.node_id,
            success=True,
            match_index=self.log.last_index(),
        )

    def tick(self) -> List[Any]:
        """Advance one logical unit of time. Returns list of RPCs to send."""
        self.time_since_last_event += 1
        if self.state in ["follower", "candidate"]:
            if self.time_since_last_event >= self.election_timeout:
                return self._start_election()
        elif self.state == "leader":
            if self.time_since_last_event >= self.heartbeat_timeout:
                return self._send_heartbeats()
        return []

    def _start_election(self) -> List[RequestVote]:
        """Transition to candidate and initiate election."""
        self.state = "candidate"
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = {self.node_id}
        self.time_since_last_event = 0

        rpcs = []
        for peer in self.peer_ids:
            rpcs.append(
                RequestVote(
                    term=self.current_term,
                    sender_id=self.node_id,
                    candidate_id=self.node_id,
                    last_log_index=self.log.last_index(),
                    last_log_term=self.log.last_term(),
                )
            )
        return rpcs

    def handle_vote_response(self, response: RequestVoteResponse) -> None:
        """Process a received vote."""
        if self.state != "candidate" or response.term != self.current_term:
            return

        if response.vote_granted:
            self.votes_received.add(response.sender_id)
            if len(self.votes_received) > (len(self.peer_ids) + 1) / 2:
                self._become_leader()

    def _become_leader(self) -> None:
        """Transition to leader and immediately send heartbeats."""
        self.state = "leader"
        self.time_since_last_event = 0

        # Initialize leader state
        last_idx = self.log.last_index()
        for peer in self.peer_ids:
            self.next_index[peer] = last_idx + 1
            self.match_index[peer] = 0

    def _send_heartbeats(self) -> List[AppendEntries]:
        """Generate heartbeats/appends for all peers."""
        self.time_since_last_event = 0
        rpcs = []
        for peer in self.peer_ids:
            # Send entries starting from next_index[peer]
            entries_data = self.log.get_entries(self.next_index[peer])
            entries = [
                LogEntry(
                    index=idx + self.next_index[peer],
                    term=e["term"],
                    command=e["command"],
                )
                for idx, e in enumerate(entries_data)
            ]
            prev_idx = self.next_index[peer] - 1

            # Simplified: in real Raft, we'd look up the term of prev_idx
            prev_term = 0

            rpcs.append(
                AppendEntries(
                    term=self.current_term,
                    sender_id=self.node_id,
                    leader_id=self.node_id,
                    prev_log_index=prev_idx,
                    prev_log_term=prev_term,
                    entries=entries,
                    leader_commit=self.commit_index,
                )
            )
        return rpcs

    def handle_append_entries_response(self, response: AppendEntriesResponse) -> None:
        """Process response from peer to log replication/heartbeat."""
        if self.state != "leader" or response.term != self.current_term:
            return

        peer_id = response.sender_id
        if response.success:
            # Update matchIndex and nextIndex for follower
            self.match_index[peer_id] = max(
                self.match_index.get(peer_id, 0), response.match_index
            )
            self.next_index[peer_id] = self.match_index[peer_id] + 1
            self._update_leader_commit_index()
        else:
            # If AppendEntries fails because of log inconsistency, decrement nextIndex and retry
            self.next_index[peer_id] = max(1, self.next_index[peer_id] - 1)

    def _update_leader_commit_index(self) -> None:
        """Advance commitIndex if there exists N > commitIndex such that a majority of matchIndex[i] >= N."""
        # Simplistic majority check
        match_indices = sorted(
            list(self.match_index.values()) + [self.log.last_index()]
        )
        # For N nodes, we need majority (N // 2 + 1)
        # With 3 nodes, index 1 (0, 1, 2) is the "majority" point
        majority_idx = len(match_indices) // 2
        if len(match_indices) % 2 == 0:
            majority_idx -= 1  # adjust for even clusters if needed

        N = match_indices[majority_idx]

        if N > self.commit_index:
            # Raft 5.4.2: leader only commits entries from its current term by counting replicas
            # For now, we assume current term for simplicity in scaffolding
            old_commit = self.commit_index
            self.commit_index = N
            self._trigger_commit_callbacks(old_commit + 1, self.commit_index)

    def _trigger_commit_callbacks(self, start: int, end: int) -> None:
        """Notify observers of committed entries."""
        entries = self.log.get_entries(start, end + 1)
        for entry in entries:
            for callback in self.on_commit_callbacks:
                callback(entry)

    def propose(self, command: Dict[str, Any]) -> int:
        """Propose a new command to the cluster (Leader only)."""
        if self.state != "leader":
            return -1

        entry = {"term": self.current_term, "command": command}
        return self.log.append(entry)
