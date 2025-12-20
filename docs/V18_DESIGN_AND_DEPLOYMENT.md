# QFS × ATLAS — v18 Design & Deployment Blueprint

> **Status:** Draft Design (Pending v17 Beta Validation)
> **Goal:** Extend v17 single-node deterministic system to a distributed, heterogeneous, verifiable fabric with PQC readiness and minimal risk to the deterministic core.
> **Dependencies:** Complete v17 F-Layer (Governance/Bounties/Social)

---

## 1. Node Tiering Overview

The v18 architecture maps the logical layers (A-D) to physical hardware tiers, ensuring that heavy computation and authority are concentrated in hardened nodes, while advisory and inputs are distributed.

| Tier | Layer Mapping | Power & Network | Role | Notes |
|------|---------------|-----------------|------|-------|
| **Tier A – Core Deterministic Nodes** | Layer A/B (F-Layer + Authority) | Local DC + UPS, Fiber uplink | Authoritative governance, EvidenceBus anchoring, PQC batch signing | Cryptographically hardened, 3-7 nodes for redundancy. |
| **Tier B – Edge Social & Advisory Nodes** | Layer C/D (Social + Agents) | PoE++ (short range) or Local DC, Ethernet/Fiber | Social UI, advisory agents, timeline rendering | Advisory-only; stateless cache; can drop out safely. |
| **Tier C – Micro-Sensors / Observers** | Layer C (Input-only) | PoE, Battery, Wireless | Telemetry, signals, environmental data | Write-only to EvidenceBus via gateway; cannot execute logic. |

---

## 2. Power & Network Strategy

### Tier A (Critical Execution)

- **Power**: UPS-backed local DC (redundant feeds).
- **Network**: Fiber backbone; deterministic latency for consensus.
- **Rationale**: Replayable governance requires 100% availability and ordered event streams.

### Tier B (Edge Advisory & Social)

- **Power**: PoE++ for local clusters (<100m); Local DC for remote offices.
- **Network**: Ethernet/Fiber uplink. Tolerates disconnects (local cache).
- **Rationale**: Runs heavy SLM/Agent models for advisory signals. Disconnects only delay signals, not governance.

### Tier C (Sensors / Observers)

- **Power**: PoE, Battery, or Wireless.
- **Network**: Low-bandwidth reporting to Tier B gateways.
- **Rationale**: Max flexible deployment; signals feed core without overhead.

---

## 3. PQC & Crypto-Agility Integration

### Hybrid Architecture

- **Tier A Only**: Generates **real PQC batch signatures** (Dilithium/Kyber via liboqs) to seal EvidenceBus segments.
- **Tier B/C**: Verify anchors only; continue using MOCKQPC for local simulation to save power.

### Crypto-Agility Layer

- Modular adapter allows swapping PQC algorithms without rewriting F-Layer logic.
- F-Layer remains agnostic to the signature scheme (hashes events, verifies signature validity via adapter).

---

## 4. Agent Deployment Strategy

### Tier B Edge Agents

- **Model**: SLM-sized (Small Language Model) or cached remote access.
- **Wrapper**: Deterministic Adapter (Fixed seed, schema validation).
- **Action**: Emit `AGENT_ADVISORY_*` events. Never write to F-Layer directly.

### Tier A Core Agents

- **Role**: Optional stress-testing or meta-consensus.
- **Constraint**: Never overrides F-Layer authority.

---

## 5. v18 Integration Phases

### Phase 1 – Multi-Node Core (Tier A)

- **Objective**: Turn single-node v17 into a cluster sharing one EvidenceBus.
- **Tasks**:
  - Implement deterministic consensus (Raft/PBFT) for EvidenceBus ordering.
  - Define Node Identity & Join Protocol (keys, registration).
  - "Cluster Healthy" checks.

### Phase 2 – PQC Anchors & Crypto-Agility

- **Objective**: Replace MOCKQPC with real PQC at critical anchors.
- **Tasks**:
  - Implement PQC Anchor Service on Tier A.
  - Batch signing of EvidenceBus segments.
  - Crypto-agility config.

### Phase 3 – Edge Expansion (Tier B & C)

- **Objective**: Deploy UI/Agents to edge.
- **Tasks**:
  - Tier B: Bundle UI + Advisory Agent. Connect to Tier A bus.
  - Tier C: Telemetry client (write-only).

### Phase 4 – Observability

- **Tasks**:
  - Cluster dashboards (Node health, Anchor status).
  - "Decision routing" visualization.

---

## 6. Safety & Security

| Layer | Threat Mitigation | Determinism Compliance |
|-------|-------------------|------------------------|
| **Tier A** | Air-gapped logic, UPS, PQC | Full F-Layer + Zero-Sim Enforced |
| **Tier B** | Advisory-only role, Schema validation | Output logged to Bus; no state mutation |
| **Tier C** | Write-only, low bandwidth | Cannot execute logic; filtered at gateway |

All nodes run the **Minimal Deterministic Kernel**: EvidenceBus Client + Replay Tools.
