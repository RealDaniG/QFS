# QFS x ATLAS API Integration Contract (v1.0)

**Version:** 1.0.0
**Status:** DRAFT
**Last Updated:** 2025-12-17

## Overview

This document defines the interface between ATLAS (Social Layer) and QFS (Economic Layer).
ATLAS acts as the user-facing frontend, while QFS manages the authoritative economic state.

## Shared Data Models

All integrations MUST strictly adhere to the canonical types defined in `v13.libs.canonical`.

| Model | Source | Description |
|-------|--------|-------------|
| `UserIdentity` | QFS | Authoritative user mapping (Wallet <-> UserID) |
| `ContentMetadata` | ATLAS | Content context for economic attribution |
| `EconomicEvent` | QFS | Deterministic record of value transfer |

## Authentication

- **ATLAS to QFS:**
  - Transport: gRPC / REST (Internal)
  - Auth: Mutual TLS (mTLS) + API Key
  - Headers: `X-QFS-Client-ID: atlas-v1`
- **User Actions:**
  - All economic actions MUST be signed by the user's PQC key.
  - QFS validates signatures before state mutation.

## Endpoints

### 1. User Onboarding

**POST /v1/users/register**

- **Request:**

  ```json
  {
    "wallet_address": "0x...",
    "public_key": "dilithium5_...",
    "signature": "..."
  }
  ```

- **Response:** `UserIdentity`
- **Side Effect:** Creates new Account Ledger entry.

### 2. Event Ingestion (Batch)

**POST /v1/events/batch**

- **Purpose:** ATLAS reports user actions (posts, likes, referrals) to QFS for processing.
- **Request:**

  ```json
  {
    "batch_id": "uuid",
    "timestamp_tick": 123456789,
    "events": [
      {
        "content_meta": { ...ContentMetadata... },
        "action_type": "CREATE_POST",
        "actor_id": "user_hash...",
        "signature": "..."
      }
    ]
  }
  ```

- **Response:**

  ```json
  {
    "status": "ACCEPTED",
    "processed_count": 50,
    "job_id": "job_123"
  }
  ```

### 3. Economic State Query

**GET /v1/users/{user_id}/balance**

- **Response:**

  ```json
  {
    "CHR": "100.00",
    "ATR": "50.50",
    "NUD": "10.00"
  }
  ```

**GET /v1/explain/reward/{event_id}**

- **Purpose:** "Explain This" feature.
- **Response:**

  ```json
  {
    "event_id": "evt_123",
    "calculation_trace": [
      "Base Reward: 10.0 CHR",
      "Multiplier (Quality): x1.5",
      "Multiplier (Advisory): x1.1"
    ],
    "final_amount": "16.5 CHR"
  }
  ```

## Error Handling

- **400 Bad Request:** Schema validation failed (Canonical types).
- **401 Unauthorized:** Invalid signature or API key.
- **409 Conflict:** Double spending or replay attack detected.
- **500 Internal Error:** Determinism breach or system failure.
