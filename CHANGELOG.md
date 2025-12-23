# Changelog

All notable changes to QFS × ATLAS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### ATLAS v18.9 App Alpha (Transition)

- **Unified Auth Integration**: Migrated ATLAS API to Ascon-protected v18.5 session tokens (Complete).
- **Distributed App Bridge**: Implementing `v18ClusterAdapter` to connect ATLAS UI to the consensus leader.
- **Live Social Projection**: Wiring Secure Chat and Governance to consensus-backed EvidenceBus.
- **User Data Strategy**: Implemented three-tier data classification (Class A/B/C) for deterministic, privacy-first storage.

## [v18.6.0-auth-sync] - 2025-12-20

### Added

- **Stateless Ascon Session Tokens**:
  - Embedded all session claims (wallet_address, scopes, created_at, expires_at) in Ascon-encrypted payload.
  - Zero server-side session storage required for validation.
  - Tokens validated on any Tier A node with same key_id.
- **Multi-Node Auth Validation**:
  - Sessions created on Node A successfully validate on Node B.
  - Test suite: 12/12 tests passing (lifecycle, PoE, multi-node, determinism).
- **User Data Model & Storage Strategy**:
  - Three-tier classification: Class A (ledger-critical), Class B (social/personal), Class C (ephemeral).
  - Pseudonymization with user_id indirection.
  - Privacy and deletion flows documented.

### Changed

- **SessionManager (v15/auth)**: Refactored from in-memory to stateless token architecture.
- **PoE Events**: Added `stateless: True` flag to AUTH_LOGIN and AUTH_LOGOUT events.
- **Frontend Hooks**: Updated `useWalletAuth` to validate `ascon1.*` token prefix.
- **API Client**: Created `atlasFetch` utility for centralized session token handling.

### Tests

- `v18/tests/test_ascon_sessions.py`: Comprehensive test suite covering:
  - Token creation and validation
  - Expiry and revocation
  - PoE event emissions
  - Multi-node validation (cross-node session verification)
  - Deterministic session IDs and Ascon contexts
  - Stateless token contract requirements

## [v18.0.0-alpha] - 2025-12-20

### Added

- **Distributed Tier A Backbone**:
  - Raft-based deterministic replication (log consensus, leader election, majority commits).
  - Multi-node simulation harness (v18/consensus/simulator.py).
- **PQC Anchoring Service**:
  - Deterministic batch signatures over EvidenceBus segments.
  - Verification logic for PQC anchors across the fabric.
- **v18.5 Edge Security (Ascon)**:
  - Deterministic Ascon AEAD adapter for session and message protection.
  - `ASYNC_CRYPTO_EVENT` logging to EvidenceBus.
- **EvidenceBus Integration**:
  - Consensus-driven commits with term/cluster metadata.
  - Full replayability across distributed nodes.

### Ongoing Development

The system continues to evolve with the following enhancement areas:

- Admin/Moderator Panel optimization
- Agent layer refinement (stateless services, sampling strategies)
- Additional cross-platform deployment tooling
- Performance optimization for high-volume scenarios

## Current Baseline Capabilities

### Summary of Core Baseline

- **Cost-Efficient Architecture Documentation**:
  - `COST_EFFICIENT_ARCHITECTURE.md` - Complete cost optimization guide
  - `MASTER_PROMPT_v15.5.md` - Unified authoritative reference
  - `BETA_DEPLOYMENT_PLAN.md` - $0-50/month deployment strategy
- **Admin/Moderator Panel Specification**:
  - Deterministic decision engine `F(content, scores, rules, role)`
  - Hash-chained decision log with MOCKQPC signatures
  - RBAC scopes: `mod:read`, `mod:act`, `admin:override`, `audit:*`
  - Rule versioning and governance-controlled updates
- **MOCKQPC Integration**:
  - Crypto abstraction layer: `sign_poe(hash, env)`, `verify_poe(hash, sig, env)`
  - Environment-tagged events (`env=dev|beta|mainnet`)
  - Batched PoE signing (100-1,000 events per batch)
- **Implementation Planning**:
  - Phase 1: Backend Foundations (rule schema, decision models, hash-chained log)
  - Phase 2: Panel APIs (queue, decision, audit endpoints)
  - Phase 3: Frontend Panel (scope-driven UI, PoE indicators)
