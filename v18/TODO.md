# v18 Distributed Fabric - Tasks

> **Status:** Planning
> **Blueprint:** `docs/V18_DESIGN_AND_DEPLOYMENT.md`

## Phase 1: Multi-Node Core (Consensus)

- [ ] Define Node Identity Protocol (Keys, Registration)
- [ ] Implement Raft/PBFT Log Replication for `EvidenceBus`
- [ ] Add `v18/consensus/` module (Interface only first)

## Phase 2: PQC Anchors (Tier A)

- [ ] Define `IPQCProvider` extension for Batched Signing
- [ ] Select LibOQS bindings (Dilithium/Kyber)
- [ ] Implement `v18/pqc/anchor_service.py`

## Phase 3: Edge Expansion (Tier B/C)

- [ ] Define Edge Node Bootstrap Config
- [ ] Implement Tier C Telemetry Gateway
- [ ] Bundle UI for Edge deployment

## Phase 4: Observability

- [ ] Cluster Status Dashboard
