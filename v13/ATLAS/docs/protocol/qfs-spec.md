# ATLAS x QFS: QFS Protocol Specification

**Version**: 1.0.0  
**Status**: Draft  
**Last Updated**: December 13, 2025

---

## 1. Overview

The QFS (Quantum Financial System) Protocol defines the deterministic, distributed computation layer for content coherence scoring, economic reward allocation, and guard evaluation in the ATLAS network. QFS operates as a **distributed protocol**, not a centralized backend, with multiple nodes executing computations and publishing verifiable results to the Event Ledger.

### Design Goals

- **Determinism**: Same inputs always produce same outputs
- **Verifiability**: Computation results can be independently verified
- **Decentralization**: No single QFS authority; multiple nodes compete
- **Transparency**: All rules, policies, and computations are auditable
- **Performance**: Sub-second response times for user-facing operations

---

## 2. Three-Layer Architecture

### 2.1 On-Chain Rules (Layer 1)

**Stored**: Smart contracts or L2 modules  
**Purpose**: Define base economic parameters governed by the network

```solidity
// Pseudocode for RewardTypes contract
contract RewardTypes {
  enum RewardType { Content, Engagement, Coherence, Governance, Infrastructure }
  
  struct RewardConfig {
    uint256 baseRate;      // Base FLX per unit
    uint256 cap;           // Maximum per event
    uint256 vestingDays;   // Vesting period
  }
  
  mapping(RewardType => RewardConfig) public configs;
  
  function updateRewardConfig(RewardType rt, RewardConfig memory config)
    external
    onlyGovernance
  {
    configs[rt] = config;
    emit RewardConfigUpdated(rt, config);
  }
}
```

**Governed Parameters**:

- Reward types and base rates
- Token limits (min/max per action)
- Penalty rates
- Reputation dimensions and weights
- Node operator reward formulas

### 2.2 Off-Chain Verifiable Computation (Layer 2)

**Executed by**: Distributed QFS nodes  
**Purpose**: Complex computations (coherence scoring, reward calculations)

**Key Modules**:

1. **CoherenceEngine**: Ranks content by coherence score
2. **TreasuryEngine**: Calculates rewards and penalties
3. **Guards**: Evaluate content safety, economics, Sybil resistance
4. **ReputationEngine**: Aggregates multi-dimensional reputation

**Verifiability Mechanism**:

```typescript
interface ComputationResult {
  input_hash: string;           // Hash of inputs
  output: unknown;              // Computation result
  merkle_proof: string[];       // Proof of computation steps
  policy_version: string;       // PolicyRegistry version used
  computation_hash: string;     // Hash of (inputs + policy + output)
  node_signature: string;       // Node's signature on computation_hash
}
```

### 2.3 Versioned Policies & Guards (Layer 3)

**Stored**: PolicyRegistry (on ledger or on-chain)  
**Purpose**: Versioned rules that QFS nodes MUST follow

```typescript
interface Policy {
  policy_id: string;
  version: string;              // Semantic versioning (e.g., "1.2.3")
  effective_from: number;       // Sequence number
  effective_until?: number;     // Optional expiration
  rules: PolicyRules;
  guards_config: GuardConfig[];
  activation_event_id: string;  // Ledger event that activated this policy
}
```

---

## 3. CoherenceEngine Specification

### 3.1 Purpose

Rank content by **coherence score**: a measure of how well content aligns with community values, engagement quality, and economic contribution.

### 3.2 Inputs

```typescript
interface CoherenceInput {
  content_cid: string;            // IPFS CID of content
  author_did: string;             // Author's DID
  context: {
    community_id?: string;        // Optional community context
    topic_tags: string[];         // Content categorization
    timestamp: number;            // Logical timestamp
  };
  signals: {
    engagement_count: number;     // Likes, comments, reposts
    unique_engagers: number;      // Distinct DIDs
    engagement_quality: number;   // Avg reputation of engagers
    decay_factor: number;         // Time-based decay (optional)
  };
  policy_version: string;
}
```

