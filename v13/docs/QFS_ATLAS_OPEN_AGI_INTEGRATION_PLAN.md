# QFS × ATLAS × Open-AGI Integration Plan (Detailed)

**Status:** APPROVED  
**Target Version:** V13.9 / V14.0  
**Based on:** Open-AGI Secure Chat Analysis

## 1. Executive Strategy

We are hardening the QFS Network Layer by integrating Open-AGI's secure chat capabilities with QFS's PQC and Ledger requirements. The goal is to move from "Zero-Sim" (internal determinism) to "Secure-Net" (network-level integrity).

## 2. Implementation Phases

### Phase 1: Core Security Integration (Current Focus)

**Goal:** Establish a quantum-secure, identity-verified, and auditable P2P foundation.

* [x] **Task 1.1: PQC Adapter** (`v13/integrations/openagi_pqc_adapter.py`)
  * Wraps Open-AGI CryptoEngine.
  * Adds CRYSTALS-Dilithium signatures alongside Ed25519.
* [x] **Task 1.2: AEGIS DID Bootstrap** (`v13/ATLAS/src/p2p/aegis_bootstrap.py`)
  * Verifies peer identity via AEGIS Registry before handshake.
  * Prevents MITM on first contact.
* [ ] **Task 1.3: Secure Message Logging** (`v13/ATLAS/src/p2p/secure_message_logger.py`)
  * Logs encrypted message metadata (hashes, signatures) to `CoherenceLedger`.
  * Ensures immutable audit trail without leaking plaintext.

### Phase 2: Message Integrity & Ordering

**Goal:** Prevent replay attacks, reordering, and ensure forward secrecy compliance.

* [ ] **Task 2.1: Sequence Number Enforcement**
  * Modify message payload to include `sequence_num`.
  * Track `peer_message_sequences` to reject replays/gaps.
* [ ] **Task 2.2: Time-Based Ratchet Rotation**
  * Enhance `CryptoEngine` to rotate keys every 1 hour (or 50 messages).

### Phase 3: QFS-Specific Enhancements

**Goal:** Connect P2P activity to the Token Economy and Observability layers.

* [ ] **Task 3.1: P2P Bandwidth Economics** (`v13/ATLAS/src/p2p/bandwidth_economics.py`)
  * Track encrypted traffic volume per peer.
  * Feed metrics into `NODInvariantChecker` for NOD token rewards.
* [ ] **Task 3.2: Explain-This for P2P** (`v13/ATLAS/src/api/routes/explain_p2p.py`)
  * New API endpoint to visualize P2P trust, bandwidth, and security status.

## 3. Architecture constraints

* **Fail-Closed:** All security checks must raise exceptions on failure; no fallbacks.
* **Zero-Sim:** All non-IO logic (ratchets, economics) must remain deterministic.
* **Auditability:** Every secure message exchange must leave a hash trace on the ledger.
