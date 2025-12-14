# Storage Node Failure Recovery Runbook

## Scope & Preconditions

**When to Use**: This runbook should be executed when a storage node in the QFS V13.5 decentralized storage system becomes unreachable, fails health checks, or is manually marked as failed.

**Preconditions**:
- Active AEGIS telemetry snapshots are available
- Administrative access to the storage system
- Access to the StorageEngine instance
- Access to node logs and metrics

**Owner**: SRE/Infra Team
**Integration Points**: AEGIS Node Verification, StorageEngine, Monitoring System

## Step-by-Step Procedure

### 1. Identify Failed Node
```bash
# Check node status in StorageEngine
python -c "
from v13.core.StorageEngine import StorageEngine
from v13.libs.CertifiedMath import CertifiedMath
cm = CertifiedMath()
storage_engine = StorageEngine(cm)
nodes = storage_engine.nodes
for node_id, node in nodes.items():
    print(f'Node {node_id}: Status={node.status}, AEGIS Verified={node.is_aegis_verified}')
"
```

Expected outcome: List of nodes with their statuses, identifying failed/unreachable nodes.

### 2. Isolate Failed Node
```bash
# Mark node as inactive in StorageEngine
python -c "
from v13.core.StorageEngine import StorageEngine
from v13.libs.CertifiedMath import CertifiedMath
cm = CertifiedMath()
storage_engine = StorageEngine(cm)
failed_node_id = 'NODE_ID_TO_REPLACE'  # Replace with actual node ID
success = storage_engine.set_node_status(failed_node_id, 'inactive')
print(f'Node {failed_node_id} marked as inactive: {success}')
"
```

Expected outcome: Confirmation that the node has been marked as inactive.

### 3. Trigger Shard Redistribution
```bash
# Advance epoch to trigger node re-verification and shard redistribution
python -c "
from v13.core.StorageEngine import StorageEngine
from v13.libs.CertifiedMath import CertifiedMath
cm = CertifiedMath()
storage_engine = StorageEngine(cm)

# Get current epoch and increment
new_epoch = storage_engine.current_epoch + 1
print(f'Advancing to epoch {new_epoch}')

# Advance epoch with updated registry/telemetry snapshots
# In production, these would come from AEGIS
registry_snapshot = {}  # Replace with actual registry snapshot
telemetry_snapshot = {}  # Replace with actual telemetry snapshot

storage_engine.advance_epoch(new_epoch, registry_snapshot, telemetry_snapshot)
print('Epoch advanced and shard redistribution triggered')
"
```

Expected outcome: Epoch advanced and shard redistribution initiated for active nodes.

### 4. Verify Shard Redistribution
```bash
# Check that shards previously assigned to failed node have been reassigned
python -c "
from v13.core.StorageEngine import StorageEngine
from v13.libs.CertifiedMath import CertifiedMath
cm = CertifiedMath()
storage_engine = StorageEngine(cm)

# List all shards and their assigned nodes
for shard_id, shard in storage_engine.shards.items():
    if 'FAILED_NODE_ID' in shard.assigned_nodes:  # Replace with actual failed node ID
        print(f'Shard {shard_id} still assigned to failed node')
    else:
        print(f'Shard {shard_id} reassigned to: {shard.assigned_nodes}')
"
```

Expected outcome: All shards previously assigned to the failed node have been reassigned to healthy nodes.

### 5. Validate Data Integrity
```bash
# Run consistency checks on redistributed shards
python -c "
from v13.core.StorageEngine import StorageEngine
from v13.libs.CertifiedMath import CertifiedMath
cm = CertifiedMath()
storage_engine = StorageEngine(cm)

# Verify proofs for redistributed shards
for shard_id, shard in storage_engine.shards.items():
    try:
        proof = storage_engine.get_storage_proof(shard.object_id, shard.version, shard_id)
        print(f'Proof verification for shard {shard_id}: SUCCESS')
    except Exception as e:
        print(f'Proof verification for shard {shard_id}: FAILED - {e}')
"
```

Expected outcome: All redistributed shards pass proof verification.

## Verification

### Check Evidence Files
- `docs/evidence/storage/assurance/node_failure_recovery_YYYYMMDD.json` - Should show node failure detected and recovery completed
- `docs/evidence/storage/storage_node_lifecycle.json` - Should reflect node status changes

### Metrics to Monitor
- Active node count should return to expected level
- Shard distribution should be balanced across remaining nodes
- Proof success rate should remain above 99%

## Failure Handling

### If Step 2 Fails
- Manually update node status in persistent storage if using external database
- Escalate to SRE/Infra team for infrastructure-level node isolation

### If Step 3 Fails
- Check AEGIS telemetry snapshots are current and valid
- Verify network connectivity to AEGIS services
- Manually trigger epoch advancement with forced redistribution

### If Step 4 Fails
- Rollback node status to active temporarily
- Investigate shard assignment algorithm for bugs
- Engage Backend team for manual shard redistribution

### Safe Abort/Rollback
```bash
# Restore node to active status if recovery fails
python -c "
from v13.core.StorageEngine import StorageEngine
from v13.libs.CertifiedMath import CertifiedMath
cm = CertifiedMath()
storage_engine = StorageEngine(cm)
failed_node_id = 'NODE_ID_TO_REPLACE'  # Replace with actual node ID
storage_engine.set_node_status(failed_node_id, 'active')
print(f'Node {failed_node_id} restored to active status')
"
```

## Escalation Path

**Warning (Minor Issues)**:
- Page: Ops Team Lead
- Slack Channel: #qfs-ops-alerts
- Runbook: Continue with manual verification

**Critical (Data Loss/Service Impact)**:
- Page: SRE/Infra Team, Backend Team
- Slack Channel: #qfs-critical-alerts
- Runbook: Initiate disaster recovery procedures

## Alerting Integration
- **Stack**: Prometheus + Alertmanager
- **Metric**: `storage_node_count_low`
- **Threshold**: Critical when active nodes < minimum required nodes
- **Runbook Link**: This document