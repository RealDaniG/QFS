# ATLAS x QFS: Node Operation Protocol

**Version**: 1.0.0  
**Status**: Draft  
**Last Updated**: December 13, 2025

---

## 1. Overview

The Node Operation Protocol defines the requirements, responsibilities, and reward mechanisms for independent nodes participating in the ATLAS x QFS decentralized network.

### Node Types

1. **Ledger Node**: Maintains event ledger, validates events
2. **QFS Node**: Executes QFS computations (CoherenceEngine, TreasuryEngine, Guards)
3. **IPFS Node**: Stores and serves content via IPFS/Filecoin
4. **Messaging Node**: Relays E2E encrypted messages
5. **OPEN-AGI Node**: Provides advisory observations and simulations

**Note**: A single physical server can run multiple node types.

---

## 2. Minimum Node Requirements

### 2.1 Hardware Specs

**Minimum**:

- CPU: 2 cores, 2.5 GHz+
- RAM: 4 GB
- Storage: 100 GB SSD
- Network: 10 Mbps symmetric

**Recommended**:

- CPU: 4 cores, 3.0 GHz+
- RAM: 16 GB
- Storage: 500 GB NVMe SSD
- Network: 100 Mbps symmetric

### 2.2 Software Requirements

- OS: Linux (Ubuntu 22.04+), macOS 13+, Windows 11+ with WSL2
- Runtime: Python 3.11+, Node.js 20+
- Containers: Docker 24+, Docker Compose 2.20+
- Network: Static IP or dynamic DNS

---

## 3. Node Registration

### 3.1 Registration Process

1. **Generate DID**: Create unique node identity (`did:key:...`)
2. **Stake Tokens**: Lock minimum stake (e.g., 1000 FLX)
3. **Declare Capabilities**: Specify which node types running
4. **Submit Registration**: Publish `NodeRegistered` event to ledger

### 3.2 Registration Event Schema

```json
{
  "event_type": "NodeRegistered",
  "inputs": {
    "node_did": "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK",
    "node_types": ["ledger", "qfs", "ipfs"],
    "endpoint": "https://atlas-node.example.com",
    "stake_amount": 1000.0,
    "stake_token": "FLX",
    "capabilities": {
      "qfs_modules": ["CoherenceEngine", "TreasuryEngine", "SafetyGuard"],
      "ipfs_storage_gb": 500,
      "bandwidth_mbps": 100
    },
    "operator_contact": "operator@example.com"
  },
  "outcome": {
    "status": "registered",
    "node_id": "node_001"
  }
}
```

---

## 4. Node Responsibilities

### 4.1 Ledger Node

**Must**:

- Accept valid events from authorized entities
- Verify event signatures and hash-links
- Maintain append-only log
- Serve events via REST API and WebSocket
- Participate in consensus (if using distributed ledger)

**Performance Targets**:

- Event write latency: < 100ms
- Event query latency: < 50ms
- Uptime: ≥ 99%

### 4.2 QFS Node

**Must**:

- Query PolicyRegistry before each computation
- Execute CoherenceEngine, TreasuryEngine, Guards deterministically
- Generate Merkle proofs for verifiability
- Publish computation results to ledger
- Respond to verification challenges from light nodes

**Performance Targets**:

- Coherence computation: < 500ms
- Reward calculation: < 200ms
- Guard evaluation: < 1s
- Uptime: ≥ 95%

### 4.3 IPFS Node

**Must**:

- Pin critical content (as incentivized by PolicyRegistry)
- Serve content via IPFS gateway
- Report pinned CIDs to ledger
- Participate in Filecoin deals (optional)

**Performance Targets**:

- Content retrieval: < 2s for pinned content
- Uptime: ≥ 99%

### 4.4 Messaging Node

**Must**:

- Relay encrypted messages between users
- Publish metadata events to ledger (thread creation, membership)
- NOT store message content (privacy requirement)
- Maintain WebSocket connections

**Performance Targets**:

