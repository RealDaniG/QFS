# p2p-architecture.md

## 1. Canonical Message Model

All P2P messages must adhere to the `MessageEnvelope` structure. Strict adherence to serialization rules is required to maintain deterministic hashing across Python and TypeScript.

### Envelope Fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `space_id` | String | Unique identifier for the context (e.g., UUID). |
| `sender_pubkey` | Hex String | Wallet public key of the sender. |
| `payload_ciphertext` | Hex String | Ascon-128 encrypted payload. |
| `payload_hash` | Hex String | **SHA3-256** hash of the canonical JSON payload. |
| `intent` | String | Action type (e.g., `chat.message`, `presence.signal`). |
| `signature` | Hex String | MOCKQPC (or PQC) signature of the envelope. |
| `client_seq` | Integer | Monotonic, sender-local sequence number. |

### Serialization Rules

1. **JSON Serialization**:
    * Keys must be sorted alphabetically.
    * No spaces after separators: `separators=(',', ':')`.
    * Example: `{"a":1,"b":2}` (Compact).
2. **Binary Encoding**:
    * All binary data (keys, hashes, signatures) must be represented as Lowercase Hex Strings in the JSON envelope.

### Minimal Example (JSON)

```json
{
  "client_seq": 42,
  "intent": "chat.message",
  "payload_ciphertext": "f4e663...",
  "payload_hash": "a1b2c3...",
  "sender_pubkey": "0x123...",
  "signature": "mock_sig...",
  "space_id": "space-uuid-v4"
}
```

## 2. Session-Scoped Keys

Keys are ephemeral and derived deterministically to ensure forward secrecy and session isolation.

### Key Derivation Formulas

**1. General Session Key (Spaces)**
Used for group contexts (Spaces, Channels).

```python
# Python Reference
key = sha256(wallet_pubkey || space_id || session_nonce || evidence_head)
```

* `wallet_pubkey`: Sender's identity.
* `space_id`: Context identifier.
* `session_nonce`: Random nonce exchanged during handshake.
* `evidence_head`: Hash of the latest EvidenceBus block (binds key to system state).

**2. Direct Message (DM) Key**
Used for 1:1 private communication.

```python
# Python Reference
sorted_keys = sorted([sender_pubkey, recipient_pubkey])
key = sha256(sorted_keys[0] || sorted_keys[1] || session_nonce)
```

* **ordering**: Public keys must be sorted bytes-wise or string-wise (lexicographically) before hashing to ensure both parties derive the same key.

### Semantics

* **Scope**: Keys are valid only for the duration of the defined "Session".
* **Ephemeral**: Keys are never stored persistently on disk; they are re-derived in memory.
* **Forward Safety**: Compromise of a long-term wallet key does not automatically decrypt past sessions if the `session_nonce` was discarded (though in this deterministic model, nonces are often reproducible/recoverable from the log).

## 3. P2P Node Responsibilities

### Session Bootstrap Flow

1. **Auth**: User authenticates via Wallet.
2. **Request**: Frontend calls `/api/p2p/session` with `space_id`.
3. **Derivation**: Backend computes `session_nonce` and `session_key`.
4. **Response**: Backend returns `session_nonce`, `evidence_head`, and `session_key` (hex encoded).

### Envelope Lifecycle

1. **Creation**:
    * Frontend constructs payload.
    * Serializes and Hashes Payload.
    * Encrypts Payload using `session_key` (See Ascon section).
    * Constructs Envelope.
    * Signs Envelope.
2. **Send**:
    * Publishes Envelope to `libp2p` topic `/qfs/atlas/space/{id}`.
3. **Verification (Receiver)**:
    * Checks `signature` against `sender_pubkey`.
    * Verifies `client_seq` > last seen (gap detection).
4. **Decryption**:
    * Uses derivation logic to obtain `session_key` for `sender_pubkey`.
    * Decrypts `payload_ciphertext`.
    * Deserializes JSON.
5. **Event Emission**:
    * Valid messages are emitted to the UI.
    * Hashes are committed to EvidenceBus.

### Transport Abstraction

* **Current (v19)**: WebSocket / Direct IPC (simulated P2P).
* **Future**: Full `libp2p` stack (GossipSub, DHT).

## 4. Crypto Parity & Specifications (v19 Locked)

### 4.1 Cipher Suite

| Component | Standard | Notes |
| :--- | :--- | :--- |
| **AEAD** | **Ascon-128** | Not Ascon-128a. |
| **Key Size** | 16 bytes | 128-bit session key. |
| **Nonce Size** | 16 bytes | Derived from `SHA3-256(spaceID + seq)[:16]`. |
| **Tag** | Appended | Standard `ciphertext || tag` format. |
| **Hashing** | **SHA3-256** | Used for all envelope hashing (Python `hashlib.sha3_256`, TS `js-sha3`). |
| **Signing** | MOCKQPC | SHAKE-256 (Placeholder for Dilithium/Kyber). |

### 4.2 Interoperability Standard ("Empty AD")

A persistent interoperability mismatch exists between Python `ascon` and TypeScript `ascon-js` regarding Associated Data (AD) padding.

**Decision**: We standardize on **Zero-Length Associated Data**.

* **Logic**: Domain separation is enforced by the key/nonce derivation.
* **Implementation Rule**:
  * **Python**: Pass `b""` (Empty Bytes).
  * **TypeScript**: Pass `undefined` (NOT `new Uint8Array(0)`).

### 4.3 Cross-Language Parity Tests

Mandatory verification pipelines for v19:

1. **Python -> TS**: `scripts/verify_envelope_parity.py`
    * Python generates a valid `MessageEnvelope`.
    * Outputs JSON with SHA3-256 hash and Ascon-128 ciphertext.
2. **TS -> Python**: `scripts/verify_envelope_parity.ts`
    * Ingests the Python JSON.
    * Decrypts using `ascon-js`.
    * Verifies payload integrity.

**Constraint**: Any change to envelope format or crypto must keep these scripts green.
