from v18.consensus.simulator import ClusterSimulator


def test_election_single_leader():
    """Verify that a 3-node cluster elects exactly one leader when staggered."""
    sim = ClusterSimulator(["n1", "n2", "n3"])

    # Stagger timeouts to force a specific leader (deterministic simulation)
    sim.nodes["n1"].election_timeout = 5
    sim.nodes["n2"].election_timeout = 10
    sim.nodes["n3"].election_timeout = 15

    # Step through time
    for _ in range(20):
        sim.step()

    leader = sim.get_leader()
    assert leader == "n1"
    assert sim.nodes[leader].state == "leader"

    # Peers should be followers and in the same term
    for nid in ["n2", "n3"]:
        assert sim.nodes[nid].state == "follower"
        assert sim.nodes[nid].current_term == sim.nodes[leader].current_term


def test_leader_failover():
    """Verify that a new leader is elected if the current leader fails."""
    sim = ClusterSimulator(["n1", "n2", "n3"])
    sim.nodes["n1"].election_timeout = 5
    sim.nodes["n2"].election_timeout = 10
    sim.nodes["n3"].election_timeout = 15

    # 1. Elect n1 as leader
    for _ in range(20):
        sim.step()

    leader = sim.get_leader()
    assert leader == "n1"
    term_1 = sim.nodes[leader].current_term

    # 2. Crash n1 (remove from simulation entirely)
    del sim.transport.nodes[leader]
    del sim.nodes[leader]
    sim.node_ids.remove(leader)

    # 3. Step forward. n2 and n3 should timeout and elect a new leader.
    # n2 has shorter timeout, should win.
    for _ in range(20):
        sim.step()

    new_leader = sim.get_leader()
    assert new_leader == "n2"
    assert sim.nodes[new_leader].current_term > term_1
    assert sim.nodes["n3"].state == "follower"


def test_simulation_determinism():
    """Verify that the simulation is 100% deterministic given the same initial config."""
    results = []
    for _ in range(2):
        sim = ClusterSimulator(["n1", "n2", "n3"])
        sim.nodes["n1"].election_timeout = 5
        sim.nodes["n2"].election_timeout = 10
        sim.nodes["n3"].election_timeout = 15

        for _ in range(30):
            sim.step()

        # Snapshot state
        state = {
            nid: (node.state, node.current_term, node.log.last_index())
            for nid, node in sim.nodes.items()
        }
        results.append(state)

    assert results[0] == results[1]
