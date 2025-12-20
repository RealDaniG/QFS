# QFS × ATLAS — Cluster Operations Guide

> **Version:** v18.0.0-alpha  
> **Status:** Alpha (Simulation-first)

This guide provides instructions for configuring and operating a Tier A distributed cluster.

## 1. Consensus Configuration

The v18 backbone uses a Raft-derived deterministic consensus.

- **Election Timeout:** Default 100-300 simulation ticks (randomized).
- **Heartbeat Interval:** Default 1 tick.
- **Quorum:** `(N // 2) + 1` nodes required for commitment.

## 2. Managing Nodes

### Onboarding a Node (Manual)

Currently, nodes are registered in the `ClusterSimulator`.

**Future:** Onboarding will be governed by v17 governance proposals, emitting `NODE_JOINED` events to the EvidenceBus.

### Monitoring Health

Inspect the cluster state via logs or the simulator:

```python
# From a running simulator
leader_id = sim.get_leader()
nodes_healthy = [n.node_id for n in sim.nodes.values() if n.is_active()]
```

## 3. Failure Recovery

- **Leader Failover:** The cluster automatically elects a new leader if the current one stops sending heartbeats.
- **Log Reconciliation:** Followers automatically catch up with the leader's log on reconnection.

## 4. Operational Commands

### Manual Log Replay

Verify a node's state against the EvidenceBus:

```bash
# Replay full cluster history onto a node
python v18/tests/test_consensus_simulation.py
```

---

**Note:** In Phase 4 (Next), a dedicated Cluster Dashboard will be integrated into the Admin Panel for real-time visibility.
