# v18 Distributed Fabric - Tasks

> **Status:** Phase 2/3 Implementation
> **Blueprint:** `docs/V18_DESIGN_AND_DEPLOYMENT.md`

## Phase 1: Multi-Node Core (Consensus)

- [x] Raft Log Replication for `EvidenceBus` (Interfaces, Logic, & Multi-node Simulator)
- [x] Add `v18/consensus/` module (Interfaces, Schemas, State Machine Core)
- [x] Multi-node Simulation Harness (`simulator.py`)
- [ ] Define Node Identity Protocol (Keys, Registration)

## Phase 2: PQC Anchors (Tier A)

- [x] Implement `v18/pqc/anchors.py` (BatchAnchorService Interface & Mock)
- [x] Deterministic PQC Anchor generation and verification tests
- [ ] Define `IPQCProvider` extension for Batched Signing (Real LibOQS)
- [ ] Select LibOQS bindings (Dilithium/Kyber)

## Phase 3: Consensus & Bus Integration

- [x] Implement `EvidenceBusConsensusAdapter` (Consensus Commit -> EBus wiring)
- [x] End-to-end integration test (Propose -> Consensous -> EBus Append)
- [ ] Define Edge Node Bootstrap Config
- [ ] Implement Tier C Telemetry Gateway
- [ ] Bundle UI for Edge deployment

## Phase 4: Observability

- [ ] Cluster Status Dashboard