- Message delivery latency: < 200ms
- Concurrent connections: ≥ 1000
- Uptime: ≥ 99.9%

---

## 5. Node Discovery

### 5.1 Node Registry

All registered nodes are indexed in **NodeRegistry** (on-chain or ledger-based):

```typescript
interface NodeInfo {
  did: string;
  node_types: ("ledger" | "qfs" | "ipfs" | "messaging" | "agi")[];
  endpoint: string;
  stake_amount: number;
  metrics: {
    uptime_percent: number;
    avg_latency_ms: number;
    verification_pass_rate: number;  // For QFS nodes
    storage_used_gb?: number;         // For IPFS nodes
  };
  reputation_score: number;
  last_heartbeat: number;
}
```

### 5.2 Client Selection Algorithm

Clients query NodeRegistry and select nodes based on:

```typescript
function scoreNode(node: NodeInfo): number {
  return (
    node.metrics.uptime_percent * 0.4 +
    (100 - node.metrics.avg_latency_ms) * 0.3 +
    node.metrics.verification_pass_rate * 0.2 +
    node.reputation_score * 0.1
  );
}
```

---

## 6. Availability & Heartbeats

### 6.1 Heartbeat Protocol

Nodes MUST publish heartbeat events every 5 minutes:

```json
{
  "event_type": "NodeAvailabilityReport",
  "inputs": {
    "node_did": "did:key:node1",
    "timestamp": 1702483200000,
    "metrics": {
      "cpu_usage": 45.2,
      "memory_usage": 62.1,
      "disk_usage": 38.5,
      "active_connections": 127,
      "events_processed_last_5min": 543
    }
  }
}
```

### 6.2 Health Checks

External monitors (or other nodes) perform active health checks:

```
GET https://atlas-node.example.com/health
Response: {
  "status": "healthy",
  "uptime_seconds": 86400,
  "version": "1.0.2",
  "capabilities": ["ledger", "qfs"]
}
```

### 6.3 Downtime Penalties

- **< 95% uptime**: Warning, reduced rewards
- **< 90% uptime**: Reputation penalty
- **< 80% uptime**: Stake slashing (10%)
- **Offline > 7 days**: Deregistration

---

## 7. Verification & Challenges

### 7.1 Light Node Verification

Light nodes perform spot checks on QFS computations:

1. Sample random computation results from ledger
2. Download Merkle proof from IPFS
3. Re-execute deterministic computation
4. Compare with published result

### 7.2 Challenge Submission

If mismatch found:

```json
{
  "event_type": "ComputationDispute",
  "inputs": {
    "disputed_event_id": "evt_qfs_001",
    "challenger_did": "did:key:light-node1",
    "expected_result": { "coherence_score": 0.85 },
    "actual_result": { "coherence_score": 0.87 },
    "proof_cid": "bafybei..."
  }
}
```

### 7.3 Dispute Resolution

1. Other nodes re-verify the disputed computation
2. Majority vote (weighted by stake + reputation)
3. **If original node wrong**: Stake slashed (20%), reputation penalty
4. **If challenger wrong**: Reputation penalty, gas fees forfeited

---

## 8. Node Rewards

### 8.1 Reward Sources

Nodes earn **NOD tokens** for:

| Activity | Reward Formula |
|----------|----------------|
| **Uptime** | `base_rate * uptime_percent` |
| **QFS Computation** | `per_computation * correctness_rate` |
| **IPFS Pinning** | `per_gb_per_day * storage_provided` |
| **Message Relay** | `per_message * 0.0001` |
| **Verification** | `per_challenge * (if correct)` |

### 8.2 Reward Distribution

Rewards calculated every **epoch** (e.g., 24 hours):

```json
{
  "event_type": "NodeRewardAllocated",
  "inputs": {
    "epoch_id": "epoch_123",
    "node_did": "did:key:node1",
    "breakdown": {
      "uptime": 5.2,
      "computation": 12.3,
      "storage": 3.1,
      "verification": 1.0
    }
  },
  "outcome": {
    "total_nod": 21.6,
    "vesting_schedule": "immediate"
  }
}
```

