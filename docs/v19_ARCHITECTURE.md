# ATLAS v19: Decentralized Intelligence Architecture

**Version:** 19.0.0-alpha
**Date:** 2025-12-23

## Executive Summary

ATLAS v19 shifts the platform from a centralized web application to a **Security-First, Peer-to-Peer Intelligence Network**. It introduces four sovereign layers: Trust (Crypto), Storage (IPFS), Network (P2P Mesh), and Intelligence (Advisory Agents).

---

## 1. The Trust Layer (L0)

**Location:** `backend/lib/trust`, `src/lib/trust`

The foundation of the entire system. Nothing happens without a `TrustedEnvelope`.

### Core Components

- **TrustedEnvelope**: A standardized JSON wrapper for all content.
  - `payload_cid`: IPFS hash of the actual content.
  - `signature`: Cryptographic signature of the envelope fields (ASCON-128/Ed25519).
  - `author_address`: EVM address of the signer.
  - `timestamp`: UTC timestamp.
- **PeerIdentity**: Binds an ephemeral P2P PeerID to a persistent Wallet Address via a signed handshake.

### Invariants

1. **No Signature, No Entry**: Envelopes without valid signatures are rejected at the edge.
2. **Deterministic IDs**: Content IDs are derived solely from content processing, not random UUIDs.

---

## 2. The Storage Layer (L1)

**Location:** `backend/lib/ipfs`, `src/lib/ipfs`

The "Long-Term Memory" of ATLAS. Replaces the SQL database for content bodies.

### Core Components

- **IPFSService**: Python wrapper around `aiohttp` to communicate with Kubo Daemon (5001).
- **ContentStore**: Abstract interface ensuring we can swap storage backends (currently `IPFSContentStore`).
- **Pins**: All valid local content is specificallly "pinned" to prevent GC.

---

## 3. The Network Layer (L2)

**Location:** `backend/lib/p2p`, `src/lib/p2p`

The "Nervous System" enabling real-time signal propagation.

### Core Components

- **ATLASLibp2pNode** (Backend):
  - Acts as a GossipSub router.
  - Maintains `peers` (outbound) and `inbound_peers` (clients).
  - Deduplicates messages via `msg_history`.
- **ATLASBrowserP2PClient** (Frontend):
  - WebSocket client connecting to Backend Node.
  - Subscribes to topics (`/atlas/feed`).
  - Broadcasts locally signed Envelopes.

### Topics

- `/atlas/feed`: Global content stream.
- `/atlas/governance`: Proposals and votes.
- `/atlas/bounty`: Bounty claims and validations.

---

## 4. The Intelligence Layer (L3)

**Location:** `backend/lib/intelligence`

The "Brain" providing analysis and safety checks. **Strictly Advisory.**

### Design Philosophy

- **Read-Only**: Agents analyze data but CANNOT mutate ledger state directly.
- **Immutable Reports**: Analysis results are themselves stored as `AgentReport` Envelopes in IPFS.
- **Determinism**: Given the same Input Envelope, an agent must produce the same Report.

### Active Agents (v19.1)

1. **BountyValidator**: Verifies structural compliance of bounty claims (e.g., presence of evidence).
2. **FraudDetector**: Temporal and Structural sanity checks (e.g., anti-time-travel).
3. **ReputationScorer**: Assigns trust weights based on on-chain history and behavior.
4. **GovernanceAnalyzer**: Heuristics for proposal risk assessment (e.g., "Emergency" keywords).

---

## System Flow

1. **User Creates Content** (Frontend)
   - Content hashed -> `payload_cid`.
   - `TrustedEnvelope` created and signed by Wallet.
   - Pushed to `IPFS` (Storage Layer).
   - Broadcast to `P2P Network` (Network Layer).

2. **Network Propagation**
   - Backend Node receives Envelope.
   - **Step 1:** Verify Signature (Trust Layer).
   - **Step 2:** Store/Pin (Storage Layer).
   - **Step 3:** Re-broadcast to other peers.

3. **Intelligence Analysis** (Async)
   - `AgentRegistry` picks up new valid Envelopes.
   - Agents run analysis (`analyze()`).
   - `AgentReport` is generated, signed by Node, and published to Overlay Network.

4. **Consumption** (Frontend)
   - UI updates via `useP2PFeed`.
   - Badges/Warnings displayed based on `AgentReport`s (e.g., "Fraud Detected").

---

## Deployment

### Requirements

- Docker (for IPFS `atlas_ipfs` container)
- Python 3.11+ (Backend)
- Node.js 20+ (Frontend)

### Ports

- **3000**: Next.js Frontend
- **8001**: Backend API
- **9000**: P2P WebSocket Node
- **5001**: IPFS API
- **8080**: IPFS Gateway
