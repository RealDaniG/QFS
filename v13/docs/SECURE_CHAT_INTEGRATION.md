# ATLAS Secure Chat Integration

**Version**: 13.9
**Status**: Implemented
**Module**: `v13.atlas.chat`

## Overview

The Secure Chat module provides deterministic, encrypted messaging capabilities for ATLAS. It supports persistent sessions, PQC-ready key negotiation, and economic integration via the QFS Ledger.

## Architecture

### Components

#### `ChatSessionManager` (`v13/atlas/chat/chat_session.py`)

- **Responsibility**: Manages lifecycle of chat sessions.
- **Key Methods**:
  - `create_session`: Deterministic ID generation.
  - `join_session`: Idempotent participant management.
  - `send_message`: Message distribution and event emission.

#### `ChatEvents` (`v13/atlas/chat/chat_events.py`)

- **Responsibility**: Emits `EconomicEvent`s for chat actions.
- **Events**:
  - `chat_created`: 1.0 FLX cost.
  - `message_sent`: 0.01 FLX cost.

#### `ChatModels` (`v13/atlas/chat/chat_models.py`)

- **Responsibility**: Pydantic models for strict typing.
- **Models**: `ChatSessionState`, `ChatParticipant`, `ChatMessage`.

## Critical Constraints & Zero-Sim Compliance

### 1. Deterministic IDs

- **Session ID**: `SHA256(owner_wallet + ":" + timestamp + ":QFS_CHAT")`
- **Message ID**: `SHA256(session_id + ":" + sender + ":" + sequence_num + ":" + timestamp)`

### 2. Privacy & Encryption

- **Content**: Messages are stored as `content_encrypted` (hex string). The system implies client-side encryption; the server stores the ciphertext.
- **PQC**: `pqc_signature` field provided for post-quantum authenticity proof.

### 3. Economic Model

- All actions producing state change emit `EconomicEvent`s using `CertifiedMath` and `BigNum128` for precise token accounting.

## Testing Strategy

- **Unit Tests**: `v13/tests/test_secure_chat.py` uses Real `CertifiedMath` to verify economics and logic.
- **Prototype**: `v13/atlas/chat/phase_v_prototype_chat.py` validates the full lifecycle (Create -> Join -> Message -> Reply -> End) with log integrity checks.