### 3.3 Computation

**Formula** (simplified, actual formula in `QFS-Repo/src/core/CoherenceEngine.py`):

```python
def compute_coherence(inputs: CoherenceInput, policy: Policy) -> float:
    """
    Coherence score ∈ [0, 1]
    
    coherence = w1 * engagement_quality +
                w2 * uniqueness_bonus +
                w3 * topic_alignment +
                w4 * reputation_factor +
                (1 - decay)
    
    Where weights (w1, w2, w3, w4) are in policy.rules
    """
    policy_weights = policy.rules.coherence_weights
    
    # Ensure determinism: use CertifiedMath for all floating-point ops
    engagement_score = certified_log(inputs.signals.engagement_count + 1)
    quality_score = inputs.signals.engagement_quality
    
    # Combine with policy weights
    raw_score = (
        policy_weights.engagement * engagement_score +
        policy_weights.quality * quality_score +
        ...
    )
    
    # Clamp to [0, 1]
    return min(max(raw_score, 0.0), 1.0)
```

### 3.4 Outputs

```typescript
interface CoherenceOutput {
  content_cid: string;
  coherence_score: number;      // [0, 1]
  breakdown: {
    engagement: number;
    quality: number;
    alignment: number;
    reputation: number;
  };
  merkle_proof: string[];       // Proof of computation steps
}
```

### 3.5 Ledger Event

QFS node publishes:

```json
{
  "event_type": "CoherenceScored",
  "inputs": {
    "content_cid": "bafybei...",
    "input_hash": "0xabc123..."  // Hash of full CoherenceInput
  },
  "outcome": {
    "coherence_score": 0.87,
    "breakdown": {...},
    "computation_proof_cid": "bafybei..."  // IPFS CID of full proof
  },
  "policy_version": "v1.0.0",
  "signer_did": "did:key:qfs-node1"
}
```

---

## 4. TreasuryEngine Specification

### 4.1 Purpose

Calculate deterministic rewards and penalties based on content quality, engagement, and governance participation.

### 4.2 Inputs

```typescript
interface RewardInput {
  event_id: string;             // Ledger event (e.g., ContentCreated)
  event_type: string;
  actor_did: string;
  metrics: {
    coherence_score?: number;
    engagement_count?: number;
    guard_pass_rate?: number;
    governance_participation?: number;
  };
  policy_version: string;
}
```

### 4.3 Computation

```python
def calculate_reward(inputs: RewardInput, policy: Policy) -> RewardOutput:
    """
    Reward = base_rate * multiplier * caps
    
    multiplier depends on:
    - Coherence score
    - Guard pass rate
    - Reputation
    """
    reward_config = policy.rules.reward_configs[inputs.event_type]
    
    base = reward_config.base_rate
    multiplier = (
        inputs.metrics.coherence_score *
        inputs.metrics.guard_pass_rate *
        reputation_factor(inputs.actor_did)
    )
    
    raw_reward = base * multiplier
    
    # Apply cap
    return min(raw_reward, reward_config.cap)
```

### 4.4 Outputs

```typescript
interface RewardOutput {
  recipient_did: string;
  amount: number;
  token: string;              // "FLX", "CHR", etc.
  vesting_schedule?: {
    immediate: number;
    vested_over_days: number;
  };
  breakdown: {
    base_rate: number;
    coherence_multiplier: number;
    reputation_multiplier: number;
    final_amount: number;
  };
}
```

### 4.5 Ledger Event

```json
{
  "event_type": "RewardAllocated",
  "inputs": {
    "content_event_id": "evt_content_001",
    "calculation_proof_cid": "bafybei..."
  },
  "outcome": {
    "recipient": "did:key:user123",
    "amount": 10.5,
    "token": "FLX",
    "breakdown": {...}
  },
  "policy_version": "v1.0.0"
}
```

