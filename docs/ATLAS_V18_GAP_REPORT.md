# ATLAS v18 Readiness: Gap Report & Phased Plan

## 1. Executive Summary

The QFS × ATLAS backbone (v18.0) and edge crypto (v18.5 Ascon) are implemented and verified. However, the **ATLAS User Application** (Secure Chat, Spaces, Governance UI) is currently "v17-detached," meaning it runs against mock stubs and in-memory state that does not yet leverage the v18 distributed consensus or the PQC verification anchor.

The platform now has a strong deterministic and distributed core, but the **wallet + app stack is only v18-ready once ATLAS runs end-to-end on the cluster** with unified auth, real data wiring, and full UI coverage.

## 2. Wallet System: Readiness Inventory

### Wallet: Ready / Implemented ✅

- **EIP-191 Auth Flow**: Deterministic challenge -> sign -> verify.
- **Ascon Protected Sessions**: Stateless tokens with embedded claims for multi-node validation.
- **PoE Integration**: All auth lifecycle events emitted to EvidenceBus with PQC anchors.
- **Deterministic Adapters**: Standardized crypto adapters for AEAD/Hash.
- **Multi-Node Auth**: Sessions created on Node A validate on Node B (12/12 tests passing).

### Missing for Full Operation ❌

- **E2E Validation**: Lack of Playwright tests (Login -> Ascon Session -> Distributed Validation -> PoE Event).

## 3. ATLAS App: Readiness Inventory

### App: Ready / Implemented ✅

- **UI Foundations**: Premium Shadcn UI for Dashboard, Chat, and Governance.
- **Explain-This Architecture**: Solid drill-down pattern for deterministic explanations.
- **API Structure**: Standardized FastAPI routes for all social and economic actions.

### Missing for "v18.9 App Alpha" ❌

- **Secure Chat Persistence**: messages reside in local dictionaries; needs consensus-backed persistence via EvidenceBus (`MESSAGE_POSTED`).
- **Live Data Streams**: Dashboards for Governance and Bounties use `setTimeout` stubs; needs connection to v17 Social/Bounty Projections.
- **PQC Verification UX**: Explain-This panel needs real metadata links to consensus logs and PQC anchor artifacts.
- **Cluster Observability**: No UI view of Raft state, node health, or PQC anchor progress.

## 4. Detailed Gap Inventory

### 1. Unified Wallet & Session Management (P0)

- **Problem**: Divergence between `v13/atlas` (legacy) and `v15/auth` (Ascon).
- **Fix**: Migrate ATLAS to `v15.auth.session_manager`. Ensure `useWalletAuth.ts` honors the Ascon token lifecycle.

### 2. QFSClient → v18 Cluster Bridge (P0)

- **Problem**: `QFSClient` uses a `StubAdapter` that denies writes.
- **Fix**: Implement `v18ClusterAdapter` for leader discovery and transaction forwarding. Replace `StubAdapter` in all ATLAS route dependencies.

### 3. Social & Governance Data Wiring (P1)

- **Problem**: In-memory state and mock feed lists.
- **Fix**: Map UI events to EvidenceBus events (e.g., `MESSAGE_POSTED`, `PROPOSAL_CREATED`). Refactor SocialProjections to read from the distributed log.

### 4. Explain-This & PQC UX (P1)

- **Problem**: No "Proof of Evidence" drill-down to real v18 artifacts.
- **Fix**: Connect UI to `QFSReplaySource` for v18.3 PQC verification. Add "Verified by PQC" badges to anchored entries.

### 5. Cluster Observability Dashboard (P2)

- **Problem**: "Black box" cluster state.
- **Fix**: Build a Tier A status view in Admin UI showing Leader, Term, Commit Index, and PQC Anchor timelines.

## 5. Implementation Roadmap (Phased)

### Phase 1: Auth & Bridge Sync (v18.6)

- [ ] Migrate ATLAS API to Ascon-protected sessions.
- [ ] Implement `v18ClusterAdapter` for QFSClient.
- [ ] Add Multi-Node login validation tests.

### Phase 2: Live Data Integration (v18.7)

- [ ] Connect Secure Chat to EvidenceBus events.
- [ ] Wire Governance/Bounties to real v17 F-Layer Projections.
- [ ] Verify state consistency across 3-node restarts.

### Phase 3: PQC & Observability (v18.8)

- [ ] Build Cluster Health Dashboard.
- [ ] Wire Explain-This to v18 verification logs.
- [ ] Implement PQC Anchor visualizations.

## 6. Readiness Criteria for `v18.0.0-alpha-app`

- ✅ Auth stack unified (Ascon-only).
- ✅ `v18ClusterAdapter` operational (No stubs).
- ✅ Core social flows (Chat/Gov) wired to EvidenceBus.
- ✅ Basic E2E UI Tests passing (3-node Playwright suite).
