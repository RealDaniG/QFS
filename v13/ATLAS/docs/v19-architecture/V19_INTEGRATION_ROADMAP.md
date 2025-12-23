# ATLAS v19 Integration Roadmap

**Strategy:** Layered Integration with Security-First Principals

## Phase 1: The Trust Layer (Foundation) - v19.0

**Focus:** Enabling distributed data without losing verification.

- [ ] **Data Schemas & Envelopes**
  - Define `TrustedEnvelope` protobuf/JSON schema (Payload + Signature + Metadata).
  - Implement `EnvelopeVerifier` in Core.
- [ ] **Identity Binding**
  - Implement `PeerIdentity` handshake (Wallet <-> PeerID).
- [ ] **Storage Interface (Local-First)**
  - Implement the "Content Store" interface (abstracting backend).
  - default implementation: Local DB (SQLite/JSON) behaving *like* IPFS (CID addressing).

## Phase 2: The Storage Layer (IPFS) - v19.1

**Focus:** Content addressing and distribution.

- [ ] **IPFS Sidecar Integration**
  - Connect Core to IPFS node.
  - Implement `IPFSContentStore` (implements Phase 1 interface).
- [ ] **Pinning Strategy**
  - Implement "Cluster Pinning" (Node A/B/C replication).
- [ ] **GC Policies**
  - Implement "Least Recently Used" or "Reputation Based" unpinning.

## Phase 3: The Network Layer (libp2p) - v19.2

**Focus:** Real-time synchronization.

- [ ] **GossipSub Integration**
  - Topics: `/atlas/envelope/v1` (Strictly envelope exchange).
- [ ] **Deterministic Verification Gate (DVG)**
  - The Firewall for P2P: Validates incoming envelopes *before* they hit the app state.
- [ ] **Peer Discovery**
  - mDNS (Local) + Bootstrap config.

## Phase 4: The Intelligence Layer (Open-A.G.I) - v19.3

**Focus:** Autonomous assistance with safety rails.

- [ ] **Agent Sandbox**
  - Define `AgentAuthority` contracts.
  - specialized agents: `BountyAnalyst`, `FeedCurator`.
- [ ] **Forensic Logging**
  - All agent inputs/outputs recorded to immutable audit log.
- [ ] **Human-in-the-Loop UI**
  - Interfaces for users to "Approve/Reject" agent suggestions.

## Phase 5: Full Convergence - v19.4

**Focus:** Integration and Polish.

- [ ] **Reputation-based Routing**
  - Content priority based on Author Reputation.
- [ ] **System Degradation drills**
  - Verify app works when IPFS/P2P/AGI are offline.
