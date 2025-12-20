# v18 ClusterAdapter Specification

> **Version:** v18.9  
> **Status:** Design Specification  
> **Purpose:** Bridge ATLAS application writes to the distributed Raft-backed EvidenceBus

## Overview

The `V18ClusterAdapter` replaces the `StubAdapter` in `QFSClient`, enabling ATLAS to submit governance actions, bounty operations, and chat messages to the distributed Tier A cluster. It handles leader discovery, request forwarding, and retry logic while maintaining deterministic behavior.

---

## Interface Definition

### Core Methods

```python
class V18ClusterAdapter:
    """
    Adapter for submitting write operations to the v18 distributed cluster.
    
    Responsibilities:
    - Discover and cache current Raft leader
    - Forward write requests to leader node
    - Handle leader changes and redirects
    - Return deterministic transaction results
    """
    
    def __init__(self, node_endpoints: List[str], timeout_seconds: int = 10):
        """
        Initialize cluster adapter.
        
        Args:
            node_endpoints: List of Tier A node URLs (e.g., ["http://node-a:8000", ...])
            timeout_seconds: Request timeout for cluster operations
        """
        pass
    
    def submit_governance_action(self, cmd: GovernanceCommand) -> TxResult:
        """
        Submit a governance action to the cluster.
        
        Args:
            cmd: Governance command (proposal creation, vote, finalization)
            
        Returns:
            TxResult with commit status and EvidenceBus event IDs
            
        Raises:
            ClusterUnavailableError: All nodes unreachable
            CommandRejectedError: Leader rejected command (validation failure)
        """
        pass
    
    def submit_bounty_action(self, cmd: BountyCommand) -> TxResult:
        """
        Submit a bounty action to the cluster.
        
        Args:
            cmd: Bounty command (creation, claim, payment)
            
        Returns:
            TxResult with commit status and EvidenceBus event IDs
        """
        pass
    
    def submit_chat_message(self, cmd: ChatCommand) -> TxResult:
        """
        Submit a chat message to the cluster.
        
        Args:
            cmd: Chat command (message post, reaction, edit)
            
        Returns:
            TxResult with commit status and EvidenceBus event IDs
        """
        pass
    
    def get_cluster_status(self) -> ClusterStatus:
        """
        Query current cluster health and leader information.
        
        Returns:
            ClusterStatus with leader, term, and node health
        """
        pass
```

---

## Data Structures

### TxResult

```python
@dataclass
class TxResult:
    """
    Result of a cluster write operation.
    
    All fields must be deterministic and replayable.
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
    """Commit timestamp (deterministic in controlled environments)."""
    
    error_code: Optional[str] = None
    """Error code if commit failed (e.g., 'NOT_LEADER', 'VALIDATION_FAILED')."""
    
    error_message: Optional[str] = None
    """Human-readable error message."""
```

### Command Types

```python
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
```

### ClusterStatus

```python
@dataclass
class ClusterStatus:
    """Current state of the Raft cluster."""
    leader_node_id: str
    leader_endpoint: str
    current_term: int
    commit_index: int
    nodes: List[NodeInfo]
    
@dataclass
class NodeInfo:
    """Information about a single cluster node."""
    node_id: str
    endpoint: str
    is_leader: bool
    is_reachable: bool
    last_heartbeat: float
```

---

## Behavior Specification

### Leader Discovery

**Initial Discovery:**

1. Query `/cluster/status` on each configured node (sequential)
2. First responsive node returns current leader info
3. Cache leader endpoint and term

**Discovery Refresh:**

- On `NOT_LEADER` response
- On connection timeout/error
- On term change detected

**Algorithm:**

```python
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
            status = requests.get(f"{endpoint}/cluster/status", timeout=2)
            if status.ok:
                data = status.json()
                return data["leader_endpoint"]
        except RequestException:
            continue
    raise ClusterUnavailableError("No cluster nodes reachable")
```

### Write Request Flow

**Successful Path:**

```
1. Client → Adapter: submit_governance_action(cmd)
2. Adapter → Leader: POST /cluster/submit
3. Leader → Raft: Propose entry
4. Raft → Consensus: Replicate to majority
5. Consensus → EvidenceBus: Append events
6. Leader → Adapter: TxResult(committed=True, ...)
7. Adapter → Client: Return TxResult
```

**Leader Redirect:**

```
1. Client → Adapter: submit_governance_action(cmd)
2. Adapter → NodeA: POST /cluster/submit
3. NodeA → Adapter: 307 Redirect, Location: NodeB
4. Adapter → NodeB: POST /cluster/submit (retry)
5. NodeB → Raft: Propose entry
6. ... (continue as successful path)
```

**Failure Handling:**

```
1. Adapter attempts write to cached leader
2. If NOT_LEADER: refresh leader cache, retry once
3. If VALIDATION_FAILED: return TxResult with error
4. If TIMEOUT: try next node, max 3 attempts
5. If all fail: raise ClusterUnavailableError
```

### Determinism Requirements

**Guaranteed:**

- Same command + same cluster state → same EvidenceBus events
- Same command + same term → same commit index
- Event IDs are deterministic hashes of content

**Not Guaranteed:**

- Exact timing of commit (network variability)
- Which follower handled redirect (implementation detail)

