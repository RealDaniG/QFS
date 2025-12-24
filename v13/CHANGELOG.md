# Changelog

All notable changes to ATLAS will be documented in this file.

## [20.0.0-alpha] - 2025-12-24

### 🎊 Major Release: Decentralized Intelligence Architecture

#### Added

**Trust Layer (Phase 1)**

- `TrustedEnvelope` schema for cryptographic content verification
- `PeerIdentity` binding (wallet ↔ network peer)
- Signature verification at all ingress points
- Deterministic hash generation

**Storage Layer (Phase 2)**

- IPFS integration via Kubo 0.39.0
- Content-addressed storage (immutable CIDs)
- Pinning service for persistence
- `IPFSService` and `IPFSContentStore` implementations

**Network Layer (Phase 3)**

- WebSocket-based P2P mesh (backend)
- GossipSub-style message propagation
- Topics: `/atlas/feed`, `/atlas/governance`, `/atlas/bounties`
- Message deduplication
- Bi-directional peer tracking

**Frontend P2P Client (Phase 3.5)**

- `ATLASBrowserP2PClient` WebSocket integration
- `useP2PConnection` and `useP2PFeed` React hooks
- Real-time feed updates (no polling)
- P2P status indicator in UI
- Content publishing to mesh

**Intelligence Layer (Phase 4)**

- `AgentRegistry` for agent lifecycle management
- 4 advisory agents:
  - `BountyValidator` – Validates bounty claims
  - `FraudDetector` – Catches time-travel and malformed data
  - `ReputationScorer` – Calculates trust metrics
  - `GovernanceAnalyzer` – Flags high-risk proposals
- `AgentReport` schema for immutable analysis results
- Advisory-only verdicts (no auto-enforcement)

#### Changed from v18

- **Storage:** Centralized DB → IPFS
- **Networking:** HTTP → WebSocket P2P mesh
- **Content IDs:** UUIDs → IPFS CIDs
- **Updates:** Polling → Real-time pub/sub
- **Trust:** Basic auth → Cryptographic envelopes

#### Removed

- Centralized content storage
- HTTP polling for updates
- Mutable content references

### Verification

All phases verified with automated scripts:

- ✅ `verify_trust_layer.py`
- ✅ `verify_ipfs_layer.py`
- ✅ `verify_p2p_layer.py`
- ✅ `verify_intelligence_layer.py`

### Known Issues

- AGI agents are advisory only (no auto-enforcement)
- IPFS daemon must run separately
- P2P node must be running for real-time updates
- Alpha stability (not production-ready)

---

## [18.0.0] - 2025-12-22

### Added

- URL-based navigation (fixed state propagation)
- Wallet authentication (RainbowKit/MetaMask)
- Internal credit system
- Desktop Electron app
- Comprehensive E2E testing

### Fixed

- React state propagation issues
- Dynamic import hydration errors
- CORS configuration
- Navigation architecture

---

## Previous Versions

See Git tags for v15.5, v14, v13 changelogs.
