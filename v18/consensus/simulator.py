from typing import Dict, List, Any, Optional
from v18.consensus.state_machine import ConsensusNode
from v18.consensus.schemas import (
    RequestVote,
    RequestVoteResponse,
    AppendEntries,
    AppendEntriesResponse,
)
from v18.consensus.mocks import InMemoryConsensusLog


class SimulatedTransport:
    """In-memory transport for multi-node consensus simulation."""

    def __init__(self):
        self.nodes: Dict[str, "ConsensusNode"] = {}
        self.message_queue: List[tuple] = []  # (sender, target, message)

    def register_node(self, node_id: str, node: ConsensusNode) -> None:
        self.nodes[node_id] = node

    def send(self, sender: str, target: str, message: Any) -> None:
        """Queue a message for delivery."""
        self.message_queue.append((sender, target, message))

    def flush(self) -> None:
        """Deliver all currently queued messages."""
        current_queue = self.message_queue
        self.message_queue = []
        for sender, target, msg in current_queue:
            if target not in self.nodes:
                continue

            node = self.nodes[target]
            if isinstance(msg, RequestVote):
                resp = node.handle_request_vote(msg)
                self.send(target, sender, resp)
            elif isinstance(msg, RequestVoteResponse):
                node.handle_vote_response(msg)
            elif isinstance(msg, AppendEntries):
                resp = node.handle_append_entries(msg)
                self.send(target, sender, resp)
            elif isinstance(msg, AppendEntriesResponse):
                node.handle_append_entries_response(msg)


class ClusterSimulator:
    """Manages a cluster of ConsensusNodes for deterministic testing."""

    def __init__(self, node_ids: List[str]):
        self.node_ids = node_ids
        self.transport = SimulatedTransport()
        self.nodes: Dict[str, ConsensusNode] = {}

        for nid in node_ids:
            peers = [p for p in node_ids if p != nid]
            node = ConsensusNode(nid, InMemoryConsensusLog(), peers)
            self.nodes[nid] = node
            self.transport.register_node(nid, node)

        self.logical_time = 0

    def step(self) -> None:
        """Advance simulation by one logical tick."""
        self.logical_time += 1

        # 1. Ticking all nodes and collecting outbound RPCs
        for nid in self.node_ids:
            rpcs = self.nodes[nid].tick()
            for rpc in rpcs:
                # We assume tick() returns messages for peers
                # The state machine internally knows its peers
                for peer in self.nodes[nid].peer_ids:
                    self.transport.send(nid, peer, rpc)

        # 2. Flush transport (delivery logic)
        self.transport.flush()

    def get_leader(self) -> Optional[str]:
        """Check if exactly one leader exists."""
        leaders = [nid for nid, node in self.nodes.items() if node.state == "leader"]
        if len(leaders) == 1:
            return leaders[0]
        return None