**PoE Logging:**
All cluster operations emit telemetry events:

- `CLUSTER_WRITE_SUBMITTED`: command_type, wallet, target_node
- `CLUSTER_LEADER_DISCOVERED`: leader_node, term
- `CLUSTER_WRITE_REDIRECTED`: from_node, to_node
- `CLUSTER_WRITE_COMMITTED`: event_ids, commit_index, term

---

## Error Handling

### Error Codes

| Code | Meaning | Recovery |
|------|---------|----------|
| `NOT_LEADER` | Node is not current leader | Refresh leader, retry |
| `VALIDATION_FAILED` | Command rejected by F-layer | Return error to client |
| `DUPLICATE_ENTRY` | Command already in log | Return original TxResult |
| `CLUSTER_UNAVAILABLE` | No nodes reachable | Raise exception |
| `TIMEOUT` | Request exceeded timeout | Try next node |
| `TERM_CONFLICT` | Stale term detected | Refresh and retry |

### Retry Policy

**Bounded Retries:**

- Max attempts: 3
- Retry delay: Exponential backoff (100ms, 200ms, 400ms)
- Only retry on: `NOT_LEADER`, `TIMEOUT`
- Never retry on: `VALIDATION_FAILED`, `DUPLICATE_ENTRY`

**Node Ordering:**

- Try configured nodes in deterministic order
- Prefer cached leader first
- Fall back to sequential scan on failure

---

## Integration with QFSClient

### Current (Stubbed)

```python
class StubAdapter:
    async def submit_bundle(self, bundle):
        raise NotImplementedError("Write ops not enabled")
```

### New (Cluster-Backed)

```python
class QFSClient:
    def __init__(self, cluster_adapter: V18ClusterAdapter, ...):
        self._cluster = cluster_adapter
    
    async def submit_governance_action(self, action):
        cmd = GovernanceCommand(...)
        result = self._cluster.submit_governance_action(cmd)
        
        if not result.committed:
            raise TransactionError(result.error_message)
        
        return TransactionReceipt(
            event_ids=result.evidence_event_ids,
            committed_at=result.timestamp,
            ...
        )
```

---

## Performance Characteristics

### Latency

**Expected (3-node cluster, local network):**

- Leader discovery: 1-5ms (cached), 10-30ms (fresh)
- Write commit: 10-50ms (Raft consensus + EvidenceBus append)
- Redirect: +5-15ms (one extra network hop)

**Worst Case:**

- Cluster unavailable: 3 × timeout (default: 30 seconds)
- Leader election in progress: 150-500ms (Raft election timeout)

### Throughput

**Bottleneck:** Raft commit rate (~1000 ops/sec per leader)

**Scaling:**

- Reads: Scale horizontally (any node)
- Writes: Limited by single leader
- Future: Raft batching for higher throughput

---

## Testing Requirements

### Unit Tests

1. **Leader Discovery:**
   - `test_discover_leader_from_healthy_nodes`
   - `test_discover_leader_with_one_node_down`
   - `test_discover_leader_raises_on_all_nodes_down`

2. **Write Submission:**
   - `test_submit_governance_action_to_leader`
   - `test_submit_bounty_action_returns_event_ids`
   - `test_submit_chat_message_deterministic`

3. **Error Handling:**
   - `test_handles_not_leader_redirect`
   - `test_handles_validation_failure`
   - `test_retry_on_timeout`
   - `test_raises_on_cluster_unavailable`

4. **Determinism:**
   - `test_same_command_yields_same_events`
   - `test_poe_events_emitted_for_writes`

### Integration Tests

1. **Multi-Node Cluster:**
   - `test_write_survives_leader_failover`
   - `test_simultaneous_writes_ordered_correctly`
   - `test_follower_redirects_to_leader`

---

## Security Considerations

### Authentication

- Commands include `wallet_address` from authenticated session
- Cluster nodes verify session tokens via Ascon validation
- Unauthorized commands rejected before Raft proposal

### Authorization

- F-layer validates command permissions (scopes, role checks)
- Rejected commands never enter Raft log
- Authorization failures return `VALIDATION_FAILED`

### Tampering

- Commands are hashed before Raft proposal
- EvidenceBus events include content hashes
- Replay attacks prevented by nonce/timestamp checks (future)

---

## Migration Path

### Phase 1: Adapter Implementation (Current)

- Define interfaces and data structures
- Implement basic leader discovery
- Wire single-action type (governance) as proof-of-concept

### Phase 2: Full Integration

- Add bounty and chat command support
- Replace all `StubAdapter` usage in ATLAS API
- Add comprehensive error handling

### Phase 3: Production Hardening

- Implement connection pooling
- Add circuit breakers for failing nodes
- Optimize leader caching and refresh logic

---

## References

- [v18 Consensus Implementation](../../v18/consensus/state_machine.py)
- [EvidenceBus Consensus Adapter](../../v18/consensus/ebus_adapter.py)
- [ATLAS v18 Gap Report](./ATLAS_V18_GAP_REPORT.md)
- [Auth Sync Migration](./AUTH_SYNC_V18_MIGRATION.md)

---

**Maintained by:** QFS × ATLAS Core Team  
**Last Updated:** 2025-12-20  
**Status:** Ready for Implementation
