from v18.consensus.state_machine import ConsensusNode
from v18.consensus.mocks import InMemoryConsensusLog
from v18.consensus.schemas import RequestVote, AppendEntries


def test_node_grants_vote_initially():
    log = InMemoryConsensusLog()
    node = ConsensusNode(node_id="node1", log=log, peer_ids=["node2", "node3"])

    rv = RequestVote(
        term=1,
        sender_id="node2",
        candidate_id="node2",
        last_log_index=0,
        last_log_term=0,
    )

    response = node.handle_request_vote(rv)
    assert response.vote_granted is True
    assert node.voted_for == "node2"
    assert node.current_term == 1


def test_node_rejects_vote_if_already_voted():
    log = InMemoryConsensusLog()
    node = ConsensusNode(node_id="node1", log=log, peer_ids=["node2", "node3"])
    node.current_term = 1
    node.voted_for = "node2"

    rv = RequestVote(
        term=1,
        sender_id="node3",
        candidate_id="node3",
        last_log_index=0,
        last_log_term=0,
    )

    response = node.handle_request_vote(rv)
    assert response.vote_granted is False
    assert node.voted_for == "node2"


def test_node_rejects_older_term_vote():
    log = InMemoryConsensusLog()
    node = ConsensusNode(node_id="node1", log=log, peer_ids=["node2", "node3"])
    node.current_term = 2

    rv = RequestVote(
        term=1,
        sender_id="node2",
        candidate_id="node2",
        last_log_index=0,
        last_log_term=0,
    )

    response = node.handle_request_vote(rv)
    assert response.vote_granted is False
    assert node.current_term == 2


def test_node_updates_term_and_grants_vote():
    log = InMemoryConsensusLog()
    node = ConsensusNode(node_id="node1", log=log, peer_ids=["node2", "node3"])
    node.current_term = 1
    node.voted_for = "node1"  # voted for self in old term

    rv = RequestVote(
        term=2,
        sender_id="node2",
        candidate_id="node2",
        last_log_index=0,
        last_log_term=0,
    )

    response = node.handle_request_vote(rv)
    assert response.vote_granted is True
    assert node.current_term == 2
    assert node.voted_for == "node2"


def test_heartbeat_resets_follower():
    log = InMemoryConsensusLog()
    node = ConsensusNode(node_id="node1", log=log, peer_ids=["node2", "node3"])
    node.state = "candidate"

    ae = AppendEntries(
        term=1,
        sender_id="node2",
        leader_id="node2",
        prev_log_index=0,
        prev_log_term=0,
        entries=[],
        leader_commit=0,
    )

    response = node.handle_append_entries(ae)
    assert response.success is True
    assert node.state == "follower"
    assert node.current_term == 1
