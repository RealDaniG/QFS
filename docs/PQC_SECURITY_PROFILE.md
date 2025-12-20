# QFS × ATLAS — PQC Security Profile

> **Version:** v18.0.0-alpha  
> **Status:** Initial Profile (Anchors Only)  
> **Transition Roadmap:** NIST IR 8547 Aligned

This document defines the Post-Quantum Cryptography (PQC) posture for the QFS × ATLAS ecosystem.

## 1. PQC Anchoring (Implemented)

The EvidenceBus uses batched PQC signatures to anchor event segments, ensuring long-term integrity against quantum adversaries.

- **Algorithm:** Dilithium (NIST Category 2/3) via `liboqs`.
- **Infrastructure:** `PQCBatchAnchorService` (Tier A only).
- **Scope:** EvidenceBus segment sealing (replicated across consensus).
- **Fallback:** `MOCKQPC` (Deterministic SHA3-based simulation) for Dev/Beta/CI environments.

## 2. Node Identity & Transport (Planned)

Full decentralized security requires PQC at the network and identity layers.

- **Node Identity:** PQC-based keypairs for Tier A validators.
- **Secure Channels:** Hybrid TLS (Classical Diffie-Hellman + PQC KEM) for node-to-node communication.
- **Status:** Under research for Phase 5.

## 3. Wallet & Auth Migration (Future)

- **User Wallets:** Current EIP-191 (ECDSA) remains the baseline.
- **Migration Path:** Cross-signing with PQC identity once stable standards emerge for EVM-compatible PQC.

## 4. Security Verification

Nodes can verify the PQC posture of the fabric by inspecting the EvidenceBus segments:

```bash
# Verify v18 segments and their PQC anchors
python v18/tests/test_pqc_anchors.py
```

---

**Policy:** PQC refers to real cryptographic signatures on Tier A Mainnet deployments and `MOCKQPC` simulation in all other environments to preserve the Zero-Sim guarantee without high operational costs.
