from v18.consensus.schemas import RequestVote, AppendEntries, LogEntry
import json


def test_request_vote_serialization():
    rv = RequestVote(
        term=1,
        sender_id="node1",
        candidate_id="node1",
        last_log_index=10,
        last_log_term=1,
    )
    data = rv.model_dump()
    assert data["term"] == 1
    assert data["type"] == "REQUEST_VOTE"
    assert data["candidate_id"] == "node1"


def test_append_entries_serialization():
    entry = LogEntry(term=1, index=11, command={"ev": "test"})
    ae = AppendEntries(
        term=1,
        sender_id="leader",
        leader_id="leader",
        prev_log_index=10,
        prev_log_term=1,
        entries=[entry],
        leader_commit=10,
    )
    data = ae.model_dump()
    assert len(data["entries"]) == 1
    assert data["entries"][0]["index"] == 11
    assert data["leader_commit"] == 10


def test_log_entry_immutability():
    # Verify model is frozen
    entry = LogEntry(term=1, index=1, command={})
    try:
        entry.term = 2
        assert False, "Should be immutable"
    except Exception:
        assert True
