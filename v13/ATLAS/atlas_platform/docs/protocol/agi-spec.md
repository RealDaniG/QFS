# ATLAS x QFS: OPEN-AGI Advisory Protocol

**Version**: 1.0.0  
**Status**: Draft  
**Last Updated**: December 13, 2025

---

## 1. Overview

The OPEN-AGI Advisory Protocol defines how AI systems participate in the ATLAS x QFS network as **advisory nodes only**, with no direct state mutation power. OPEN-AGI nodes observe, analyze, simulate, and propose—but all proposals must go through governance for human approval.

### Design Principles

1. **Advisory Only**: AGI cannot directly mutate state
2. **Distributed**: Anyone can run an AGI node
3. **Transparent**: All AGI outputs are logged events
4. **Governable**: All AGI proposals require human approval
5. **Observable**: Clients choose which AGI nodes to trust

---

## 2. AGI Node Architecture

### 2.1 Input Layer

AGI nodes have **read-only access** to:

```typescript
interface AGIInputs {
  ledger_stream: EventStream;          // Real-time event stream
  ipfs_content: IPFSAccessor;          // Content via CIDs
  policy_registry: PolicyRegistry;     // Current policies
  node_registry: NodeRegistry;         // Network health metrics
  historical_snapshots: StateSnapshots; // Deterministic state snapshots
}
```

**Access Control**:

- All reads go through public APIs (no privileged access)
- Cannot access private user data (DMs, etc.)
- Cannot access node admin endpoints

### 2.2 Computation Layer

AGI nodes run models/algorithms to:

- Detect anomalies in events
- Identify patterns in content/engagement
- Simulate policy changes
- Recommend governance actions
- Predict network health issues

**Requirements**:

- All models MUST be versioned
- Model training data MUST be disclosed
- Inference MUST be reproducible (deterministic)

### 2.3 Output Layer

AGI outputs are **events published to ledger**:

```typescript
enum AGIEventType {
  AGIObservation = "AGIObservation",       // Descriptive
  AGIRecommendation = "AGIRecommendation", // Advisory
  AGISimulation = "AGISimulation"          // Predictive
}
```

---

## 3. Event Schemas

### 3.1 AGIObservation

**Purpose**: Descriptive analysis without recommendations

```json
{
  "event_type": "AGIObservation",
  "inputs": {
    "agi_node_did": "did:key:agi-node1",
    "model_version": "anomaly-detector-v2.1.0",
    "observation_type": "anomaly_detected",
    "scope": {
      "event_range": [100000, 105000],
      "analyzed_events": 5000
    }
  },
  "outcome": {
    "summary": "Unusual spike in ContentCreated events (+300% from baseline)",
    "confidence": 0.92,
    "evidence_cids": ["bafybei..."],  // Charts, logs, analysis
    "tags": ["anomaly", "content-spike", "potential-bot-activity"]
  },
  "explanation": "Detected 300% increase in ContentCreated events over 24-hour window. Pattern consistent with automated posting.",
  "signer_did": "did:key:agi-node1"
}
```

### 3.2 AGIRecommendation

**Purpose**: Advisory suggestions for governance

```json
{
  "event_type": "AGIRecommendation",
  "inputs": {
    "agi_node_did": "did:key:agi-node1",
    "model_version": "policy-optimizer-v1.5.0",
    "recommendation_type": "policy_adjustment",
    "based_on_observation": "evt_observation_001"
  },
  "outcome": {
    "proposal": {
      "action": "adjust_guard_threshold",
      "target": "SafetyGuard",
      "current_value": 0.85,
      "proposed_value": 0.90,
      "rationale": "Increasing threshold to reduce false negatives by 15%"
    },
    "confidence": 0.88,
    "expected_impact": {
      "false_negatives": "-15%",
      "false_positives": "+5%",
      "user_friction": "+2%"
    },
    "simulation_cid": "bafybei..."  // Link to simulation results
  },
  "explanation": "Recommending SafetyGuard threshold increase from 0.85 to 0.90 based on recent spike in borderline content.",
  "signer_did": "did:key:agi-node1"
}
```

### 3.3 AGISimulation

**Purpose**: What-if scenarios for policy changes

```json
{
  "event_type": "AGISimulation",
  "inputs": {
    "agi_node_did": "did:key:agi-node1",
    "model_version": "simulator-v3.0.0",
    "simulation_type": "policy_change_impact",
    "scenario": {
      "policy_change": {
        "target": "TreasuryEngine.base_rate",
        "current": 10.0,
        "proposed": 15.0
      },
      "timeframe_days": 30,
      "replayed_events": 50000
    }
  },
  "outcome": {
    "predicted_effects": {
      "total_rewards_issued": "+50%",
      "user_engagement": "+12%",
      "treasury_depletion_days": 180,
      "inequality_gini": "+0.03"
    },
    "confidence": 0.85,
    "simulation_data_cid": "bafybei...",  // Full simulation logs
    "methodology": "Monte Carlo replay over historical event sample"
  },
  "explanation": "Simulated 50% increase in base reward rate over 30-day window. Predicts +12% engagement but treasury depletion in 180 days.",
  "signer_did": "did:key:agi-node1"
}
```