### 8.3 Stake Requirements

- **Ledger Node**: 1000 FLX minimum
- **QFS Node**: 2000 FLX minimum
- **IPFS Node**: 500 FLX minimum
- **Messaging Node**: 500 FLX minimum
- **OPEN-AGI Node**: 1500 FLX minimum

---

## 9. Slashing Conditions

Stake is slashed for:

| Violation | Penalty |
|-----------|---------|
| **Publishing incorrect computation** | 20% stake |
| **Censoring events** | 50% stake |
| **Double-signing** | 100% stake + deregistration |
| **Downtime > 80%** | 10% stake |
| **Failed verification challenge** | 5% stake |

---

## 10. Node Deregistration

### 10.1 Voluntary Deregistration

Node operator can withdraw by:

1. Publishing `NodeDeregistered` event
2. Waiting for unbonding period (7 days)
3. Claiming stake back (minus any penalties)

### 10.2 Forced Deregistration

Network can force deregister nodes that:

- Are offline > 7 days
- Have been slashed ≥ 2 times
- Fail governance vote (e.g., malicious behavior)

---

## 11. Security Hardening

### 11.1 DDoS Protection

- Rate limiting: 100 req/s per IP
- WebSocket connection limits: 1000 concurrent
- Use Cloudflare or similar DDoS mitigation

### 11.2 Access Control

- Admin endpoints (e.g., `/admin/*`) protected by API keys
- Ledger write access requires valid DID signatures
- CORS restricted to known client origins

### 11.3 Monitoring & Alerts

Node operators SHOULD:

- Monitor disk usage (alert at 80%)
- Monitor memory usage (alert at 90%)
- Set up log aggregation (ELK stack, Loki, etc.)
- Configure alerting (PagerDuty, Opsgenie, etc.)

---

## 12. Deployment Guide

### 12.1 Quick Start (Docker)

```bash
# Clone node repository
git clone https://github.com/atlas-qfs/node.git
cd node

# Configure environment
cp .env.example .env
# Edit .env: set NODE_DID, STAKE_AMOUNT, ENDPOINT

# Start node
docker-compose up -d

# Check logs
docker-compose logs -f

# Register node
docker-compose exec node python scripts/register_node.py
```

### 12.2 Configuration File

```yaml
# config.yml
node:
  did: "did:key:z6Mkh..."
  types: ["ledger", "qfs"]
  endpoint: "https://node.example.com"
  
stake:
  amount: 2000
  token: "FLX"

ledger:
  substrate: "postgresql"  # or "cosmos-sdk"
  connection_string: "postgresql://..."

qfs:
  modules:
    - "CoherenceEngine"
    - "TreasuryEngine"
    - "SafetyGuard"
  
ipfs:
  api_url: "http://ipfs:5001"
  gateway_url: "http://ipfs:8080"
  pin_strategy: "policy-based"  # or "all", "manual"

performance:
  max_concurrent_computations: 100
  cache_size_mb: 512
```

---

## 13. Best Practices

### 13.1 High Availability

- Run multiple instances behind load balancer
- Use database replication (for ledger nodes)
- Geographic distribution for redundancy

### 13.2 Performance Optimization

- Cache PolicyRegistry queries (TTL: 5 minutes)
- Use SSD storage for ledger
- Enable HTTP/2 for endpoints
- Compress API responses (gzip)

### 13.3 Operational Security

- Rotate API keys monthly
- Update software weekly
- Backup ledger data daily
- Use hardware security modules (HSM) for DID private keys

---

## 14. Support & Community

- **Documentation**: <https://docs.atlas-qfs.network>
- **Forum**: <https://forum.atlas-qfs.network>
- **Discord**: <https://discord.gg/atlas-qfs>
- **GitHub**: <https://github.com/atlas-qfs/node>

---

**End of Node Operation Protocol v1.0.0**