- **Documentation Suite**:
  - `implementation_plan_v15.5.md` - Detailed tasks with MOCKQPC integration
  - `STATE_OF_THE_UNION_v15.5.md` - Architectural decisions
  - `task_v15.5.md` - Subtasks and acceptance criteria
  - `walkthrough_v15.5_admin_panel.md` - Architecture deep dive
  - `QUICK_REFERENCE_v15.5.md` - Developer quick guide

### Changed

- **PoE Architecture**: Defaults to MOCKQPC in dev/beta, batched signatures in all environments
- **Agent Layer**: Strictly advisory, feeds deterministic function `F`, never decides directly
- **Cost Model**: All new features must pass cost-efficiency checklist (MOCKQPC-first, batched PoE, agent sampling)
- **Development Workflow**: MOCKQPC mandatory for all v15.5 work, mainnet activation gated on governance approval

## [v15.4.0] - 2025-12-19

### Added

- **Wallet Authentication (Phases 1-2)** - Complete end-to-end wallet auth:
  - `NonceManager` - Ephemeral challenge generation (TTL, single-use)
  - `WalletAuth` - EIP-191 signature verification (EVM/`eth_account`)
  - `SessionManager` - Token-based session state (scopes, expiry)
  - Frontend `useWalletAuth` hook and `WalletConnectButton` component
- **Protected Bounty Features (Phase 3)** - Frontend integration complete:
  - `BountyList` component - Browse and claim bounties with scope enforcement
  - `MyBounties` component - View claimed bounties by connected wallet
  - `BountyDashboard` component - Unified dashboard with tab navigation
  - Auth middleware for bounty routes (`bounty:read`, `bounty:claim` scopes)
  - Integration tests for end-to-end protected routes flow
- **Import Resolution**:
  - Fixed `v13.libs.economics` package initialization
  - Resolved circular import issues in bounty system

### Changed

- **Session Management**: Wallet-based sessions with scope enforcement
- **API Security**: All bounty endpoints protected with wallet authentication
- **Frontend UX**: Scope-driven UI (hide unavailable actions)

### Documentation

- `PHASE_3_BROWSER_VERIFICATION.md` - Comprehensive browser testing checklist
- Updated README with v15.4 Phase 3 completion status
- Task tracking updated for v15.4/v15.5 roadmap

## [v15.3.0] - 2025-12-18

### Added

- **Governance + PoE Fully Wired**:
  - End-to-end flow: create proposal → vote → finalize → execute → PoE → verify
  - Hash-chained governance index for deterministic replay
  - CLI tools: `verify_poe.py`, `replay_gov_cycle.py`, `governance_index_manager.py`
- **PoE Schema v1.0**:
  - Standardized PoE artifact format with PQC signatures
  - Governance event anchoring and verification
- **Validation Scripts**:
  - `validate_end_to_end_cycle.py` - Full governance cycle verification
  - Automated detection of BigNum128 overflows, VoteTally errors, PoE gaps

### Fixed

- BigNum128 overflow in viral pool calculations
- VoteTally type errors (`total()` method vs property)
- PoE setup issues in governance execution
- Deterministic replay verification

### Planned (v15 Protocol Layer)

## [v14.0-social-layer] - 2025-12-18

### Added

- **v14 Social Layer** - Three production-ready modules:
  - Spaces (audio rooms with capacity limits)
  - Wall Posts (social feed with reactions and threading)
  - Chat (secure messaging with E2EE metadata)
- **Economic Events** - 11 new event types with CHR/FLX rewards:
  - `space_created`, `space_joined`, `space_left`
  - `post_created`, `post_liked`, `post_quoted`, `post_pinned`
  - `conversation_created`, `message_sent`, `message_read`, `reaction_added`
- **Regression Testing** - Canonical v14 social regression scenario
  - `v13/tests/regression/phase_v14_social_full.py`
  - SHA-256 regression hash: `v14_regression_hash.txt`
  - CI-gated verification (pre-release workflow)
- **Zero-Sim Contract v1.4** - Formalized determinism guarantees
  - All social events deterministic and replayable
  - 0 Zero-Sim violations across v14 modules