---

## 5. Guards Specification

### 5.1 Purpose

Evaluate content against safety, economic, and community standards **before** it impacts rewards or visibility.

### 5.2 Guard Interface

All guards MUST implement:

```typescript
interface Guard {
  name: string;
  version: string;
  
  evaluate(context: GuardContext): GuardResult;
}

interface GuardContext {
  content_cid: string;
  author_did: string;
  community_id?: string;
  policy: Policy;
}

interface GuardResult {
  pass: boolean;
  score: number;           // [0, 1] confidence
  reason?: string;         // Explanation if failed
  evidence_cid?: string;   // Optional: IPFS CID of detailed evidence
}
```

### 5.3 Standard Guards

**SafetyGuard**:

- Detects harmful content (violence, abuse, illegal activity)
- Uses deterministic content classification models (versioned)
- Output: `{ pass: true/false, score: 0.95, reason: "No safety violations" }`

**EconomicsGuard**:

- Prevents gaming, collusion, manipulation
- Checks for Sybil patterns, vote buying, wash trading
- Output: `{ pass: true/false, score: 0.88, reason: "No economic manipulation detected" }`

**SybilGuard**:

- Reputation-based Sybil resistance
- Checks author reputation, past behavior, network position
- Output: `{ pass: true/false, score: 0.92, reason: "Author reputation sufficient" }`

### 5.4 Guard Evaluation Flow

```
Content Submission →
  Query PolicyRegistry for active guards →
    Run each guard in sequence →
      Aggregate results →
        If all pass: accept content, eligible for rewards
        If any fail: log GuardFailed event, content visible but no rewards
```

### 5.5 Ledger Event

```json
{
  "event_type": "GuardEvaluated",
  "inputs": {
    "content_cid": "bafybei...",
    "guards": ["SafetyGuard", "EconomicsGuard"]
  },
  "outcome": {
    "results": [
      { "guard": "SafetyGuard", "pass": true, "score": 0.95 },
      { "guard": "EconomicsGuard", "pass": true, "score": 0.88 }
    ],
    "overall_pass": true
  },
  "policy_version": "v1.0.0"
}
```

---

## 6. PolicyRegistry Specification

### 6.1 Purpose

Centralized, versioned repository of all policies. QFS nodes MUST query PolicyRegistry before every computation.

### 6.2 Storage

**Option A**: On-chain smart contract  
**Option B**: Ledger-based (PolicyActivated events)

### 6.3 Policy Structure

```typescript
interface PolicyRules {
  coherence_weights: {
    engagement: number;
    quality: number;
    alignment: number;
    reputation: number;
  };
  reward_configs: {
    [event_type: string]: {
      base_rate: number;
      cap: number;
      vesting_days: number;
    };
  };
  guard_thresholds: {
    [guard_name: string]: {
      min_score: number;
      required: boolean;
    };
  };
}
```

### 6.4 Policy Lifecycle

```
1. Proposal: PolicyProposed event
2. Simulation: QFS nodes run what-if scenarios
3. Vote: Governance vote (on-chain or weighted by reputation)
4. Activation: PolicyActivated event → new version effective
5. Deactivation: PolicyDeactivated event (if rollback needed)
```

### 6.5 Querying Active Policy

```typescript
function getActivePolicy(timestamp: number): Policy {
  // Find policy where:
  // effective_from <= timestamp < effective_until
  return policyRegistry.query({ active_at: timestamp });
}
```

---

## 7. Verifiable Computation Protocol

### 7.1 Computation Proof Structure

```typescript
interface ComputationProof {
  inputs: {
    content_cid: string;
    policy_version: string;
    // ... other inputs
  };
  steps: Array<{
    operation: string;        // e.g., "multiply", "log", "clamp"
    operands: number[];
    result: number;
    intermediate_hash: string;
  }>;
  final_output: unknown;
  merkle_root: string;        // Merkle root of all steps
}
```

