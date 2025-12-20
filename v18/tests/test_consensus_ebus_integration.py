from unittest.mock import patch
from v18.consensus.simulator import ClusterSimulator
from v18.consensus.ebus_adapter import EvidenceBusConsensusAdapter


def test_consensus_to_ebus_wiring():
    """Verify that a committed consensus entry triggers an EvidenceBus emission."""
    sim = ClusterSimulator(["n1", "n2", "n3"])
    # Set timeouts to be very stable for testing
    sim.nodes["n1"].election_timeout = 2
    sim.nodes["n2"].election_timeout = 10
    sim.nodes["n3"].election_timeout = 10

    adapter = EvidenceBusConsensusAdapter()

    # Attach adapter as observer
    for node in sim.nodes.values():
        node.on_commit_callbacks.append(adapter.on_entry_committed)

    # 1. Step until leader emerged
    for _ in range(20):
        sim.step()

    leader_id = sim.get_leader()
    assert leader_id == "n1", (
        f"Expected n1 to be leader, but got {leader_id}. Nodes: { {nid: n.state for nid, n in sim.nodes.items()} }"
    )
    leader = sim.nodes[leader_id]

    # 2. Propose a command
    command = {
        "type": "GOVERNANCE_PROPOSAL",
        "payload": {"id": "prop_1", "action": "increase_bounty"},
    }

    # Use a real list to capture events if patch fails for some reason
    captured_events = []

    def mock_emit_fn(etype, payload):
        captured_events.append((etype, payload))
        return {}

    with patch("v15.evidence.bus.EvidenceBus.emit", side_effect=mock_emit_fn):
        leader.propose(command)

        # 3. Tick many times to allow replication and commitment
        for _ in range(100):
            sim.step()
            if len(captured_events) > 0:
                break

        # 4. Check results
        assert len(captured_events) > 0, (
            f"EvidenceBus.emit was not called. Commit Index: {leader.commit_index}. Node states: { {nid: n.state for nid, n in sim.nodes.items()} }"
        )
        etype, payload = captured_events[0]
        assert etype == "GOVERNANCE_PROPOSAL"
        assert payload["id"] == "prop_1"
        assert "v18_consensus_term" in payload
