# QFS × ATLAS — Ascon Edge Crypto Adapter

> **Version:** v18.5-Ascon (Alpha)  
> **Status:** Deterministic Simulation Ready  
> **Scope:** Tier B/C Integrated Security

This document specifies the **Ascon Edge Crypto Adapter**, a modular enhancement for edge security that provides lightweight AEAD (Authenticated Encryption with Associated Data) and hashing.

## 1. Overview

Ascon is designed for constrained devices and high-throughput edge nodes. In QFS × ATLAS, it serves as a **non-authoritative integrity layer** that strengthens Tier B/C nodes without increasing the cost of Tier A PQC anchors.

### Key Applications

- **Advisory Output Integrity**: Hashing Layer D scores/flags before emission.
- **Telemetry Protection**: Encrypting sensor data from Tier C to Tier B gateways.
- **Local Cache Security**: Protecting EvidenceBus snapshots on disk.

## 2. Deterministic Adapter Spec

To preserve **Zero-Simulation (Zero-Sim)** compliance, all Ascon operations must be pure functions of their inputs and an explicit context.

### 2.1 AsconContext

Every operation requires an `AsconContext` which dictates the deterministic derivation of nonces and IVs.

| Field | Description |
| :--- | :--- |
| `node_id` | Persistent identity of the originating node. |
| `channel_id` | Logical stream (e.g., `telemetry`, `advisory`, `cache`). |
| `evidence_seq` | Monotonic counter or EvidenceBus index to prevent replay. |
| `key_id` | Version identifier for the logical key used. |

### 2.2 Nonce Derivation

Nonces are derived using:  
`Nonce = SHA3-256(node_id || channel_id || evidence_seq || key_id) [0..16]`

## 3. EvidenceBus Integration

Every call to the adapter emits an `ASYNC_CRYPTO_EVENT` to the EvidenceBus. This ensures that the cryptographic history of the edge is as replayable as the governance history of the core.

### Event Schema

- `event_type`: `ASCON_AEAD_ENCRYPT`, `ASCON_AEAD_DECRYPT`, or `ASCON_HASH`.
- `context`: Full `AsconContext` (minus raw keys).
- `digest_or_tag`: Truncated digest/tag for verification without leaking sensitive data.
- `v18_crypto`: Version tag (e.g., `ascon-v18.5`).

## 4. Usage Example (Python)

```python
from v18.crypto.ascon_adapter import ascon_adapter, AsconContext

# 1. Define Context
ctx = AsconContext(
    node_id="edge-1",
    channel_id="telemetry",
    evidence_seq=1234,
    key_id="v1"
)

# 2. Encrypt Data
plaintext = b"sensor_reading: 22.5c"
ad = b"gatewayheader"
key = b"0123456789abcdef" # Managed via secure key hierarchy

res = ascon_adapter.ascon_aead_encrypt(ctx, plaintext, ad, key)

# 3. Decrypt/Verify
decrypted = ascon_adapter.ascon_aead_decrypt(ctx, res, ad, key)
```

## 5. Security Limitations

- **Optional**: Ascon is an enhancement. The system trust root remains the **PQC Anchors** on Tier A.
- **Mock Fallback**: In Dev/CI environments, the adapter uses a SHA3-based deterministic simulation to avoid native library dependencies while preserving logic correctness.

---

**Protocol Guarantee**: Ascon usage in QFS × ATLAS follows strict "No Random Nonce" rules to ensure 100% replayability.