### 7.2 Proof Generation

QFS node:

1. Executes computation step-by-step
2. Records each operation (using CertifiedMath for determinism)
3. Builds Merkle tree of steps
4. Publishes result + Merkle root to ledger
5. Stores full proof on IPFS

### 7.3 Verification by Light Nodes

Light node:

1. Fetch computation result from ledger event
2. Download Merkle proof from IPFS (if needed)
3. Re-execute deterministic computation
4. Compare result with published result
5. If mismatch: publish `ComputationDispute` event

### 7.4 Dispute Resolution

```
1. Light node publishes ComputationDispute event
2. Other nodes re-verify the disputed computation
3. Majority vote determines correct result
4. If original node was wrong: penalty (stake slashing)
5. If disputer was wrong: penalty (reputation loss)
```

---

## 8. Node Operation Requirements

### 8.1 Minimum Node Spec

A QFS node MUST:

- Maintain connection to Event Ledger (read/write)
- Access to IPFS/Filecoin for content retrieval
- Implement all QFS modules (CoherenceEngine, TreasuryEngine, Guards)
- Query PolicyRegistry before every computation
- Publish results with Merkle proofs

### 8.2 Node Registration

```json
{
  "event_type": "NodeRegistered",
  "inputs": {
    "node_did": "did:key:qfs-node1",
    "endpoint": "https://qfs-node1.example.com",
    "stake_amount": 1000.0,
    "capabilities": ["CoherenceEngine", "TreasuryEngine", "Guards"]
  }
}
```

### 8.3 Node Rewards

Nodes earn rewards for:

- **Uptime**: Responding to health checks
- **Correctness**: Passing verification checks
- **Latency**: Fast response times
- **Capacity**: Handling high request volumes

Reward formula (in PolicyRegistry):

```python
node_reward = (
    uptime_factor * base_rate +
    correctness_bonus +
    latency_bonus
)
```

---

## 9. Client Integration

### 9.1 Node Selection

Clients query NodeRegistry (on-chain or ledger-based) for available QFS nodes:

```typescript
interface NodeInfo {
  did: string;
  endpoint: string;
  uptime_percent: number;
  avg_latency_ms: number;
  verification_pass_rate: number;
}

function selectNode(nodes: NodeInfo[]): NodeInfo {
  // Sort by uptime + latency + verification
  return nodes.sort((a, b) =>
    (a.uptime_percent * a.verification_pass_rate / a.avg_latency_ms) -
    (b.uptime_percent * b.verification_pass_rate / b.avg_latency_ms)
  )[0];
}
```

### 9.2 API Calls

**Get Feed Rankings**:

```
GET https://qfs-node1.example.com/api/qfs/coherence/rank?community=general&limit=50
Response: {
  "rankings": [
    { "content_cid": "bafybei...", "coherence_score": 0.92 },
    ...
  ],
  "computation_proof_cid": "bafybei...",
  "policy_version": "v1.0.0",
  "signature": "0x..."
}
```

**Calculate Rewards (Preview)**:

```
POST https://qfs-node1.example.com/api/qfs/rewards/calculate
Body: {
  "content_cid": "bafybei...",
  "preview_only": true
}
Response: {
  "estimated_reward": 12.5,
  "token": "FLX",
  "breakdown": {...}
}
```

---

## 10. Security Considerations

### 10.1 Threat Model

**Threats**:

- Malicious QFS node publishing incorrect results
- Node collusion to game rewards
- Front-running computations
- Denial of service attacks

**Mitigations**:

- Verifiable computation with proofs
- Light nodes perform spot checks
- Majority voting on disputes
- Stake slashing for malicious behavior
- Rate limiting on node APIs

### 10.2 Determinism Requirements

QFS nodes MUST:

- Use CertifiedMath for all floating-point operations
- Avoid wall-clock timestamps (use logical clocks)
- Avoid RNG (use deterministic PRNGs seeded from ledger state)
- Run Zero-Sim compliance scans regularly

