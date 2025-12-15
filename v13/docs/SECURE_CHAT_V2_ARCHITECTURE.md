# QFS-Native Secure Chat Architecture (V2)

## 1. Context & Problem Statement

The original Open-A.G.I `secure-chat` dapp was a decentralized Ethereum-based application using Solidity contracts for state and IPFS for storage. However, incorporating this directly into QFS V13.8 presents several blockers:

1. **Dependency on External Chain**: Reliance on Ethereum/Hardhat violates QFS's "Zero-Simulation" requirement for deterministic, self-contained economic logic.
2. **Performance**: On-chain block times are unsuitable for real-time chat.
3. **Governance**: QFS requires all signal actions (like messaging) to be visible to the `CoherenceLedger` for scoring, which is hard to bridge from an external EVM chain efficiently.

## 2. Decision: QFS-Native Hybrid Architecture

We will implement a **QFS-Native Secure Chat** that preserves the *security guarantees* of the original dapp (E2E encryption, signed identity) while using QFS infrastructure for *transport and persistence*.

### Core Components

| Feature | Original Dapp | QFS-Native Solution | Justification |
| :--- | :--- | :--- | :--- |
| **Transport** | P2P / IPFS Polling | **ATLAS WebSocket** | Sub-second latency, lower bandwidth cost. |
| **Persistence** | Ethereum Smart Contract | **GenesisLedger (QFS)** | Deterministic, auditable, high throughput. |
| **Encryption** | Client-side (Metamask keys) | **SecureMessageV2** (AES-256 + Ratchets) | Forward secrecy, QFS-compliant crypto. |
| **Identity** | EVM Wallet Address | **PQC/EVM Dual Identity** | Bridges generic wallets to Post-Quantum security. |
| **Storage** | IPFS | **IPFS (Pinned by ATLAS)** | Keeps large payloads off-ledger but hash-linked. |

## 3. Implementation Specification

### 3.1 Data Flow

1. **Client (React)**: Encrypts message using `SecureMessageV2` format (AES-GCM key derived from ECDH shared secret).
2. **Transport**: Sends JSON payload via WebSocket (`wss://api.atlas.app/v1/chat/ws`).
3. **Server (ATLAS API)**:
    * Authenticates JWT.
    * Validates message sequence (anti-replay).
    * **Does NOT** decrypt content (Server is blind).
4. **Persistence**:
    * Logs event to `GenesisLedger` (Type: `MESSAGE`, Data: `{hash, sender, recipient, nonce}`).
    * Broadcasts to recipient's active socket.

### 3.2 Schema: `SecureMessageV2` (from repository)

```python
{
    "ciphertext": "base64...",
    "nonce": "base64...",
    "seq": 105,
    "ts": 1234567890.123,
    "hash": "sha256(ciphertext+nonce+seq)"
}
```

### 3.3 Zero-Simulation Compliance

* **Ordering**: Enforced by the central `GenesisLedger` commit order (primary truth).
* **Rewards**: `CoherenceEngine` reads the `GenesisLedger` to calculate activity rewards, ensuring no "hidden" off-chain messages reward users.
* **Auditability**: Every message leaves a hash trace on-chain.

## 4. Migration Plan

1. **Deprecate** `v13/ATLAS/src/api/routes/secure_chat.py` (Legacy incomplete port).
2. **Enhance** `v13/ATLAS/src/api/chat.py` (New WebSocket MVP) to support `SecureMessageV2` structure.
3. **Build** Frontend `ChatWindow.tsx` to handle client-side encryption.

## 5. Security Invariants

* **Invariant 1**: Server MUST NEVER store plaintext.
* **Invariant 2**: All messages MUST be logged to `GenesisLedger` to be eligible for Coherence Rewards.
* **Invariant 3**: Message sequence numbers MUST strictly increase to prevent replay.
