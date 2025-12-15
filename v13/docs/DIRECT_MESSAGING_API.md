# QFS × ATLAS: Direct Messaging API & Architecture

**Version:** 1.0

## 1. System Architecture

```mermaid
graph TD
    UserA[User A (Client)] -->|1. Lookup| Directory[Identity Directory]
    UserA -->|2. Encrypt & Sign| local[Local Crypto Engine]
    UserA -->|3. Upload Payload| Storage[Decentralized Storage / Relay]
    UserA -->|4. Emit Signal| Bridge[QFS Interaction Bridge]
    
    Bridge -->|5. Verify & Log| Ledger[QFS Ledger]
    
    UserB[User B (Client)] -->|6. Listen| Bridge
    UserB -->|7. Fetch Payload| Storage
    UserB -->|8. Decrypt| localB[Local Crypto Engine]
```

## 2. API Definition

### 2.1 Identity Management

#### `GET /api/v1/dm/identity/{user_id}`

Returns the Public Identity Bundle for a user.

- **Response**:

  ```json
  {
    "user_id": "0x...",
    "public_key": "...",
    "encryption_algo": "Dilithium+Kyber",
    "min_coherence_required": 300
  }
  ```

#### `POST /api/v1/dm/identity`

Publish or update current user's identity keys.

- **Auth**: Required
- **Body**: `{ "public_key": "...", "proof": "..." }`

### 2.2 Messaging Operations

#### `POST /api/v1/dm/send`

Sends a message signal. NOTE: The actual payload must be uploaded to storage *before* calling this.

- **Body**:

  ```json
  {
    "recipient_id": "0x...",
    "storage_uri": "ipfs://...",
    "content_hash": "sha256...",
    "metadata": { "ttl": 86400 }
  }
  ```

- **Process**:
  1. Checks Sender Coherence > Recipient.min_coherence_required.
  2. Rate limit check.
  3. Emits `DM_SIGNAL` to Ledger.

#### `GET /api/v1/dm/inbox`

Retrieves message signals for the current user.

- **Params**: `since_timestamp`, `limit`
- **Response**: List of signal objects (User then fetches actual content from `storage_uri`).

### 2.3 Storage Interface (Client-Side)

The client usually interacts directly with the storage node, but for V1 we may provide a proxy generic endpoint:
`POST /api/v1/storage/upload`
`GET /api/v1/storage/download/{hash}`

## 3. Python Module Structure (`v13.services.dm`)

- `identity.py`: Handling key registry and lookups.
- `crypto.py`: Wrapper for encryption/decryption logic (PQC).
- `messenger.py`: Main service logic for signaling and checking rules.
- `storage_proxy.py`: Abstraction for the storage layer.

## 4. Database Schema (Relational Cache)

While the Ledger is the source of truth, the generic API uses a projection:

- `dm_signals`: `id`, `sender`, `recipient`, `hash`, `uri`, `timestamp`, `read_status`