---

## 11. Performance Benchmarks

### 11.1 Target Latencies

- **CoherenceEngine**: < 500ms per content item
- **TreasuryEngine**: < 200ms per reward calculation
- **Guard Evaluation**: < 1s for full stack
- **Feed Ranking**: < 2s for 50 items

### 11.2 Throughput

- **Events processed**: 1000/second per node
- **Concurrent computations**: 100 simultaneous
- **Network capacity**: 10 nodes = 10,000 events/second

---

## 12. Governance & Evolution

### 12.1 Policy Changes

All policy changes follow:

1. **Proposal**: Submit to governance forum
2. **Simulation**: QFS nodes run simulations using proposed policy
3. **Review**: Community reviews simulation results
4. **Vote**: On-chain or reputation-weighted vote
5. **Activation**: If approved, PolicyActivated event published

### 12.2 Protocol Upgrades

Major QFS protocol changes (e.g., new computation modules) require:

- 2-week discussion period
- ≥66% governance approval
- 4-week migration period (support both old and new versions)

---

## 13. Examples

### 13.1 Full Coherence Computation

**Input**:

```json
{
  "content_cid": "bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi",
  "author_did": "did:key:zQ3shP2m...",
  "context": {
    "topic_tags": ["technology", "decentralization"],
    "timestamp": 1702483200
  },
  "signals": {
    "engagement_count": 150,
    "unique_engagers": 87,
    "engagement_quality": 0.75
  },
  "policy_version": "v1.0.0"
}
```

**Computation Steps** (abbreviated):

```
1. Fetch policy v1.0.0 → weights = {engagement: 0.3, quality: 0.4, ...}
2. Log(engagement_count + 1) = log(151) = 5.017
3. Normalize engagement: 5.017 / 10 = 0.5017
4. Quality score: 0.75 (from input)
5. Combine: 0.3 * 0.5017 + 0.4 * 0.75 + ... = 0.87
6. Clamp to [0, 1]: 0.87
```

**Output**:

```json
{
  "coherence_score": 0.87,
  "breakdown": {
    "engagement": 0.15,
    "quality": 0.30,
    "alignment": 0.25,
    "reputation": 0.17
  },
  "merkle_proof": ["0xstep1hash", "0xstep2hash", ...],
  "computation_hash": "0xfinal..."
}
```

**Ledger Event**:

```json
{
  "event_type": "CoherenceScored",
  "content_cid": "bafybeigdyrzt...",
  "coherence_score": 0.87,
  "computation_proof_cid": "bafybei...",
  "policy_version": "v1.0.0",
  "signer_did": "did:key:qfs-node1"
}
```

---

## 14. Reference Implementation

See: `QFS-Repo/src/core/` for Python reference implementation:

- `CoherenceEngine.py`
- `TreasuryEngine.py`
- `Guards/SafetyGuard.py`, `Guards/EconomicsGuard.py`, etc.
- `PolicyRegistry.py`
- `CertifiedMath.py` (deterministic math library)

---

**End of QFS Protocol Specification v1.0.0**

---

## Appendix A: Token Economics Summary

| Token | Purpose | Issued For |
|-------|---------|------------|
| FLX | Liquidity | General rewards, transactions |
| CHR | Coherence | High coherence content |
| Ψ (PSI) | Synchronization | Cross-module alignment |
| ATR | Attention | Engagement quality |
| RES | Resources | Infrastructure, storage |
| NOD | Node Operations | Node operator rewards (orthogonal) |

## Appendix B: CertifiedMath Requirements

All QFS computations MUST use `CertifiedMath` library for:

- Logarithms (`certified_log`)
- Exponentials (`certified_exp`)
- Trigonometric functions (`certified_sin`, `certified_cos`)
- Division (`certified_div` with fixed precision)
- Square roots (`certified_sqrt`)

This ensures bit-identical results across different hardware/OS.