- **Developer Rewards Foundation** - Bounty system infrastructure:
  - Bounty schema (`Bounty`, `BountySubmission`, `ContributorProfile`)
  - Economic events (`dev_bounty_paid`, `atr_boost_applied`)
  - Dev Rewards Treasury (bounded reserves)

### Changed

- **HSMF** - Fixed CoherenceEngine sort key for deterministic ordering
- **CI Pipeline** - Enhanced with structured logging and fail-fast
  - Pinned GitHub Actions to SHAs (supply chain security)
  - Added minimal permissions to all jobs
  - Implemented violation summaries and step timing

### Security

- **CI Hard Gates** - Blocking checks for main and releases:
  - All tests must pass (60+ tests, 100% pass rate)
  - Zero-Sim analyzer (0 violations required)
  - Regression hash verification (v14 frozen)
- **Pinned Actions** - All GitHub Actions pinned to specific SHAs
- **Minimal Permissions** - Tightened permissions on all CI jobs
- **Depletion Alerts** - Treasury monitoring at 20% (low) and 10% (critical)

### Documentation

- **v14 Evidence Deck** - Audit-ready compliance documentation
- **v14 Release Notes** - Complete feature and change documentation
- **Security Notes** - Trust assumptions and limitations
- **CI Improvements** - Phase 1 improvements and roadmap
- **Repository Structure** - Canonical organization guide
- **v15 Protocol Spec** - Timeless execution plan (additive layer)

### Fixed

- CoherenceEngine deterministic event ordering
- Zero-Sim violations in HSMF (0 violations achieved)
- Root directory cleanup (32 → 18 files, 44% reduction)

## [v13.5] - 2025-12-23

### Added

- **HSMF Math Contracts & PoE Logging**:
  - `HSMFProof` dataclass for Proof-of-Evaluation (PoE) records
  - `_emit_hsmf_poe()` method for structured logging
  - 13 invariant tests in `test_hsmf_math_contracts.py`
  - 9 replay/PoE tests in `test_hsmf_replay.py`
- **HSMF × ATLAS Social Pipeline**:
  - `HSMFIntegrationService` for AEGIS→HSMF→RewardAllocator flow
  - `HSMFWallService` for HSMF-scored wall posts/quotes/reactions
  - 8 integration tests in `test_hsmf_wall_integration.py`
  - Every wall action produces `ScoredPost` + `HSMFProof`
- **CLI Explainer Tool**:
  - `tools/explain_hsmf_action.py` for human-readable HSMF explanations
  - Reconstructs action cost, c_holo, and rewards from raw inputs
- **Documentation**:
  - `HSMF_MathContracts.md` — Formulas, invariants, test specifications
  - `hsmf_harmonic_design.md` — Theoretical grounding, flow diagrams
  - Updated `HSMF_API.md` with HSMFProof and integration details
  - Updated `INDEX.md` with HSMF documentation section

### Changed

- **PQC Mocks**: Centralized in `conftest.py` for liboqs-free HSMF testing
- **HSMF.py**: Now 720+ lines with PoE logging and full integration support

### Tests

- **30 new tests** across math contracts, replay, and wall integration
- All tests pass without `liboqs` dependency (crypto-agnostic)

## [v13.9] - 2025-12-15

### Added

- HSMF integration planning
- Governance roadmap
- Phase 3 Zero-Sim cleanup

### Fixed

- PQC runtime errors
- Gateway explain functionality
- Test collection issues

## [v13.8] - 2025-11-20

### Added

- CertifiedMath HSMF Phase 4 compliance
- StateTransitionEngine integration
- CoherenceEngine deterministic logging

### Fixed

- CertifiedMath structural corruption
- HSMF argument passing issues
- Proof vector coverage

---

## Version Naming Convention

- **v14.x** - Social Layer (frozen baseline)
- **v15.x** - Living Posts + Developer Rewards (parallel layer)
- **v16.x** - NOD Integration (future)

## Migration Notes

### v13.x → v14.0

- No breaking changes to v13 core
- Social modules are additive
- Existing economic events unchanged

### v14.0 → v15.0 (Planned)

- v14 remains frozen and unchanged
- v15 is a parallel, additive layer
- No v14 semantic or economic changes
- v15 can be disabled without affecting v14

---

**Maintained by**: QFS × ATLAS Core Team  
**Last Updated**: 2025-12-18
