from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any


class ConsensusMessage(BaseModel):
    """Base message for consensus RPCs."""

    term: int
    sender_id: str
    model_config = ConfigDict(frozen=True, extra="forbid")


class RequestVote(ConsensusMessage):
    """Candidate requests vote from peer."""

    type: str = "REQUEST_VOTE"
    candidate_id: str
    last_log_index: int
    last_log_term: int


class RequestVoteResponse(ConsensusMessage):
    """Response to vote request."""

    type: str = "REQUEST_VOTE_RESPONSE"
    vote_granted: bool


class LogEntry(BaseModel):
    """A single entry in the replicated log."""

    term: int
    index: int
    command: Dict[str, Any]  # EvidenceBus event payload
    model_config = ConfigDict(frozen=True, extra="forbid")


class AppendEntries(ConsensusMessage):
    """Leader replicates log entries to follower."""

    type: str = "APPEND_ENTRIES"
    leader_id: str
    prev_log_index: int
    prev_log_term: int
    entries: List[LogEntry]
    leader_commit: int


class AppendEntriesResponse(ConsensusMessage):
    """Response to log replication."""

    type: str = "APPEND_ENTRIES_RESPONSE"
    success: bool
    match_index: int