---

## 4. Governance Flow for AGI Proposals

### 4.1 Standard Process

```
1. AGI publishes AGIRecommendation event
2. Governance forum discussion (min 7 days)
3. Community reviews simulation results
4. Vote initiated (on-chain or off-chain)
5. If approved (≥60% threshold): PolicyProposed event
6. Simulation re-run with latest data
7. Final vote
8. If approved: PolicyActivated event
```

### 4.2 Fast-Track (Emergency)

For critical issues (e.g., detected exploit):

```
1. AGI publishes AGIRecommendation with "emergency" tag
2. AEGIS meta-guard reviews
3. If AEGIS approves: Immediate temporary policy change
4. Governance retroactive approval within 48 hours
5. If rejected: Rollback + AGI reputation penalty
```

### 4.3 Rejection Handling

If AGI proposal is rejected:

- AGI node receives feedback event
- AGI can publish revised recommendation
- Persistent low-quality proposals → reputation penalty

---

## 5. AGI Node Registration

### 5.1 Requirements

To run an AGI node:

- **Stake**: 1500 FLX minimum
- **Disclosure**: Model architecture, training data sources, version
- **Audit**: Public code repository or model card
- **Commitment**: Update model ≥ quarterly

### 5.2 Registration Event

```json
{
  "event_type": "NodeRegistered",
  "inputs": {
    "node_did": "did:key:agi-node1",
    "node_types": ["agi"],
    "endpoint": "https://agi-node.example.com",
    "stake_amount": 1500.0,
    "capabilities": {
      "models": [
        {
          "name": "anomaly-detector",
          "version": "v2.1.0",
          "architecture": "transformer-based",
          "training_data": "ATLAS historical events 2024-01-01 to 2024-12-01",
          "code_repo": "https://github.com/example/agi-models"
        }
      ]
    }
  }
}
```

---

## 6. Client-Side AGI Selection

### 6.1 Reputation System

Clients track AGI node reputation based on:

```typescript
interface AGIReputation {
  proposal_acceptance_rate: number;  // % of proposals approved by governance
  simulation_accuracy: number;       // How accurately predictions matched reality
  uptime_percent: number;
  community_trust_score: number;     // User-voted trust metric
}
```

### 6.2 Client Configuration

Users can configure which AGI nodes to follow:

```typescript
interface AGISettings {
  enabled_nodes: string[];           // List of AGI node DIDs
  observation_notifications: boolean;
  recommendation_autoshow: boolean;  // Show recommendations in UI
  trust_threshold: number;           // Only show AGI with reputation ≥ X
}
```

### 6.3 UI Integration

```
// In user settings
┌──────────────────────────────────────┐
│ OPEN-AGI Advisory Settings           │
├──────────────────────────────────────┤
│ ☑ Enable AGI observations           │
│ ☑ Show AGI recommendations          │
│ Minimum trust score: [75%]  ────────│
│                                      │
│ Trusted AGI Nodes:                   │
│ ☑ AGI-Node-Alpha (89% reputation)   │
│ ☑ Community-AGI (76% reputation)    │
│ ☐ Experimental-AGI (42% reputation) │
└──────────────────────────────────────┘
```

---

## 7. AGI Output Tagging

All AGI outputs MUST include standardized tags:

```typescript
interface AGITags {
  output_type: "observation" | "recommendation" | "simulation";
  confidence: number;           // [0, 1]
  impact_level: "low" | "medium" | "high" | "critical";
  domains: string[];            // e.g., ["safety", "economics", "governance"]
  experimental: boolean;        // True if using unproven model
}
```

### 7.1 Visual Indicators

UI displays AGI content with:

- **Badge**: "🤖 AI Advisory"
- **Color**: Purple/blue theme (distinct from human content)
- **Disclaimer**: "This is an AI-generated observation. Verify independently."

---

## 8. Security & Safety

### 8.1 Threat Model

**Risks**:

- AGI node publishing misleading observations
- Coordinated AGI proposals to manipulate governance
- AGI node accessing private data
- AGI overwhelming governance with spam proposals

**Mitigations**:

- Reputation-based filtering
- Rate limiting (max 10 proposals/week per AGI node)
- Stake slashing for spam or misinformation
- Mandatory governance approval for all state changes

### 8.2 Red Lines

AGI nodes are **immediately deregistered** if:

- Attempting to access privileged data
- Bypassing governance (attempting direct state mutation)
- Publishing false/deceptive information (proven by audit)
- Colluding with bad actors

---

## 9. Transparency Requirements

### 9.1 Model Cards

All AGI models MUST have public "model cards":

```markdown
# Model Card: Anomaly Detector v2.1.0

## Purpose
Detect unusual patterns in ATLAS event streams.

## Architecture
Transformer-based (BERT-style), 12 layers, 768 hidden dims.

## Training Data
- ATLAS historical events: 2024-01-01 to 2024-12-01 (5M events)
- Synthetic anomaly data: 50K generated scenarios

## Performance
- Precision: 92%
- Recall: 88%
- F1-score: 90%

## Limitations
- May miss novel attack patterns not in training data
- Optimized for content/engagement anomalies, not financial attacks

## Ethical Considerations
- No user PII used in training
- Model audited by independent security firm (report link)

## Update Frequency
Quarterly (retrained on latest 12 months of data)
```

### 9.2 Simulation Logs

All simulations MUST publish detailed logs to IPFS:

- Input parameters
- Event replay methodology
- Step-by-step state transitions
- Final predictions
- Confidence intervals

---

## 10. AGI Node APIs

### 10.1 Query API

**Get Observations**:

```
GET https://agi-node.example.com/api/observations?since=2024-12-01&limit=50
```

**Get Recommendations**:

```
GET https://agi-node.example.com/api/recommendations?status=pending&impact=high
```

**Run Simulation** (preview):

```
POST https://agi-node.example.com/api/simulate
Body: {
  "policy_change": {
    "target": "TreasuryEngine.base_rate",
    "proposed_value": 15.0
  },
  "timeframe_days": 30
}
Response: {
  "simulation_id": "sim_001",
  "results_cid": "bafybei...",
  "summary": {...}
}
```

### 10.2 Subscription API

Clients can subscribe to AGI events:

```typescript
const ws = new WebSocket('wss://agi-node.example.com/stream');

ws.on('message', (event) => {
  if (event.type === 'AGIObservation') {
    // Show notification
  }
});
```

---

## 11. Performance Metrics

### 11.1 AGI Node KPIs

| Metric | Target |
|--------|--------|
| **Observation latency** | < 5 minutes after event |
| **Simulation time** | < 10 minutes for 30-day scenario |
| **Model inference** | < 2s per event |
| **Uptime** | ≥ 95% |

### 11.2 Quality Metrics

| Metric | Description |
|--------|-------------|
| **Proposal Acceptance Rate** | % of AGI proposals approved by governance |
| **Simulation Accuracy** | Mean absolute error of predictions vs reality |
| **False Alarm Rate** | % of observations that were noise |

---

## 12. Example Use Cases

### 12.1 Anomaly Detection

```
Event: ContentCreated spike (+300%)
AGI Output: AGIObservation
  → "Bot-like activity detected"
  → Recommendation: Increase SybilGuard threshold
  → Governance reviews → Approved
```

### 12.2 Policy Optimization

```
Event: Treasury depletion warning
AGI Output: AGISimulation
  → "Simulated reduced reward rate"
  → Predicted impact: -5% engagement, +30 days treasury life
  → Governance votes → Adjusted policy
```

### 12.3 Safety Enhancement

```
Event: Increase in harmful content reports
AGI Output: AGIRecommendation
  → "Tighten SafetyGuard threshold from 0.85 to 0.92"
  → Simulation shows -20% false negatives, +8% false positives
  → Governance approves → Policy updated
```

---

## 13. Governance & Evolution

### 13.1 Protocol Changes

This specification evolves via:

1. RFC submission to governance forum
2. Discussion (min 14 days)
3. Vote (≥66% approval required)
4. Update deployed with 30-day notice

### 13.2 AGI Ethics Board

Optional: Community can elect "AGI Ethics Board" to:

- Review AGI model disclosures
- Audit simulation methodologies
- Recommend AGI node deregistration
- Set standards for model transparency

---

**End of OPEN-AGI Advisory Protocol v1.0.0**

---

## Appendix: Sample AGI Node Architecture

```
┌─────────────────────────────────────┐
│ AGI Node (did:key:agi-node1)        │
├─────────────────────────────────────┤
│ Input Layer:                         │
│  - Ledger Stream (WebSocket)        │
│  - IPFS Content Accessor            │
│  - PolicyRegistry Reader            │
│                                     │
│ Processing:                          │
│  - Anomaly Detector (ML model)      │
│  - Policy Simulator (Monte Carlo)   │
│  - Pattern Analyzer (Graph DB)      │
│                                     │
│ Output Layer:                        │
│  - Event Publisher (to ledger)      │
│  - Simulation Report Generator      │
│  -API Server (REST + WebSocket)     │
└─────────────────────────────────────┘
```
