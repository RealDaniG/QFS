# ATLAS API Reference

## Overview

The ATLAS API provides the interface for the P2P social layer, implementing the "Explain-This" philosophy directly in its endpoints.

## Core Endpoints

### `/explain`

* **Purpose**: Provides causal explanations for any system state or value.
* **Method**: `GET /explain/{entity_type}/{entity_id}`
* **Response**: `ExplanationResponse` (Trace of ledger events leading to current state).
* **Zero-Sim**: All explanations are verified against the deterministic `StorageEngine` replay.

### `/referral`

* **Purpose**: Manage the ledger-based referral graph.
* **Endpoints**:
  * `POST /referral/create_link`: Generate a deterministic referral code.
  * `POST /referral/accept`: Link a new user to a referrer (enforces anti-fraud caps).

### `/p2p` (Planned)

* **Purpose**: Secure messaging transport.
* **Status**: Currently relay-based, migrating to full Double Ratchet P2P.

## Authentication

All write endpoints require a valid Dilithium-5 signature from a verified wallet session.

## Error Handling

Errors return standard HTTP codes with a `VerificationResult` payload detailing the specific invariant violation (e.g. `REFERRAL_CAP_EXCEEDED`).
